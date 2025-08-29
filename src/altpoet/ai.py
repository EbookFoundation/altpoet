import base64
import logging

import requests
from anthropic import Anthropic

from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)

client = Anthropic(
    api_key=settings.ANTHROPIC_API_KEY,
)

#MODEL_NAME = "claude-3-opus-20240229"
MODEL_NAME = "claude-3-haiku-20240307"
def ai_agent():
    Agent = apps.get_model('altpoet', 'Agent')
    agent, created = Agent.objects.get_or_create(name=MODEL_NAME)
    return agent

def ai_alts(document):
    Alt = apps.get_model('altpoet', 'Alt')
    Img = apps.get_model('altpoet', 'Img')
    docnum = document.item
    imgs = Img.objects.filter(document__item=docnum)
    numimgs = imgs.count()
    logger.info(f'getting ai alt text for {numimgs} img elements in document {docnum}')
    done_urls = {}
    for img in imgs:
        # handle lines
        if img.image.x < 3 or img.image.y < 3:
            new_alt, created = Alt.objects.get_or_create(img=img, text='[decorative image]')
            continue
    
        img_url = img.image.url
        try:
            old_alt = Alt.objects.get(source=ai_agent(), img=img)
            logger.info(f'not over-writing alt {old_alt.id}, from {ai_agent().name} already exists')

            # we could, instead, have a criterion to override (there's a unique constraint)
            done_urls[img_url] = old_alt
            continue
        except Alt.DoesNotExist:
            new_alt = None
        
        # already done the image for another img
        if img_url in done_urls:
            done_alt = done_urls[img_url]
            new_alt, created = Alt.objects.get_or_create(
                img=img, text=done_alt.text, source=done_alt.source)
            continue
    
        # duplicate image in another book (same hash) 
        duplicates = Alt.objects.filter(img__image__hash=img.image.hash).exclude(img=img)
        # ... with a preferred alt
        for dupe in duplicates.filter(img__alt__isnull=False).order_by('-created'):
            new_alt, created = Alt.objects.get_or_create(
                img=img, text=dupe.text, source=dupe.source)
            break
        if new_alt:
            continue
        # ... or with same source as current
        for dupe in duplicates.filter(source=ai_agent()).order_by('-created'):
            new_alt, created = Alt.objects.get_or_create(
                img=img, text=dupe.text, source=dupe.source)
            break
        if new_alt:
            continue       
            
        try:
            image_req = requests.get(img_url)
            if image_req.status_code == 200:
                binary_data = image_req.content 
                base_64_encoded_data = base64.b64encode(binary_data)
                base64_string = base_64_encoded_data.decode('utf-8')
        except e:
            logger.exception(e)
            
        language = img.document.lang.split('-')[0]
        ext = img_url.split('.')[-1]
        if ext.lower() in {'jpg', 'jpeg'}:
            img_type = "image/jpeg"
        elif ext.lower() in {'png', }:
            img_type = "image/png"
        elif ext.lower() in {'svg', }:
            img_type = "image/svg+xml"
        elif ext.lower() in {'gif', }:
            img_type = "image/gif"
        else:
            img_type = "?"
    
        if img.image.x < 13  and img.image.y < 13:
            prompt = f"Describe this image, using language={language}. Be concise. Omit the preamble. It may be a single unicode character, if so just give the unicode character."
        else:
            prompt = f"Describe this image, using language={language} for someone who can't see it. Be concise. Omit the preamble."
        #prompt = f"Provide alt-text for this image, using language={language}.  Omit the preamble."
        #prompt = f"Give the likely type for this image. Choose from: 'drawing', 'photograph', 'book cover', 'decoration', 'text', 'figure' or 'other'. Then give alt-text for this image, using language={language}, omitting the preamble."
        message_list = [
            {
                "role": 'user',
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": img_type, "data": base64_string}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2048,
            messages=message_list,
            temperature=0.0
        )
        new_alt, created = Alt.objects.get_or_create(
            img=img, text=response.content[0].text, source=ai_agent())
        done_urls[img_url] = new_alt
    logger.info(f'returned {len(done_urls)} alts for document #{docnum}')
    return done_urls.values()
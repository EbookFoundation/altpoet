from django.conf import settings
from django.db import models


class Project(models.Model):
    ''' for example, Project Gutenberg '''
    
    # for example, "Project Gutenberg"
    name = models.CharField(max_length=80, null=False)

    # for example, "https://www.gutenberg.org"
    url = models.CharField(max_length=80, default="")

    # a template string for example, "/cache/epub/{item}/pg{item}-images.html"
    basepath = models.CharField(max_length=80, default="/{item)")


class Page(models.Model):
    ''' representation of a a book or a webpage '''

    #a project that the page is part of. if null, then the item must 
    project = models.ForeignKey("Project", null=True, related_name='pages',
        on_delete=models.SET_NULL)

    # the identifier within the project. Or the full URL if no project
    item = models.CharField(max_length=80, default="/{item)")
    
    # a url set by the base of the Page (Image urls are always relative to this base,
    # which in turn, is always relative the the page it is in
    base = models.CharField(max_length=80, default="")
    
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    
class Img(models.Model):
    # page that contains the image
    page = models.ForeignKey("Page", null=False, related_name='imgs',
        on_delete=models.CASCADE)

    # 
    image = models.ForeignKey("Image", null=True, related_name='images', on_delete=models.SET_NULL)


    # the id set on the img element
    img_id = models.CharField(max_length=80, null=True)

    # whether the associated image is normal (0), purely decorative (1), a cover (2),  
    # button (3), other? (-1)
    img_type = models.IntegerField(default=0)

    # whether the associated image is inside a figure element.
    is_figure = models.BooleanField
    
    # if the associated image is described by something else. If so, an id
    described_by = models.CharField(max_length=80, null=True)

    # this is the preferred alt
    alt = models.ForeignKey("Image", null=True, related_name='imgs', on_delete=models.SET_NULL)


class Image(models.Model):
    # always relative to the 'base' of the img base
    url = models.CharField(max_length=80)
    
    # hash of the image
    hash = models.CharField(max_length=32)


class Alt(models.Model):
    # alt text for the image
    text = models.CharField(max_length=1000, default="")
    
    # where did the alt text come from? if null, it came with the page
    source = models.ForeignKey("Agent", null=True, related_name='alts',  on_delete=models.SET_NULL)
    
    created = models.DateTimeField(auto_now_add=True, db_index=True)

class Agent(models.Model):
    # entity supplying the alt text
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, related_name='agents')    

    name = models.CharField(max_length=80, null=True) 

    created = models.DateTimeField(auto_now_add=True, db_index=True)
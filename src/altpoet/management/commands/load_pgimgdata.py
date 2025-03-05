from csv import DictReader, excel
from urllib.parse import urljoin

from django.core.management.base import BaseCommand
from django.db.utils import DataError

from altpoet import models 

class Command(BaseCommand):
    help = "load img data from csv"
    def add_arguments(self, parser):
        parser.add_argument('filename', help="filename")    

    def handle(self, filename, **options):
        (pg, created) = models.Project.objects.get_or_create(
            name="Project Gutenberg",
            url="https://www.gutenberg.org/",
            basepath="/cache/epub/{item}/pg{item}-images.html",
        )
        lineno = 0
        sheetreader = DictReader(open(filename,'rU'), dialect=excel)
        for altdata in sheetreader:
            lineno += 1
            try:
                (doc, created) = models.Document.objects.get_or_create(
                    project=pg,
                    item=altdata["pg_id"],
                )
                if created:
                    doc.base = urljoin(doc.project.url, altdata["url"])
                    doc.save()    
                (image, created) = models.Image.objects.get_or_create(
                    url = urljoin(doc.base, altdata["img_url"])
                )
                (img, created) = models.Img.objects.get_or_create(
                    document=doc,
                    img_id=altdata["img_id"],
                )
                if created:
                    img.image = image
                    img.is_figure = altdata["in_a_figure"] == True
                    img.save()
                (alt, created) = models.Alt.objects.get_or_create(
                    text=altdata["alt_txt"][:2000] if altdata["alt_txt"] else '',
                    img=img,
                )
            except DataError as de:
                self.stdout.write(f'Error {de} on line {lineno}')
                
        self.stdout.write(f"finished loading {models.Img.objects.all().count()} alts for {models.Document.objects.all().count()} docs")

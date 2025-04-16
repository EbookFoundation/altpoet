'''
load image data from the csv file at https://www.gutenberg.org/cache/epub/feeds/img_data.csv.gz

'''



from csv import DictReader, excel
from urllib.parse import urljoin

from django.core.management.base import BaseCommand
from django.db.utils import DataError

from altpoet import models 

innames = ['item', 'img_id', 'alt_txt', 'img_url', 'in_a_figure', 'x', 'y', 'len', 'hash']

class Command(BaseCommand):
    help = "load imgage data from csv"
    def add_arguments(self, parser):
        parser.add_argument('filename', help="filename")    

    def handle(self, filename, **options):
        def makeint(num):
            try:
                return int(num)
            except:
                return None
        (pg, created) = models.Project.objects.get_or_create(
            name="Project Gutenberg",
            url="https://www.gutenberg.org/",
            basepath="/cache/epub/{item}/pg{item}-images.html",
        )
        infilename = filename or 'img_data.csv' 
        lineno = 0
        sheetreader = DictReader(open(filename,'r'), dialect=excel, fieldnames=innames)
        for altdata in sheetreader:
            lineno += 1
            try:
                (doc, created) = models.Document.objects.get_or_create(
                    project=pg,
                    item=altdata["item"],
                )
                if created:
                    doc.base = urljoin(doc.project.url, pg.basepath.format(item=doc.item))
                    doc.save()    
                (image, created) = models.Image.objects.get_or_create(
                    url = urljoin(doc.base, altdata["img_url"])
                )
                image.x = makeint(altdata['x'])
                image.y = makeint(altdata['y'])
                image.filesize = makeint(altdata['len'])
                image.hash = altdata['hash']
                image.save()
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

        self.stdout.write(f"finished loading {lineno} alts for {models.Image.objects.all().count()} docs")

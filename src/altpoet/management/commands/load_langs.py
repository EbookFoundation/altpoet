'''
load lanf data from a csv file

'''

from csv import DictReader, excel

from django.core.management.base import BaseCommand
from django.db.utils import DataError

from altpoet import models 

innames = ['oid', 'item', 'lang']

class Command(BaseCommand):
    help = "load language data from csv"
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
        infilename = filename or 'data/mn_books_langs.csv' 
        lineno = 0
        sheetreader = DictReader(open(filename,'r'), dialect=excel, fieldnames=innames)
        for altdata in sheetreader:
            lineno += 1
            try:
                doc = models.Document.objects.get(
                    project=pg,
                    item=altdata["item"],
                )
                doc.lang = altdata['lang']
                doc.save()
            except models.Document.DoesNotExist:
                continue

        self.stdout.write(f"finished loading langs")

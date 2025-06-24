from django.core.management.base import BaseCommand

from altpoet.models import Document
from altpoet.ai import ai_alts

class Command(BaseCommand):
    help = "list common duplicate alt text"
    args = "<docnum>"
    def add_arguments(self, parser):
        parser.add_argument('docnum', nargs='?', type=str, help="PG book number")

    def handle(self, docnum, **options):
        try:
            doc = Document.objects.get(item=docnum)
        except Document.DoesNotExist:
            self.stdout.write(f"document {docnum} is not in the database")
            exit()
        new_alts = list(ai_alts(doc))
        self.stdout.write(f"{len(new_alts)} returned for document {docnum}")

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.utils import DataError

from altpoet import models 

class Command(BaseCommand):
    help = "list common duplicate alt text"

    def handle(self, **options):
        common_alts = models.Alt.objects.values('text').annotate(
            count=Count('text')
        ).order_by('-count')

        for alt in common_alts.filter(count__gte=10):
            self.stdout.write(f"{alt['count']}: \"{alt['text']}\"")

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from charsearch_app.models import Thread


class Command(BaseCommand):
    help = "Prune threads that are older than a certain number of days. This will permanently destroy the data! --days is a required parameter"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            action='store',
            type=int,
            dest='days',
            required=True,
            help='Prune threads older than this (measured in days)')

    def handle(self, *args, **options):
        self.prune_threads(options['days'])

    def prune_threads(days):
        killdate = datetime.now() - timedelta(days=days)
        to_prune = Thread.objects.filter(last_update__lte=killdate)
        for pruner in to_prune:
            print 'Removing [%s] thread that is expired past %s days' % (pruner.thread_title, days)
            if pruner.character:
                for skill in pruner.character.skills.all():
                    skill.delete()
                for standing in pruner.character.standings.all():
                    standing.delete()
                pruner.character.delete()
        to_prune.delete()

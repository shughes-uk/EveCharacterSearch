from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import now

from _utils import STUPID_OLDNAMELOOKUP, scrape_skills
from charsearch_app.models import Character, CharSkill, Skill, Thread


class Command(BaseCommand):
    help = "Rescrape eveboard for characters that have threads updated in the last X days"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            action='store',
            type=int,
            dest='limit',
            default=1,
            required=True,
            help='Refresh characters with threads updated in the last X days')
        parser.add_argument(
            '--staleness',
            action='store',
            type=int,
            dest='staleness',
            default=5,
            help='Required number of days since the last refresh')

    def handle(self, *args, **options):
        self.refresh_characters(options['limit'], options['staleness'])

    def refresh_characters(self, limit, staleness):
        staledate = datetime.now() - timedelta(days=staleness)
        update_limit = datetime.now() - timedelta(days=limit)
        updated_threads = Thread.objects.filter(last_update__gte=update_limit)
        stale_characters = Character.objects.filter(
            Q(last_update__lte=staledate) | Q(last_update=None), thread__in=updated_threads)
        for character in stale_characters:
            skills = scrape_skills(character.name, character.password)
            new_sp_total = 0
            for skill in skills:
                existing_skill = character.skills.filter(skill__name=skill[0])
                if len(existing_skill) > 0:
                    existing_skill[0].skill_points = skill[2]
                    existing_skill[0].level = skill[1]
                    new_sp_total += skill[2]
                    existing_skill[0].save()
                else:
                    cs = CharSkill()
                    cs.character = character
                    if skill[0] in STUPID_OLDNAMELOOKUP:
                        cs.skill = Skill.objects.filter(name=STUPID_OLDNAMELOOKUP[skill[0]])[0]
                    else:
                        cs.skill = Skill.objects.filter(name=skill[0])[0]
                    cs.level = skill[1]
                    cs.skill_points = skill[2]
                    cs.save()
                    character.skills.add(cs)
                    new_sp_total = +skill[2]
            character.total_sp = new_sp_total
            character.last_update = now()
            character.save()

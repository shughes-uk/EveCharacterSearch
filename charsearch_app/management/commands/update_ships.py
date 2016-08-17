import logging
import sqlite3
from xml.dom.minidom import parseString

from django.core.management.base import BaseCommand

from charsearch_app.models import RequiredSkill, Ship, Skill

logger = logging.getLogger("charsearch.update_ships")


class Command(BaseCommand):
    help = "Used for scraping the forums and optionally updating skills and corps from the eve api"

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        if verbosity == 0:
            logger.setLevel(logging.WARN)
        elif verbosity == 1:  # default
            logger.setLevel(logging.INFO)
        elif verbosity > 1:
            logger.setLevel(logging.DEBUG)
        if verbosity > 2:
            logger.setLevel(logging.DEBUG)
        update_ships()


def update_ships():
    ship_query = open('charsearch_app/management/commands/ship_query.sql').read()
    conn = sqlite3.connect('eve_online_latest.sqlite')
    c = conn.cursor()
    for row in c.execute(ship_query):
        #(u'Abaddon', ITEMID24692, u'Battleship', GROUPID27, u'Amarr Battleship', SKILL_REQUIRED_ID3339, LEVEL REQUIRED (FLOAT OR INT)1.0)
        required_skill, created = RequiredSkill.objects.get_or_create(
            typeID=row[5], level=int(row[6]), skill=Skill.objects.get(typeID=row[5]))
        ship, created = Ship.objects.get_or_create(name=row[0], itemID=row[1], groupName=row[2], groupID=row[3])
        if required_skill not in ship.required_skills.all():
            ship.required_skills.add(required_skill)
    conn.commit()
    for ship in Ship.objects.all():
        print ship.name, " | ", ship.groupName
        print "Required skills :"
        for skill in ship.required_skills.all():
            print '\t', skill.skill.name, skill.level
        print "---"

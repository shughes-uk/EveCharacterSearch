import logging
import urllib
from xml.dom.minidom import parseString

from django.core.management.base import BaseCommand

from charsearch_app.models import Skill

logger = logging.getLogger("charsearch.update_api")
api_site = 'https://api.eveonline.com'
skill_tree = '/eve/SkillTree.xml.aspx'


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
        grab_skills()


def grab_api(url, id=None, vcode=None, params={}):
    p = params
    if id and vcode:
        p['keyID'] = id
        p['vCode'] = vcode
    p = urllib.urlencode(p)
    request = urllib.urlopen(url, p)
    result = request.read()
    return parseString(result)


def grab_skills():
    print 'Grabbing latest skills from EVE API'
    skilltree = grab_api(api_site + skill_tree)
    rowset = skilltree.getElementsByTagName('rowset')
    skillgroups = rowset[0]
    for group in skillgroups.childNodes:
        if group.nodeType == 1:
            groupName = group.getAttribute('groupName')
            groupID = int(group.getAttribute('groupID'))
            skills = group.childNodes[1].childNodes
            for skill in skills:
                if skill.nodeType == 1:
                    skillName = skill.getAttribute('typeName')
                    skilltypeID = int(skill.getAttribute('typeID'))
                    existing = Skill.objects.filter(typeID=skilltypeID)
                    if len(existing) > 0:
                        s = existing[0]
                    else:
                        s = Skill()
                        print "New Skill : " + skill.getAttribute('typeName')
                    s.typeID = skilltypeID
                    s.name = skillName
                    # descriptions can be blank
                    description = skill.getElementsByTagName('description')[0]
                    if description.nodeType == 1:
                        description = ''
                    else:
                        description = skill.getElementsByTagName('description')[0].firstChild.nodeValue
                    s.description = description
                    s.rank = int(skill.getElementsByTagName('rank')[0].firstChild.nodeValue)
                    s.groupID = groupID
                    s.groupName = groupName
                    s.save()

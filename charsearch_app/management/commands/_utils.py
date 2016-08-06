import logging
import re
import urllib
import urllib2

from BeautifulSoup import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now

from charsearch_app.models import (Character, CharSkill, NPC_Corp, Skill, Standing)

logger = logging.getLogger("charsearch.utils")
STUPID_OLDNAMELOOKUP = {
    'Production Efficiency': 'Material Efficiency',
    'Capital Energy Emission Systems': 'Capital Capacitor Emission Systems'
}

R_SKILL_NAME = r"(.+[\w'-]+) / Rank"
R_SKILL_LEVEL_SP = r"Level: ([0-6]) / SP: ([0-9]+(,[0-9]+)*)"
EVEBOARD_URL = 'http://eveboard.com/pilot/%s'


def buildchar(charname, skills, standings, password):
    logger.debug("Building new character, %s" % charname)
    char = Character()
    char.name = charname
    char.total_sp = 0
    char.save()
    for skill in skills:
        cs = CharSkill()
        cs.character = char
        if skill[0] in STUPID_OLDNAMELOOKUP:
            cs.skill = Skill.objects.filter(name=STUPID_OLDNAMELOOKUP[skill[0]])[0]
        else:
            cs.skill = Skill.objects.filter(name=skill[0])[0]
        cs.level = skill[1]
        cs.skill_points = skill[2]
        cs.save()
        logger.debug("Created CharSkill for {0}".format(skill))
        char.skills.add(cs)
        char.total_sp += skill[2]
    for standing in standings:
        try:
            corp = NPC_Corp.objects.get(name=standing[0])
        except ObjectDoesNotExist:
            corp = NPC_Corp.objects.create(name=standing[0])
            corp.save()
            logger.info('Created new npc corp {0}'.format(standing[0]))
            logger.info('Adding standing to all old characters, set to 0'.format(standing[0]))
            for char in Character.objects.all():
                try:
                    char.standings.get(corp=corp)
                except:
                    char.standings.add(Standing.objects.create(corp=corp, value=0))
                    char.save()

        char.standings.add(Standing.objects.create(corp=corp, value=standing[1]))
    if standings:
        for corp in NPC_Corp.objects.all():
            try:
                char.standings.get(corp=corp)
            except ObjectDoesNotExist:
                char.standings.add(Standing.objects.create(corp=corp, value=0))
    char.last_update = now()
    char.password = password
    char.save()
    logger.debug("Character built {0}".format(charname))
    return char


def scrape_skills(charname, password=None):
    logger.debug("Scraping eveboard skills for {0}".format(charname))
    soup = try_get_soup_main(charname, password=password)
    if soup:
        # grab all the skill rows
        skills = []
        for x in soup.findAll('td', attrs={'class': 'dotted', 'height': 20}):
            spans = x.findAll('span')
            if len(spans) == 1:  # max level  skills
                contents = spans[0].string.strip()
            elif len(spans) == 2:  # skill currently in training have two spans
                contents = spans[0].string.strip()
            elif len(
                    spans) == 3:  # skill currently in training and also max rank have three spans, not sure how this is possible but it is
                contents = spans[1].string.strip()
            elif x.string:  # non max rank skills
                contents = x.string.strip()
            else:
                logger.warn("Found an eveboard skill td we couldn't parse")
                logger.warn(str(x))
                contents = ''
            skill_match = re.search(R_SKILL_NAME, contents)
            if skill_match:
                skill_name = skill_match.group(1)
                level_sp = re.search(R_SKILL_LEVEL_SP, contents)
                level = int(level_sp.group(1))
                sp = int(level_sp.group(2).replace(',', ''))
                skills.append((skill_name, level, sp))
        logger.debug("Scraping eveboard for {0} suceeded, have {1} skills".format(charname, len(skills)))
        return skills
    else:
        logger.debug("Scraping eveboard for {0} failed".format(charname))
        return None


def scrape_standings(charname, password=None):
    standings = []
    logger.debug("Scraping eveboard standings for {0}".format(charname))
    soup = try_get_soup_standings(charname, password=password)
    if soup:
        # grab security status
        ssrow = soup.find('td', text='Security Status')
        if ssrow:
            ssrow = ssrow.parent.parent
            # rip out a span that messes things up
            ssrow.span.extract()
            security_status = float(ssrow('td')[1].text)
            standings.append(('-Security Status-', security_status))
            # some characters don't have standings available
            the_tables = soup.findAll(
                'table', attrs={"width": "100%",
                                "border": "0",
                                "cellpadding": "0",
                                "cellspacing": "0"})
            if len(the_tables) == 6:
                for standing_row in the_tables[5].findAll('tr'):
                    standings.append((standing_row('td')[1].text, float(standing_row('td')[2].text)))
        logger.debug("Scraping eveboard skills for {0} suceeded".format(charname))
        return standings
    else:
        logger.debug("Scraping eveboard skills for {0} failed".format(charname))
        return None


def try_get_soup_main(charname, password=None):
    url = EVEBOARD_URL % charname
    soup = fetch_soup(url, password)
    if password_required(soup):
        return None
    else:
        return soup


def try_get_soup_standings(charname, password=None):
    url = EVEBOARD_URL % charname
    url += '/standings'
    soup = fetch_soup(url, password)
    if password_required(soup):
        return None
    else:
        return soup


def password_required(soup):
    ispassworded = soup.findAll('input', attrs={'type': 'password'})
    if len(ispassworded) > 0:
        return True
    else:
        return False


def fetch_soup(url, password=None):
    if password:
        data = urllib.urlencode({'pw': password})
        req = urllib2.Request(url, data)
    else:
        req = urllib2.Request(url)
    html = urllib2.urlopen(req).read()
    return BeautifulSoup(html)

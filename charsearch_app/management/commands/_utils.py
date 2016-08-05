import re
import urllib
import urllib2

from BeautifulSoup import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist

from charsearch_app.models import (Character, CharSkill, NPC_Corp, Skill, Standing)

STUPID_OLDNAMELOOKUP = {
    'Production Efficiency': 'Material Efficiency',
    'Capital Energy Emission Systems': 'Capital Capacitor Emission Systems'
}

R_SKILL_NAME = r"(.+[\w'-]+) / Rank"
R_SKILL_LEVEL_SP = r"Level: ([0-6]) / SP: ([0-9]+(,[0-9]+)*)"
EVEBOARD_URL = 'http://eveboard.com/pilot/%s'


def buildchar(charname, skills, standings):
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
        char.skills.add(cs)
        char.total_sp += skill[2]
    for standing in standings:
        try:
            corp = NPC_Corp.objects.get(name=standing[0])
        except ObjectDoesNotExist:
            corp = NPC_Corp.objects.create(name=standing[0])
            print 'Created new npc corp', standing[0]
            corp.save()
            global NEW_CORPS
            NEW_CORPS.append(corp)
        char.standings.add(Standing.objects.create(corp=corp, value=standing[1]))
    if standings:
        for corp in NPC_Corp.objects.all():
            try:
                char.standings.get(corp=corp)
            except ObjectDoesNotExist:
                char.standings.add(Standing.objects.create(corp=corp, value=0))
    char.save()
    return char


def scrape_skills(charname, password=None):
    soup = get_soup_eveboard(charname, password=password)
    # grab all the skill rows
    skills = []
    for x in soup.findAll('td', attrs={'class': 'dotted', 'height': 20}):
        spans = x.findAll('span')
        if len(spans) > 0:
            contents = spans[0].string.strip()
        else:
            if x.string:
                contents = x.string.strip()
            else:
                contents = ''
        skill_match = re.search(R_SKILL_NAME, contents)
        if skill_match:
            skill_name = skill_match.group(1)
            level_sp = re.search(R_SKILL_LEVEL_SP, contents)
            level = int(level_sp.group(1))
            sp = int(level_sp.group(2).replace(',', ''))
            skills.append((skill_name, level, sp))
    return skills


def scrape_standings(charname, password=None):
    standings = []
    soup = get_soup_eveboard(charname, standings=True, password=password)
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
    return standings


def password_test(charname, password=None):
    if password:
        data = urllib.urlencode({'pw': password})
        req = urllib2.Request(EVEBOARD_URL % charname, data)
        html = urllib2.urlopen(req).read()
    else:
        html = urllib2.urlopen(EVEBOARD_URL % charname).read()
    soup = BeautifulSoup(html)
    # check if it requires a password
    ispassworded = soup.findAll('input', attrs={'type': 'password'})
    if len(ispassworded) > 0:
        return True


def get_soup_eveboard(charname, standings=False, password=None):
    url = EVEBOARD_URL % charname
    if standings:
        url += '/standings'
    if password:
        data = urllib.urlencode({'pw': password})
        req = urllib2.Request(url, data)
    else:
        req = urllib2.Request(url)
    html = urllib2.urlopen(req).read()
    return BeautifulSoup(html)

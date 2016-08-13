import locale
import logging
import re
import urllib
import urllib2

from BeautifulSoup import BeautifulSoup
from django.utils.timezone import now

from charsearch_app.models import (Character, CharSkill, NPC_Corp, Skill,
                                   Standing)

logger = logging.getLogger("charsearch.utils")
STUPID_OLDNAMELOOKUP = {
    'Production Efficiency': 'Material Efficiency',
    'Capital Energy Emission Systems': 'Capital Capacitor Emission Systems'
}

R_SKILL_NAME = r"(.+[\w'-]+) / Rank"
R_SKILL_LEVEL_SP = r"Level: ([0-6]) / SP: ([0-9]+(,[0-9]+)*)"
EVEBOARD_URL = 'http://eveboard.com/pilot/%s'


def buildchar(char_dict):
    logger.debug("Building new character, %s" % char_dict['charname'])
    char = Character()
    char.name = char_dict['charname']
    char.total_sp = 0
    char.save()
    for skill in char_dict['skills']:
        cs = CharSkill()
        cs.character = char
        if skill[0] in STUPID_OLDNAMELOOKUP:
            cs.skill = Skill.objects.filter(name=STUPID_OLDNAMELOOKUP[skill[0]])[0]
        else:
            cs.skill = Skill.objects.filter(name=skill[0])[0]
        cs.level = skill[1]
        cs.skill_points = skill[2]
        cs.typeID = cs.skill.typeID
        cs.save()
        logger.debug("Created CharSkill for {0}".format(skill))
        char.skills.add(cs)
        char.total_sp += skill[2]
    for standing in char_dict['standings']:
        corp = NPC_Corp.objects.filter(name=standing[0]).first()
        if corp:
            char.standings.add(Standing.objects.create(corp=corp, value=standing[1]))
        else:
            corp = NPC_Corp.objects.create(name=standing[0])
            corp.save()
            char.standings.add(Standing.objects.create(corp=corp, value=standing[1]))
            logger.info('Created new npc corp {0}'.format(standing[0]))
    char.last_update = now()
    char.unspent_skillpoints = char_dict['stats']['unallocated_sp']
    char.remaps = char_dict['stats']['remaps']
    char.password = char_dict['password'] or ''
    char.save()
    logger.debug("Character built {0}".format(char_dict['charname']))
    return char


def scrape_character(charname, password=None):
    logger.debug("Scraping eveboard skills for {0}".format(charname))
    main_soup = try_get_soup_main(charname, password=password)
    if main_soup:
        # grab all the skills
        skills = parse_skills(main_soup)
        if skills:
            stats = parse_stat_table(main_soup)
            logger.debug("Scraping eveboard for {0} finished, have {1} skills".format(charname, len(skills)))
            logger.debug("Scraping eveboard standings for {0}".format(charname))
            standing_soup = try_get_soup_standings(charname, password=password)
            if standing_soup:
                standings = parse_standings(standing_soup)
                if standings:
                    logger.debug("Parsing standings for {0} suceeded".format(charname))
                    return {'skills': skills, 'standings': standings, 'stats': stats}
                else:
                    logger.debug("Got skills but couldn't get standings for {0}".format(charname))
                    return {'skills': skills, 'standings': [], 'stats': stats}

            else:
                logger.debug("Got skills but couldn't get standings for {0}".format(charname))
                return {'skills': skills, 'standings': [], 'stats': stats}
    else:
        logger.debug("Scraping eveboard for {0} failed".format(charname))
        return None


def parse_stat_table(soup):
    stat_table_soup = soup.find('td', attrs={'class': "title"}).findParent('table')
    unallocated_sp_str = stat_table_soup.find('td', text='Unallocated').findNext('td').text
    unallocated_sp_str = unallocated_sp_str.replace(',', '')
    if unallocated_sp_str:
        unallocated_sp = locale.atoi(unallocated_sp_str)
    else:
        unallocated_sp = 0
    remaps_str = stat_table_soup.find('td', text='Remaps').findNext('td').text
    if remaps_str:
        remaps = locale.atoi(unallocated_sp_str)
    else:
        remaps = 0
    return {'unallocated_sp': unallocated_sp, 'remaps': remaps}


def parse_skills(skill_soup):
    skills = []
    for x in skill_soup.findAll('td', attrs={'class': 'dotted', 'height': 20}):
        spans = x.findAll('span')
        if len(spans) == 1:  # max level  skills
            contents = spans[0].string.strip()
        elif len(spans) == 2:  # skill currently in training have two spans
            contents = spans[0].string.strip()
        elif len(spans) == 3:
            # skill currently in training and also max rank
            # have three spans, not sure how this is possible but it is
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
    return skills


def parse_standings(standing_soup):
    standings = []
    # grab security status
    ssrow = standing_soup.find('td', text='Security Status')
    if ssrow:
        ssrow = ssrow.parent.parent
        # rip out a span that messes things up
        ssrow.span.extract()
        security_status = float(ssrow('td')[1].text)
        standings.append(('-Security Status-', security_status))
        # some characters don't have standings available
        the_tables = standing_soup.findAll(
            'table', attrs={"width": "100%",
                            "border": "0",
                            "cellpadding": "0",
                            "cellspacing": "0"})
        if len(the_tables) == 6:
            for standing_row in the_tables[5].findAll('tr'):
                standings.append((standing_row('td')[1].text, float(standing_row('td')[2].text)))
        return standings
    else:
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

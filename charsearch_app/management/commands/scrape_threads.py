import re
import urllib2
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from django.core.management.base import BaseCommand

from _utils import buildchar, password_test, scrape_skills, scrape_standings
from charsearch_app.models import Character, Standing, Thread

NEW_CORPS = []


class Command(BaseCommand):
    help = "Scrape the forums for new sale threads and to update old threads"

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            action='store',
            type=int,
            dest='pages',
            default=1,
            help='The number of pages of the bazaar to scrape')

    def handle(self, *args, **options):
        scrape_eveo(options['pages'])


R_POSTID = r't=([0-9]+)'
R_PILOT_NAME = r"eveboard.com/pilot\/([\w'-]+)"
RS_PWD = [re.compile(r"[pP]\w*[wW]\w*\s*\w*[=\-\:]*\s*([\w\d]*)"),
          re.compile(r"[pP][aA][sS]\w*\s*\w*[=\-\:]*\s*([\w\d]*)")]
FORUM_URL = 'https://forums.eveonline.com/'
BAZAAR_URL = 'default.aspx?g=topics&f=277&p=%i'
THREAD_URL = 'default.aspx?g=posts&t=%i&find=unread'


def get_bazaar_page(pagenumber):
    html = urllib2.urlopen(FORUM_URL + BAZAAR_URL % pagenumber).read()
    soup = BeautifulSoup(html)
    threads = []
    for x in soup.findAll('a', attrs={'class': 'main nonew'}):
        title = x.string
        threadID = re.search(R_POSTID, x['href']).group(1)
        threads.append({'title': title, 'threadID': int(threadID)})
    return threads


def scrape_thread(thread):
    html = urllib2.urlopen(FORUM_URL + THREAD_URL % thread['threadID']).read()
    thread_soup = BeautifulSoup(html)
    first_post = thread_soup.findAll('div', attrs={'id': 'forum_ctl00_MessageList_ctl00_DisplayPost1_MessagePost1'})[0]
    eveboard_link = first_post.find('a', href=re.compile('.*eveboard.com/pilot/.*'))
    if eveboard_link:
        pilot_name = eveboard_link['href'].split('/pilot/')[1]
        if password_test(pilot_name):
            # clean up tags and bbcode
            for a in first_post('a'):
                a.extract()
            for img in first_post('img'):
                img.extract()
            first_post = first_post.prettify().replace('<br />', ' ').replace('\n', '').replace('<i>', '').replace(
                '</i>', '').replace('<b>', '').replace('</b>', '')
            # find them passwords!
            passwords = []
            for regs in RS_PWD:
                potential_passwords = regs.finditer(first_post)
                for match in potential_passwords:
                    if match.group(1) not in passwords:
                        passwords.append(match.group(1))
            for password in passwords:
                if not password_test(pilot_name, password):
                    return pilot_name, password
            return None, None
        else:
            return pilot_name, None
    else:
        return None, None


def scrape_eveo(num_pages):
    threads = []
    for x in range(1, num_pages + 1):
        threads.extend(get_bazaar_page(x))
    for thread in threads:
        existing = Thread.objects.filter(thread_id=thread['threadID'])
        if len(existing) > 0:
            existing[0].last_update = datetime.now()
            existing[0].thread_title = thread['title']
            existing[0].save()
            continue
        else:
            charname, password = scrape_thread(thread)
            if charname:
                skills = scrape_skills(charname, password)
                standings = scrape_standings(charname, password)
                t = Thread()
                t.thread_id = thread['threadID']
                t.last_update = datetime.now()
                t.thread_text = ''
                t.thread_title = thread['title']
                if skills:
                    t.blacklisted = False
                    character = buildchar(charname, skills, standings)
                    t.character = character
                    character.password = password
                    character.save()
                    t.save()
                else:
                    t.blacklisted = True
                    t.save()
    if NEW_CORPS:
        for char in Character.objects.all():
            for corp in NEW_CORPS:
                try:
                    char.standings.get(corp=corp)
                except:
                    char.standings.add(Standing.objects.create(corp=corp, value=0))
                    char.save()

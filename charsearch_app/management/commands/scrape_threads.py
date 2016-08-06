import logging
import re
import urllib2

from BeautifulSoup import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from _utils import logger as utils_logger
from _utils import buildchar, scrape_skills, scrape_standings
from charsearch_app.models import Thread

logger = logging.getLogger("charsearch.scrape_threads")


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
        verbosity = options.get('verbosity')
        if verbosity == 0:
            utils_logger.setLevel(logging.WARN)
            logger.setLevel(logging.WARN)
        elif verbosity == 1:  # default
            utils_logger.setLevel(logging.INFO)
            logger.setLevel(logging.INFO)
        elif verbosity > 1:
            utils_logger.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        if verbosity > 2:
            utils_logger.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        scrape_eveo(options['pages'])


R_POSTID = r't=([0-9]+)'
R_PILOT_NAME = r"eveboard.com/pilot\/([\w'-]+)"
RS_PWD = [re.compile(r"[pP]\w*[wW]\w*\s*\w*[=\-\:]*\s*([\w\d]*)"),
          re.compile(r"[pP][aA][sS]\w*\s*\w*[=\-\:]*\s*([\w\d]*)")]
FORUM_URL = 'https://forums.eveonline.com/'
BAZAAR_URL = 'default.aspx?g=topics&f=277&p=%i'
THREAD_URL = 'default.aspx?g=posts&t=%i&find=unread'


def get_bazaar_page(pagenumber):
    logger.debug("Scraping grabbing bazaar page {0}".format(pagenumber))
    html = urllib2.urlopen(FORUM_URL + BAZAAR_URL % pagenumber).read()
    soup = BeautifulSoup(html)
    threads = []
    for x in soup.findAll('a', attrs={'class': 'main nonew'}):
        title = x.string
        threadID = re.search(R_POSTID, x['href']).group(1)
        threads.append({'title': title, 'threadID': int(threadID)})
        logger.debug("Found thread title : {0} | threadID : {1}".format(title.rstrip(), threadID))
    return threads


def scrape_thread(thread):
    logger.debug("Scraping thread {0}".format(thread))
    html = urllib2.urlopen(FORUM_URL + THREAD_URL % thread['threadID']).read()
    thread_soup = BeautifulSoup(html)
    first_post = thread_soup.findAll('div', attrs={'id': 'forum_ctl00_MessageList_ctl00_DisplayPost1_MessagePost1'})[0]
    eveboard_link = first_post.find('a', href=re.compile('.*eveboard.com/pilot/.*'))
    if eveboard_link:
        logger.debug("Found eveboard link {0}".format(eveboard_link))
        pilot_name = eveboard_link['href'].split('/pilot/')[1]
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
                    logger.debug("Found eveboard password {0}".format(match.group(1)))
                    passwords.append(match.group(1))
        if passwords:
            for password in passwords:
                skills = scrape_skills(pilot_name, password)
                if skills:
                    return pilot_name, skills, password
            logger.debug("Password didin't work trying without")
            return pilot_name, scrape_skills(pilot_name), None
        else:
            logger.debug("No passwords found trying without")
            return pilot_name, scrape_skills(pilot_name), None
    else:
        logger.debug("Could not find eveboard link")
        return None, None, None


def scrape_eveo(num_pages):
    threads = []
    for x in range(1, num_pages + 1):
        threads.extend(get_bazaar_page(x))
    for thread in threads:
        existing = Thread.objects.filter(thread_id=thread['threadID'])
        if len(existing) > 0:
            existing[0].last_update = now()
            existing[0].thread_title = thread['title']
            existing[0].save()
            continue
        else:
            t = Thread()
            t.thread_id = thread['threadID']
            t.last_update = now()
            t.thread_text = ''
            t.thread_title = thread['title']
            charname, skills, password = scrape_thread(thread)
            if skills:
                standings = scrape_standings(charname, password)
                logger.debug("Got character for thread".format(thread))
                t.blacklisted = False
                character = buildchar(charname, skills, standings, password)
                t.character = character
                t.save()
            else:
                logger.debug("Failed to get character for thread, blacklisting".format(thread))
                t.blacklisted = True
                t.save()

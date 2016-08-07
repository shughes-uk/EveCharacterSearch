import logging
import re
import urllib2

from BeautifulSoup import BeautifulSoup
from dateutil import parser
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import now

from _utils import logger as utils_logger
from _utils import buildchar, scrape_character
from charsearch_app.models import Thread, ThreadTitle

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
RS_PWD = [re.compile(r"[pP][wW][\w]*\s*[=\-\:]*\s*([\w]*)"), re.compile(r"[pP][aA][sS][\w]*\s*[=\-\:]*\s*([\w]*)")]
FORUM_URL = 'https://forums.eveonline.com/'
BAZAAR_URL = 'default.aspx?g=topics&f=277&p=%i'
THREAD_URL = 'default.aspx?g=posts&t=%i&find=unread'


def get_bazaar_page(pagenumber):
    logger.debug("Scraping grabbing bazaar page {0}".format(pagenumber))
    html = urllib2.urlopen(FORUM_URL + BAZAAR_URL % pagenumber).read()
    soup = BeautifulSoup(html)
    threads = []
    for thread_soup in soup.findAll('tr', attrs={'class': ['topicRow post', 'topicRow_Alt post_alt']}):
        title_soup = thread_soup.find('a', attrs={'class': ['main nonew', 'main topic_new', 'main locked']})
        title = title_soup.string
        threadID = re.search(R_POSTID, title_soup['href']).group(1)
        last_post_str = thread_soup.find('td', attrs={'class': 'topicLastPost smallfont'}).next
        last_post_dt = parser.parse(last_post_str)
        last_post_dt = timezone.make_aware(last_post_dt, timezone.get_current_timezone())
        threads.append({'title': title, 'threadID': int(threadID), 'lastPost': last_post_dt})
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
            passwords.append('1234')  # append the most commonly used password
            for password in passwords:
                scraped_info = scrape_character(pilot_name, password)
                if scraped_info:
                    scraped_info.update({'charname': pilot_name, 'password': password})
                    return scraped_info
            logger.debug("Password didin't work trying without")
            scraped_info = scrape_character(pilot_name, None)
            if scraped_info:
                scraped_info.update({'charname': pilot_name, 'password': None})
                return scraped_info
            else:
                return None
        else:
            logger.debug("No passwords found trying without")
            scraped_info = scrape_character(pilot_name, None)
            if scraped_info:
                scraped_info.update({'charname': pilot_name, 'password': None})
                return scraped_info
            else:
                return None

    else:
        logger.debug("Could not find eveboard link")
        return None


def scrape_eveo(num_pages):
    threads = []
    for x in range(1, num_pages + 1):
        threads.extend(get_bazaar_page(x))
    for thread in threads:
        existing_thread = Thread.objects.filter(thread_id=thread['threadID']).first()
        if existing_thread:
            if existing_thread.last_update != thread['lastPost']:
                existing_thread.last_update = thread['lastPost']
            if existing_thread.thread_title != thread['title']:
                old_title = ThreadTitle(title=thread['title'], date=now())
                old_title.save()
                existing_thread.title_history.add(old_title)
                existing_thread.thread_title = thread['title']
            existing_thread.save()
        else:
            t = Thread(
                thread_id=thread['threadID'],
                last_update=thread['lastPost'],
                thread_text='',
                thread_title=thread['title'])
            char_dict = scrape_thread(thread)
            if char_dict:
                logger.debug("Got character for thread {0}".format(thread['threadID']))
                t.blacklisted = False
                character = buildchar(char_dict)
                t.character = character
                t.save()
            else:
                logger.debug("Failed to get character for thread, blacklisting".format(thread))
                t.blacklisted = True
                t.save()

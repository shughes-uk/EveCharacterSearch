import urllib
from xml.dom.minidom import parseString
from django.core.management.base import BaseCommand, CommandError
from bazaar.models import *
from datetime import datetime , timedelta
from BeautifulSoup import BeautifulSoup
import urllib2
import re
import time

api_site = 'https://api.eveonline.com'

skill_tree = '/eve/SkillTree.xml.aspx'

class Command(BaseCommand):
    def handle(self, *args, **options):
        grab_skills()
        scrape_eveo()
        prune_threads()


def grab_api(url,id=None,vcode=None,params=None):
    if params == None:
        params = {}
    p = params
    if id and vcode:
        p['keyID'] = id
        p['vCode'] = vcode
    p = urllib.urlencode(p)
    request = urllib.urlopen(url,p)
    result = request.read()
    return parseString(result)

def grab_skills():
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
                    s.typeID = skilltypeID
                    s.name = skillName
                    #descriptions can be blank
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

def prune_threads():
    killdate = datetime.now() - timedelta(days=14)
    to_prune = Thread.objects.filter(last_update__lte=killdate)
    for pruner in to_prune:
        if pruner.character:
            pruner.character.delete()
    to_prune.delete()



R_POSTID = r't=([0-9]+)'
R_PILOT_NAME = r"pilot\/([\w'-]+)"
R_SKILL_NAME = r"(.+[\w'-]+) / Rank"
R_SKILL_LEVEL_SP = r"Level: ([0-6]) / SP: ([0-9]+(,[0-9]+)*)"
FORUM_URL = 'https://forums.eveonline.com/'
BAZAAR_URL = 'default.aspx?g=topics&f=277'
THREAD_URL = 'default.aspx?g=posts&t=%i&find=unread'
EVEBOARD_URL = 'http://eveboard.com/pilot/%s'

def get_first_page():
    html = urllib2.urlopen(FORUM_URL + BAZAAR_URL).read()
    soup = BeautifulSoup(html)
    threads = []
    for x in soup.findAll('a',attrs={'class':'main nonew'}):
        title = x.string
        threadID = re.search(R_POSTID,x['href']).group(1)
        threads.append( {'title':title,'threadID': int(threadID)} )
    return threads

def scrape_eveboard(charname):
    html = urllib2.urlopen(EVEBOARD_URL %charname).read()
    soup = BeautifulSoup(html)
    #check if it requires a password
    ispassworded = soup.findAll('input',attrs={'type':'password'})
    if len(ispassworded) > 0 :
        return None
    #grab all the skill rows
    skills = []
    for x in soup.findAll('td',attrs={'class':'dotted','height':20 , 'style':''}):
        spans = x.findAll('span')
        if len(spans) > 0:
            contents = spans[0].string.strip()
        else:
            contents =  x.string.strip()
        skill_name = re.search(R_SKILL_NAME,contents).group(1)
        level_sp = re.search(R_SKILL_LEVEL_SP,contents)
        level = int(level_sp.group(1))
        sp = int(level_sp.group(2).replace(',',''))
        skills.append((skill_name , level , sp))
    return skills

def scrape_thread(thread):
    html = urllib2.urlopen(FORUM_URL + THREAD_URL %thread['threadID']).read()
    thread_soup = BeautifulSoup(html)
    first_post = thread_soup.findAll('div',attrs={ 'id':'forum_ctl00_MessageList_ctl00_DisplayPost1_MessagePost1' })[0]
    eveboard_links = first_post.findAll('a')
    if eveboard_links:
        for link in eveboard_links:
            if link:
                #just grab the first eveboard link for now
                #handle multiple characters in one thread later...                
                pilot_name = re.search(R_PILOT_NAME,eveboard_links[0]['href'])
                if pilot_name:
                    return pilot_name.group(1)
    else:
        return None

def buildchar(charname,skills):
    char = Character()
    char.name = charname
    char.save()
    for skill in skills:
        cs = CharSkill()
        cs.character = char
        cs.skill = Skill.objects.filter(name=skill[0])[0]
        cs.level = skill[1]
        cs.skill_points = skill[2]
        cs.save()
        char.skills.add(cs)
    char.save()
    return char


def scrape_eveo():
    threads = get_first_page()
    for thread in threads:
        existing = Thread.objects.filter(thread_id=thread['threadID'])
        if len(existing) > 0:
            existing[0].last_update = datetime.now()
            existing[0].save()
            continue
        else:
            charname = scrape_thread(thread)
            if charname:
                skills = scrape_eveboard(charname)
                t = Thread()
                t.thread_id = thread['threadID']
                t.last_update = datetime.now()
                t.thread_text = ''
                t.thread_title = thread['title']
                if skills:
                    t.blacklisted = False
                    character = buildchar(charname,skills)
                    t.character = character
                    t.save()
                else:
                    t.blacklisted = True
                    t.save()
            
if __name__ == '__main__':
    scrape_eveo()
    
    
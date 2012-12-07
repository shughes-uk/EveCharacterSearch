from BeautifulSoup import BeautifulSoup
import urllib2
import re
import time

R_POSTID = r't=([0-9]+)'
FORUM_URL = 'https://forums.eveonline.com/'
BAZAAR_URL = 'default.aspx?g=topics&f=277'
THREAD_URL = 'default.aspx?g=posts&t=%i&find=unread'

html = urllib2.urlopen(FORUM_URL + BAZAAR_URL).read()
soup = BeautifulSoup(html)
threads = []
for x in soup.findAll('a',attrs={'class':'main nonew'}):
	title = x.string
	threadID = re.search(R_POSTID,x['href']).group(1)
	threads.append( {'title':title,'threadID': int(threadID)} )

for thread in threads:
	html = urllib2.urlopen(FORUM_URL + THREAD_URL %thread['threadID']).read()
	thread_soup = BeautifulSoup(html)
	first_post = thread_soup.findAll('div',attrs={ 'id':'forum_ctl00_MessageList_ctl00_DisplayPost1_MessagePost1' })[0]
	eveboard_link = first_post.findAll('a')
	print eveboard_link
import os
import sys
sys.path.append('C:\Users\samlaptop\Documents\GitHub\\bazaarscraper')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bazaarscraper.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
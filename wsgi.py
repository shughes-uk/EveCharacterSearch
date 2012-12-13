import os
import sys
sys.path.append('/home/sam/ECS')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bazaarscraper.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
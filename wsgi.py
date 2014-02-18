import os
import sys
#import bazaarscraper.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazaarscraper.settings')

#raise(Exception(str(sys.path)))

from django.core.wsgi import get_wsgi_application

sys.path.append('/home/teabiscuit/webapps/eve/ECS/')


application = get_wsgi_application()

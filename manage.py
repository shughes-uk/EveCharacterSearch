#!/usr/bin/env python
import sys,os

import bazaarscraper.settings

if __name__ == "__main__":
    sys.path.append('/home/teabiscuit/webapps/eve/bazaarscraper')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bazaarscraper.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

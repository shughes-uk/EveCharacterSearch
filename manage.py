#!/usr/bin/env python
import sys
sys.path.append('C:\Users\samlaptop\Documents\GitHub\\bazaarscraper')
from django.core.management import execute_manager

import bazaarscraper.settings

if __name__ == "__main__":
    execute_manager(bazaarscraper.settings)

#!/usr/bin/env python
import sys
sys.path.append('/home/sam/ESCS')
from django.core.management import execute_manager

import bazaarscraper.settings

if __name__ == "__main__":
    execute_manager(bazaarscraper.settings)

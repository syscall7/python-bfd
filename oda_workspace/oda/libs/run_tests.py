#!/usr/bin/env python
# EASY-INSTALL-ENTRY-SCRIPT: 'nose==1.3.1','console_scripts','nosetests'
__requires__ = 'nose==1.3.1'
import sys

from pkg_resources import load_entry_point

import os.path
import sys
PROJECT_DIR = os.path.dirname(__file__) # this is not Django setting.
sys.path.insert(0, os.path.join(PROJECT_DIR, "../.."))

if __name__ == '__main__':
    sys.exit(
        load_entry_point('nose==1.3.1', 'console_scripts', 'nosetests')()
    )

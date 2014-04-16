#!/usr/bin/env python
# EASY-INSTALL-ENTRY-SCRIPT: 'nose==1.3.1','console_scripts','nosetests'
__requires__ = 'nose==1.3.1'

import sys
import os

from pkg_resources import load_entry_point


if __name__ == '__main__':

    sys.path[0] = os.path.dirname(os.path.abspath(__file__)) + "/.."
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    sys.exit(
        load_entry_point('nose==1.3.1', 'console_scripts', 'nosetests')()
    )

import os
import sys

sys.stdout = sys.stderr

path = '/var/www/oda'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'oda_python.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

import os
import sys
import site

sys.stdout = sys.stderr

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/var/www/oda2/env/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
path = '/var/www/oda2/webapp'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'oda_python.settings.production'

# Activate your virtual env
activate_env=os.path.expanduser("/var/www/oda2/env/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


import os
from django.core.wsgi import get_wsgi_application

try:
    execfile(os.path.join('/etc/oda/settings.py'))
except:
    print('Missing /etc/oda/settings.py, assuming environment variables are set ...')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oda.settings.production")
application = get_wsgi_application()

import os
from django.core.wsgi import get_wsgi_application

execfile(os.path.join('/etc/oda/settings.py'))

print('Starting Application ...')
print(os.environ)

os.environ['DJANGO_SETTINGS_MODULE'] = 'oda.settings.production'
application = get_wsgi_application()

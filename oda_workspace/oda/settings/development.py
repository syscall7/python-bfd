from base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = False

import sys
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   'odatest'
    }

ALLOWED_HOSTS = (
    'localhost:8000'
)

# Use the local file system instead of GoogleStorage
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Use console email backend instead of SMTP
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

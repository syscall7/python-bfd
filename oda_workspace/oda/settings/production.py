from base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = True

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': '/var/www/oda/odaweb.db',                      # Or path to database file if using sqlite3.
        #'NAME': 'odaweb.db',                      # Or path to database file if using sqlite3.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'odapython3',
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '***REMOVED***',                  # Not used with sqlite3.
        'HOST': 'localhost',         # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ALLOWED_HOSTS = (
    'onlinedisassembler.com',
    'www.onlinedisassembler.com',
    '.onlinedisassembler.com',
    '23.236.58.138',
)
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/var/oda'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/var/www/oda/site/oda/apps/odaweb/static/'

# File storage settings
# NOTE: In order for GoogleStorage to work, you have to add the IP address of the server that will be accessing Google
#       Storage to the Google access key referenced below.  This is doen via the GoogleStorage console.
DEFAULT_FILE_STORAGE = 'django-google-storage.storage.GoogleStorage'
os.environ.get('ODA_GOOGLE_STORAGE_ACCESS_KEY_ID')
os.environ.get('ODA_GOOGLE_STORAGE_SECRET_ACCESS_KEY')
os.environ.get('ODA_GOOGLE_STORAGE_BUCKET_NAME', 'oda')

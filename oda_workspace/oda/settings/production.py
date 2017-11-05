from base import *

DEBUG = False
COMPRESS_ENABLED = True

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': '/var/www/oda/odaweb.db',                      # Or path to database file if using sqlite3.
        #'NAME': 'odaweb.db',                      # Or path to database file if using sqlite3.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'odapython3',
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': os.environ.get('ODA_MYSQL_PASSWORD'), # Not used with sqlite3.
        'HOST': 'localhost',         # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ALLOWED_HOSTS = (
    'localhost',
    'onlinedisassembler.com',
    'www.onlinedisassembler.com',
    '.onlinedisassembler.com',
    '23.236.58.138',
    'disassembler.io',
)
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/var/oda'

# File storage settings
# Credentials Must be Stored According to
# https://developers.google.com/identity/protocols/application-default-credentials
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.environ.get('ODA_GOOGLE_STORAGE_BUCKET_NAME', 'oda')
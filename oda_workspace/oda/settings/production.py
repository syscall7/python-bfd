from base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = True

ALLOWED_HOSTS = (
    'onlinedisassembler.com',
    'www.onlinedisassembler.com',
    '.onlinedisassembler.com',
    'disassembler.io',
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

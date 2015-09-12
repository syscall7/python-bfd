# -----------------------------------------------------------------------------
# File: export_users
# Description: Generate a CSV file of user email addresses for MailChimp
# Date: 12 September 2015
# -----------------------------------------------------------------------------
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

def export_users(path):

    with open(path, 'wb') as csvfile:
        fieldnames = ['email', 'first_name', 'last_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(User.objects.values())

class Command(BaseCommand):
    args = 'path=<file.csv>'
    help = 'Example: ./migrate.py export_users'

    def handle(self, *args, **options):
        path = args[0]
        export_users(path)


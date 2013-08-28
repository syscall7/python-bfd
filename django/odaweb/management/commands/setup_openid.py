from django.core.management.base import BaseCommand, CommandError
from allauth.socialaccount.models import *

class Command(BaseCommand):
    args = '<>'
    help = 'Installs Social Account Credentials'

    def handle(self, *args, **options):

        site = Site.objects.get(id=1)

        try:
            SocialApp.objects.get(provider='google')
            self.stdout.write('Google Already Installed')
        except SocialApp.DoesNotExist:
            self.stdout.write('Installing provider=google')
            google = SocialApp(provider='google', name='google',
                           client_id=os.environ.get('ODA_OPENID_GOOGLE_CLIENT_ID'), secret=os.environ.get('ODA_OPENID_GOOGLE_SECRET'))
            google.save()

            google.sites.add(site)

            google.save()

        try:
            SocialApp.objects.get(provider='github')
            self.stdout.write('Github Already Installed')
        except SocialApp.DoesNotExist:
            self.stdout.write('Installing provider=github')
            github = SocialApp(provider='github', name='github',
                           client_id=os.environ.get('ODA_OPENID_GITHUB_CLIENT_ID'), secret='3ed667c126d07d15d552a5914e4e0916cfbbaf1b1')
            github.save()
            github.sites.add(site)
            github.save()

from django.core.management.base import BaseCommand, CommandError
from allauth.socialaccount.models import *
from optparse import make_option

class Command(BaseCommand):
    help = 'Installs Social Account Credentials'
    option_list = BaseCommand.option_list + ( make_option("-m", "--mode", action="store", type="string", dest="mode"), )


    def handle(self, *args, **options):

        site = Site.objects.get(id=1)
        site.domain="onlinedisassembler.com"
        site.name='onlinedisassembler'
        site.save()

        if options['mode'] == 'prod':
            self.stdout.write('Using Production Settings')
            locations = [
            {
                'name': 'google',
                'client_id': os.environ.get('ODA_OPENID_GOOGLE_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_GOOGLE_SECRET')
            },{
                'name': 'facebook',
                'client_id': os.environ.get('ODA_OPENID_FACEBOOK_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_FACEBOOK_SECRET')
            }, {
                'name': 'twitter',
                'client_id': os.environ.get('ODA_OPENID_TWITTER_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_TWITTER_SECRET')
            }
            ]
        elif options['mode'] == 'dev':
            locations = [
            {
                  'name': 'google',
                  'client_id': os.environ.get('ODA_OPENID_GOOGLE_CLIENT_ID'),
                  'secret': os.environ.get('ODA_OPENID_GOOGLE_SECRET')
            },{
                  'name': 'facebook',
                  'client_id': os.environ.get('ODA_OPENID_FACEBOOK_CLIENT_ID'),
                  'secret': os.environ.get('ODA_OPENID_FACEBOOK_SECRET')
            },{
                'name': 'twitter',
                'client_id': os.environ.get('ODA_OPENID_TWITTER_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_TWITTER_SECRET')
            }
            ]
        else:
            raise Exception('need to set mode')


        for location in locations:
            try:
                SocialApp.objects.get(provider=location['name'])
                self.stdout.write('%s Already Installed' % (location['name']))
            except SocialApp.DoesNotExist:
                self.stdout.write('Installing provider=%s' % (location['name']))
                sa = SocialApp(provider=location['name'], name=location['name'],
                           client_id=location['client_id'], secret=location['secret'])
                sa.save()

                sa.sites.add(site)

                sa.save()

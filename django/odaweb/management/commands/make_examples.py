from django.core.management.base import BaseCommand, CommandError
from odaweb.disassembler import make_examples

class Command(BaseCommand):
    args = '<>'
    help = 'Makes the examples'

    def handle(self, *args, **options):

        make_examples()
        self.stdout.write('test')

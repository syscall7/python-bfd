import os
from django.core.management.base import BaseCommand, CommandError
import odaweb.disassembler
from odaweb.disassembler import Disassembler, examples
from odaweb.models import BinaryDisassemblyChunk, Binary, BinaryString, BinaryFile, OdaMaster, OdaOptions

def make_examples():

    EXAMPLES_DIR = os.path.join(os.path.dirname(odaweb.disassembler.__file__), 'examples')

    for example in examples:
        short_name = example['short_name']
        if OdaMaster.objects.filter(short_name=short_name).exists():
            print 'Example %s already exists in the database' % short_name
            continue

        print 'Adding example %s to database' % short_name

        options = example['options']
        options.save()

        if example['binary_type'] is 'file':
            f = open(os.path.join(EXAMPLES_DIR, example['file_name']),'rb')
            binary = BinaryFile.create(f, options)
            binary.save()
        elif example['binary_type'] is 'string':
            binary = BinaryString()
            binary.binary_string = ''.join(example['data'].split())
            binary.options = options
            binary.save()

        oda_master = OdaMaster(short_name = short_name, binary = binary)
        oda_master.save()

        disassembler = Disassembler(binary)
        disassembler.process_chunks()


class Command(BaseCommand):
    args = '<>'
    help = 'Makes the examples'

    def handle(self, *args, **options):

        make_examples()
        self.stdout.write('test')

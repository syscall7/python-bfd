import re
from odb.bfd import ofd
import logging
from odb.structures.data_string import DataString
from odb.structures.function import Function
from odb.structures.parcel import Parcel
from odb.structures.section import Section
from odb.structures.symbol import Symbol
from odb.ops.operation import Operation

logger = logging.getLogger(__name__)

class LoadOperation(Operation):
    def __init__(self, filename):
        self.filename = filename

    def operate(self, odb_file):
        logger.info("Loading %s".format(odb_file))

        odb_file.filename = self.filename

        analyzer = ofd.Ofd(odb_file.get_binary())

        loader = Loader(odb_file, analyzer)

        loader.load()


class Loader(object):
    def __init__(self, odb_file, analyzer):
        self.odb_file = odb_file
        self.analyzer = analyzer

    def load(self):
        self.load_symbols()
        self.load_sections()
        self.load_functions()
        self.load_parcels()

        self.load_strings()


    def load_symbols(self):
        #Load Symbols
        for symbol in self.analyzer.symbols():
            self.odb_file.insert_item(self.odb_file.create_item('Symbol', {
                'name': symbol.name,
                'base': symbol.base,
                'type': symbol.type,
                'value': symbol.value
            }))

    def load_sections(self):
        #Load Sections
        for section in self.analyzer.sections:
            self.odb_file.insert_item(self.odb_file.create_item('Section', {
                'name': section.name
            }))

    def load_functions(self):
        funcs = filter(lambda x: x.type == 'T' or x.type == 't', self.analyzer.symbols())
        odb_funcs = [self.odb_file.create_item('Function', {
            'name': f.name,
            'offset': f.value,
            'type': f.type,
            'xrefs': []
        }) for f in funcs]

        for f in odb_funcs:
            self.odb_file.insert_item(f)

    def load_parcels(self):
        for sec in self.analyzer.get_loadable_sections().sections:
            is_code = self.analyzer.is_code_section(sec)
            self.odb_file.insert_item(self.odb_file.create_item('Parcel', {
                'start': sec.vma,
                'end': sec.vma + sec.size,
                'is_code': is_code
            }))

    def load_strings(self):
        for s in self.analyzer.get_loadable_sections().sections:
            print('Section %s, base 0x%08x, size 0x%08x' % (s.name, s.vma, s.size))
            for m in re.finditer("([\t\x20-\x7e]{4,})", self.analyzer.bfd.raw_data(s, s.vma, s.size)):

                self.odb_file.insert_item(self.odb_file.create_item('DataString', {
                    'addr': m.start()+s.vma,
                    'value': m.group(1)
                }))

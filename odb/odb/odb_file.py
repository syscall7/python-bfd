import pickle
from odb.structures.data_string import DataString
from odb.structures.branch import Branch
from odb.structures.function import Function
from odb.structures.parcel import Parcel
from odb.structures.section import Section
from odb.structures.symbol import Symbol

__author__ = 'davis'

STRUCTURE_TYPES = [
    Function, Section, Symbol, Parcel, Branch, DataString
]


class OdaObjectFactory(object):
    def __init__(self, oda_file):
        self.oda_file = oda_file

    def create(self, type_name, parameters):
        for t in STRUCTURE_TYPES:
            if t.__name__ == type_name:
                return t(self.oda_file.get_object_id(), **parameters)
        raise Exception(repr(object) + ' Not Found')


class Options(object):
    def __init__(self):
        self.target = None
        self.architecture = None
        self.base_address = 0

    def get_endian(self):
        return 'DEFAULT'


class OdbFile(object):
    def __init__(self):

        self.filename = None
        self.object_id = 0
        self.factory = OdaObjectFactory(self)
        self.operations = []
        self.items = {k: [] for k in STRUCTURE_TYPES}

    def create_item(self, type_name, parameters):
        return self.factory.create(type_name, parameters)

    def insert_item(self, item):
        self.items[item.__class__].append(item)

    def remove_item(self, item):
        self.items[item.__class__].remove(item)

    def insert_operation(self, operation):
        self.operations.append(operation)

    def modify_item(self, item):
        for n, i in enumerate(self.items[item.__class__]):
            if n == item:
                self.items[item.__class__][i] = item
                break

    def get_object_id(self):
        self.object_id += 1
        return self.object_id

    def get_binary(self):
        assert (self.filename is not None)

        class Binary(object):
            def __init__(self):
                self.options = Options()

            @staticmethod
            def file_handle():
                return open(self.filename)

        return Binary()


class DefaultOdbSerializer(object):
    def dumps(self, odb_file):
        return pickle.dumps({
            'version': 1,
            'odb_file': odb_file
        })

    def load(self, serialized):
        return pickle.loads(serialized)['odb_file']


def scan():
    import pkgutil
    import sys

    modules = pkgutil.iter_modules(path=["odb/structures"])
    for loader, mod_name, ispkg in modules:
        loader.find_module(mod_name).load_module(mod_name)

    [x for x in sys.modules.iterkeys() if x.startswith('odb')]

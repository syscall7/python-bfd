import logging
import cPickle
import types
import zlib

from oda.libs.odb.ops.operation import ValidationError
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.label import Label
from oda.libs.odb.structures.c_struct import CStruct, CStructObject


__author__ = 'davis'

logger = logging.getLogger(__name__)

STRUCTURE_TYPES = [
    Function, Section, Symbol, Parcel, Branch, DataString, Comment, Label, CStruct, CStructObject
]


class OdaObjectFactory(object):
    def __init__(self, oda_file):
        self.oda_file = oda_file

    def create(self, class_type, parameters):
        for t in STRUCTURE_TYPES:
            if issubclass(class_type, t):
                return class_type(self.oda_file.get_object_id(), **parameters)
        raise Exception(repr(object) + ' Not Found')





class OdbFile(object):
    def __init__(self, binary=None):

        if binary:
            assert (hasattr(binary, 'file_handle'))
            assert (type(getattr(binary, 'file_handle')) == types.MethodType)

        self.binary = binary
        self.cuckoo_job = None
        self.object_id = 0
        self.factory = OdaObjectFactory(self)
        self.operations = []
        self._items = {k.__name__: [] for k in STRUCTURE_TYPES}

    def __str__(self):
        return "OdbFile binary:%s" % self.binary

    def create_item(self, class_type, parameters):
        return self.factory.create(class_type, parameters)

    def insert_item(self, item):
        #TODO check that the item being added doesn't dupe an ID
        self._items[item.item_type].append(item)
        return item

    def remove_item(self, item):
        self._items[item.item_type].remove(item)

    def get_structure_list(self, class_type):
        return self._items[class_type.__name__]

    def get_arch(self):
        #TODO Durp
        return 'i386'

    def execute(self, operation):

        operation.validate(self)

        operation.operate(self)

        dup_op = next((op for op in self.operations if op.object_id == operation.object_id), None)
        if dup_op:
            raise ValidationError('Duplicate Operation')

        self.operations.append(operation)


    def modify_item(self, item):
        for n, i in enumerate(self._items[item.item_type]):
            if n == item:
                self._items[item.item_type][i] = item
                break

    def get_object_id(self):
        self.object_id += 1
        return self.object_id

    def get_options(self):
        return self.binary.options

    def get_binary(self):
        assert (self.binary is not None)

        return self.binary


class DefaultOdbSerializer(object):
    def dumps(self, odb_file):
        return zlib.compress(cPickle.dumps({
            'version': 1,
            'odb_file': odb_file
        }))

    def load(self, serialized):
        if serialized == '':
            return None

        return cPickle.loads(str(zlib.decompress(serialized)))['odb_file']


def scan():
    import pkgutil
    import sys

    modules = pkgutil.iter_modules(path=["odb/structures"])
    for loader, mod_name, ispkg in modules:
        loader.find_module(mod_name).load_module(mod_name)

    [x for x in sys.modules.iterkeys() if x.startswith('odb')]

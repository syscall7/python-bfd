from abc import abstractmethod, abstractproperty
import commands
import hashlib
import logging
from os import unlink
import cPickle
import os
import tempfile
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


__author__ = 'davis'

logger = logging.getLogger(__name__)

STRUCTURE_TYPES = [
    Function, Section, Symbol, Parcel, Branch, DataString, Comment, Label
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
    def __init__(self, target, architecture, base_address):
        self.target = target
        self.architecture = architecture
        self.base_address = base_address
        self.endian = 'DEFAULT'
        self.selected_opts = []

    def get_endian(self):
        return self.endian

    def get_extra_options(self):
        #return {"flags": []}
        if hasattr(self, 'selected_opts'):
            return self.selected_opts

        return []


class Binary(object):
    @abstractmethod
    def file_handle(self):
        pass

    @abstractproperty
    def options(self):
        pass

    def md5(self):
        f = self.file_handle()
        md5 = hashlib.md5(f.read()).hexdigest()
        f.close()
        Binary.done(f)
        return md5

    def sha1(self):
        f = self.file_handle()
        sha = hashlib.sha1(f.read()).hexdigest()
        f.close()
        Binary.done(f)
        return sha

    def desc(self):
        if os.name == 'nt':
            line = ''
        else:
            f = self.file_handle()
            line = commands.getoutput('file -b %s' % f.name)
            f.close()
            Binary.done(f)
        return line.split(', ')

    @staticmethod
    def done(f):
        try:
            f.done()
        except AttributeError:
            pass


class BinaryFile(Binary):
    def __init__(self, filename, target, architecture):
        self.filename = filename
        self.name = filename
        self._options = Options(target, architecture, 0)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def file_handle(self):
        f = open(self.filename)
        return f


class BinaryString(Binary):
    def __init__(self, binary_string, arch):
        self.binary_string_display = binary_string
        self.binary_string = ''.join(binary_string.split())
        self.arch = arch
        self.is_live_mode = True
        self._options = Options('binary', arch, 0)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def file_handle(self):
        try:
            byte_array = self.binary_string.decode("hex")
        except TypeError:
            logger.exception("Failed to decode hex %s" % self.binary_string)

        # Create a file containing the BinaryString for passing to BFD
        #  Must use delete=False because bfd expects a file name
        t = tempfile.NamedTemporaryFile(bufsize=0, delete=False)
        t.write(byte_array)

        # Dynamic function that deletes the temp file when we are done with it
        def done(self):
            # Close the file in case it isn't already closed
            self.close()

            # Delete the temporary file permanently
            unlink(self.name)

        # Add the done function dynamically to the File instance
        #f = open(t)
        t.done = types.MethodType(done, t)

        return t


class OdbFile(object):
    def __init__(self, binary=None):

        if binary:
            assert (hasattr(binary, 'file_handle'))
            assert (type(getattr(binary, 'file_handle')) == types.MethodType)

        self.binary = binary
        self.object_id = 0
        self.factory = OdaObjectFactory(self)
        self.operations = []
        self._items = {k: [] for k in STRUCTURE_TYPES}

    def create_item(self, type_name, parameters):
        return self.factory.create(type_name, parameters)

    def insert_item(self, item):
        #TODO check that the item being added doesn't dupe an ID
        self._items[item.__class__].append(item)

    def remove_item(self, item):
        self._items[item.__class__].remove(item)

    def get_structure_list(self, name):
        return self._items[name]

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
        for n, i in enumerate(self._items[item.__class__]):
            if n == item:
                self._items[item.__class__][i] = item
                break

    def get_object_id(self):
        self.object_id += 1
        return self.object_id

    def get_options(self):
        return self.binary.options

    def get_binary(self):
        assert (self.binary is not None)

        return self.binary

    def options(self):
        return self.binary_factory.get_binary().options


class DefaultOdbSerializer(object):
    def dumps(self, odb_file):
        return zlib.compress(cPickle.dumps({
            'version': 1,
            'odb_file': odb_file
        }))

    def load(self, serialized):
        return cPickle.loads(str(zlib.decompress(serialized)))['odb_file']


def scan():
    import pkgutil
    import sys

    modules = pkgutil.iter_modules(path=["odb/structures"])
    for loader, mod_name, ispkg in modules:
        loader.find_module(mod_name).load_module(mod_name)

    [x for x in sys.modules.iterkeys() if x.startswith('odb')]

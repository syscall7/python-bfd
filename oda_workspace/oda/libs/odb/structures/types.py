from oda.libs.odb.structures.oda_object import OdaObject
from abc import ABCMeta, abstractproperty
import inspect
import sys

# NOTE: Does not inherit from OdaObject
class BuiltinType(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def size(self):
        ''''''

class Integer(BuiltinType):
    __metaclass__ = ABCMeta

    @staticmethod
    def from_bytes(bytes):
        # TODO: Handle both little endian and big endian (below assumes big endian)
        return int(bytes.encode('hex'), 16)

class SignedInteger(Integer):
    __metaclass__ = ABCMeta
    def format(self, bytes):
        return '{0:d}'.format(Integer.from_bytes(bytes[:self.size]))

class UnsignedInteger(Integer):
    __metaclass__ = ABCMeta

    def format(self, bytes):
        return '0x{0:0{width}x}'.format(Integer.from_bytes(bytes[:self.size]), width=self.size*2)

# TODO: Fix the name property which is dumb, but matches cstruct objects
class Uint8(UnsignedInteger):

    @property
    def size(self):
        return 1

    name = 'Uint8'

class Uint16(UnsignedInteger):
    @property
    def size(self):
        return 2

    name = 'Uint16'

class Uint32(UnsignedInteger):
    @property
    def size(self):
        return 4

    name = 'Uint32'

class Uint64(UnsignedInteger):
    @property
    def size(self):
        return 8

    name = 'Uint64'

class Int8(SignedInteger):
    @property
    def size(self):
        return 1

    name = 'Int8'

class Int16(SignedInteger):
    @property
    def size(self):
        return 2

    name = 'Int16'

class Int32(SignedInteger):
    @property
    def size(self):
        return 4

    name = 'Int32'

class Int64(SignedInteger):
    @property
    def size(self):
        return 8

    name = 'Int64'

def BuiltInTypes():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    clstypes = [cls for name, cls in clsmembers if hasattr(cls,'name')]
    return clstypes


def BuiltInTypeNames():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    typenames = [name for name, cls in clsmembers if hasattr(cls,'name')]
    return typenames
    #return inspect.getmembers(sys.modules[__name__], lambda member: inspect.isclass(member) and member.__module__ == __name__

def BuiltInTypeFactory(type_name):
    # for now, ignore everything after the colon
    name = 'oda.libs.odb.structures.types'
    try:
        mod = __import__(name)
    except ImportError as e:
        return None

    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    try:
        initFunc = getattr(mod, type_name)
    except:
        return None

    obj = initFunc()

    return obj
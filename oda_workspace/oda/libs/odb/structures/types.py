from oda.libs.odb.structures.oda_object import OdaObject
from abc import ABCMeta

# NOTE: Does not inherit from OdaObject
class BuiltinType():
    __metaclass__ = ABCMeta

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

class Uint8(UnsignedInteger):
    size = 1
    name = 'uint8'

class Uint16(UnsignedInteger):
    size = 2
    name = 'uint16'

class Uint32(UnsignedInteger):
    size = 4
    name = 'uint32'

class Uint64(UnsignedInteger):
    size = 8
    name = 'uint64'

class Int8(SignedInteger):
    size = 1
    name = 'int8'

class Int16(SignedInteger):
    size = 2
    name = 'int8'

class Int32(SignedInteger):
    size = 4
    name = 'int32'

class Int64(SignedInteger):
    size = 8
    name = 'int32'

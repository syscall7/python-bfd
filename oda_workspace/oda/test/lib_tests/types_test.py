from oda.libs.odb.structures.types import *
from oda.test.oda_test_case import OdaLibTestCase

class TestTypes(OdaLibTestCase):

    def test_builtin_types(self):
        bytes = '\x01\x23\x45\x67\x89\xab\xcd\xef'

        # TODO: Test little endian in addition to big endian

        # unsigned
        self.assertEqual('0x01', Uint8().format(bytes))
        self.assertEqual('0x0123', Uint16().format(bytes))
        self.assertEqual('0x01234567', Uint32().format(bytes))
        self.assertEqual('0x0123456789abcdef', Uint64().format(bytes))

        # signed
        self.assertEqual('1', Int8().format(bytes))
        self.assertEqual('291', Int16().format(bytes))
        self.assertEqual('19088743', Int32().format(bytes))
        self.assertEqual('81985529216486895', Int64().format(bytes))

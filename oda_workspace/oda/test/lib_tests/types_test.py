import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.types import *

class TestTypes(unittest.TestCase):

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

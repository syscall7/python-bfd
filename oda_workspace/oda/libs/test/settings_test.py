import unittest
from oda.libs.odb.bfd.ofd import Ofd
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperationFactory
from oda.libs.odb.ops.modify_settings import ModifySettingsFactory

__author__ = 'davis'

class TestSettings(unittest.TestCase):

    def test_load_and_get(self):
        load_operation = LoadOperationFactory.load_from_string(
            '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1',
            'arm'
        )

        odb = OdbFile()
        odb.execute(load_operation)

        binary = odb.get_binary()
        options = binary.options

        self.assertEquals("arm", options.architecture)
        self.assertEquals(0, options.base_address)
        self.assertEquals('binary', options.target)

    def test_set(self):
        load_operation = LoadOperationFactory.load_from_string(
            '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1',
            'arm'
        )

        odb = OdbFile()
        odb.execute(load_operation)

        modify = ModifySettingsFactory.set_architecture('i386')
        odb.execute(modify)
        binary = odb.get_binary()
        options = binary.options
        self.assertEquals("i386", options.architecture)

        modify = ModifySettingsFactory.set_base_address('1000')
        odb.execute(modify)
        binary = odb.get_binary()
        options = binary.options
        self.assertEquals("1000", options.base_address)

        modify = ModifySettingsFactory.set_endian('BIG')
        odb.execute(modify)
        binary = odb.get_binary()
        options = binary.options
        self.assertEquals("BIG", options.endian)




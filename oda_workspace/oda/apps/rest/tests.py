"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from oda.apps.odaweb.management.commands.setup_oda import load_examples

from oda.apps.odaweb.models import OdaMaster


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class OdaTestCase(APITestCase):
    def setUp(self):
        load_examples()


class DisplayUnitTest(OdaTestCase):
    urls = 'oda.urls'

    def test_display_units(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)
        self.assertEqual(17, len(rd))
        self.assertEqual('.data', rd[0]['section_name'])
        self.assertEqual('55', rd[0]['rawBytes'])
        self.assertEqual(False, rd[0]['isBranch'])
        self.assertEqual(False, rd[0]['isFunction'])
        self.assertEqual(0, rd[0]['offset'])
        self.assertEqual('ebp', rd[0]['operands'])

    def test_display_units_mkdir_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'mkdir', 'addr' : '0x4014d0'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], 'sub')
        self.assertEquals(rd[0]['operands'], 'rsp,0x8')
        self.assertEquals(rd[0]['rawBytes'], '4883ec08')
        self.assertEquals(rd[0]['offset'], 0x4014d0)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], True)
        self.assertEquals(rd[0]['section_name'], '.init')
        self.assertEquals(rd[0]['instStr'], 'sub    rsp,0x8')

    def test_display_units_mkdir_data(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'mkdir', 'addr' : '0x400238'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], '')
        self.assertEquals(rd[0]['operands'], '')
        self.assertEquals(rd[0]['rawBytes'], '2f')
        self.assertEquals(rd[0]['offset'], 0x400238)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], False)
        self.assertEquals(rd[0]['section_name'], '.interp')
        self.assertEquals(rd[0]['instStr'], "<span class='string'>/</span>")

    def test_display_units_mkdir_logical_data_and_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '10',
                                     'units' : '4743',
                                     'logical' : 'true'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], '')
        self.assertEquals(rd[0]['operands'], '')
        self.assertEquals(rd[0]['rawBytes'], '6c')
        self.assertEquals(rd[0]['offset'], 0x400242)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], False)
        self.assertEquals(rd[0]['section_name'], '.interp')
        self.assertEquals(rd[0]['instStr'], "<span class='string'>l</span>")

        # next data section
        self.assertEquals(rd[18]['opcode'], '')
        self.assertEquals(rd[18]['operands'], '')
        self.assertEquals(rd[18]['rawBytes'], '04')
        self.assertEquals(rd[18]['offset'], 0x400254)
        self.assertEquals(rd[18]['isBranch'], False)
        self.assertEquals(rd[18]['isFunction'], False)
        self.assertEquals(rd[18]['section_name'], '.note.ABI-tag')
        self.assertEquals(rd[18]['instStr'], " ")

        # the last entry should be the first instruction of the first code section
        self.assertEquals(rd[-1]['opcode'], 'sub')
        self.assertEquals(rd[-1]['operands'], 'rsp,0x8')
        self.assertEquals(rd[-1]['rawBytes'], '4883ec08')
        self.assertEquals(rd[-1]['offset'], 0x4014d0)
        self.assertEquals(rd[-1]['isBranch'], False)
        self.assertEquals(rd[-1]['isFunction'], True)
        self.assertEquals(rd[-1]['section_name'], '.init')
        self.assertEquals(rd[-1]['instStr'], 'sub    rsp,0x8')

    def test_display_units_mkdir_logical_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '4752',
                                     'units' : '100',
                                     'logical' : 'true'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)
        self.assertEquals(len(rd), 100)

        # first instruction of first code section
        self.assertEquals(rd[0]['opcode'], 'sub')
        self.assertEquals(rd[0]['operands'], 'rsp,0x8')
        self.assertEquals(rd[0]['rawBytes'], '4883ec08')
        self.assertEquals(rd[0]['offset'], 0x4014d0)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], True)
        self.assertEquals(rd[0]['section_name'], '.init')
        self.assertEquals(rd[0]['instStr'], 'sub    rsp,0x8')

        # first instruction of next code section
        self.assertEquals(rd[6]['opcode'], 'push')
        self.assertEquals(rd[6]['operands'], 'QWORD PTR [rip+0x20eafa]        # 0x0060fff0')
        self.assertEquals(rd[6]['rawBytes'], 'ff35faea2000')
        self.assertEquals(rd[6]['offset'], 0x4014f0)
        self.assertEquals(rd[6]['isBranch'], False)
        self.assertEquals(rd[6]['isFunction'], True)
        self.assertEquals(rd[6]['section_name'], '.plt')
        self.assertEquals(rd[6]['instStr'], 'push   QWORD PTR [rip+0x20eafa]        # 0x0060fff0')

class LabelUnitTest(OdaTestCase):
    urls = 'oda.urls'

    def test_labels(self):
        response = self.client.get('/odaweb/api/labels/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data


class FunctionUnitTest(OdaTestCase):
    urls = 'oda.urls'

    def test_functions(self):
        response = self.client.get('/odaweb/api/functions/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data

    def test_functions_mkdir(self):
        response = self.client.get('/odaweb/api/functions/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data

class CommentUnitTest(OdaTestCase):
    urls = 'oda.urls'

    def test_comments(self):
        response = self.client.get('/odaweb/api/comments/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertGreater(len(rd), 0)
        self.assertIsNotNone(rd[0]['comment'])
        self.assertIsNotNone(rd[0]['offset'])


class SectionsTest(OdaTestCase):
    urls = 'oda.urls'

    def test_sections(self):
        response = self.client.get('/odaweb/api/sections/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEqual(24, len(rd))
        self.assertIsNotNone(rd[0]['flags'])
        self.assertGreater(len(rd[0]['flags']), 0)
        self.assertIsNotNone(rd[0]['name'])
        self.assertIsNotNone(rd[0]['size'])
        self.assertIsNotNone(rd[0]['vma'])


class SymbolsTest(OdaTestCase):
    urls = 'oda.urls'

    def test_symbols(self):
        response = self.client.get('/odaweb/api/symbols/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEqual(153, len(rd))
        self.assertIsNotNone(rd[0]['name'])
        self.assertIsNotNone(rd[0]['offset'])
        self.assertNotEqual(rd[0]['offset'], 0)
        self.assertIsNotNone(rd[0]['type'])


class StringsTest(OdaTestCase):
    urls = 'oda.urls'

    def test_strings(self):
        response = self.client.get('/odaweb/api/strings/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEquals(259, len(rd))
        self.assertIsNotNone(rd[0]['addr'])
        self.assertIsNotNone(rd[0]['string'])


class BinaryStringTest(OdaTestCase):
    urls = 'oda.urls'

    def test_binary_strings(self):
        response = self.client.patch('/odaweb/api/binarystrings/1/', {
            'binary_string': 'ABCD',
            'short_name': 'strcpy_x86',
            'revision': 0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['binary_string'], 'ABCD')







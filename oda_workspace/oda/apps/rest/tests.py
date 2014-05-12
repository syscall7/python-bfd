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

    def test_display_units_mkdir(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], 'sub')
        self.assertEquals(rd[0]['operands'], 'rsp,0x8')
        self.assertEquals(rd[0]['rawBytes'], '4883ec08')
        self.assertEquals(rd[0]['offset'], 4199632)
        # self.assertEqual(17, len(rd))
        # self.assertEqual('.data', rd[0]['section_name'])
        # self.assertEqual('55', rd[0]['rawBytes'])
        # self.assertEqual(False, rd[0]['isBranch'])
        # self.assertEqual(False, rd[0]['isFunction'])
        # self.assertEqual(0, rd[0]['offset'])
        # self.assertEqual('%ebp', rd[0]['operands'])

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







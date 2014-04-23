"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from oda.apps.odaweb.models import OdaMaster


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class DisplayUnitTest(APITestCase):

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

    def test_comments(self):
        response = self.client.get('/odaweb/api/comments/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertGreater(len(rd), 0)
        self.assertIsNotNone(rd[0]['comment'])
        self.assertIsNotNone(rd[0]['offset'])


class SectionsTest(APITestCase):
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


class SymbolsTest(APITestCase):
    urls = 'oda.urls'

    def test_symbols(self):
        response = self.client.get('/odaweb/api/symbols/',
                               {'revision': 0, 'short_name': 'mkdir'},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEqual(150, len(rd))
        self.assertIsNotNone(rd[0]['name'])
        self.assertIsNotNone(rd[0]['offset'])
        self.assertIsNotNone(rd[0]['type'])


class StringsTest(APITestCase):
    urls = 'oda.urls'

    def test_symbols(self):
        response = self.client.get('/odaweb/api/strings/',
                               {'revision': 0, 'short_name': 'mkdir'},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEquals(259, len(rd))
        self.assertIsNotNone(rd[0]['addr'])
        self.assertIsNotNone(rd[0]['string'])

class BinaryStringTest(APITestCase):
    urls = 'oda.urls'

    def test_strings(self):
        response = self.client.patch('/odaweb/api/binarystrings/1/', {
            'binary_string': 'ABCD'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['binary_string'], 'ABCD')







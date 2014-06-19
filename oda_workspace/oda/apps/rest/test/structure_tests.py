"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework import status
from oda_api_tests import OdaApiTestCase

class LabelUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_labels(self):
        response = self.client.get('/odaweb/api/labels/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data


class FunctionUnitTest(OdaApiTestCase):
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

class CommentUnitTest(OdaApiTestCase):
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


class SectionsTest(OdaApiTestCase):
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


class SymbolsTest(OdaApiTestCase):
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


class StringsTest(OdaApiTestCase):
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


class BinaryStringTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_binary_strings(self):
        response = self.client.patch('/odaweb/api/binarystrings/1/', {
            'binary_string': 'ABCD',
            'short_name': 'strcpy_x86',
            'revision': 0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['binary_string'], 'ABCD')







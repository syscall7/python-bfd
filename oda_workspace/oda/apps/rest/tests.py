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

    def test_list(self):
        strcpy = OdaMaster.objects.get(short_name='strcpy_x86')
        self.assertIsNotNone(strcpy)

        #url = reverse('odaweb/api/displayunits/')
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


"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from rest_framework.test import APITestCase

from oda.apps.odaweb.models import OdaMaster


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class DisplayUnitTest(APITestCase):

    def test_list(self):
        self.assertEquals(12, len(OdaMaster.objects.all()))
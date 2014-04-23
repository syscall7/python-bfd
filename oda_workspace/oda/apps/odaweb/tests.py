"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class IndexTest(TestCase):
    def test_index(self):
        response = self.client.get('/odaweb/')

        self.assertEqual(response.status_code, 200)

        self.assertTrue('master' in response.context)
        self.assertTrue('supported_archs' in response.context)
import os
from django.test import TestCase
from rest_framework.test import APITestCase
from oda.apps.odaweb.management.commands.setup_oda import load_examples

class OdaApiTestCase(APITestCase):
    def setUp(self):
        load_examples()

class OdaLibTestCase(TestCase):
    def get_test_bin_path(self, relpath):
        cwd = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(cwd, 'test_binaries', relpath)
        return path
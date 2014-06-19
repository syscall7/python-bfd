from rest_framework.test import APITestCase
from oda.apps.odaweb.management.commands.setup_oda import load_examples

class OdaApiTestCase(APITestCase):
    def setUp(self):
        load_examples()
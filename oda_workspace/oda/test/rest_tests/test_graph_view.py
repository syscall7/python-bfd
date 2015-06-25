from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class GraphViewTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_graph_view_binary_string(self):
        response = self.client.get('/odaweb/api/graph',
                                   { 'short_name': 'strcpy_x86',
                                     'revision': 0,
                                     'vma': 0 },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        graphInfo = response.data
        self.assertIsNotNone(graphInfo)
        self.assertIn('nodes', graphInfo)
        self.assertIn('links', graphInfo)

        # verify nodes are as expected
        nodes = graphInfo['nodes']

        # verify links are as expected
        links = graphInfo['nodes']

        print 'done'

    def test_graph_view_binary_string_nonzero_base_address(self):
        pass


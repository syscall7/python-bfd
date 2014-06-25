from rest_framework import status
from oda_api_tests import OdaApiTestCase

class MakeCodeUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_make_bad_code(self):

        # attempt to make code at an address with an invalid opcode
        response = self.client.get('/odaweb/api/displayunits/1/makeCode/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4002cd},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # we *should* get an error message
        self.assertNotEqual(response.data['error'], None)

    def test_simple_make_code(self):

        # before making_data
        before_make_data = (
            ('sub',  0x4014d0, '.init', '4883ec08'),
            ('call', 0x4014d4, '.init', 'e883040000'),
            ('call', 0x4014d9, '.init', 'e812050000'),
            ('call', 0x4014de, '.init', 'e87db10000'),
            ('add',  0x4014e3, '.init', '4883c408'),
            ('ret',  0x4014e7, '.init', 'c3'),
            ('push', 0x4014f0, '.plt',  'ff35faea2000'),
        )

        # before converting back to code
        before_make_code = (
            ('sub',  0x4014d0, '.init', '4883ec08'),
            ('call', 0x4014d4, '.init', 'e883040000'),
            ('',     0x4014d9, '.init', 'e8'),
            ('',     0x4014da, '.init', '12'),
            ('',     0x4014db, '.init', '05'),
            ('',     0x4014dc, '.init', '00'),
            ('',     0x4014dd, '.init', '00'),
            ('call', 0x4014de, '.init', 'e87db10000'),
            ('add',  0x4014e3, '.init', '4883c408'),
            ('ret',  0x4014e7, '.init', 'c3'),
            ('push', 0x4014f0, '.plt',  'ff35faea2000'),
        )

        # get the display units
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x004014d0',
                                     'units' : len(before_make_data)},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        # verify they are what we expect (original code)
        for expected, actual in zip(before_make_data, rd):
            self.assertEquals(expected[0], actual['opcode'])
            self.assertEquals(expected[1], actual['offset'])
            self.assertEquals(expected[2], actual['section_name'])
            self.assertEquals(expected[3], actual['rawBytes'])

        # convert the second call instruction to data bytes
        response = self.client.get('/odaweb/api/displayunits/1/makeData/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4014d9},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)

        # get the display units (should be CODA, DATA, CODE)
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x004014d0',
                                     'units' : len(before_make_code)},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        # verify we have CODE, DATA, CODE
        for expected, actual in zip(before_make_code, rd):
            self.assertEquals(expected[0], actual['opcode'])
            self.assertEquals(expected[1], actual['offset'])
            self.assertEquals(expected[2], actual['section_name'])
            self.assertEquals(expected[3], actual['rawBytes'])

        # convert the data back to code
        response = self.client.get('/odaweb/api/displayunits/1/makeCode/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4014d9},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)

        # get the display units, should be all code again
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x004014d0',
                                     'units' : len(before_make_code)},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        # verify that we're back to the original code
        for expected, actual in zip(before_make_data, rd):
            self.assertEquals(expected[0], actual['opcode'])
            self.assertEquals(expected[1], actual['offset'])
            self.assertEquals(expected[2], actual['section_name'])
            self.assertEquals(expected[3], actual['rawBytes'])


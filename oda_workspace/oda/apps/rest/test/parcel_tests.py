from rest_framework import status
from oda_api_tests import OdaApiTestCase

class ParcelUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_simple_split(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x004014d0',
                                     'units' : '7'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        # before the split
        before = (
            ('sub',  0x4014d0, '.init', '4883ec08'),
            ('call', 0x4014d4, '.init', 'e883040000'),
            ('call', 0x4014d9, '.init', 'e812050000'),
            ('call', 0x4014de, '.init', 'e87db10000'),
            ('add',  0x4014e3, '.init', '4883c408'),
            ('ret',  0x4014e7, '.init', 'c3'),
            ('push', 0x4014f0, '.plt', 'ff35faea2000'),
        )

        # after the split
        after = (
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
            ('push', 0x4014f0, '.plt', 'ff35faea2000'),
        )

        i = 0
        for b in before:
            self.assertEquals(rd[i]['opcode'], b[0])
            self.assertEquals(rd[i]['offset'], b[1])
            self.assertEquals(rd[i]['section_name'], b[2])
            self.assertEquals(rd[i]['rawBytes'], b[3])
            i += 1

        response = self.client.get('/odaweb/api/displayunits/1/splitParcel/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4014d9},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x004014d0',
                                     'units' : '11'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        i = 0
        for a in after:
            self.assertEquals(rd[i]['opcode'], a[0])
            self.assertEquals(rd[i]['offset'], a[1])
            self.assertEquals(rd[i]['section_name'], a[2])
            self.assertEquals(rd[i]['rawBytes'], a[3])
            i += 1


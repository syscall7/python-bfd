from rest_framework import status
from oda_api_tests import OdaApiTestCase

class DisplayUnitTest(OdaApiTestCase):
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

    def test_display_units_mkdir_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'mkdir', 'addr' : '0x4014d0'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], 'sub')
        self.assertEquals(rd[0]['operands'], 'rsp,0x8')
        self.assertEquals(rd[0]['rawBytes'], '4883ec08')
        self.assertEquals(rd[0]['offset'], 0x4014d0)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], True)
        self.assertEquals(rd[0]['section_name'], '.init')
        self.assertEquals(rd[0]['instStr'], 'sub    rsp,0x8')

    def test_display_units_mkdir_data(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'mkdir', 'addr' : '0x400238'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], '')
        self.assertEquals(rd[0]['operands'], '')
        self.assertEquals(rd[0]['rawBytes'], '2f')
        self.assertEquals(rd[0]['offset'], 0x400238)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], False)
        self.assertEquals(rd[0]['section_name'], '.interp')
        self.assertEquals(rd[0]['instStr'], "<span class='string'>/</span>")

    def test_display_units_mkdir_logical_data_and_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '10',
                                     'units' : '4743',
                                     'logical' : 'true'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], '')
        self.assertEquals(rd[0]['operands'], '')
        self.assertEquals(rd[0]['rawBytes'], '6c')
        self.assertEquals(rd[0]['offset'], 0x400242)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], False)
        self.assertEquals(rd[0]['section_name'], '.interp')
        self.assertEquals(rd[0]['instStr'], "<span class='string'>l</span>")

        # next data section
        self.assertEquals(rd[18]['opcode'], '')
        self.assertEquals(rd[18]['operands'], '')
        self.assertEquals(rd[18]['rawBytes'], '04')
        self.assertEquals(rd[18]['offset'], 0x400254)
        self.assertEquals(rd[18]['isBranch'], False)
        self.assertEquals(rd[18]['isFunction'], False)
        self.assertEquals(rd[18]['section_name'], '.note.ABI-tag')
        self.assertEquals(rd[18]['instStr'], " ")

        # the last entry should be the first instruction of the first code section
        self.assertEquals(rd[-1]['opcode'], 'sub')
        self.assertEquals(rd[-1]['operands'], 'rsp,0x8')
        self.assertEquals(rd[-1]['rawBytes'], '4883ec08')
        self.assertEquals(rd[-1]['offset'], 0x4014d0)
        self.assertEquals(rd[-1]['isBranch'], False)
        self.assertEquals(rd[-1]['isFunction'], True)
        self.assertEquals(rd[-1]['section_name'], '.init')
        self.assertEquals(rd[-1]['instStr'], 'sub    rsp,0x8')

    def test_display_units_mkdir_logical_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '4752',
                                     'units' : '100',
                                     'logical' : 'true'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)
        self.assertEquals(len(rd), 100)

        # first instruction of first code section
        self.assertEquals(rd[0]['opcode'], 'sub')
        self.assertEquals(rd[0]['operands'], 'rsp,0x8')
        self.assertEquals(rd[0]['rawBytes'], '4883ec08')
        self.assertEquals(rd[0]['offset'], 0x4014d0)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], True)
        self.assertEquals(rd[0]['section_name'], '.init')
        self.assertEquals(rd[0]['instStr'], 'sub    rsp,0x8')

        # first instruction of next code section
        self.assertEquals(rd[6]['opcode'], 'push')
        self.assertEquals(rd[6]['operands'], 'QWORD PTR [rip+0x20eafa]        # 0x0060fff0')
        self.assertEquals(rd[6]['rawBytes'], 'ff35faea2000')
        self.assertEquals(rd[6]['offset'], 0x4014f0)
        self.assertEquals(rd[6]['isBranch'], False)
        self.assertEquals(rd[6]['isFunction'], True)
        self.assertEquals(rd[6]['section_name'], '.plt')
        self.assertEquals(rd[6]['instStr'], 'push   QWORD PTR [rip+0x20eafa]        # 0x0060fff0')

    def test_display_units_mkdir_size(self):
        response = self.client.get('/odaweb/api/displayunits/1/size/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)
        self.assertEquals(rd, 28439)

    def test_display_units_mkdir_vma_to_lda(self):

        tests = (
            (0x400238, 0),      # first data byte (in .interp)
            (0x4014d0, 4752),   # first instruction of executable (in .init)
            (0x6102b7, 28438),      # last data byte of executable (in .data)
            (0x6102b8, None)    # one byte beyond executable image
        )

        for vma, expected_lda in tests:
            response = self.client.get('/odaweb/api/displayunits/1/vmaToLda/',
                                       { 'revision': 0,
                                         'short_name': 'mkdir',
                                         'vma': vma},
                                       format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            actual_lda = response.data
            self.assertEquals(expected_lda, actual_lda)

    def test_display_units_mkdir_lda_to_vma(self):

        tests = (
            (0x400238, 0),      # first data byte (in .interp)
            (0x4014d0, 4752),   # first instruction of executable (in .init)
            (0x6102b7, 28438),  # last data byte of executable (in .data)
            (None, 28439)       # one lda beyond executable image
        )

        for expected_vma, lda in tests:
            response = self.client.get('/odaweb/api/displayunits/1/ldaToVma/',
                                       { 'revision': 0,
                                         'short_name': 'mkdir',
                                         'lda': lda},
                                       format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            actual_vma = response.data
            self.assertEquals(expected_vma, actual_vma)

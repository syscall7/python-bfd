import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation
from oda.libs.odb.ops.scan_operation import ScanOperation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures import parcel
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.odb_file import BinaryFile, BinaryString

class TestParcels(unittest.TestCase):

    def test_split_to_data_basic(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(ScanOperation())

        parcels_before = odb_file.get_structure_list(Parcel)
        p = parcel.find_parcel_by_vma(0x4029c0, parcels_before)
        num_p1_ldas_before = p.num_ldas()
        text_lda_before = parcel.vma_to_lda(0x4029c0, parcels_before)
        fini_lda_before = parcel.vma_to_lda(0x412bec, parcels_before)

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x4029d5, False))

        # number of parcels after the split
        parcels_after = odb_file.get_structure_list(Parcel)
        self.assertEquals(27, len(parcels_after))

        # get the three parcels
        p1 = parcel.find_parcel_by_vma(0x4029c0, parcels_after)
        p2 = parcel.find_parcel_by_vma(0x4029d5, parcels_after)
        p3 = parcel.find_parcel_by_vma(0x4029da, parcels_after)

        # make sure they are all unique
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p2, p3)

        # check num_ldas in p1 (5 instructions)
        self.assertEquals(5, p1.num_ldas())

        # check num_ldas in p2 (this one instruction has now become 5 data bytes)
        self.assertEquals(5, p2.num_ldas())

        # check num_ldas in p3 (less 5 from p1 and less 1 from p2 - remember it used to only be 1 lda before the split)
        self.assertEquals(num_p1_ldas_before - 5 - 1, p3.num_ldas())

        # make sure vmas line up
        self.assertEquals(0x4029c0, p1.vma_start)
        self.assertEquals(0x4029d5, p1.vma_end)
        self.assertEquals(0x4029d5, p2.vma_start)
        self.assertEquals(0x4029da, p2.vma_end)
        self.assertEquals(0x4029da, p3.vma_start)
        self.assertEquals(0x412bec, p3.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(text_lda_before, parcel.vma_to_lda(0x4029c0, parcels_after))
        self.assertEquals(text_lda_before+5, parcel.vma_to_lda(0x4029d5, parcels_after))

        # these changed
        self.assertEquals(text_lda_before+6, parcel.vma_to_lda(0x4029d6, parcels_after))
        self.assertEquals(text_lda_before+7, parcel.vma_to_lda(0x4029d7, parcels_after))
        self.assertEquals(text_lda_before+8, parcel.vma_to_lda(0x4029d8, parcels_after))
        self.assertEquals(text_lda_before+9, parcel.vma_to_lda(0x4029d9, parcels_after))
        self.assertEquals(text_lda_before+10, parcel.vma_to_lda(0x4029da, parcels_after))
        self.assertEquals(text_lda_before+11, parcel.vma_to_lda(0x4029db, parcels_after))

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(fini_lda_before+4, parcel.vma_to_lda(0x412bec, parcels_after))

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(0x4029c0, parcel.lda_to_vma(text_lda_before, parcels_after))
        self.assertEquals(0x4029d5, parcel.lda_to_vma(text_lda_before+5, parcels_after))

        # these changed
        self.assertEquals(0x4029d6, parcel.lda_to_vma(text_lda_before+6, parcels_after))
        self.assertEquals(0x4029d7, parcel.lda_to_vma(text_lda_before+7, parcels_after))
        self.assertEquals(0x4029d8, parcel.lda_to_vma(text_lda_before+8, parcels_after))
        self.assertEquals(0x4029d9, parcel.lda_to_vma(text_lda_before+9, parcels_after))
        self.assertEquals(0x4029da, parcel.lda_to_vma(text_lda_before+10, parcels_after))
        self.assertEquals(0x4029db, parcel.lda_to_vma(text_lda_before+11, parcels_after))

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(0x412bec, parcel.lda_to_vma(fini_lda_before+4, parcels_after))

    def test_split_to_data_at_start_of_parcel(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(ScanOperation())

        parcels_before = odb_file.get_structure_list(Parcel)

        # start of .fini section
        p = parcel.find_parcel_by_vma(0x412bec, parcels_before)
        num_p1_ldas_before = p.num_ldas()
        fini_lda_before = parcel.vma_to_lda(0x412bec, parcels_before)

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x412bec, False))

        # number of parcels after the split (should only add one more)
        parcels_after = odb_file.get_structure_list(Parcel)
        self.assertEquals(26, len(parcels_after))

        # get the two parcels
        p1 = parcel.find_parcel_by_vma(0x412bec, parcels_after)
        p2 = parcel.find_parcel_by_vma(0x412bf0, parcels_after)

        # make sure they are unique
        self.assertNotEqual(p1, p2)

        # check num_ldas in p1 (4 data bytes)
        self.assertEquals(4, p1.num_ldas())

        # check num_ldas in p2
        self.assertEquals(2, p2.num_ldas())

        # make sure vmas line up
        self.assertEquals(0x412bec, p1.vma_start)
        self.assertEquals(0x412bf0, p1.vma_end)
        self.assertEquals(0x412bf0, p2.vma_start)
        self.assertEquals(0x412bf5, p2.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(fini_lda_before, parcel.vma_to_lda(0x412bec, parcels_after))

        # these changed
        self.assertEquals(fini_lda_before+1, parcel.vma_to_lda(0x412bed, parcels_after))
        self.assertEquals(fini_lda_before+2, parcel.vma_to_lda(0x412bee, parcels_after))
        self.assertEquals(fini_lda_before+3, parcel.vma_to_lda(0x412bef, parcels_after))
        self.assertEquals(fini_lda_before+4, parcel.vma_to_lda(0x412bf0, parcels_after))
        self.assertEquals(fini_lda_before+5, parcel.vma_to_lda(0x412bf4, parcels_after))

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(0x412bec, parcel.lda_to_vma(fini_lda_before, parcels_after))

        # these changed
        self.assertEquals(0x412bed, parcel.lda_to_vma(fini_lda_before+1, parcels_after))
        self.assertEquals(0x412bee, parcel.lda_to_vma(fini_lda_before+2, parcels_after))
        self.assertEquals(0x412bef, parcel.lda_to_vma(fini_lda_before+3, parcels_after))
        self.assertEquals(0x412bf0, parcel.lda_to_vma(fini_lda_before+4, parcels_after))
        self.assertEquals(0x412bf4, parcel.lda_to_vma(fini_lda_before+5, parcels_after))

    def test_split_to_data_at_end_of_parcel(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(ScanOperation())

        parcels_before = odb_file.get_structure_list(Parcel)

        # last instruction in .plt
        p = parcel.find_parcel_by_vma(0x4029bb, parcels_before)
        p3 = parcel.find_parcel_by_vma(0x4029c0, parcels_before)
        num_p1_ldas_before = p.num_ldas()
        num_p3_ldas_before = p3.num_ldas()
        plt_lda_before = parcel.vma_to_lda(0x402320, parcels_before)
        text_lda_before = parcel.vma_to_lda(0x4029c0, parcels_before)

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x4029bb, False))

        # number of parcels after the split (should only add one more)
        parcels_after = odb_file.get_structure_list(Parcel)
        self.assertEquals(26, len(parcels_after))

        # get the two parcels (plus the .text one following)
        p1 = parcel.find_parcel_by_vma(0x402320, parcels_after)
        p2 = parcel.find_parcel_by_vma(0x4029bb, parcels_after)
        p3 = parcel.find_parcel_by_vma(0x4029c0, parcels_after)

        # make sure they are all unique
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p2, p3)

        # check num_ldas in p1 (5 instructions)
        self.assertEquals(num_p1_ldas_before - 1, p1.num_ldas())

        # check num_ldas in p2 (this one instruction has now become 5 data bytes)
        self.assertEquals(5, p2.num_ldas())

        # check num_ldas in p3 (should not have changed)
        self.assertEquals(num_p3_ldas_before, p3.num_ldas())

        # make sure vmas line up
        self.assertEquals(0x402320, p1.vma_start)
        self.assertEquals(0x4029bb, p1.vma_end)
        self.assertEquals(0x4029bb, p2.vma_start)
        self.assertEquals(0x4029c0, p2.vma_end)
        self.assertEquals(0x4029c0, p3.vma_start)
        self.assertEquals(0x412bec, p3.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(plt_lda_before, parcel.vma_to_lda(0x402320, parcels_after))
        self.assertEquals(plt_lda_before+num_p1_ldas_before-2, parcel.vma_to_lda(0x4029b6, parcels_after))
        self.assertEquals(plt_lda_before+num_p1_ldas_before-1, parcel.vma_to_lda(0x4029bb, parcels_after))

        # these changed
        self.assertEquals(plt_lda_before+num_p1_ldas_before, parcel.vma_to_lda(0x4029bc, parcels_after))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+1, parcel.vma_to_lda(0x4029bd, parcels_after))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+2, parcel.vma_to_lda(0x4029be, parcels_after))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+3, parcel.vma_to_lda(0x4029bf, parcels_after))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+4, parcel.vma_to_lda(0x4029c0, parcels_after))

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(text_lda_before+4, parcel.vma_to_lda(0x4029c0, parcels_after))

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(0x402320, parcel.lda_to_vma(plt_lda_before, parcels_after))
        self.assertEquals(0x4029b6, parcel.lda_to_vma(plt_lda_before+num_p1_ldas_before-2, parcels_after))
        self.assertEquals(0x4029bb, parcel.lda_to_vma(plt_lda_before+num_p1_ldas_before-1, parcels_after))

        # these changed
        self.assertEquals(0x4029bc, parcel.lda_to_vma(plt_lda_before+num_p1_ldas_before, parcels_after))
        self.assertEquals(0x4029bd, parcel.lda_to_vma(plt_lda_before+num_p1_ldas_before+1, parcels_after))
        self.assertEquals(0x4029be, parcel.lda_to_vma(plt_lda_before+num_p1_ldas_before+2, parcels_after))
        self.assertEquals(0x4029bf, parcel.lda_to_vma(plt_lda_before+num_p1_ldas_before+3, parcels_after))
        self.assertEquals(0x4029c0, parcel.lda_to_vma(plt_lda_before+num_p1_ldas_before+4, parcels_after))

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(0x4029c0, parcel.lda_to_vma(text_lda_before+4, parcels_after))

    def test_split_to_data_single_inst_in_parcel(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd,
                    'data/code_split_single_instruction/split_parcel_single'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(ScanOperation())

        parcels_before = odb_file.get_structure_list(Parcel)

        # only one instruction in .single
        p = parcel.find_parcel_by_vma(0x400598, parcels_before)
        p_text = parcel.find_parcel_by_vma(0x400597, parcels_before)
        p_fini = parcel.find_parcel_by_vma(0x4005a0, parcels_before)
        p_got = parcel.find_parcel_by_vma(0x600fe0, parcels_before)
        num_ldas_before = p.num_ldas()
        num_text_ldas_before = p_text.num_ldas()
        num_fini_ldas_before = p_fini.num_ldas()
        single_lda_before = p.lda_start
        fini_lda_before = p_fini.lda_start
        text_lda_before = p_text.lda_start
        got_lda_before = p_got.lda_start

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x400598, False))

        # number of parcels after the split (should not have changed)
        parcels_after = odb_file.get_structure_list(Parcel)
        self.assertEquals(25, len(parcels_after))

        # get the parcels
        p = parcel.find_parcel_by_vma(0x400598, parcels_after)
        p_text = parcel.find_parcel_by_vma(0x400597, parcels_after)
        p_fini = parcel.find_parcel_by_vma(0x4005a0, parcels_after)

        # make sure they are all unique
        self.assertNotEqual(p, p_text)
        self.assertNotEqual(p, p_fini)
        self.assertNotEqual(p_text, p_fini)

        # check num_ldas in p (1 instruction become 7 data bytes)
        self.assertEquals(7, p.num_ldas())

        # check num_ldas in text didn't change
        self.assertEquals(num_text_ldas_before, p_text.num_ldas())

        # check num_ldas in fini didn't change
        self.assertEquals(num_fini_ldas_before, p_fini.num_ldas())

        # make sure vmas line up
        self.assertEquals(0x4003d0, p_text.vma_start)
        self.assertEquals(0x400598, p_text.vma_end)
        self.assertEquals(0x400598, p.vma_start)
        self.assertEquals(0x40059f, p.vma_end)
        self.assertEquals(0x4005a0, p_fini.vma_start)
        self.assertEquals(0x4005ae, p_fini.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(text_lda_before, parcel.vma_to_lda(0x4003d0, parcels_after))
        self.assertEquals(text_lda_before+num_text_ldas_before-1, parcel.vma_to_lda(0x400597, parcels_after))
        self.assertEquals(single_lda_before, parcel.vma_to_lda(0x400598, parcels_after))

        # these changed
        self.assertEquals(single_lda_before+1, parcel.vma_to_lda(0x400599, parcels_after))
        self.assertEquals(single_lda_before+2, parcel.vma_to_lda(0x40059a, parcels_after))
        self.assertEquals(single_lda_before+3, parcel.vma_to_lda(0x40059b, parcels_after))
        self.assertEquals(single_lda_before+4, parcel.vma_to_lda(0x40059c, parcels_after))
        self.assertEquals(single_lda_before+5, parcel.vma_to_lda(0x40059d, parcels_after))
        self.assertEquals(single_lda_before+6, parcel.vma_to_lda(0x40059e, parcels_after))

        # 1 instruction turned into 7 data bytes, so it shifted the following parcels by 6 ldas
        self.assertEquals(fini_lda_before+6, parcel.vma_to_lda(0x4005a0, parcels_after))
        self.assertEquals(got_lda_before+6, parcel.vma_to_lda(0x600fe0, parcels_after))

        #
        # make sure lda->vma mappings line up
        #

        self.assertEquals(text_lda_before, parcel.vma_to_lda(0x4003d0, parcels_after))
        self.assertEquals(text_lda_before+num_text_ldas_before-1, parcel.vma_to_lda(0x400597, parcels_after))
        self.assertEquals(single_lda_before, parcel.vma_to_lda(0x400598, parcels_after))

        # these shouldn't have changed
        self.assertEquals(0x4003d0, parcel.lda_to_vma(text_lda_before, parcels_after))
        self.assertEquals(0x400597, parcel.lda_to_vma(text_lda_before+num_text_ldas_before-1, parcels_after))
        self.assertEquals(0x400598, parcel.lda_to_vma(single_lda_before, parcels_after))

        # these changed
        self.assertEquals(0x400599, parcel.lda_to_vma(single_lda_before+1, parcels_after))
        self.assertEquals(0x40059a, parcel.lda_to_vma(single_lda_before+2, parcels_after))
        self.assertEquals(0x40059b, parcel.lda_to_vma(single_lda_before+3, parcels_after))
        self.assertEquals(0x40059c, parcel.lda_to_vma(single_lda_before+4, parcels_after))
        self.assertEquals(0x40059d, parcel.lda_to_vma(single_lda_before+5, parcels_after))
        self.assertEquals(0x40059e, parcel.lda_to_vma(single_lda_before+6, parcels_after))

        # 1 instruction turned into 7 data bytes, so it shifted the following parcels by 6 ldas
        self.assertEquals(0x4005a0, parcel.lda_to_vma(fini_lda_before+6, parcels_after))
        self.assertEquals(0x600fe0, parcel.lda_to_vma(got_lda_before+6, parcels_after))



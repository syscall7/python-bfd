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

    def test_basic_split(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(ScanOperation())

        parcels_before = odb_file.get_structure_list(Parcel)
        p = parcel.find_parcel_by_vma(0x4029c0, parcels_before)
        num_p1_ldas_before = p.num_ldas()
        text_lda_before = p.vma_to_lda(0x4029c0)

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


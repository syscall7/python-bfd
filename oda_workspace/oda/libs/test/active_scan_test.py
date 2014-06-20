import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.odb_file import BinaryFile

class TestActiveScanOperation(unittest.TestCase):

    def test_basic_active_scan(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        # we load this ELF as a raw binary, because it has an invalid opcode fairly early on
        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))
        p = parcels_before.find_parcel_by_vma(0x400245)
        num_p1_ldas_before = p.num_ldas

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(ActiveScanOperation(0x400245))

        # number of parcels after the split
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(26, len(parcels_after))

        # get the three parcels
        p1 = parcels_after.find_parcel_by_vma(0x400238)
        p2 = parcels_after.find_parcel_by_vma(0x400245)

        # make sure they are all unique
        self.assertNotEqual(p1, p2)

        # check num_ldas in p1 (13 bytes)
        self.assertEquals(13, p1.num_ldas)

        # check num_ldas in p2
        self.assertEquals(6, p2.num_ldas)

        # check num_ldas in p3 (less 5 from p1 and less 1 from p2 - remember it used to only be 1 lda before the split)
        #self.assertEquals(num_p1_ldas_before - 5 - 1, p3.num_ldas)

        # make sure vmas line up
        #self.assertEquals(0x4029c0, p1.vma_start)
        #self.assertEquals(0x4029d5, p1.vma_end)
        #self.assertEquals(0x4029d5, p2.vma_start)
        #self.assertEquals(0x4029da, p2.vma_end)
        #self.assertEquals(0x4029da, p3.vma_start)
        #self.assertEquals(0x412bec, p3.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        #self.assertEquals(text_lda_before, parcels_after.vma_to_lda(0x4029c0))
        #self.assertEquals(text_lda_before+5, parcels_after.vma_to_lda(0x4029d5))
        #self.assertEquals(True, p1.is_code)
        #self.assertEquals(True, p3.is_code)

        # these changed
        #self.assertEquals(text_lda_before+6, parcels_after.vma_to_lda(0x4029d6))
        #self.assertEquals(text_lda_before+7, parcels_after.vma_to_lda(0x4029d7))
        #self.assertEquals(text_lda_before+8, parcels_after.vma_to_lda(0x4029d8))
        #self.assertEquals(text_lda_before+9, parcels_after.vma_to_lda(0x4029d9))
        #self.assertEquals(text_lda_before+10, parcels_after.vma_to_lda(0x4029da))
        #self.assertEquals(text_lda_before+11, parcels_after.vma_to_lda(0x4029db))
        #self.assertEquals(False, p2.is_code)

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        #self.assertEquals(fini_lda_before+4, parcels_after.vma_to_lda(0x412bec))

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        #self.assertEquals(0x4029c0, parcels_after.lda_to_vma(text_lda_before))
        #self.assertEquals(0x4029d5, parcels_after.lda_to_vma(text_lda_before+5))

        # these changed
        #self.assertEquals(0x4029d6, parcels_after.lda_to_vma(text_lda_before+6))
        #self.assertEquals(0x4029d7, parcels_after.lda_to_vma(text_lda_before+7))
        #self.assertEquals(0x4029d8, parcels_after.lda_to_vma(text_lda_before+8))
        #self.assertEquals(0x4029d9, parcels_after.lda_to_vma(text_lda_before+9))
        #self.assertEquals(0x4029da, parcels_after.lda_to_vma(text_lda_before+10))
        #self.assertEquals(0x4029db, parcels_after.lda_to_vma(text_lda_before+11))

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        #self.assertEquals(0x412bec, parcels_after.lda_to_vma(fini_lda_before+4))

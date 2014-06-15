from oda.libs.odb.structures.oda_object import OdaObject
from bidict import bidict

import logging
logger = logging.getLogger(__name__)

def vma_to_lda(vma, parcels):
    for p in parcels:
        lda = p.vma_to_lda(vma)
        if lda is not None:
            return lda
    return None

def lda_to_vma(lda, parcels):
    for p in parcels:
        vma = p.lda_to_vma(lda)
        if vma is not None:
            return vma
    return None

def find_parcel_by_vma(vma, parcels):
    for p in parcels:
        if p.contains_vma(vma):
            return p
    return None

class Parcel(OdaObject):
    def __init__(self, object_id, is_code, vma_start, vma_end):
        super(Parcel, self).__init__(object_id)
        self.is_code = is_code
        self.vma_start = vma_start
        self.vma_end = vma_end
        self.sample_offsets = []
        self.lda_start = 0

        # lda_bidict[lda_rel_to_start] = vma
        self.lda_bidict = bidict({})

    def __repr__(self):
        return "Parcel {is_code=%s, start=%s, end=%s>" % (self.is_code, self.vma_start, self.vma_end)

    # returns True if this parcel contains the given virtual memory address (vma)
    def contains_vma(self, addr):
        return addr >= self.vma_start and addr < self.vma_end

    # returns True if this parcel contains the given logical display unit address (lda)
    def contains_lda(self, lda):
        return lda >= self.lda_start and (lda -self.lda_start) < self.num_ldas()

    def num_ldas(self):
        if self.is_code:
            return len(self.lda_bidict)
        else:
            return self.vma_end - self.vma_start

    def push_vma(self, vma):
        """ Used to build up the lda<->vma mapping, assumes it is built in order of increasing vma """
        raise NotImplementedError("Please Implement this method in a child class")

    def vma_to_lda(self, vma):
        """ Convert a vma to lda """
        raise NotImplementedError("Please Implement this method in a child class")

    def lda_to_vma(self, vma):
        """ Convert a lda to vma """
        raise NotImplementedError("Please Implement this method in a child class")

    def split(self, vma, to_code):
        """ Split a parcel """
        raise NotImplementedError("Please Implement this method in a child class")

class CodeParcel(Parcel):

    @property
    def item_type(self):
        """ Consider us to be whatever item type our parent is """
        return 'Parcel'

    def _find_inst_boundary(self, vma):
        for i in range(vma - self.vma_start + 1):
            # snap to closest vma that is less than the given vma
            closest_vma = vma - i
            if closest_vma in self.lda_bidict.values():
                return closest_vma

        return None

    def push_vma(self, vma):
        self.lda_bidict[len(self.lda_bidict)] = vma

    # converts the given vma to lda
    def vma_to_lda(self, vma):
        if not self.contains_vma(vma):
            return None

        if self.is_code:
            inst_vma = self._find_inst_boundary(vma)
            if inst_vma is not None:
                return self.lda_bidict[:inst_vma] + self.lda_start

        return None

    # converts the given lda to vma
    def lda_to_vma(self, lda):
        if not self.contains_lda(lda):
            return None

        return self.lda_bidict[lda-self.lda_start]

    def split(self, odb_file, vma, to_code):
        if (to_code):
            logger.warn("Attempting to split a code parcel to code does not make any sense!")
            return None

        if not self.contains_vma(vma):
            logger.error("Attempting to split a code parcel at a bad vma!")
            return None

        inst_vma = self._find_inst_boundary(vma)

        # The current parcel will potentially become three parcels: CODE, DATA, CODE
        # TODO:
        first = self
        second = DataParcel()
        third = DataParcel()


class DataParcel(Parcel):

    @property
    def item_type(self):
        """ Consider us to be whatever item type our parent is """
        return 'Parcel'

    def push_vma(self, vma):
        return

    def vma_to_lda(self, vma):
        if not self.contains_vma(vma):
            return None

        return self.lda_start + (vma - self.vma_start)

    def lda_to_vma(self, lda):
        if not self.contains_lda(lda):
            return None

        return self.vma_start + (lda - self.lda_start)


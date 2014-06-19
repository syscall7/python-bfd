from oda.libs.odb.structures.oda_object import OdaObject
from bidict import bidict
from abc import ABCMeta, abstractmethod, abstractproperty

import logging
logger = logging.getLogger(__name__)

class ParcelList(list):
    """ Represents a group of parcels on which to operate as a whole """

    def vma_to_lda(self, vma):
        for p in self:
            lda = p.vma_to_lda(vma)
            if lda is not None:
                return lda
                # TODO: Keep iterating and ensure duplicate mapping is not found
        return None

    def lda_to_vma(self, lda):
        for p in self:
            vma = p.lda_to_vma(lda)
            if vma is not None:
                return vma
                # TODO: Keep iterating and ensure duplicate mapping is not found
        return None

    def find_parcel_by_vma(self, vma):
        for p in self:
            if p.contains_vma(vma):
                return p
                # TODO: Keep iterating and ensure duplicate mapping is not found
        return None

    def split(self, vma):
        p = self.find_parcel_by_vma(vma)
        if p is not None:
            return p.split(vma)
        return None

    def sum_ldas(self):
        sum = 0
        for p in self:
            sum += p.num_ldas
        return sum

class ParcelTransaction(object):
    """ Represents a set of parcels that should be added or removed from a parcel list """
    def __init__(self, to_add=[], to_remove=[], adjustment=0):
        self.to_add = to_add
        self.to_remove = to_remove
        self.adjustment = adjustment


class Parcel(OdaObject):
    """ Abstract class representing a contiguous group of display units """

    __metaclass__ = ABCMeta

    def __init__(self, object_id, vma_start, vma_end):
        super(Parcel, self).__init__(object_id)
        self.vma_start = vma_start
        self.vma_end = vma_end
        self.sample_offsets = []
        self.lda_start = 0

        # lda_bidict[lda_rel_to_start] = vma
        self.lda_bidict = bidict({})

    def __repr__(self):
        return "Parcel {is_code=%s, start=%s, end=%s>" % (self.is_code, self.vma_start, self.vma_end)

    def is_empty(self):
        return self.vma_start == self.vma_end

    # returns True if this parcel contains the given virtual memory address (vma)
    def contains_vma(self, addr):
        return addr >= self.vma_start and addr < self.vma_end

    # returns True if this parcel contains the given logical display unit address (lda)
    def contains_lda(self, lda):
        return lda >= self.lda_start and (lda -self.lda_start) < self.num_ldas

    def copy_from(self, other):
        self.vma_start = other.vma_start
        self.vma_end = other.vma_end
        self.lda_start = other.lda_start
        self.lda_bidict = other.lda_bidict
        self.sample_offsets = other.sample_offsets

    @abstractproperty
    def is_code(self):
        """ Whether or not this parcel is code """
        raise NotImplementedError("Please Implement this method in a child class")

    @abstractproperty
    def num_ldas(self):
        """ Get the total number of logical display units in this parcel """
        raise NotImplementedError("Please Implement this method in a child class")

    @abstractmethod
    def push_vma(self, vma):
        """ Used to build up the lda<->vma mapping, assumes it is built in order of increasing vma """
        raise NotImplementedError("Please Implement this method in a child class")

    @abstractmethod
    def vma_to_lda(self, vma):
        """ Convert a vma to lda """
        raise NotImplementedError("Please Implement this method in a child class")

    @abstractmethod
    def lda_to_vma(self, vma):
        """ Convert a lda to vma """
        raise NotImplementedError("Please Implement this method in a child class")

    @abstractmethod
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

    @property
    def is_code(self):
        return True

    @property
    def num_ldas(self):
        """ Get the total number of logical display units in this parcel """
        return len(self.lda_bidict)

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

    def split(self, vma):

        if not self.contains_vma(vma):
            logger.error("Attempting to split a code parcel at a bad vma!")
            return None

        # the number of code ldas that are being converted to data ldas
        NUM_LDAS_TO_DATA = 1

        # edge cases
        # 1. The split occurs on the first instruction of the parcel
        #    This case results in only two parcels
        # 2. The split occurs on the last instruction of the parcel
        #    This case results in only two parcels
        # 3. The split occurs on the first and last instruction of the parcel (only 1 instruction in parcel)
        #    This case results in only one parcel

        # get lda/vma by nearest lower instruction boundary
        inst_lda = self.vma_to_lda(vma)
        inst_vma = self.lda_to_vma(inst_lda)

        # The current parcel will potentially become three parcels: CODE, DATA, CODE
        first = self

        # setup second parcel
        second_vma_end = self.lda_to_vma(inst_lda + NUM_LDAS_TO_DATA)

        # this can happen when splitting on the last instruction of a code parcel
        if second_vma_end is None:
            second_vma_end = first.vma_end
        second = DataParcel(0, vma_start=inst_vma, vma_end=second_vma_end)
        second.lda_start = inst_lda

        # setup third parcel
        third = CodeParcel(0, vma_start=second.vma_end, vma_end=first.vma_end)
        third.lda_start = inst_lda+second.num_ldas

        # fixup the first parcel
        first.vma_end = inst_vma

        # transfer ldas to second/third
        for lda,vma in self.lda_bidict.items():
            abs_lda = lda + self.lda_start
            if abs_lda >= second.lda_start:
                if abs_lda < second.lda_start + NUM_LDAS_TO_DATA:
                    second.push_vma(self.lda_bidict[lda])
                else:
                    third.push_vma(self.lda_bidict[lda])

                del self.lda_bidict[lda]

        # the parcels to add and the parcels to remove
        to_add = [second]
        to_remove = []

        if first.is_empty():
            to_remove.append(first)

        if not third.is_empty():
            to_add.append(third)

        return ParcelTransaction(to_add, to_remove, second.num_ldas - NUM_LDAS_TO_DATA)


class DataParcel(Parcel):

    @property
    def item_type(self):
        """ Consider us to be whatever item type our parent is """
        return 'Parcel'

    @property
    def is_code(self):
        return False

    @property
    def num_ldas(self):
        """ Get the total number of logical display units in this parcel """
        return self.vma_end - self.vma_start

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

    def split(self, vma):
        if not self.contains_vma(vma):
            logger.error("Attempting to split a data parcel at a bad vma!")
            return None

        # check if the vma is even pointing to a valid instruction


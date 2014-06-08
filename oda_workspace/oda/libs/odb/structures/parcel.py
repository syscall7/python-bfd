from oda.libs.odb.structures.oda_object import OdaObject
from bidict import bidict

__author__ = 'davis'

class Parcel(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(Parcel, self).__init__(object_id)
        self.is_code = kwargs['is_code']
        self.start = kwargs['start']
        self.end = kwargs['end']
        self.sample_offsets = []
        self.lda_start = 0
        self.lda_bidict = bidict({})

    def __repr__(self):
        return "Parcel {is_code=%s, start=%s, end=%s>" % (self.is_code, self.start, self.end)

    # returns True if this parcel contains the given virtual memory address (vma)
    def contains_vma(self, addr):
        return addr >= self.start and addr < self.end

    # returns True if this parcel contains the given logical display unit address (lda)
    def contains_lda(self, lda):
        return lda >= self.lda_start and (lda -self.lda_start) < self.num_ldas()

    def num_ldas(self):
        if self.is_code:
            return len(self.lda_bidict)
        else:
            return self.end - self.start

    def push_vma(self, vma):
        if self.is_code:
            self.lda_bidict[self.lda_start + len(self.lda_bidict)] = vma

    # converts the given vma to lda
    def vma_to_lda(self, vma):
        if not self.contains_vma(vma):
            return None

        if self.is_code:
            for i in range(vma - self.start):
                # snap to closest vma that is less than the given vma
                closest_vma = vma - i
                if closest_vma in self.lda_bidict.values():
                    return self.lda_bidict[:closest_vma]
        else:
            return self.lda_start + (vma - self.start)

        return None

    # converts the given lda to vma
    def lda_to_vma(self, lda):
        if not self.contains_lda(lda):
            return None

        if self.is_code:
            return self.lda_bidict[lda]
        else:
            return self.start + (lda - self.lda_start)


    '''
    def vma_to_lda(self, vma):
        """Convert a vma to lda"""
        raise NotImplementedError("Please Implement this method in a child class")

    def lda_to_vma(self, vma):
        """Convert a lda to vma"""
        raise NotImplementedError("Please Implement this method in a child class")

    def push_vma(self, vma):
        """ Used to build up the lda<->vma mapping, assumes it is built in order of increasing vma"""
        raise NotImplementedError("Please Implement this method in a child class")
    '''

'''
class CodeParcel(Parcel):

    def push_vma(self, vma):
        self.lda_bidict[len(self.lda_bidict)] = vma

    # converts the given vma to lda
    def vma_to_lda(self, vma):
        if not self.contains_vma(vma):
            return None

        for i in range(vma - self.start):
            # snap to closest vma that is less than the given vma
            closest_vma = vma - i
            if closest_vma in self.lda_bidict.values():
                return self.lda_bidict[:closest_vma]

        return None

    # converts the given lda to vma
    def lda_to_vma(self, lda):
        if not self.contains_lda(lda):
            return None

        return self.lda_bidict[lda]

class DataParcel(Parcel):

    def push_vma(self, vma):
        return

    def vma_to_lda(self, vma):
        if not self.contains_vma(vma):
            return None
        return self.lda_start + (vma - self.start)

    def lda_to_vma(self, lda):
        if not self.contains_lda(lda):
            return None

        return self.start + (lda - self.lda_start)
'''


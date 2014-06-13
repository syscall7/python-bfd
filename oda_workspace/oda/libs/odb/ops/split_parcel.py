import logging
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures import parcel

logger = logging.getLogger(__name__)

class SplitParcelOperation(Operation):

    def __init__(self, vma, to_code):
        super(SplitParcelOperation, self).__init__()
        self.object_id = -1
        self.to_code = to_code
        self.vma = vma

    def operate(self, odb_file):
        assert (len(odb_file.get_structure_list(Parcel)) > 0)

        self.object_id = odb_file.get_object_id()

        parcels = odb_file.get_structure_list(Parcel)

        orig_parcel = parcel.find_parcel_by_vma(self.vma, parcels)
        assert (orig_parcel is not None)

        # TODO
        #orig_parcel.split



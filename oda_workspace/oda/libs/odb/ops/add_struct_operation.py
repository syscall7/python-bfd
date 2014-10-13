import logging
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.parcel import CodeParcel, DataParcel
from oda.libs.odb.structures.c_struct import CStructObject

logger = logging.getLogger(__name__)

class AddStructOperation(Operation):

    def __init__(self, vma, struct_type, variable_name):
        super(AddStructOperation, self).__init__()
        self.object_id = -1
        self.struct_type = struct_type
        self.variable_name = variable_name
        self.vma = vma

    def operate(self, odb_file):
        assert (len(odb_file.get_structure_list(Parcel)) > 0)

        self.object_id = odb_file.get_object_id()

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        tgt_parcel = None
        for p in parcels:
            if self.vma >= p.vma_start and self.vma<p.vma_end:
                tgt_parcel = p
                break


        # TODO: Throw an exception here
        assert (tgt_parcel is not None)
        assert (tgt_parcel.is_code is not True)

        struct_obj = odb_file.create_item(CStructObject, {
                'addr': self.vma,
                'variable_name': self.variable_name,
                'struct_type': self.struct_type,
            })

        tgt_parcel.add_struct_variable(self.vma, struct_obj)



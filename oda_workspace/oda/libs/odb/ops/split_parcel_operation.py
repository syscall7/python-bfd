import logging
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures import parcel
from oda.libs.odb.structures.parcel import CodeParcel, DataParcel

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
        parcels_to_adjust = [p for p in parcels if p.vma_start > self.vma]

        orig_parcel = parcel.find_parcel_by_vma(self.vma, parcels)
        assert (orig_parcel is not None)

        (to_add, to_remove, ldas_added) = orig_parcel.split(self.vma, self.to_code)

        for p in to_remove:
            odb_file.remove_item(p)

        for p in to_add:
            if p.is_code:
                parcel_class = CodeParcel
            else:
                parcel_class = DataParcel

            inserted_p = odb_file.insert_item(odb_file.create_item(parcel_class, {
                'is_code': p.is_code,
                'vma_start': p.vma_start,
                'vma_end': p.vma_end,
            }))

            inserted_p.copy_from(p)

        # fixup parcel lda offsets
        for p in parcels_to_adjust:
            p.lda_start += ldas_added


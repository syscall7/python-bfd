import logging
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.parcel import CodeParcel, DataParcel

logger = logging.getLogger(__name__)

class SplitParcelOperation(Operation):

    def __init__(self, vma):
        super(SplitParcelOperation, self).__init__()
        self.object_id = -1
        self.vma = vma

    def operate(self, odb_file):
        assert (len(odb_file.get_structure_list(Parcel)) > 0)

        self.object_id = odb_file.get_object_id()

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        parcels_to_adjust = [p for p in parcels if p.vma_start > self.vma]

        transaction = parcels.split(self.vma)

        # TODO: Throw an exception here
        assert (transaction is not None)

        # remove dead parcels
        for p in transaction.to_remove:
            odb_file.remove_item(p)

        # add new parcels
        for p in transaction.to_add:
            if p.is_code:
                parcel_class = CodeParcel
            else:
                parcel_class = DataParcel

            inserted_p = odb_file.insert_item(odb_file.create_item(parcel_class, {
                'vma_start': p.vma_start,
                'vma_end': p.vma_end,
                'sec_name': p.sec_name,
            }))

            inserted_p.copy_from(p)

        # fixup parcel lda offsets in affected parcels
        for p in parcels_to_adjust:
            p.lda_start += transaction.adjustment

        #
        # consolidate parcels
        #
        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        transaction = parcels.consolidate()

        # remove dead parcels
        for p in transaction.to_remove:
            odb_file.remove_item(p)


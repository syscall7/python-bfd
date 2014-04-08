from odb.ops.operation import Operation

__author__ = 'davis'


class AddOperation(Operation):
    def __init__(self, item, validators):
        super(AddOperation, self).__init__(validators)

        self.item = item
        self.object_id = -1

    def operate(self, odb_file):
        self.object_id = odb_file.get_object_id()
        odb_file.insert_item(self.item)

    def invert(self, odb_file):
        if odb_file.operations[-1] != self:
            raise Exception("You can only invert the last function applied")
        #func = next(x for x in odb_file.functions if x.object_id == self.function_object_id)
        odb_file.operations.pop()
        odb_file.remove_item(self.item)







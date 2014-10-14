from oda.libs.odb.structures.oda_object import OdaObject
from oda.libs.odb.ops.operation import ValidationError
from oda.libs.odb.ops.add_operation import AddOperation
from abc import ABCMeta, abstractmethod, abstractproperty

__author__ = 'thomaskeeley'

class CStructFieldDoesNotExistError(Exception):
    pass

class CStructFieldAlreadyExistsError(Exception):
    pass

class FieldsValidator(object):
    def validate(self, operation, odb_file):
        fields = operation.item.fields
        for field in fields:
            if not isinstance(field,Field):
                raise ValidationError("Field is not a valid type")


def generate_operation(op, *args):
    factory = {
        AddOperation: AddOperation(args[0], [FieldsValidator()])
    }
    if op in factory:
        return factory[op]

    return op(*args)

class Field(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, type, is_array=False, array_len=0, size=1):
        self.name = name
        self.type = type
        self.is_array = is_array
        self.array_len = array_len
        #self.size = size

    @abstractproperty
    def size(self):
        """ Whether or not this parcel is code """
        #raise NotImplementedError("Please Implement this method in a child class")

class BuiltinField(Field):
    def __init__(self, name, type, is_array=False, array_len=1):
        super(BuiltinField, self).__init__(name,type,is_array,array_len)

    @property
    def size(self):
        return self.type.size*self.array_len

class CStructField(Field):
    def __init__(self, name, c_struct_obj, is_array=False, array_len=1):
        super(CStructField, self).__init__(name,CStruct,is_array,array_len)
        self.cstruct = c_struct_obj

    @property
    def size(self):
        return self.cstruct.size*self.array_len


class CStruct(OdaObject):
    def __init__(self, object_id, name, is_packed=True):
        super(CStruct, self).__init__(object_id)
        self.name = name
        self.fields = []
        self.is_packed = is_packed

    @property
    def size(self):
        if len(self.fields):
            # TODO: Handle unpacked structs (by architecture type?)
            return sum(field.size for field in self.fields)
        else:
            return 0

    def append_field(self, new_field):
        # Field name must be unique
        for field in self.fields:
            if field.name == new_field.name:
                raise CStructFieldAlreadyExistsError("Field with name already exists in the struct")
        self.fields.append(new_field)

    def prepend_field(self, new_field):
        self.fields.insert(0,new_field)

    def delete_field(self, name):
        for field in self.fields:
            if field.name == name:
                self.fields.remove(field)


class CStructObject(OdaObject):
    def __init__(self, object_id, addr, variable_name, struct_type):
        super(CStructObject, self).__init__(object_id)
        self.name = variable_name
        self.struct_type = struct_type
        self.addr = addr


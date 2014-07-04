import json
from oda.apps.odaweb.models import OdaMaster
from rest_framework import serializers


class CommentSerializer(serializers.Serializer):
    comment = serializers.CharField()
    offset = serializers.IntegerField()

class BinaryFileSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=128)
    filesize = serializers.IntegerField()
    hash = serializers.CharField(max_length=128)

class DataStringSerializer(serializers.Serializer):
    string = serializers.CharField()
    addr = serializers.IntegerField()

class BinaryStringSerializer(serializers.Serializer):
    binary_string = serializers.CharField()

class SymbolSerializer(serializers.Serializer):
    name = serializers.CharField()
    offset = serializers.IntegerField()
    type = serializers.CharField()

class LabelSerializer(serializers.Serializer):
    label = serializers.CharField()
    offset = serializers.IntegerField()

class OdaMasterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OdaMaster
        fields = ('project_name', 'short_name', 'revision', 'creation_date')

class FunctionSerializer(serializers.Serializer):
    retval = serializers.CharField(required=False)
    args = serializers.CharField()
    offset = serializers.IntegerField()
    name = serializers.CharField()

class StringListField(serializers.WritableField):
    def to_native(self, obj):
        return json.dumps(obj)
    def from_native(self, obj):
        return json.loads(obj)

class ParcelSerializer(serializers.Serializer):
    vma_start = serializers.IntegerField()
    vma_end = serializers.IntegerField()
    lda_start = serializers.IntegerField()
    is_code = serializers.BooleanField()

class RefSerializer(serializers.Serializer):
    offset = serializers.IntegerField()

class DisplayUnitSerializer(serializers.Serializer):
    section_name = serializers.CharField()
    offset = serializers.IntegerField()
    rawBytes = serializers.CharField()
    instStr = serializers.CharField()
    branch = serializers.CharField()
    branch_label = serializers.CharField()
    opcode = serializers.CharField()
    operands = serializers.CharField()
    stringRef = RefSerializer(required=False)
    branchRef = RefSerializer(required=False)
    targetRef = RefSerializer(required=False)
    crossRef = RefSerializer(required=False, many=True)
    isBranch = serializers.BooleanField()
    isFunction = serializers.BooleanField()
    labelName = serializers.CharField()


class SectionFlagSerializer(serializers.Serializer):
    abbrev = serializers.CharField()
    desc = serializers.CharField()
    name = serializers.CharField()
    val = serializers.IntegerField()

class SectionSerializer(serializers.Serializer):
    name = serializers.CharField()
    size = serializers.IntegerField()
    vma = serializers.IntegerField()
    flags = SectionFlagSerializer()
    #alignment_base = serializers.IntegerField()
    #alignment_exp = serializers.IntegerField()

    def restore_fields(self, data, files):
        pass
    def restore_object(self, attrs, instance=None):
        pass

class StringSerializer(serializers.Serializer):
    addr  = serializers.CharField()
    string = serializers.CharField()

class FindResultsSerializer(serializers.Serializer):
    addr  = serializers.CharField()
    section = serializers.CharField()

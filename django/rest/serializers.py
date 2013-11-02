import json
from odaweb.models import OdaMaster, Comment, BinaryFile, BinaryString
from rest_framework import serializers



class BinaryFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BinaryFile
        fields = ('filename', 'filesize', 'hash')

class BinaryStringSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BinaryString
        fields = ['binary_string']

class BinaryObjectRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `tagged_object` generic relationship.
    """

    def to_native(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if isinstance(value, BinaryFile):
            serializer = BinaryFileSerializer(value)
        elif isinstance(value, BinaryString):
            serializer = BinaryStringSerializer(value)
        else:
            raise Exception('Unexpected type of ' + value.__class__.__name__)

        return serializer.data

class OdaMasterSerializer(serializers.HyperlinkedModelSerializer):
    binary = BinaryObjectRelatedField()

    class Meta:
        model = OdaMaster
        fields = ('project_name', 'short_name', 'revision', 'creation_date', 'binary')


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ('comment', 'offset')

class StringListField(serializers.WritableField):
    def to_native(self, obj):
        return json.dumps(obj)
    def from_native(self, obj):
        return json.loads(obj)

class BinarySuperChunkSerializer(serializers.Serializer):
    start = serializers.IntegerField()
    end = serializers.IntegerField()
    is_boundary = serializers.BooleanField()


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
    offset = serializers.CharField()
    string = serializers.CharField()

class SymbolSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    offset = serializers.CharField()
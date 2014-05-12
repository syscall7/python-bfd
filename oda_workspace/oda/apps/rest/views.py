import logging

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from oda.apps.odaweb.models import OdaMaster

from oda.apps.rest.serializers import OdaMasterSerializer, SectionSerializer, StringSerializer, DisplayUnitSerializer, \
    BinaryParcelSerializer, \
    FindResultsSerializer, CommentSerializer, FunctionSerializer, DataStringSerializer, SymbolSerializer, \
    LabelSerializer
from oda.libs.odb.bfd.disassembler import Disassembler
from oda.libs.odb.odb_file import OdbFile, DefaultOdbSerializer
from oda.libs.odb.ops.load_operation import LoadOperationFactory
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.label import Label
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol


logger = logging.getLogger(__name__)


class OdaMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = OdaMaster.objects.all()
    serializer_class = OdaMasterSerializer
    paginate_by = 10


class OdaStructureViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super(OdaStructureViewSet, self).__init__(**kwargs)
        self.odb_file = None

    def get_structure_list(self):
        return self.odb_file.get_structure_list(self.structure)

    def map_item(self, item):
        return item

    def list(self, request, format=None):
        short_name = request.QUERY_PARAMS.get('short_name', None)
        revision = request.QUERY_PARAMS.get('revision', None)

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        self.odb_file = oda.odb()

        structure_list = self.get_structure_list()
        mapped_structure_list = [self.map_item(i) for i in structure_list]
        serializer = self.get_serializer(mapped_structure_list, many=True)
        return Response(serializer.data)


class CommentViewSet(OdaStructureViewSet):
    serializer_class = CommentSerializer
    structure = Comment


class FunctionViewSet(OdaStructureViewSet):
    serializer_class = FunctionSerializer
    structure = Function


class SectionsViewSet(OdaStructureViewSet):
    serializer_class = SectionSerializer
    structure = Section

    def get_structure_list(self):
        sections = self.odb_file.get_structure_list(Section)
        return filter(lambda s: s.is_loadable(), sections)


class StringsViewSet(OdaStructureViewSet):
    serializer_class = DataStringSerializer
    structure = DataString

    def map_item(self, item):
        return {
            'string': item.value,
            'addr': item.addr
        }


class LabelsViewSet(OdaStructureViewSet):
    serializer_class = LabelSerializer
    structure = Label

class SymbolsViewSet(OdaStructureViewSet):
    serializer_class = SymbolSerializer
    structure = Symbol

    def get_structure_list(self):
        return [x for x in self.odb_file.get_structure_list(Symbol) if x.type == 't' or x.type=='T']


class BinaryStringViewSet(viewsets.GenericViewSet):
    def partial_update(self, request, pk):
        oda_master = OdaMaster.objects.get(short_name=request.DATA['short_name'], revision=request.DATA['revision'])

        load_operation = LoadOperationFactory.load_from_string(
            request.DATA['binary_string'], 'i386:x86-64'
        )
        odb_file = OdbFile()
        odb_file.execute(load_operation)
        oda_master.odb_file = DefaultOdbSerializer().dumps(odb_file)
        oda_master.save()

        logger.info("updating...")

        return Response({'binary_string': request.DATA['binary_string']})


class DisplayUnitsViewSet(viewsets.GenericViewSet):
    serializer_class = DisplayUnitSerializer

    def list(self, request):

        start = 0
        units = 100
        if request.QUERY_PARAMS.get('addr'):
            start = int(request.QUERY_PARAMS.get('addr'), 10)
        if request.QUERY_PARAMS.get('units'):
            units = int(request.QUERY_PARAMS.get('units'), 10)

        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                    revision=request.QUERY_PARAMS.get('revision'))

        dasm = Disassembler(oda.odb())
        dunits = dasm.analyze(start, units)

        logger.debug("DisplayUnitsViewSet: Generate serialized data")
        serializer = self.get_serializer(dunits, many=True)
        serialData = Response(serializer.data)
        logger.debug("DisplayUnitsViewSet: Serial data complete")
        return serialData


class FindViewSet(viewsets.GenericViewSet):
    serializer_class = FindResultsSerializer

    def list(self, request):
        bytes = self.request.QUERY_PARAMS.get('bytes', None)
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                    revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        dasm = Disassembler(binary)
        results = [{'addr': key, 'section': value} for key, value in
                   sorted(dasm.find(bytes).items(), key=lambda s: s[0])]
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)



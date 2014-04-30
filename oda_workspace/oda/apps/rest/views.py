import logging

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from oda.apps.odaweb.models import OdaMaster

from oda.apps.rest.serializers import OdaMasterSerializer, SectionSerializer, StringSerializer, DisplayUnitSerializer, BinaryParcelSerializer, \
    FindResultsSerializer, CommentSerializer, FunctionSerializer, DataStringSerializer, SymbolSerializer
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.function import Function
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

class SymbolsViewSet(OdaStructureViewSet):
    serializer_class = SymbolSerializer
    structure = Symbol

# class ParcelsViewSet(viewsets.GenericViewSet):
#     serializer_class = BinaryParcelSerializer
#
#     def list(self, request):
#         oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
#                                   revision=request.QUERY_PARAMS.get('revision'))
#
#         binary = oda.binary
#         jcp = JsonChunkProcessor(binary)
#         parcels = jcp.get_all_parcels()
#
#         serializer = self.get_serializer(parcels, many=True)
#         return Response(serializer.data)
#
# class DisplayUnitsViewSet(viewsets.GenericViewSet):
#     serializer_class = DisplayUnitSerializer
#
#     def list(self, request):
#
#         start = 0
#         units = 100
#         if request.QUERY_PARAMS.get('addr'):
#             start = int(request.QUERY_PARAMS.get('addr'),10)
#         if request.QUERY_PARAMS.get('units'):
#             units = int(request.QUERY_PARAMS.get('units'),10)
#
#         oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
#                                   revision=request.QUERY_PARAMS.get('revision'))
#
#         dasm = Disassembler(oda.binary)
#         dunits = dasm.analyze(start, units)
#
#         logger.debug("DisplayUnitsViewSet: Generate serialized data")
#         serializer = self.get_serializer(dunits, many=True)
#         serialData = Response(serializer.data)
#         logger.debug("DisplayUnitsViewSet: Serial data complete")
#         return serialData
#
#


# class SymbolsViewSet(viewsets.ModelViewSet):
#     model = Symbol
#
#     def get_queryset(self):
#         queryset = Symbol.objects.all()
#         short_name = self.request.QUERY_PARAMS.get('short_name', None)
#         revision = self.request.QUERY_PARAMS.get('revision', None)
#         if short_name is not None:
#             queryset = Symbol.get_for_binary(OdaMaster.objects.get(short_name=short_name, revision=revision).binary)
#
#         return queryset


# class BinaryStringViewSet(viewsets.ModelViewSet):
#     model = BinaryString
#
# class FunctionsViewSet(viewsets.ModelViewSet):
#     model = Function
#
#     def get_queryset(self):
#         queryset = Function.objects.all()
#         short_name = self.request.QUERY_PARAMS.get('short_name', None)
#         revision = self.request.QUERY_PARAMS.get('revision', None)
#         if short_name is not None:
#             queryset = Function.get_for_binary(OdaMaster.objects.get(short_name=short_name, revision=revision).binary)
#
#         return queryset
#
# class LabelsViewSet(viewsets.ModelViewSet):
#     model = Label
#
#     def get_queryset(self):
#         queryset = Label.objects.all()
#         short_name = self.request.QUERY_PARAMS.get('short_name', None)
#         revision = self.request.QUERY_PARAMS.get('revision', None)
#         if short_name is not None:
#             queryset = Label.get_for_binary(OdaMaster.objects.get(short_name=short_name, revision=revision).binary)
#
#         return queryset

# class OdaOptionsViewSet(viewsets.ModelViewSet):
#     model = OdaOptions
#
#     def get_queryset(self):
#         queryset = OdaOptions.objects.all()
#         short_name = self.request.QUERY_PARAMS.get('short_name', None)
#         revision = self.request.QUERY_PARAMS.get('revision', None)
#         if short_name is not None:
#             queryset = OdaOptions.get_for_binary(OdaMaster.objects.get(short_name=short_name, revision=revision).binary)
#
#         return queryset


class FindViewSet(viewsets.GenericViewSet):
    serializer_class = FindResultsSerializer

    def list(self, request):
        bytes = self.request.QUERY_PARAMS.get('bytes', None)
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                    revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        dasm = Disassembler(binary)
        results = [{'addr': key, 'section': value} for key, value in sorted(dasm.find(bytes).items(), key=lambda s: s[0])]
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)



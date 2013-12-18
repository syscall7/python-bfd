from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.response import Response
from odaweb.disassembler import Disassembler, analyzerFactory
from odaweb.models import OdaMaster, Comment, BinaryParcel, Function, Label, Symbol, BinaryString
from rest.serializers import OdaMasterSerializer, FunctionSerializer, SectionSerializer, StringSerializer, DisplayUnitSerializer, BinaryParcelSerializer, RefSerializer
import logging

logger = logging.getLogger(__name__)

class OdaMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = OdaMaster.objects.all()
    serializer_class = OdaMasterSerializer
    paginate_by = 10

class CommentViewSet(viewsets.ModelViewSet):
    #queryset = Comment.objects.all()
    #serializer_class = CommentSerializer
    model = Comment

    def get_queryset(self):
        queryset = Comment.objects.all()
        short_name = self.request.QUERY_PARAMS.get('short_name', None)
        revision = self.request.QUERY_PARAMS.get('revision', None)
        if short_name is not None:
            oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
            return Comment.get_for_binary(oda.binary)

        return queryset

class FunctionViewSet(viewsets.ModelViewSet):
    #serializer_class = FunctionSerializer
    model = Function

    def get_queryset(self):
        oda = OdaMaster.objects.get(short_name=self.request.QUERY_PARAMS.get('short_name'),
                                    revision=self.request.QUERY_PARAMS.get('revision'))

        return Function.get_for_binary(oda.binary)

class SectionsViewSet(viewsets.GenericViewSet):
    serializer_class = SectionSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                  revision=request.QUERY_PARAMS.get('revision'))
        d = Disassembler(oda.binary)
        section_info = d.ofd.get_loadable_sections()
        serializer = self.get_serializer(section_info.sections, many=True)
        return Response(serializer.data)

class ParcelsViewSet(viewsets.GenericViewSet):
    serializer_class = BinaryParcelSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                  revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        jcp = JsonChunkProcessor(binary)
        parcels = jcp.get_all_parcels()

        serializer = self.get_serializer(parcels, many=True)
        return Response(serializer.data)

class DisplayUnitsViewSet(viewsets.GenericViewSet):
    serializer_class = DisplayUnitSerializer

    def list(self, request):

        start = 0
        if request.QUERY_PARAMS.get('addr'):
            start = int(request.QUERY_PARAMS.get('addr'),10)

        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                  revision=request.QUERY_PARAMS.get('revision'))

        dasm = Disassembler(oda.binary)
        dunits = dasm.analyze(start, 100)

        logger.debug("DisplayUnitsViewSet: Generate serialized data")
        serializer = self.get_serializer(dunits, many=True)
        serialData = Response(serializer.data)
        logger.debug("DisplayUnitsViewSet: Serial data complete")
        return serialData


class StringsViewSet(viewsets.GenericViewSet):
    serializer_class = StringSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                    revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        dasm = Disassembler(binary)
        strings = [{'addr': key, 'string': value} for key, value in sorted(dasm.ofd.strings().items(), key=lambda s: s[0])]
        serializer = self.get_serializer(strings, many=True)
        return Response(serializer.data)

class SymbolsViewSet(viewsets.ModelViewSet):
    model = Symbol

    def get_queryset(self):
        queryset = Symbol.objects.all()
        short_name = self.request.QUERY_PARAMS.get('short_name', None)
        revision = self.request.QUERY_PARAMS.get('revision', None)
        if short_name is not None:
            queryset = Symbol.get_for_binary(OdaMaster.objects.get(short_name=short_name, revision=revision).binary)

        return queryset


class BinaryStringViewSet(viewsets.ModelViewSet):
    model = BinaryString

class FunctionsViewSet(viewsets.ModelViewSet):
    model = Function

    def get_queryset(self):
        queryset = Function.objects.all()
        short_name = self.request.QUERY_PARAMS.get('short_name', None)
        revision = self.request.QUERY_PARAMS.get('revision', None)
        if short_name is not None:
            queryset = Function.get_for_binary(OdaMaster.objects.get(short_name=short_name, revision=revision).binary)

        return queryset

class LabelsViewSet(viewsets.ModelViewSet):
    model = Label

    def get_queryset(self):
        queryset = Label.objects.all()
        short_name = self.request.QUERY_PARAMS.get('short_name', None)
        revision = self.request.QUERY_PARAMS.get('revision', None)
        if short_name is not None:
            queryset = Label.get_for_binary(OdaMaster.objects.get(short_name=short_name, revision=revision).binary)

        return queryset

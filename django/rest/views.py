from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.response import Response
from odaweb.disassembler import Disassembler, JsonChunkProcessor, analyzerFactory
from odaweb.models import OdaMaster, Comment, BinaryParcel, Function, Label
from rest.serializers import OdaMasterSerializer, FunctionSerializer, SectionSerializer, StringSerializer, SymbolSerializer, DisplayUnitSerializer, BinaryParcelSerializer, RefSerializer
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
        oda = OdaMaster.objects.get(short_name=self.request.QUERY_PARAMS.get('short_name'),
                                  revision=self.request.QUERY_PARAMS.get('revision'))

        return Comment.get_for_binary(oda.binary)

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
        section_info = d.get_loadable_sections()
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
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                  revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        ctype = ContentType.objects.get_for_model(binary)

        jcp = JsonChunkProcessor(binary)

        start = 0
        if request.QUERY_PARAMS.get('addr'):
            start = int(request.QUERY_PARAMS.get('addr'),10)

        parcels = BinaryParcel.objects.filter(content_type=ctype.id, object_id= binary.id, end__gte = start)[:]

        #architecture = binary.options.architecture
        #analyzer = analyzerFactory(architecture)
        #analyzer.analyze(dasm, parcels, startAddr=start, onlySymbols=True)
        #parcels = jcp.get_all_parcels()

        display_units = jcp.process_parcels_disassembly(parcels, start)
        sorted_du = display_units.values()
        sorted_du.sort(key=lambda x: x.offset, reverse=False)
        serializer = self.get_serializer(sorted_du[:250], many=True)

        logger.debug("DisplayUnitsViewSet: Generate serialized data")
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
        strings = [{'addr': key, 'string': value} for key, value in sorted(dasm.strings().items(), key=lambda s: s[0])]
        serializer = self.get_serializer(strings, many=True)
        return Response(serializer.data)

class SymbolsViewSet(viewsets.GenericViewSet):
    serializer_class = SymbolSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                    revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        dasm = Disassembler(binary)

        ctype = ContentType.objects.get_for_model(binary)

        parcels = BinaryParcel.objects.filter(content_type=ctype.id, object_id= binary.id)[:]

        architecture = binary.options.architecture
        analyzer = analyzerFactory(architecture)
        analyzer.analyze(dasm, parcels, onlySymbols=True)
        serializer = self.get_serializer(analyzer.functions.values(), many=True)
        return Response(serializer.data)

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

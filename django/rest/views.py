from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.response import Response
from odaweb.disassembler import Disassembler, JsonChunkProcessor, analyzerFactory
from odaweb.models import OdaMaster, Comment, BinaryParcel
from rest.serializers import OdaMasterSerializer, CommentSerializer, SectionSerializer, StringSerializer, SymbolSerializer, DisplayUnitSerializer, BinaryParcelSerializer



class OdaMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = OdaMaster.objects.all()
    serializer_class = OdaMasterSerializer

class CommentViewSet(viewsets.ModelViewSet):
    #queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    model = Comment

    def get_queryset(self):
        oda = OdaMaster.objects.get(short_name=self.request.QUERY_PARAMS.get('short_name'),
                                  revision=self.request.QUERY_PARAMS.get('revision'))

        return Comment.get_for_binary(oda.binary)


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
        jcp = JsonChunkProcessor(binary)
        parcels = jcp.get_all_parcels()
        display_units = jcp.process_parcels_disassembly(parcels)
        serializer = self.get_serializer(display_units, many=True)
        return Response(serializer.data)

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
        analyzer.analyze(dasm, parcels)
        serializer = self.get_serializer(analyzer.functions.values(), many=True)
        return Response(serializer.data)
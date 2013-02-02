from django.shortcuts import render, redirect

from odaweb.models import OdaMaster, BinaryFile
import views
from odaweb import engine
from django import forms
import dischunk

from utils import id_generator

def index(request, disassembly_id):

    oda_master = create_session(request, disassembly_id)

    return render(request, 'refactor/index.djhtml',{
        #'disassembly_id': oda_master.short_name
    })


def save(request):
    disassembly_session_id = request.session["disassembly_session_id"]
    return redirect('/odaweb/' + disassembly_session_id)

def create_session(request, disassembly_id):

    disassembly_session_id = request.session.get('disassembly_session_id')

    if not disassembly_session_id:
        if disassembly_id:
            disassembly_id = 'some_default'

        diassembly_session_id = id_generator()
        request.session["disassembly_session_id"] = diassembly_session_id

        OdaMaster(short_name = disassembly_session_id)
        #Copy Disassembly ID into

def get_session(request):

    disassembly_session_id = request.session.get('disassembly_session_id')
    return OdaMaster.objects.get(short_name = disassembly_session_id)

def set(request):
    pass

def hex(request):
    pass

def functions(request):
    pass

def strings(request):
    pass


class UploadFileForm(forms.Form):
    filedata = forms.FileField()
    #filename = forms.CharField()

def upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        binary_file = BinaryFile.create(request.FILES['filedata'])
        binary_file.save()
        #platform_options = engine.platform_options(binary_file)

        oda_master = OdaMaster(short_name = id_generator(), content_object = binary_file)
        oda_master.save()
        return redirect('/odaweb/' + oda_master.short_name)
    else:
        raise Exception("error" )



def disassemble(request):
    oda_master = get_session(request)

    platform = oda_master.content_object.options.platform

    analyzer = views.analyzerFactory(platform)

    bfd = engine.OdaBfd(o.uuid, 'binary', platform)
    chunks = []
    sec_names = ['.data']
    ignore, next_addr, num_lines = bfd.disassemble(sec_names[0], 0, len(byte_array), numLines=0, endian=endian, options=bfdDisOpts)
    chunks.append( dischunk.DisChunk(0, next_addr, num_lines, sec_names[0]) )
    analyzer.analyze(bfd, chunks)

    print 'disassemble'
    return
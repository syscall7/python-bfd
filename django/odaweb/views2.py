from django.shortcuts import render, redirect

from odaweb.models import OdaMaster, BinaryFile, OdaOptions, Comment
import views
from odaweb import engine
from django import forms
import dischunk
from django.contrib.contenttypes.models import ContentType
from disassembler import Disassembler, JsonChunkProcessor, create_default_view
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson

from utils import id_generator


def render_to_json(context):
    return HttpResponse(simplejson.dumps(context)  , mimetype='application/json')


def index(request, disassembly_id):

    render_dict = {}
    oda_master = create_session(request, disassembly_id)

    if oda_master:
        section_info = Disassembler(oda_master.binary).get_code_sections()
        render_dict['section_info'] = section_info
        render_dict['binary'] = oda_master.binary

    return render(request, 'refactor/index.djhtml', render_dict)


def save(request):
    print 'Saving...'
    disassembly_session_id = request.session["disassembly_session_id"]
    return redirect('/odaweb/' + disassembly_session_id)


def create_session(request, disassembly_id):

    if not disassembly_id:
        #They've arrived at odaweb/
        diassembly_session_id = id_generator()
        print 'New session_id is ', diassembly_session_id
        request.session["disassembly_session_id"] = diassembly_session_id
        create_default_view(diassembly_session_id)

    disassembly_session_id = request.session.get('disassembly_session_id')
    if not disassembly_session_id:
        #TODO They've not been here before, copy the disassembly_id into they session
        pass

    return OdaMaster.objects.get(short_name = disassembly_session_id)



def get_session(request):

    disassembly_session_id = request.session.get('disassembly_session_id')
    print("Loading short_name = %s" %(disassembly_session_id))
    return OdaMaster.objects.get(short_name = disassembly_session_id)

def set(request):
    pass

def hex(request):
    pass

def fileinfo(request):
    oda_master = get_session(request)

    binary = oda_master.binary
    dasm = Disassembler(binary)

    fileinfo_tab = render_to_string('tab_fileinfo.djhtml', {
        'binary': binary,
        })

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({
        'fileinfo_tab' : fileinfo_tab,
        #'section_flags' : dasm.sectionFlagsInfo(),
    }),
                        mimetype='application/json')
def sections(request):
    oda_master = get_session(request)

    binary = oda_master.binary
    dasm = Disassembler(binary)

    sections_tab = render_to_string('sections_tab.djhtml', {
        'sections' : dasm.sections,
        'sectionFlagsInfo' : dasm.sectionFlagsInfo(),
    })

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({
        'sections_tab' : sections_tab,
        #'section_flags' : dasm.sectionFlagsInfo(),
        }),
        mimetype='application/json')

def symbols(request):
    oda_master = get_session(request)

    binary = oda_master.binary
    dasm = Disassembler(binary)

    syms = render_to_string('symbols.djhtml', {
        'symbols' : dasm.symbols(),
    })

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'symbols_html' : syms })  , mimetype='application/json')

def strings(request):
    pass

class UploadFileForm(forms.Form):
    filedata = forms.FileField()
    #filename = forms.CharField()

def upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():

        #platform_options = engine.platform_options(binary_file)
        #if options can't be determined, we need to display another dialog to get user input on
        #possible options
        options = OdaOptions(target='elf32-i386', architecture='i386')
        options.save()

        binary_file = BinaryFile.create(request.FILES['filedata'], options)
        binary_file.save()

        oda_master = OdaMaster(short_name = id_generator(), binary = binary_file)
        oda_master.save()
        request.session["disassembly_session_id"] = oda_master.short_name

        #we can farm this out to a background thread and return before complete
        #then the client can spin until we're done
        disassembler = Disassembler(binary_file)
        disassembler.process_chunks()

        return redirect('/odaweb/' + oda_master.short_name)
        #return redirect('/odaweb/_refresh')
    else:
        raise Exception("error" )


def refresh_disassembly(request):
    oda_master = get_session(request)

    binary = oda_master.binary

    addr = int(request.GET.get('addr','0'))

    chunks, chunk_list = JsonChunkProcessor(binary).get_chunk_html(addr, 7)

    for c in chunks:
        c.attach_comments(binary)

    dis = render_to_string('listing.djhtml', { 'chunks' : chunks, 'functions' : [] } )
    hex = render_to_string('hex_listing.djhtml', { 'chunks' : chunks } )

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'disassembly' : dis,
                                          'hex_dump' : hex,
                                          'chunks' : chunk_list })  , mimetype='application/json')

def comment(request):

    class CommentForm(forms.Form):
        comment = forms.CharField()
        offset = forms.CharField()

    form = CommentForm(request.POST, request.FILES)

    if form.is_valid():
        print 'Adding comment at offset %s: %s' % (form.cleaned_data['offset'], form.cleaned_data['comment'])

        oda_master = get_session(request)
        binary = oda_master.binary
        ctype = ContentType.objects.get_for_model(binary)

        comment = Comment(content_type=ctype, object_id=binary.id, comment = form.cleaned_data['comment'], offset = int(form.cleaned_data['offset'],16))
        comment.save()
        #return render_to_json({"status" : "ok"})
        return HttpResponse()


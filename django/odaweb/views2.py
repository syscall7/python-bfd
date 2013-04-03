from django.shortcuts import render, redirect

from odaweb.models import OdaMaster, BinaryFile, OdaOptions, Comment, InstDoc
from django import forms
from django.contrib.contenttypes.models import ContentType
from disassembler import Disassembler, JsonChunkProcessor, examples, get_supported_archs, copy_disassembly
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
import dns.resolver

from utils import id_generator


def render_to_json(context):
    return HttpResponse(simplejson.dumps(context), mimetype='application/json')


def index(request, disassembly_id):

    context = {}
    oda_master = create_session(request, disassembly_id, 0)

    if oda_master:
        d = Disassembler(oda_master.binary)
        section_info = d.get_code_sections()
        context['section_info'] = section_info
        context['binary'] = oda_master.binary
        context['disassembly_id'] = disassembly_id
        context['share_url'] =  request.build_absolute_uri()
        context['examples'] = examples
        context['supported_archs'] = get_supported_archs()

    #from pprint import pprint
    #print(pprint(context))
    return render(request, 'refactor/index.djhtml', context)


def save(request):
    o_id = request.session["disassembly_token"]['id']
    return redirect('/odaweb/' + o_id)


def create_session(request, to_copy_id, to_copy_version):

    request.session['files'] = []

    if not to_copy_id:
        to_copy_id = 'strcpy_x86'
        to_copy_version =  0

    request.session["disassembly_token"] = {
        'id': id_generator(),
        'version': 0
    }

    print '#####' + request.session["disassembly_token"]['id']
    copy_disassembly(to_copy_id, to_copy_version,
                     request.session["disassembly_token"]['id'])

    return OdaMaster.objects.get(
        short_name=request.session["disassembly_token"]['id'],
        revision=request.session["disassembly_token"]['version'])

def get_session(request):
    o_id = request.session["disassembly_token"]['id']
    version = request.session["disassembly_token"]['version']

    print("LOADING #### " + o_id + " " + str(version))
    o = OdaMaster.objects.get(short_name = o_id, revision = version)
    print ("FOUND $$$$ " + str(o))
    return o


def set(request):

    class HexUploadForm(forms.Form):
        hex_val = forms.CharField(required=False)
        arch = forms.CharField(required=False)

    form = HexUploadForm(request.POST) # A form bound to the POST data
    if form.is_valid():

        oda_master = get_session(request)

        if form.cleaned_data['hex_val']:
            hex_string = form.cleaned_data['hex_val']
            try:
                cleaned_hex_string = ''.join(hex_string.split())
                byte_array = cleaned_hex_string.decode("hex")
            except TypeError,e:
                if (e.args[0]=='Non-hexadecimal digit found'):
                    return HttpResponseServerError('<div>NON HEX DIGIT</div>')
                else:
                    cleaned_hex_string = (cleaned_hex_string + '0')

            oda_master.binary.binary_string = cleaned_hex_string
            oda_master.binary.save()

        if form.cleaned_data['arch']:
            oda_master.binary.options.architecture = form.cleaned_data['arch']
            oda_master.binary.options.save()



        disassembler = Disassembler(oda_master.binary)
        disassembler.process_chunks()

        return render_to_json({"status" : "ok"})

def hex(request):
    pass

def fileinfo(request):
    oda_master = get_session(request)

    binary = oda_master.binary
    dasm = Disassembler(binary)

    malware = False

    try:
        [cymru_record,] = dns.resolver.query('%s.malware.hash.cymru.com' % binary.md5(), 'TXT')
        malware = True
        print 'cymru is %s' % cymru_record
    except dns.resolver.NXDOMAIN:
        pass

    fileinfo_tab = render_to_string('tab_fileinfo.djhtml', {
        'binary': binary,
        'malware': malware,
        })

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({
        'fileinfo_tab' : fileinfo_tab,
        #'section_flags' : dasm.sectionFlagsInfo(),
    }), mimetype='application/json')

def instdoc(request):

    class InstDocForm(forms.Form):
        mnemonic = forms.CharField()

    form = InstDocForm(request.POST, request.FILES)

    if form.is_valid():
        instdoc_html = 'Invalid instruction'

        mnemonic = form.cleaned_data['mnemonic']
        print 'Getting instruction documentation for "%s"' % (mnemonic)

        # TODO: Get the actual platform
        result = InstDoc.objects.filter(platform = 'i386', mnemonic = mnemonic.upper())
        if result:
            doc = result[0]

            oda_master = get_session(request)
            binary = oda_master.binary

            instdoc_html = render_to_string('refactor/inst-doc-content.djhtml', {
                'description': doc.short,
                })

        return HttpResponse(simplejson.dumps({
            'instdoc' : instdoc_html,
        }), mimetype='application/json')

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
    oda_master = get_session(request)

    binary = oda_master.binary
    dasm = Disassembler(binary)

    strings = render_to_string('strings.djhtml', {
        'strings' : dasm.strings(),
        })

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'strings' : strings })  , mimetype='application/json')

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
        request.session["disassembly_id"] = oda_master.short_name

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

    addr = int(request.POST.get('addr','0'))
    print "TotalRefresh: addr",addr

    superchunks, chunk_list = JsonChunkProcessor(binary).get_chunks_from_addr(addr, 3)

    dis = render_to_string('listing.djhtml', { 'chunks' : superchunks, 'functions' : [] } )
    hex = render_to_string('hex_listing.djhtml', { 'chunks' : superchunks } )

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'disassembly' : dis,
                                          'hex_dump' : hex,
                                          'chunks' : chunk_list })  , mimetype='application/json')

def partial_refresh_disassembly(request):
    oda_master = get_session(request)

    binary = oda_master.binary

    start =int(request.POST.get('start','0'))
    end=int(request.POST.get('end', '0'))
    count=int(request.POST.get('count', '0'))
    direction=int(request.POST.get('dir', '0'))

    print "PartialRefresh: START 0x%08x COUNT %d DIR %d" % (start,count,direction)

    superchunks, chunk_list = JsonChunkProcessor(binary).get_chunks_from_chunk(start, end, direction, count)

    dis = render_to_string('listing.djhtml', { 'chunks' : superchunks, 'functions' : [] } )
    hex = render_to_string('hex_listing.djhtml', { 'chunks' : superchunks } )

    print "PartialRefresh: Disassembly", dis[:128]

    for chunk in chunk_list:
        print "CHUNK: ADDR=0x%08x BOUNDARY=%d" % (chunk['startOffset'], chunk['isBoundary'])

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


def owned_files(request):

    files = [OdaMaster.objects.filter(short_name=short_name) for short_name in request.session['files']]

    owned_files = [{'name': f.binary.name, 'short_name': f.short_name} for f in files]

    file_list =  render_to_string('open-existing-list.djhtml', {'files' : owned_files})

    return HttpResponse(simplejson.dumps({'file_list_html' : file_list}), mimetype='application/json')


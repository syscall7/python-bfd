import json
import socket
import logging

from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson

from oda.apps.odaweb.models import OdaMaster, InstDoc, BinaryFile, BinaryFileModel
from oda.libs.odb.bfd.disassembler import  get_supported_archs, get_supported_endians, get_platform_options, \
    Disassembler
#from disassembler import Disassembler, get_supported_archs, \
#    copy_disassembly, get_supported_endians, get_platform_options
from examples import Examples
import dns.resolver
from oda.libs.odb.bfd.ofd import Ofd
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.modify_settings import ModifySettingsFactory
from oda.libs.odb.ops.scan_operation import ScanOperation
from oda.libs.odb.structures.section import Section


logger = logging.getLogger(__name__)

from utils import id_generator


def render_to_json(context):
    return HttpResponse(simplejson.dumps(context), mimetype='application/json')


def index(request, disassembly_id, version=0):
    logger.info('create session, user=' + str(request.user))

    context = {}

    saved = request.session.get('saved', False)

    #try:
    oda_master = create_session(request, disassembly_id, version)
    #except Exception as e:
    #    logger.exception("Failed to create_session [%s] [%s]", e.args, disassembly_id)
    #    return redirect('/odaweb/')

    if oda_master:
        #d = Disassembler(oda_master.binary)
        section_info = Ofd(oda_master.odb_file.get_binary()).get_loadable_sections()
        context['master'] = oda_master
        context['section_info'] = section_info
        context['binary'] = oda_master.odb_file.get_binary()
        context['project_name'] = oda_master.project_name
        context['disassembly_id'] = oda_master.short_name
        context['share_url'] = request.build_absolute_uri()
        context['examples'] = Examples
        context['supported_archs'] = get_supported_archs()
        context['arch'] = oda_master.odb_file.get_binary().options.architecture #oda_master.binary.options.architecture
        context['saved'] = saved

        context['supported_endians'] = get_supported_endians()
        context['options'] = get_platform_options(oda_master.odb_file.get_binary().options.architecture )
        context['defaults'] = []
        context['user'] = request.user
        context['form_type'] = 'live'

    request.session['saved'] = False
    #from pprint import pprint
    #print(pprint(context))
    return render(request, 'index.djhtml', context)


def save(request):
    request.session['saved'] = True
    try:
        o_id = request.session["disassembly_token"]['id']
        o_revision = request.session['disassembly_token']['version']
    except:
        logger.warn("Save Called With Missing disassembly_token")
        return redirect('/odaweb/')

    return redirect('/odaweb/' + o_id + '/' + str(o_revision))


def create_session(request, to_copy_id, to_copy_version):
    request.session['files'] = []

    if not to_copy_id:
        to_copy_id = 'strcpy_x86'

    if not to_copy_version:
        to_copy_version = 0

    oda_master = OdaMaster.objects.get(short_name=to_copy_id, revision=to_copy_version)
    oda_master.id = None
    oda_master.short_name = id_generator()
    oda_master.save()
    request.session["disassembly_token"] = {
        'id': oda_master.short_name,
        'version': oda_master.revision
    }
    logger.info(
        '%s(%d)' % (request.session["disassembly_token"]['id'], request.session['disassembly_token']['version']))



    return oda_master


def get_session(request):
    try:
        o_id = request.session["disassembly_token"]['id']
        version = request.session["disassembly_token"]['version']

        logger.info("LOADING %s %s", o_id, str(version))
        o = OdaMaster.objects.get(short_name=o_id, revision=version)
        logger.info("FOUND $$$$ " + str(o))
        return o
    except KeyError:
        logger.warn("disassembly_token isn't set")
        return None


def options_form(request):
    oda_master = get_session(request)
    arch = oda_master.odb_file.get_binary().options.architecture
    baseAddr = oda_master.odb_file.get_binary().options.base_address
    selected_opts = []

    class HexUploadForm(forms.Form):
        hex_val = forms.CharField(required=False)
        arch = forms.CharField(required=False)
        base_address = forms.CharField(required=False)
        endian = forms.CharField(required=False)

    return render(request, 'form-platform-options.djhtml', {
        'arch': arch,
        'supported_archs': get_supported_archs(),
        'supported_endians': get_supported_endians(),
        'options': get_platform_options(arch),
        'base_address': baseAddr,
        'selected_opts': selected_opts,
        'form': HexUploadForm(),
        'form_type': 'live'

    })


def set(request):
    class HexUploadForm(forms.Form):
        hex_val = forms.CharField(required=False)
        arch = forms.CharField(required=False)
        base_address = forms.CharField(required=False)
        endian = forms.CharField(required=False)

        # set to True on the last time the options form is submitted (file upload) or always (live hex)
        disassemble = forms.BooleanField(required=False)

        def clean_hex_val(self):
            # strip whitespace
            cleaned_hex_string = ''.join(self.cleaned_data['hex_val'].split())

            # ensure strings have an even length
            if len(cleaned_hex_string) % 2:
                cleaned_hex_string += '0'

            self.cleaned_data['hex_val'] = cleaned_hex_string
            return self.cleaned_data['hex_val']

        def clean_base_address(self):
            baseAddr = self.cleaned_data['base_address']
            try:
                if baseAddr:
                    baseAddr = int(baseAddr, 16)
            except:
                raise forms.ValidationError("Address must be in the form 0x12345678")

            # always return the cleaned data, whether you have changed it or not
            return self.cleaned_data['base_address']

        def clean_arch(self):
            arch = self.cleaned_data['arch']
            return arch.strip()

    form = HexUploadForm(request.POST)  # A form bound to the POST data

    # initialize base_address with whatever was in the form data, even if it is invalid
    baseAddr = 0
    try:
        baseAddr = form.data['base_address']
    except MultiValueDictKeyError:
        logger.warn("base_address not set")

    selected_opts = []
    arch = 'i386'

    if form.is_valid():

        oda_master = get_session(request)

        if form.cleaned_data['hex_val']:
            cleaned_hex_string = form.cleaned_data['hex_val']
            try:
                cleaned_hex_string.decode("hex")
            except (TypeError, UnicodeEncodeError) as e:
                return HttpResponseServerError('<div>NON HEX DIGIT</div>')

            selected_opts = request.POST.getlist('options[]')
            #oda_master.binary.binary_string = cleaned_hex_string
            #form.cleaned_data['base_address']
            odb_file = oda_master.odb_file
            odb_file.execute(ModifySettingsFactory.set_values({
                'architecture': form.cleaned_data['arch'],
                'base_address': baseAddr,
                'endian': form.cleaned_data['endian'],
                'selected_opts': selected_opts

            }))
            oda_master.save()
            formType = "live"
        else:
            formType = "open"
            odb_file = oda_master.odb_file
            selected_opts = request.POST.getlist('options[]')
            odb_file.execute(ModifySettingsFactory.set_values({
                'architecture': form.cleaned_data['arch'],
                'base_address': baseAddr,
                'endian': form.cleaned_data['endian'],
                'selected_opts': selected_opts

            }))

            if form.cleaned_data['disassemble']:
                odb_file.execute(LoadOperation())
                odb_file.execute(ScanOperation())
                oda_master.save()

        #if form.cleaned_data['arch']:

            #oda_master.binary.options.architecture = arch
            #oda_master.binary.options.reset_extra_options()
            #oda_master.binary.options.save()


        #selected_opts = request.POST.getlist('options[]')
        #oda_master.binary.options.set_extra_options(selected_opts)

        #endian = request.POST.get('endian')
        #if (endian):
        #    oda_master.binary.options.set_endian(endian)

        #oda_master.binary.options.save()

        # if we need to disassemble this data for the first time
        #if form.cleaned_data['disassemble']:
        #    disassembler = Disassembler(oda_master.binary)
        #    disassembler.analyze_first_time()

    form_html = render_to_string('form-platform-options.djhtml', {
        'arch': arch,
        'supported_archs': get_supported_archs(),
        'supported_endians': get_supported_endians(),
        'options': get_platform_options(arch),
        'base_address': baseAddr,
        'selected_opts': selected_opts,
        'form': form,
        'oda_master': oda_master,
        'form_type': formType
    })

    return HttpResponse(simplejson.dumps({
        'form_html': form_html,
    }), mimetype='application/json')


class ShowOptionsForm(forms.Form):
    platformId = forms.CharField()
    options = forms.CharField(required=False)


def show_options(request):
    form = ShowOptionsForm(request.POST)  # A form bound to the POST data
    if form.is_valid():
        #print "Show_options"
        platform = form.cleaned_data['platformId']
        options = form.cleaned_data['options']
        opts_defaults = []
        #if options:
        #    for str_pair in options.split('---'):
        #        pairs = str_pair.split('--')
        #        opts_defaults.append((pairs[0],pairs[1]))

        #print opts_defaults

        return render(request, 'show_options.djhtml', {
            'supported_endians': get_supported_endians,
            'options': get_platform_options(platform),
            'defaults': opts_defaults
        })

    return HttpResponse(status=400)


def hex(request):
    pass


def fileinfo(request):
    oda_master = get_session(request)
    if not oda_master:
        return HttpResponse("Session Not Initialized", status=400)

    binary = oda_master.binary
    dasm = Disassembler(binary)

    malware = False

    # lookup in malware hash registry
    try:
        [cymru_record, ] = dns.resolver.query('%s.malware.hash.cymru.com' % binary.md5(), 'TXT')
        malware = True
        logger.info('cymru is %s' % cymru_record)
    # if the name does not exist, this binary is not recognized as malware
    except dns.resolver.NXDOMAIN:
        pass
    # Timeout should not ever happen, but sometimes it does
    # TODO: Indicate to the user, that it is unknown
    except dns.resolver.Timeout:
        pass

    # lookup in national software reference library
    benign = False
    try:
        sock = socket.create_connection(('nsrl.kyr.us', 9120), timeout=0.5)
        sock.send('Version: 2.0\n')
        ack_ver = sock.recv(4096)
        sock.send('query %s\n' % binary.md5())
        ack_sum = sock.recv(4096)
        sock.send('BYE\n')
        if ack_ver.startswith('OK') and ack_sum.startswith('OK 1'):
            benign = True
        sock.close()
    except Exception:
        pass

    fileinfo_tab = render_to_string('tab_fileinfo.djhtml', {
        'binary': binary,
        'malware': malware,
        'benign': benign,
        'project_name': oda_master.project_name,
    })

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({
        'fileinfo_tab': fileinfo_tab,
        #'section_flags' : dasm.sectionFlagsInfo(),
    }), mimetype='application/json')


def instdoc(request):
    class InstDocForm(forms.Form):
        mnemonic = forms.CharField()

    form = InstDocForm(request.POST, request.FILES)

    if form.is_valid():
        instdoc_html = 'Help not available'

        mnemonic = form.cleaned_data['mnemonic']
        logger.info('Getting instruction documentation for "%s"' % (mnemonic))

        # TODO: Get the actual platform
        result = InstDoc.objects.filter(platform='i386', mnemonic=mnemonic.upper())
        if result:
            doc = result[0]

            oda_master = get_session(request)
            binary = oda_master.binary

            instdoc_html = render_to_string('inst-doc-content.djhtml', {
                'description': doc.short,
            })

        return HttpResponse(simplejson.dumps({
            'instdoc': instdoc_html,
        }), mimetype='application/json')


#def sections(request):
#    oda_master = get_session(request)
#    if not oda_master:
#        return HttpResponse("Session Not Initialized", status=400)
#
#    binary = oda_master.binary
#    dasm = Disassembler(binary)
#
#
#    sections_tab = render_to_string('sections_tab.djhtml', {
#        'sections' : dasm.sections,
#        'sectionFlagsInfo' : dasm.sectionFlagsInfo(),
#    })
#
#    # Return the new disassembly
#    return HttpResponse(simplejson.dumps({
#        'sections_tab' : sections_tab,
#        #'section_flags' : dasm.sectionFlagsInfo(),
#        }),
#        mimetype='application/json')

#def symbols(request):
#    oda_master = get_session(request)
#    if not oda_master:
#        return HttpResponse("Session Not Initialized", status=400)
#
#    binary = oda_master.binary
#    dasm = Disassembler(binary)
#
#    ctype = ContentType.objects.get_for_model(binary)
#
#    superchunks = BinaryDisassemblySuperChunk.objects.filter(
#            content_type=ctype.id, object_id = binary.id)[:]
#
#    architecture = binary.options.architecture
#    analyzer = analyzerFactory(architecture)
#    analyzer.analyze(dasm, superchunks)
#
#    syms = render_to_string('symbols.djhtml', {
#        'symbols' : sorted(analyzer.functions.values(), key=lambda t: t.offset)
#    })
#
#    # Return the new disassembly
#    return HttpResponse(simplejson.dumps({'symbols_html' : syms })  , mimetype='application/json')

#def strings(request):
#    oda_master = get_session(request)
#    if not oda_master:
#        return HttpResponse("Session Not Initialized", status=400)
#
#    binary = oda_master.binary
#    dasm = Disassembler(binary)
#
#    strings = render_to_string('strings.djhtml', {
#        'strings' : dasm.strings(),
#        })
#
#    # Return the new disassembly
#    return HttpResponse(simplejson.dumps({'strings' : strings })  , mimetype='application/json')

class UploadFileForm(forms.Form):
    MAX_UPLOAD_SIZE_KB = 2500
    filedata = forms.FileField()
    project_name = forms.CharField(max_length=64)

    def clean_filedata(self):
        if self.cleaned_data['filedata'].size > self.MAX_UPLOAD_SIZE_KB * 1024:
            raise forms.ValidationError("File must be less than %d KB!" % self.MAX_UPLOAD_SIZE_KB)

        # always return the cleaned data, whether you have changed it or not
        return self.cleaned_data['filedata']


def upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    arch = ''
    target = ''
    html = ''
    id = ''
    msg = ''
    if form.is_valid():

        project_name = form.cleaned_data['project_name']
        #options = OdaOptions(target='', architecture='')
        #options.save()

        binary_file = BinaryFile.create(request.FILES['filedata'])
        binary_file.save()

        oda_master = OdaMaster(short_name=id_generator(), project_name=project_name,
                               ipAddress=request.META.get('REMOTE_ADDR'))
        if request.user.is_authenticated():
            oda_master.owner = request.user

        oda_master.save()

        request.session["disassembly_id"] = oda_master.short_name
        request.session["disassembly_token"] = {
            'id': oda_master.short_name,
            'version': 0
        }

        arch, target = Disassembler.guess_bfd_arch(binary_file.file_handle().name)
        binary_file.architecture = arch
        binary_file.target = target
        binary_file.save()

        oda_master.odb_file = OdbFile(BinaryFileModel(binary_file.id))
        oda_master.save()

        id = oda_master.short_name
        msg = render_to_string('alert-platform-options.djhtml', {
            'arch': arch,
            'target': target,
            'file_format': binary_file.desc()
        })

    else:
        html = render_to_string('modal-open.djhtml', {
            'form': form
        })

    return HttpResponse(simplejson.dumps({
        'html': html,
        'arch': arch,
        'target': target,
        'id': id,
        'msg': msg
    }), mimetype='application/json')


def refresh_hex(request):
    oda_master = get_session(request)
    if not oda_master:
        return HttpResponse("Session Not Initialized", status=400)

    binary = oda_master.binary

    addr = int(request.POST.get('addr', '0'))
    logger.info("TotalRefreshHex: 0x%08x" % (addr))

    jcp = JsonChunkProcessor(binary)

    superchunks = jcp.get_chunks_from_addr(addr, 3)
    jcp.process_chunks_hex(superchunks)
    chunk_list = jcp.get_chunk_list(superchunks)

    hex = render_to_string('hex_listing.djhtml', {'chunks': superchunks})

    return HttpResponse(simplejson.dumps({'hex_dump': hex,
                                          'chunks': chunk_list}), mimetype='application/json')


def refresh_disassembly(request):
    oda_master = get_session(request)

    binary = oda_master.binary

    addr = int(request.POST.get('addr', '0'))
    logger.info("TotalRefresh: addr %s", addr)

    jcp = JsonChunkProcessor(binary)

    superchunks = jcp.get_chunks_from_addr(addr, 3)
    jcp.process_chunks_disassembly(superchunks)
    chunk_list = jcp.get_chunk_list(superchunks)

    dis = render_to_string('listing.djhtml', {'chunks': superchunks, 'functions': []})

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'disassembly': dis,
                                          'chunks': chunk_list}), mimetype='application/json')


def partial_refresh_hex(request):
    oda_master = get_session(request)
    if not oda_master:
        return HttpResponse("Session Not Initialized", status=400)

    binary = oda_master.binary

    start = int(request.POST.get('start', '0'))
    end = int(request.POST.get('end', '0'))
    count = int(request.POST.get('count', '0'))
    direction = int(request.POST.get('dir', '0'))

    logger.info("PartialRefreshHex: START 0x%08x COUNT %d DIR %d" % (start, count, direction))

    jcp = JsonChunkProcessor(binary)

    superchunks = jcp.get_chunks_from_chunk(start, end, direction, count)
    jcp.process_chunks_hex(superchunks)
    chunk_list = jcp.get_chunk_list(superchunks)

    hex = render_to_string('hex_listing.djhtml', {'chunks': superchunks})

    logger.info("PartialRefreshHex: Disassembly", hex[:128])

    for chunk in chunk_list:
        logger.info("CHUNK: ADDR=0x%08x BOUNDARY=%d" % (chunk['startOffset'], chunk['isBoundary']))

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'hex_dump': hex,
                                          'chunks': chunk_list}), mimetype='application/json')


def partial_refresh_disassembly(request):
    oda_master = get_session(request)
    if not oda_master:
        return HttpResponse("Session Not Initialized", status=400)

    binary = oda_master.binary

    start = int(request.POST.get('start', '0'))
    end = int(request.POST.get('end', '0'))
    count = int(request.POST.get('count', '0'))
    direction = int(request.POST.get('dir', '0'))

    logger.info("PartialRefresh: START 0x%08x COUNT %d DIR %d" % (start, count, direction))

    jcp = JsonChunkProcessor(binary)

    superchunks = jcp.get_chunks_from_chunk(start, end, direction, count)
    jcp.process_chunks_disassembly(superchunks)
    chunk_list = jcp.get_chunk_list(superchunks)

    dis = render_to_string('listing.djhtml', {'chunks': superchunks, 'functions': []})

    #logger.info("PartialRefresh: Disassembly", dis[:128])

    for chunk in chunk_list:
        logger.info("CHUNK: ADDR=0x%08x BOUNDARY=%d" % (chunk['startOffset'], chunk['isBoundary']))

    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'disassembly': dis,
                                          'chunks': chunk_list}), mimetype='application/json')


def comment(request):
    class CommentForm(forms.Form):
        comment = forms.CharField()
        offset = forms.CharField()

    form = CommentForm(request.POST, request.FILES)

    if form.is_valid():
        logger.info('Adding comment at offset %s: %s' % (form.cleaned_data['offset'], form.cleaned_data['comment']))

        oda_master = get_session(request)
        if not oda_master:
            return HttpResponse("Session Not Initialized", status=400)

        binary = oda_master.binary
        ctype = ContentType.objects.get_for_model(binary)

        comment = Comment(content_type=ctype, object_id=binary.id, comment=form.cleaned_data['comment'],
                          offset=int(form.cleaned_data['offset'], 16))
        comment.save()
        #return render_to_json({"status" : "ok"})
        return HttpResponse()
    else:
        return HttpResponse("Session Not Initialized", status=400)


def convert_to_data(request):
    class ConvertDataForm(forms.Form):
        offset = forms.CharField()

    form = ConvertDataForm(request.POST, request.FILES)

    if form.is_valid():
        offset = int(form.cleaned_data['offset'])
        logger.info('Convert to data at offset 0x%08x' % (offset))

        oda_master = get_session(request)
        if not oda_master:
            return HttpResponse("Session Not Initialized", status=400)

        binary = oda_master.binary
        jcp = JsonChunkProcessor(binary)
        parcel = jcp.get_parcel_from_addr(offset)

        # TODO: Due the parcel conversion here


        return HttpResponse()
    else:
        return HttpResponse("Session Not Initialized", status=400)


def owned_files(request):
    files = [OdaMaster.objects.filter(short_name=short_name) for short_name in request.session['files']]

    owned_files = [{'name': f.binary.name, 'short_name': f.short_name} for f in files]

    file_list = render_to_string('open-existing-list.djhtml', {'files': owned_files})

    return HttpResponse(simplejson.dumps({'file_list_html': file_list}), mimetype='application/json')


def download_text_listing(request):
    oda_master = get_session(request)
    dasm = Disassembler(oda_master.binary)
    response = HttpResponse(dasm.get_text_listing(), content_type='text')
    response['Content-Disposition'] = 'attachment; filename="%s"' % oda_master.project_name
    return response


def ace(request):
    #oda_master = OdaMaster.objects.get(short_name='mkdir', revision=0)
    #odb_file = oda_master.odb_file
    #dasm = Disassembler(odb_file)
    #dunits = dasm.analyze(0, 10000000)
    return render(request, 'ace.djhtml', {
        #'units': simplejson.dumps(dunits)
    })

def ace2(request):
    #oda_master = OdaMaster.objects.get(short_name='mkdir', revision=0)
    #odb_file = oda_master.odb_file
    #dasm = Disassembler(odb_file)
    #dunits = dasm.analyze(0, 10000000)
    return render(request, 'ace2.djhtml', {
        #'units': simplejson.dumps(dunits)
    })
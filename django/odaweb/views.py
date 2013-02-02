#from django.shortcuts import render
import django.shortcuts
from django.template import Context, loader
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django import forms

from django.utils import simplejson
from odaweb.models import OdaFile, BinaryFile, DisassemblyChunk
from odaweb import engine
from odaweb import dischunk 

import re
import tempfile
import itertools

# Minimum number of lines to send to the browser at a time
# Note: this number must be odd
DISASSEMBLY_WINDOW_SIZE_CHUNKS = 7

def render(request, template, context):
    return django.shortcuts.render(request, template, base_context(request, context))
    
def analyzerFactory(arch):
    
    # for now, ignore everything after the colon
    arch = arch.split(':')[0]
    name = 'odaweb.analyzers.'+arch
    try:
        mod = __import__(name)
    except ImportError:
        return analyzerFactory('defaultAnalyzer')
        
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
        
    initFunc = getattr(mod, arch)
    obj = initFunc()
    
    return obj


def run_hex(request, snippet_id = None):
   
    return render(request, 'run_hex.djhtml', {
        'supported_archs': engine.get_supported_archs,
        'supported_endians': engine.get_supported_endians
    })
    
def get_arch(uuid):    
    bfd = None
    try: 
        bfd = engine.OdaBfd(uuid, None, None)
    except:
        pass  
    return (bfd.arch() if bfd  else '')  

def base_context(request, context = {}):
    file_ids = request.session.get('files', [])
    files = map(lambda x : [OdaFile.objects.get(uuid=x), get_arch(x)], file_ids )
    return dict(context.items() + { 'files' : files }.items())
    
 
def file_upload(request):
       
    return render(request, 'file_upload.djhtml',base_context(request, {                                                    
        'supported_archs': engine.get_supported_archs
    }))
    
def clear(request):
    request.session['files'] = []
    return HttpResponseRedirect(reverse('odaweb.views.file_upload'))

def download(request, file_id): 
    platform=request.GET.get('platformId', 'i386')
    o = OdaFile.objects.get(uuid=file_id)    
    temp = engine.disassemble_to_file(o, platform)
        
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='text')
    response['Content-Disposition'] = 'attachment; filename=%s' %  (o.filename.replace('.','_') + "_asm.txt")
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
    
 
class HexUploadForm(forms.Form):
    hex_val = forms.CharField()
    #endian = forms.CharField()
    offset = forms.CharField()
    platformId = forms.CharField()
    options = forms.CharField(required=False)
    print forms

class ShowOptionsForm(forms.Form):
    platformId = forms.CharField()
    options = forms.CharField(required=False)
    print forms
    

def refresh_disassembly(request, file_id):
    addr =int(request.GET.get('addr','0'))
    platform=request.GET.get('platformId', 'i386')
    analyzer = analyzerFactory(platform)
    o = OdaFile.objects.get(uuid=file_id)

    try: 
        bfd = engine.OdaBfd(o.uuid)
    except: 
        bfd = engine.OdaBfd(o.uuid,'binary', platform)

    # Find the chunk corresponding to the given address
    permachunks = o.disassemblychunk_set.all()
    chunk_count = o.disassemblychunk_set.count()
    i = 0
    chunk_index = -1
    for chunk in permachunks:
        if addr >= chunk.start and addr < chunk.end:
            chunk_index = i
            break
        i += 1
    
    if chunk_index == -1:
        return
    
    # Determine the number of chunks to return
    count = DISASSEMBLY_WINDOW_SIZE_CHUNKS
    if chunk_count < DISASSEMBLY_WINDOW_SIZE_CHUNKS:
        count = chunk_count
    
    # Determine the range of chunks to return    
    start_index = chunk_index - (DISASSEMBLY_WINDOW_SIZE_CHUNKS/2)
    if start_index < 0:
        start_index = 0
    if (start_index + count) > chunk_count:
        start_index = chunk_count - count
    
    return process_chunks(bfd, analyzer, permachunks, start_index, count)


def process_chunks(bfd, analyzer, permachunks, index, count):

    # Build a list of chunks to process
    new_chunks = []    
    for chunk in permachunks[index:index+count]:
        new_chunks.append( dischunk.DisChunk(chunk.start, chunk.end, chunk.bfd_lines, chunk.sec_name, chunk.is_boundary) )
                
    analyzer.analyze( bfd, new_chunks )
                
    # Build a primitive object containing the list of chunk data to pass back to the client 
    chunk_list = []
    for chunk in new_chunks:
        chunk_list.append ({ 'sec_name': chunk.sec_name, 'startOffset': chunk.start, 'endOffset': chunk.end, 'isBoundary': chunk.is_boundary, 'lines': chunk.lines  })
    
    # Return the new disassembly
    return HttpResponse(simplejson.dumps({'disassembly' : render_to_string('listing.djhtml', { 'chunks' : analyzer.chunks, 'functions' : analyzer.functions } ),
                                          'chunks' : chunk_list 
                                          }))

    
def update_disassembly(request, file_id):
    sec_name=request.GET.get('name', '.data')
    start =int(request.GET.get('start','0'))
    end=int(request.GET.get('end', '0'))
    count=int(request.GET.get('count', '0'))
    direction=int(request.GET.get('dir', '0'))
    platform=request.GET.get('platformId', 'i386')
    analyzer = analyzerFactory(platform)
    o = OdaFile.objects.get(uuid=file_id)

    # Get the sections to process 
    try: 
        bfd = engine.OdaBfd(o.uuid)

    except: 
        bfd = engine.OdaBfd(o.uuid,'binary', platform)

    # Get the chunks
    permachunks = o.disassemblychunk_set.all()
    chunk_count = o.disassemblychunk_set.count()
    
    # Find the start at which chunks are being requested
    i = 0
    for chunk in permachunks:
        if chunk.sec_name == sec_name and chunk.start == start and chunk.end == end:
            if direction == 1:
                request_start_index = i + 1
                # Can't request beyond existing chunks
                if request_start_index + count > chunk_count:
                    count = chunk_count - request_start_index
            else:
                request_start_index = i - count
                # Can't request beyond existing chunks
                if request_start_index < 0:
                    count = i
                    request_start_index = 0                    
        i += 1

    return process_chunks(bfd, analyzer, permachunks, request_start_index, count)


def is_code_section( bfd, name ):
    if name in bfd.sections():
        sec = bfd.sections()[name]
        for flag in sec.flags:
            # Find the earliest section with a start address greater than the offset
            if flag.abbrev == "CODE":
                return True
    return False

def is_data_section( bfd, name ):
    if name in bfd.sections():
        sec = bfd.sections()[name]
        for flag in sec.flags:
            # Find the earliest section with a start address greater than the offset
            if flag.abbrev == "DATA":
                return True
    return False

def filter_sections( bfd ):
    code_sections = []
    for sec_name in bfd.sections():
        if is_code_section( bfd, sec_name ):
            code_sections.append(sec_name)
    return code_sections
    
def sort_sections( bfd ):    
    unsorted_sec_names = filter_sections( bfd )
    sorted_sec_names = []
    
    # Place the sections in order from lowest addr to highest
    #print "Sorting Sections",unsorted_sec_names
    while len(unsorted_sec_names):
        target_section = None
        lower_bound = None

        # Find the lowest addressed section
        # Note: Assumes no overlapping sections
        for sec_name in unsorted_sec_names:    
            sec = bfd.sections()[sec_name]
            if (lower_bound is None) or (sec.vma < lower_bound):
                lower_bound = sec.vma
                target_section = sec_name
    
        sorted_sec_names.append(target_section)
        unsorted_sec_names.remove(target_section)
    
    #print "Sorted Sections=",sorted_sec_names
    return sorted_sec_names 

def disassemble(request,file_id):
    platform=request.GET.get('platformId', 'i386')
    analyzer = analyzerFactory(platform)
    o = OdaFile.objects.get(uuid=file_id)
    
    from cStringIO import StringIO
    file_str = StringIO()

    chunks = []

    # Get the sections to process 
    try: 
        bfd = engine.OdaBfd(o.uuid)
        sec_names = sort_sections(bfd)

    except: 
        bfd = engine.OdaBfd(o.uuid,'binary', platform)
        sec_names = ['.data']
        
    # Initialize loop variables
    sec_index = 0    
    sec_offset_addr = bfd.sections()[sec_names[sec_index]].vma
    sec_consumed = 0
    
    # Disassemble the entire file, dividing it into disassembly chunks
    while sec_index < len(sec_names):            
        
        # Disassemble a chunk
        target_section = sec_names[sec_index]
        sec = bfd.sections()[target_section]
        chunk_size = min( dischunk.DisChunk.MIN_CHUNK_SIZE_BYTES,sec.size-sec_consumed)
        disassembly, next_addr, num_lines = bfd.disassemble(target_section, sec_offset_addr, sec_offset_addr+chunk_size, 0)      
        
        # Save the disassembly
        file_str.write( disassembly )
        
        # Save the chunk
        chunks.append( dischunk.DisChunk(sec_offset_addr, next_addr, num_lines, target_section) )
        
        # Update loop variables
        sec_consumed += chunk_size
        sec_offset_addr = next_addr  
        
        # Check if it's time to get the next section          
        if sec_consumed >= sec.size:
            sec_index += 1
            sec_consumed = 0
            if sec_index < len(sec_names):
                sec_offset_addr = bfd.sections()[sec_names[sec_index]].vma
    
    # Note the boundary chunks
    chunks[0].is_boundary = True
    chunks[len(chunks)-1].is_boundary = True
        
    # We now have the contents of the entire disassembly parsed by bfd
    #  TODO: Some analysis to identify other persistently stored info and store it
    #    - Other stored info should include things like branch targets, etc
    
    # Don't store the chunks if we've done so previously
    if o.disassemblychunk_set.count() == 0:
        # Persistently store the chunks
        for chunk in chunks:
            ch = DisassemblyChunk(id=None, 
                                  sec_name=chunk.sec_name, 
                                  start=chunk.start, 
                                  end=chunk.end, 
                                  bfd_lines=chunk.lines, 
                                  is_boundary=chunk.is_boundary,
                                  odafile=o)
            ch.save()
    
    
    # Analyze enough chunks to fill the current window
    window_chunks = []
    
    if len(chunks) > DISASSEMBLY_WINDOW_SIZE_CHUNKS:
        window_chunks = chunks[0:DISASSEMBLY_WINDOW_SIZE_CHUNKS]
    else:
        window_chunks = chunks

    analyzer.analyze( bfd, window_chunks )
    
    return render(request, 'disassembly.djhtml',{
        'disassembly' : analyzer.listing,
        'rawBytes' : analyzer.rawBytes,
        'offsets' : analyzer.offsetStr,
        'branchLines' : analyzer.branchLineHtml,
        'symbols' : bfd.symbols(),
        'sections' : bfd.sections(),
        'sectionFlagsInfo' : bfd.sectionFlagsInfo(),
        'strings' : bfd.strings(),
        'platformId' : platform, 
        'odafile' : o,
        'rawBytesFieldLen' : analyzer.largestInstSize*10, 
        'functions' : analyzer.functions,
        'chunks' : analyzer.chunks
    })
    
def upload_hex(request):
    form = HexUploadForm(request.POST) # A form bound to the POST data
    if form.is_valid():
        hex_string = form.cleaned_data['hex_val']
        platform = form.cleaned_data['platformId']
        #endian = int(form.cleaned_data['endian'])
        options = form.cleaned_data['options']
        #print 'options =', options
        #print 'endian is %d' % endian
        try :
            cleaned_hex_string = ''.join(hex_string.split())
            byte_array = cleaned_hex_string.decode("hex")
        except TypeError,e:
            if (e.args[0]=='Non-hexadecimal digit found'):
                return HttpResponse('<div>NON HEX DIGIT</div>')
            else: 
                byte_array = (cleaned_hex_string + '0').decode('hex')
            print e.args[0]
                    
        a = ''.join('%02x' % ord(byte) for byte in byte_array)
        
        t = tempfile.NamedTemporaryFile()
        t.write(byte_array)
   
        analyzer = analyzerFactory(platform)
        if analyzer == None:
            analyzer = analyzerFactory('defaultAnalyzer')
            
        o = OdaFile.create(t, request.META["REMOTE_ADDR"])
        o.save()
        bfd = engine.OdaBfd(o.uuid, 'binary', platform)
        
        # Parse passed in options
        bfdDisOpts = ''
        endian = engine.get_supported_endians()['DEFAULT']
        if options:
            for str_pair in options.split('---'):
                pairs = str_pair.split('--')
    
                # Strip off widget name
                pairs[0] = re.sub('[sS]elect$', '', pairs[0])
                #print "PAIRS:",pairs[0],pairs[1]
                
                # Only process non-defaults
                if pairs[1] != 'DEFAULT':                
                    if bfdDisOpts:
                        bfdDisOpts = bfdDisOpts + ',' + pairs[1]
                    else:
                        bfdDisOpts = pairs[1]
                if pairs[0] == 'endian':
                    #print "ENDIAN?=",pairs[1]
                    endian = int(pairs[1])
                    
        chunks = []
                    
        #print "BFD OPTS=",bfdDisOpts
        sec_names = ['.data']
        ignore, next_addr, num_lines = bfd.disassemble(sec_names[0], 0, len(byte_array), numLines=0, endian=endian, options=bfdDisOpts)
        chunks.append( dischunk.DisChunk(0, next_addr, num_lines, sec_names[0]) )
        analyzer.analyze(bfd, chunks)       
        
        return render(request, 'run_hex_disassembly.djhtml',{
            'disassembly' : analyzer.listing,
            'rawBytes' : analyzer.rawBytes,
            'offsets' : analyzer.offsetStr,
            'branchLines' : analyzer.branchLineHtml,
            'rawBytesFieldLen' : analyzer.largestInstSize*8 + 10,
            'chunks' : analyzer.chunks
        })        


def show_options(request):
    form = ShowOptionsForm(request.POST) # A form bound to the POST data
    if form.is_valid():
        #print "Show_options"
        platform = form.cleaned_data['platformId']
        options = form.cleaned_data['options']
        opts_defaults = []
        if options:
            for str_pair in options.split('---'):
                pairs = str_pair.split('--')
                opts_defaults.append((pairs[0],pairs[1]))
                                
        #print opts_defaults
                
        djhtmlOpts = []
        analyzer = analyzerFactory(platform)
        if analyzer == None:
            analyzer = analyzerFactory('defaultAnalyzer')
        
        #print "Checking if"
        if analyzer.options:
            #print "ANalyzer",analyzer.options 
            for opt in analyzer.options:        
                # Form the name of the widget by stripping out options
                widgetName = opt[0].replace(' ', '')
                widgetType = ''
                if opt[2] == 'CHOICE' or opt[2] == 'BOOL':
                    widgetType = 'select'
                    widgetName += widgetType
                
                # Build the Modal
                djhtmlOpts.append((widgetName,widgetType) + opt)
        #print 'DHTML',djhtmlOpts
        return render(request, 'show_options.djhtml',{
            'supported_endians': engine.get_supported_endians,
            'options' : djhtmlOpts,
            'defaults' : opts_defaults
        })        


def handle_uploaded_file(f):
    filename = '/tmp/oda_upload/' + f.name
    destination = open(filename, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    print(run_objdump(filename))

def run_objdump(filename):
    import subprocess
    bindir = '/usr/local/bin/'
    prefix = 'i686-elf-'
    objdump = "%(bindir)s%(prefix)sobjdump" % ({
                                   'bindir' : bindir, 
                                   'prefix': prefix})
    output = subprocess.Popen([objdump,'-D', filename], stdout=subprocess.PIPE).communicate()[0]
    return output


class UploadFileForm(forms.Form):
    filedata  = forms.FileField()    
    
def check_existing(request):
    return HttpResponse("0", mimetype="text/plain")
    
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            o = OdaFile.create(request.FILES['filedata'], request.META["REMOTE_ADDR"])
            o.save()  
            bfd = None        
            try: 
                bfd = engine.OdaBfd(o.uuid, None, None)
                binary_file = BinaryFile()
                binary_file.odafile = o
                binary_file.platform = bfd.arch()
                binary_file.save()
            except:
                pass         
            files_uploaded = request.session.get('files', [])
            files_uploaded.append(o.uuid)            
            request.session['files'] = files_uploaded            
            rendered = render_to_string('arch_combo.djhtml', {                                                    
                'supported_archs': engine.get_supported_archs,
                'arch' : (bfd.arch() if bfd  else '')
            })
            return HttpResponse(simplejson.dumps({
                                                  'result':'ok', 
                                                  'uuid' : o.uuid, 
                                                  'target': (bfd.target() if bfd else ''),
                                                  'arch': rendered}))
    else:
        form = UploadFileForm()
    #return render_to_response('upload.html', {'form': form})
    
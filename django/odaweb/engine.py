from django.contrib import admin
from django import forms
from odaweb.models import *
import bfd
import re

# ------------------------------------------------------------------------------
# External module-level functions
# ------------------------------------------------------------------------------
def get_supported_archs():
    '''Return a list of all architectures supported
    '''
    supportedArchs = bfd.list_architectures()
    
    # Remove Problem archs
    problemArchs = ['MicroBlaze',
                    'i960:ka_sa',
                    'i960:kb_sb', 
                    'r800',
                    'moxie',
                    ]
        
    for arch in problemArchs:
        supportedArchs.remove(arch)
        
    return supportedArchs

def get_supported_targets():
    '''Return a list of all file formats supported
    '''
    return bfd.list_targets()

def get_supported_endians():
    
    endians = {
       'DEFAULT' : bfd.ENDIAN_DEFAULT,
        'LITTLE'  : bfd.ENDIAN_LITTLE,
        'BIG'     : bfd.ENDIAN_BIG
    }
    
    return endians

# ------------------------------------------------------------------------------
# Internal utility functions
# ------------------------------------------------------------------------------
def funcFmtAddr(bfd, addr):
    addrStr = '0x%08x' % addr
    if bfd.syms_by_addr.has_key(addr):
        addrStr += ' <%s>' % bfd.syms_by_addr[addr].name
    return addrStr

def funcFmtLine(addr, rawData, instr, abfd):
    from cStringIO import StringIO
    file_str = StringIO()
    if abfd.syms_by_addr.has_key(addr):
        file_str.write('\n0%08x <%s>:\n' % (addr, abfd.syms_by_addr[addr].name))
    if abfd.bpc > 1 and (abfd.endian is bfd.ENDIAN_LITTLE or abfd.endian is bfd.ENDIAN_DEFAULT):
        bytes = ''.join(['%02x ' % i for i in reversed(rawData)])       
    else:
        bytes = ''.join(['%02x ' % i for i in rawData])
        
    file_str.write(' %08x %-32s %s\n' % (addr, bytes, instr))
    return file_str.getvalue()        

def disassemble_to_file(o, platform):

    import tempfile
    t = tempfile.TemporaryFile()
        
    #analyzer = analyzerFactory(platform)
    #o = OdaFile.objects.get(uuid=file_id)
        
    try: 
        bfd = OdaBfd(o.uuid)
        disassembly, ignore = bfd.disassemble('.text')
    except: 
        bfd = OdaBfd(o.uuid,'binary', platform)
        disassembly, ignore = bfd.disassemble('.data')
    t.write(disassembly)
    return t

# ------------------------------------------------------------------------------
# External class that wraps BFD access
# ------------------------------------------------------------------------------    
class OdaBfd():

    def __init__(self, uuid, target=None, machine=None):
        '''Load a new executable file
        '''        
        self.uuid = uuid
        oda_file = OdaFile.objects.get(uuid=uuid)
        self.filename = oda_file.file_handle().name
        
        self.bfd = bfd.Bfd(self.filename, target, machine)

        # Convert to list, ordered by ascending addresses
        self.sections = list(self.bfd.sections.values())

        for s in self.sections:
            for f in bfd.FLAGS:
                if f.name in s.flags:
                    setattr(self, f.name, True) # i.e, section.SEC_ALLOC = True
                else:
                    setattr(self, f.name, False) # i.e, section.SEC_ALLOC = False



    def raw_data(self, sec_name, addr, size):
        return bfd.raw_data(bfd.sections[sec_name], addr, size)

    def target(self):
        return self.bfd.target
    
    def arch(self):
        return self.bfd.arch

    def sections_iter(self, flags=[]):
        '''Iterate over all sections (in ascending address order) that have all give flags specified'''
        for sec in self.sections:
            sec_flags = [f.name for f in sec.flags]
            if set(flags).issubset(sec_flags):
                yield sec

    def section(self, name):
        '''Get a section by section name'''
        return self.bfd.sections[name]

    def sectionFlagsInfo(self):
        return bfd.FLAGS

    def symbols(self):
        '''Returns a list of Symbols sorted by increasing address'''
        return [sym for (name, sym) in sorted(self.bfd.syms_by_name.iteritems(), key=lambda (name, sym): sym.value)]
    
    def strings(self):
        strs = []
        bin = open(self.filename, "rb").read()
        for m in re.finditer("([\t\x20-\x7e]{4,})", bin):
            strs.append((m.start(), m.group(1)))            
        return strs
    
    def disassemble(self, name, start=None, stop=None, numLines=None, endian=bfd.ENDIAN_DEFAULT, options=''):
        sec = self.bfd.sections[name]

        # this is to force the i386 strcpy example to use intel syntax...need a better solution
        if self.bfd.arch.startswith('i386') and options == '':
            options = 'intel-mnemonic'

        dis = self.bfd.disassemble(sec, start, stop, numLines, funcFmtAddr, funcFmtLine, endian, options)
        return dis
    

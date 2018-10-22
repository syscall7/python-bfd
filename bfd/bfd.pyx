# cython: profile=True
# cython: c_string_type = unicode
# cython: c_string_encoding = ascii
# cython: language_level=3str
import tempfile
import sys
import logging

from libc.stdio cimport *
from libc.setjmp cimport *
from libc.signal cimport *
from libc.string cimport memset

if sys.version_info < (2, 7):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

# the global context we use to restore state after catching a signal
# NOTE: We must save context with setjmp for each entry point into this module
#       in order to recover and raise an exception.
cdef jmp_buf ctx

logger = logging.getLogger('bfd.pyx')

# our signal handler
cdef handler(int signum):
    global ctx
    logger.info("caught signal %d" % signum)

    # restore the last saved context
    longjmp(ctx, 1)

# Set our signal handler
signal(SIGSEGV, <sighandler_t> handler)
signal(SIGABRT, <sighandler_t> handler)

# ------------------------------------------------------------------------------
# PROTOTYPES
# ------------------------------------------------------------------------------

cdef extern from "stdlib.h":
    ctypedef int size_t
    ctypedef long intptr_t
    void *malloc(size_t size)
    void free(void* ptr)

cdef extern from "stdio.h":
    void* stdout
    #int fprintf  (FILE *stream, const char *template, ...)

cdef extern from "string.h":
    void* memcpy (void *dest, void *src, size_t n)


# Idiom for accessing Python files.
# First, declare the Python macro to access files:
#cdef extern from "Python.h":
#    ctypedef struct FILE
#    FILE* PyFile_AsFile(object)
# Next, enter the builtin file class into the namespace:
#cdef extern from "fileobject.h":
#    ctypedef class __builtin__.file [object PyFileObject]:
#        pass

cdef extern from "bfd.h":

    # --------------------------------------------------------------------------
    # CONSTANTS
    # --------------------------------------------------------------------------
    ctypedef enum flags:
        HAS_SYMS = 0x10
        DYNAMIC = 0x40

    ctypedef enum bfd_format:
        bfd_unknown = 0,  # File format is unknown.
        bfd_object,       # Linker/assembler/compiler output.
        bfd_archive,      # Object archive file.
        bfd_core,         # Core dump.
        bfd_type_end      # Marks the end; don't use it!

    ctypedef enum bfd_error_type:
        bfd_error_no_error = 0,
        bfd_error_system_call,
        bfd_error_invalid_target,
        bfd_error_wrong_format,
        bfd_error_wrong_object_format,
        bfd_error_invalid_operation,
        bfd_error_no_memory,
        bfd_error_no_symbols,
        bfd_error_no_armap,
        bfd_error_no_more_archived_files,
        bfd_error_malformed_archive,
        bfd_error_file_not_recognized,
        bfd_error_file_ambiguously_recognized,
        bfd_error_no_contents,
        bfd_error_nonrepresentable_section,
        bfd_error_no_debug_section,
        bfd_error_bad_value,
        bfd_error_file_truncated,
        bfd_error_file_too_big,
        bfd_error_on_input,
        bfd_error_invalid_error_code

    ctypedef enum bfd_flavour:
        bfd_target_unknown_flavour = 0

    ctypedef enum bfd_architecture:
        bfd_arch_unknown

    ctypedef enum bfd_endian:
        BFD_ENDIAN_BIG
        BFD_ENDIAN_LITTLE
        BFD_ENDIAN_UNKNOWN

    # --------------------------------------------------------------------------
    # TYPES
    # --------------------------------------------------------------------------
    ctypedef long long file_ptr
    ctypedef int bfd_boolean
    ctypedef unsigned int flagword
    ctypedef unsigned long long symvalue
    ctypedef unsigned long long bfd_vma
    ctypedef unsigned long long bfd_size_type
    ctypedef struct symbol_info:
        symvalue value
        char type
    ctypedef struct asymbol
    ctypedef struct symbol_info
    ctypedef struct asection
    ctypedef struct asection:
        unsigned int alignment_power
        char* name
        asection* next
        bfd_vma vma
    ctypedef struct bfd_arch_info
    ctypedef bfd_arch_info bfd_arch_info_type
    ctypedef struct bfd_target:
        bfd_endian byteorder

    ctypedef struct bfd:
        asection* sections
        bfd_arch_info* arch_info
        const bfd_target* xvec

    ctypedef unsigned char bfd_byte

    # --------------------------------------------------------------------------
    # Macros
    # --------------------------------------------------------------------------
    char* bfd_get_target "bfd_get_target" (bfd* abfd)
    long bfd_get_symtab_upper_bound "bfd_get_symtab_upper_bound" (bfd* abfd)
    long bfd_get_dynamic_symtab_upper_bound "bfd_get_dynamic_symtab_upper_bound" (bfd* abfd)
    long bfd_canonicalize_symtab  "bfd_canonicalize_symtab" (bfd* abfd, asymbol **sy)
    long bfd_canonicalize_dynamic_symtab  "bfd_canonicalize_dynamic_symtab" (bfd* abfd, asymbol **sy)
    long bfd_get_file_flags "bfd_get_file_flags" (bfd* abfd)
    bfd_flavour bfd_get_flavour "bfd_get_flavour" (bfd* abfd)
    bfd_boolean bfd_big_endian "bfd_big_endian" (bfd* abfd)
    bfd_boolean bfd_little_endian "bfd_little_endian" (bfd* abfd)
    flagword bfd_get_section_flags "bfd_get_section_flags" (bfd* abfd, asection* sec)

    # symbol macros
    bfd_vma bfd_asymbol_base(asymbol* sy)
    bfd_vma bfd_asymbol_value(asymbol* sy)
    char* bfd_asymbol_name(asymbol* sy)
    void bfd_get_symbol_info(bfd* abfd, asymbol* asym, symbol_info* si)

    # section macros
    char* bfd_section_name "bfd_section_name" (bfd* abfd, asection* section)
    bfd_size_type bfd_section_size "bfd_section_size" (bfd* abfd, asection* section)
    bfd_vma bfd_section_vma "bfd_section_vma" (bfd* abfd, asection* section)
    bfd_vma bfd_section_lma "bfd_section_lma" (bfd* abfd, asection* section)
    long bfd_section_alignment "bfd_section_alignment" (bfd* abfd, asection* section)

    # --------------------------------------------------------------------------
    # Functions
    # --------------------------------------------------------------------------
    const char** bfd_arch_list()
    const char** bfd_target_list()
    bfd* bfd_openr(char *filename, char *target)
    bfd_boolean bfd_close(bfd *abfd)
    bfd_boolean bfd_check_format(bfd *abfd, bfd_format fmt)
    bfd_boolean bfd_check_format_matches(bfd *abfd, bfd_format fmt, char ***matching)
    bfd_error_type bfd_get_error()
    char* bfd_errmsg(bfd_error_type error_tag)
    void bfd_map_over_sections(bfd *abfd, void (*func)(bfd*, asection*, void*), object obj)
    unsigned long bfd_get_mach(bfd *abfd)
    bfd_architecture bfd_get_arch(bfd *abfd)
    const char* bfd_printable_arch_mach(bfd_architecture arch, unsigned long machine)
    unsigned int bfd_octets_per_byte (bfd *abfd)
    bfd_boolean bfd_get_section_contents(bfd* abfd, asection* section, void* location, file_ptr offset, bfd_size_type count)
    const bfd_arch_info_type* bfd_scan_arch (char *string)

cdef extern from "dis-asm.h":

    ctypedef int (*fprintf_ftype) (void* filep, char* fmt, ...)
    ctypedef struct disassemble_info
    # pre-declare
    ctypedef struct disassemble_info
    ctypedef struct disassemble_info:
        fprintf_ftype fprintf_func
        void* stream
        void* application_data
        bfd_flavour flavour
        bfd_architecture arch
        unsigned long mach
        bfd_endian endian
        bfd_endian endian_code
        void *insn_sets
        asection *section
        asymbol **symbols
        int num_symbols
        asymbol **symtab
        int symtab_pos
        int symtab_size
        unsigned long flags
        void *private_data
        int (*read_memory_func) (bfd_vma memaddr, bfd_byte *myaddr, unsigned int length, disassemble_info *dinfo)
        void (*memory_error_func) (int status, bfd_vma memaddr, disassemble_info *dinfo)
        void (*print_address_func) (bfd_vma addr, disassemble_info *dinfo)
        int (* symbol_at_address_func) (bfd_vma addr, disassemble_info *dinfo)
        bfd_boolean (* symbol_is_valid) (asymbol *, disassemble_info *dinfo)
        bfd_byte *buffer
        bfd_vma buffer_vma
        unsigned int buffer_length
        int bytes_per_line
        int bytes_per_chunk
        bfd_endian display_endian
        unsigned int octets_per_byte
        unsigned int skip_zeroes
        unsigned int skip_zeroes_at_end
        bfd_boolean disassembler_needs_relocs
        char insn_info_valid
        char branch_delay_insns
        char data_size
        #dis_insn_type insn_type
        bfd_vma target
        bfd_vma target2
        char * disassembler_options
        int insn_type

    ctypedef int (*disassembler_ftype)(bfd_vma vma, disassemble_info* dinfo)

    void init_disassemble_info(disassemble_info* info, void* stream, fprintf_ftype fprintf_func)
    void* disassembler(bfd_architecture arc, bfd_boolean big, unsigned long mach, bfd* abfd)
    void disassembler_usage (void* stream)
    void disassemble_init_for_target(disassemble_info * dinfo)

# ------------------------------------------------------------------------------
# MODULE-LEVEL FUNCTONS
# ------------------------------------------------------------------------------
def list_architectures():
    cdef const char** a
    archs = []
    a = bfd_arch_list()
    i = 0
    while a[i] != NULL:
        archs.append(a[i])
        i += 1
    free(a)
    return archs

def list_targets():
    cdef const char** t
    targets = []
    t = bfd_target_list()
    i = 0
    while t[i] != NULL:
        targets.append(t[i])
        i += 1
    free(t)
    return targets


# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class BfdErr(Exception):
    def __init__(self, value):
        cdef bfd_error_type err
        err = bfd_get_error();
        self.value = '%s: (error %d) %s' % (value, err, bfd_errmsg(err))
    def __str__(self):
        return repr(self.value)

class BfdFileFormatException(BfdErr):
    pass

class BfdHaltDisassembly(Exception):
    pass

class BfdSegFault(Exception):
    pass

# ------------------------------------------------------------------------------
# CLASS Symbol
# ------------------------------------------------------------------------------
cdef class Symbol:

    cdef public:
        symvalue value
        bfd_vma base
        char* name
        object dynamic
        unicode type

    def __cinit__(self):
        pass

    cdef load(self, bfd* abfd, asymbol* asym, object dynamic):
        cdef symbol_info syminfo
        bfd_get_symbol_info (abfd, asym, &syminfo)

        #self.value = bfd_asymbol_value(asym)
        #self.base = bfd_asymbol_base(asym)
        self.name = bfd_asymbol_name(asym)
        self.value = syminfo.value
        self.type = chr(syminfo.type)
        self.dynamic = dynamic

class SectionFlag:

    def __init__(self, name, abbrev, val, desc):
        self.name = name
        self.abbrev = abbrev
        self.val = val

        # the popover content field can't handle newlines in the django
        # template right now, so replace them with spaces for now.
        self.desc = desc.replace('\n', ' ')

    def isset(self, object flags):
        return self.val & flags != 0

# The following section flags are from bfd.h and MAY change in future versions of bfd
FLAGS = (
    SectionFlag('SEC_ALLOC', 'ALLOC', 0x001,
                'Tells the OS to allocate space for this section when loading.\n' \
                'This is clear for a section containing debug information only.'),

    SectionFlag('SEC_LOAD', 'LOAD', 0x002,
                'Tells the OS to load the section from the file when loading.\n' \
                'This is clear for a .bss section.'),

    SectionFlag('SEC_RELOC', 'RELOC', 0x004,
                'The section contains data still to be relocated, so there is\n' \
                'some relocation information too.'),

    SectionFlag('SEC_READONLY', 'READONLY', 0x008,
                'A signal to the OS that the section contains read only data.'),

    SectionFlag('SEC_CODE', 'CODE', 0x010,
                'The section contains code only.'),

    SectionFlag('SEC_DATA', 'DATA', 0x020,
                'The section contains data only.'),

    SectionFlag('SEC_ROM', 'ROM', 0x040,
                'The section will reside in ROM.'),

    SectionFlag('SEC_CONSTRUCTOR', 'CONSTRUCTOR', 0x080,
                'The section contains constructor information. This section\n' \
                'type is used by the linker to create lists of constructors and\n' \
                'destructors used by <<g++>>. When a back end sees a symbol\n' \
                'which should be used in a constructor list, it creates a new\n' \
                'section for the type of name (e.g., <<__CTOR_LIST__>>), attaches\n' \
                'the symbol to it, and builds a relocation. To build the lists\n' \
                'of constructors, all the linker has to do is catenate all the\n' \
                'sections called <<__CTOR_LIST__>> and relocate the data\n' \
                'contained within - exactly the operations it would peform on\n' \
                'standard data.'),

    SectionFlag('SEC_HAS_CONTENTS', 'CONTENTS', 0x100,
                'The section has contents - a data section could be\n' \
                '<<SEC_ALLOC>> | <<SEC_HAS_CONTENTS>>; a debug section could be\n' \
                '<<SEC_HAS_CONTENTS>>.'),

    SectionFlag('SEC_NEVER_LOAD', 'NEVER_LOAD', 0x200,
                'An instruction to the linker to not output the section\n' \
                'even if it has information which would normally be written.'),

    SectionFlag('SEC_THREAD_LOCAL', 'THREAD_LOCAL', 0x400,
                'The section contains thread local data.'),

    SectionFlag('SEC_HAS_GOT_REF', 'GOT_REF', 0x800,
                'The section has GOT references.  This flag is only for the\n' \
                'linker, and is currently only used by the elf32-hppa back end.\n' \
                'It will be set if global offset table references were detected\n' \
                'in this section, which indicate to the linker that the section\n' \
                'contains PIC code, and must be handled specially when doing a\n' \
                'static link.'),

    SectionFlag('SEC_IS_COMMON', 'COMMON', 0x1000,
                'The section contains common symbols (symbols may be defined\n' \
                'multiple times, the value of a symbol is the amount of\n' \
                'space it requires, and the largest symbol value is the one\n' \
                'used).  Most targets have exactly one of these (which we\n' \
                'translate to bfd_com_section_ptr), but ECOFF has two.'),

    SectionFlag('SEC_DEBUGGING', 'DEBUGGING', 0x2000,
                'The section contains only debugging information.  For\n' \
                'example, this is set for ELF .debug and .stab sections.\n' \
                'strip tests this flag to see if a section can be\n' \
                'discarded.'),

    SectionFlag('SEC_IN_MEMORY', 'IN_MEMORY', 0x4000,
                'The contents of this section are held in memory pointed to\n' \
                'by the contents field.  This is checked by bfd_get_section_contents,\n' \
                'and the data is retrieved from memory if appropriate.'),

    SectionFlag('SEC_EXCLUDE', 'EXCLUDE', 0x8000,
                'The contents of this section are to be excluded by the\n' \
                'linker for executable and shared objects unless those\n' \
                'objects are to be further relocated.'),

    SectionFlag('SEC_SORT_ENTRIES', 'SORT_ENTRIES', 0x10000,
                'The contents of this section are to be sorted based on the sum of\n' \
                'the symbol and addend values specified by the associated relocation\n' \
                'entries.  Entries without associated relocation entries will be\n' \
                'appended to the end of the section in an unspecified order.'),

    SectionFlag('SEC_LINK_ONCE', 'LINK_ONCE', 0x20000,
                'When linking, duplicate sections of the same name should be\n' \
                'discarded, rather than being combined into a single section as\n' \
                'is usually done.  This is similar to how common symbols are\n' \
                'handled.  See SEC_LINK_DUPLICATES below.'),

    SectionFlag('SEC_LINK_DUPLICATES', 'LINK_DUPLICATES', 0xc0000,
                'If SEC_LINK_ONCE is set, this bitfield describes how the linker\n' \
                'should handle duplicate sections.'),

    SectionFlag('SEC_LINK_DUPLICATES_DISCARD', 'LINK_DUPLICATES_DISCARD', 0x0,
                'This value for SEC_LINK_DUPLICATES means that duplicate\n' \
                'sections with the same name should simply be discarded.'),

    SectionFlag('SEC_LINK_DUPLICATES_ONE_ONLY', 'LINK_DUPLICATES_ONE_ONLY', 0x40000,
                'This value for SEC_LINK_DUPLICATES means that the linker\n' \
                'should warn if there are any duplicate sections, although\n' \
                'it should still only link one copy.'),

    SectionFlag('SEC_LINK_DUPLICATES_SAME_SIZE', 'LINK_DUPLICATES_SAME_SIZE', 0x80000,
                'This value for SEC_LINK_DUPLICATES means that the linker\n' \
                'should warn if any duplicate sections are a different size.'),

    SectionFlag('SEC_LINK_DUPLICATES_SAME_CONTENTS', 'LINK_DUPLICATES_SAME_CONTENTS', 0x40000|0x80000,
                'This value for SEC_LINK_DUPLICATES means that the linker\n' \
                'should warn if any duplicate sections contain different\n' \
                'contents.'),

    SectionFlag('SEC_LINKER_CREATED', 'LINKER_CREATED', 0x100000,
                'This section was created by the linker as part of dynamic\n' \
                'relocation or other arcane processing.  It is skipped when\n' \
                'going through the first-pass output, trusting that someone\n' \
                'else up the line will take care of it later.'),

    SectionFlag('SEC_KEEP', 'KEEP', 0x200000,
                'This section should not be subject to garbage collection.\n' \
                'Also set to inform the linker that this section should not be\n' \
                'listed in the link map as discarded.'),

    SectionFlag('SEC_SMALL_DATA', 'SMALL_DATA', 0x400000,
                'This section contains "short" data, and should be placed\n' \
                '"near" the GP.'),

    SectionFlag('SEC_MERGE', 'MERGE', 0x800000,
                'Attempt to merge identical entities in the section.\n' \
                ' Entity size is given in the entsize field.\n'),

    SectionFlag('SEC_STRINGS', 'STRINGS', 0x1000000,
                'If given with SEC_MERGE, entities to merge are zero terminated\n' \
                'strings where entsize specifies character size instead of fixed\n' \
                'size entries.'),

    SectionFlag('SEC_GROUP', 'GROUP', 0x2000000,
                'This section contains data about section groups.'),

    SectionFlag('SEC_COFF_SHARED_LIBRARY', 'COFF_SHARED_LIBRARY', 0x4000000,
                'The section is a COFF shared library section.  This flag is\n' \
                'only for the linker.  If this type of section appears in\n' \
                'the input file, the linker must copy it to the output file\n' \
                'without changing the vma or size.  FIXME: Although this\n' \
                'was originally intended to be general, it really is COFF\n' \
                'specific (and the flag was renamed to indicate this).  It\n' \
                'might be cleaner to have some more general mechanism to\n' \
                'allow the back end to control what the linker does with\n' \
                'sections.'),

    SectionFlag('SEC_COFF_SHARED', 'COFF_SHARED', 0x8000000,
                'This section contains data which may be shared with other\n' \
                'executables or shared objects. This is for COFF only.\n'),

    SectionFlag('SEC_TIC54X_BLOCK', 'TIC54X_BLOCK', 0x10000000,
                'When a section with this flag is being linked, then if the size of\n' \
                'the input section is less than a page, it should not cross a page\n' \
                'boundary.  If the size of the input section is one page or more,\n' \
                'it should be aligned on a page boundary.  This is for TI\n' \
                'TMS320C54X only.'),

    SectionFlag('SEC_TIC54X_CLINK', 'TIC54X_CLINK', 0x20000000,
                'Conditionally link this section; do not link if there are no\n' \
                'references found to any symbol in the section.  This is for TI\n' \
                'TMS320C54X only.'),

    SectionFlag('SEC_COFF_NOREAD', 'COFF_NOREAD', 0x40000000,
                'Indicate that section has the no read flag set. This happens\n' \
                ' when memory read flag isn\'t set.'),
)

# ------------------------------------------------------------------------------
# CLASS Section
# ------------------------------------------------------------------------------
cdef class Section:

    cdef public:
        bfd_vma vma
        bfd_vma lma
        long alignment
        char* name
        bfd_size_type size
        object flags

        # this is a hack until I can figure out how to add weak references dynamically in upper layers
        object color

    cdef:
        bfd* abfd
        asection* section

    def __cinit__(self):
        self.flags = []
        pass

    def __str__(self):
        return '%-32s %8d 0x%08x 0x%08x 2**%u' % (
            self.name, self.size, self.vma, self.lma, self.alignment)

    def __repr__(self):
        return str(self)

    cdef load(self, bfd* abfd, asection* section):
        self.abfd = abfd
        self.section = section

        self.name = bfd_section_name(abfd, section)
        self.vma = bfd_section_vma(abfd, section)
        self.lma = bfd_section_lma(abfd, section)
        self.size = bfd_section_size(abfd, section)
        self.alignment = bfd_section_alignment(abfd, section)
        flags = bfd_get_section_flags(abfd, section)

        for f in FLAGS:
            if f.isset(flags):
                self.flags.append(f)

    cdef get_section_contents(self, bfd_byte* buf, offset=0, size=0):
        if size == 0:
            size = self.size
        bfd_get_section_contents(<bfd*>self.abfd, <asection*>self.section, buf, offset, size)
        return

ENDIAN_DEFAULT=BFD_ENDIAN_UNKNOWN
ENDIAN_LITTLE=BFD_ENDIAN_LITTLE
ENDIAN_BIG=BFD_ENDIAN_BIG

cdef internalFuncFmtAddr(bfd, addr):
    addrStr = '0x%08x' % addr
    if addr in bfd.syms_by_addr:
        addrStr += ' <%s>' % bfd.syms_by_addr[addr].name
    return addrStr

# returns a tuple of all matching (target,arch) pairs, even with ones with unknown arch
def guess_target_arch(path):

    cdef char **matching
    cdef bfd_arch_info_type* inf
    matches = []
    targets = []

    logger.info('guessing target')
    # open BFD file
    abfd = bfd_openr(path.encode('UTF-8'), NULL)
    if (NULL == abfd):
        raise BfdErr('Unable to open file %s' % path)

    # check if we have an object file
    if bfd_check_format_matches(abfd, bfd_object, &matching) == 0:

        # if we failed to match, check for ambiguous match
        if bfd_get_error() == bfd_error_file_ambiguously_recognized:

            # for each potential match
            i = 0
            while matching[i] != NULL:
                matches.append(matching[i])
                i = i+1

            free(matching)
    else:
        matches.append(bfd_get_target(abfd))
        logger.info('guessed target %s' % matches)

    # for each target, retrieve identified arch if known
    for match in matches:
        abfd = bfd_openr(path, match)
        if bfd_check_format(abfd, bfd_object):
            # NOTE the rest of our code depends on bfd returning the exact string 'UNKNOWN!' when arch is unknown
            arch = bfd_printable_arch_mach(bfd_get_arch(abfd), bfd_get_mach(abfd))
            targets.append((match, arch))

    logger.info('Targets: %s' % targets)
    return targets

# ------------------------------------------------------------------------------
# CLASS Bfd
# ------------------------------------------------------------------------------
cdef class Bfd:

    cdef bfd* abfd
    cdef public object syms_by_name
    cdef public object syms_by_addr
    cdef public object sections
    cdef public object target
    cdef public object funcFmtAddr
    cdef public unsigned long mach
    cdef public bfd_architecture archId
    cdef public const char* arch
    cdef public object bpc
    cdef public object endian

    def __cinit__(self, path, object target = None, object machine = None):

        cdef char **matching
        cdef const bfd_arch_info_type* inf
        global ctx

        if setjmp(ctx) != 0:
            raise BfdSegFault('Something very bad happened in the Bfd constructor!')

        # a dictionary of Symbols indexed by name
        self.syms_by_name = {}
        self.syms_by_addr = {}
        self.sections = OrderedDict()

        if target:
            self.abfd = bfd_openr(path.encode('UTF-8'), target.encode('UTF-8'))
            #logger.info('PyBfd: target is %s' % target.encode('UTF-8'))
        else:
            self.abfd = bfd_openr(path.encode('UTF-8'), NULL)

        # open BFD file

        if (NULL == self.abfd):
            raise BfdErr('Unable to open file %s' % path)

        # set machine
        if machine:
            inf = bfd_scan_arch(machine.encode('UTF-8'))
            self.abfd.arch_info = inf

            # if we failed to match
        if bfd_check_format(self.abfd, bfd_object) == 0:
            logger.info("Failed to get match")
            raise BfdFileFormatException('Unable to identify target format')

        if bfd_get_flavour(self.abfd) == bfd_target_unknown_flavour:
            # we do not want to raise an exception, as the BFD is
            # still usable, just empty */
            #print '[BFD] Warning: unknown BFD flavour'
            pass

        #cdef asection* sec
        #sec = self.abfd.sections
        #while sec != NULL:
        #    #print sec.name, sec.alignment_power
        #    sec = sec.next

        # set target machine architecture
        self.archId = bfd_get_arch(self.abfd)
        self.mach = bfd_get_mach(self.abfd)
        self.arch = bfd_printable_arch_mach(self.archId, self.mach)
        self.target = bfd_get_target(self.abfd)

        # do not let these errors stop us
        try:

            # load the static symbols
            self._load_static_syms()

            # load the dynamic symbols
            self._load_dynamic_syms()

        except BfdErr, e:
            logger.info('Caught exception: %s, but continuing anyway' % e)

        # load sections
        self._load_sections()

    def __dealloc__(self):
        # do free()s on anything we've allocated
        pass

    def close(self):
        bfd_close(self.abfd)

    cdef _add_syms(self, asymbol** asym, long num, object dynamic):
        # must declare C type first
        cdef Symbol s
        for 0 <= i < num:
            s = Symbol()
            s.load(self.abfd, asym[i], dynamic)
            self.syms_by_name[s.name] = s
            self.syms_by_addr[s.value] = s

    cdef _load_static_syms(self):
        cdef long size
        #cdef unsigned int i
        cdef long num
        cdef asymbol ** syms

        if ((bfd_get_file_flags(self.abfd) & HAS_SYMS) == 0):
            #print 'No static symbols found'
            return

        size = bfd_get_symtab_upper_bound(self.abfd)
        if ( size <= 0 ):
            raise BfdErr('Failed to get symtab upper bound')

        syms = <asymbol**> malloc(size)
        if ( syms == NULL ):
            raise BfdErr('Failed to malloc static syms')

        num = bfd_canonicalize_symtab(self.abfd, syms)

        self._add_syms(syms, num, False)
        free(syms)

    cdef _load_dynamic_syms(self):
        cdef long size
        cdef unsigned int i
        cdef long num
        cdef asymbol ** syms

        size = bfd_get_dynamic_symtab_upper_bound(self.abfd)
        if size < 0:
            if ((bfd_get_file_flags(self.abfd) & DYNAMIC) == 0):
                #raise BfdErr('Cannot get dynamic symbols from non-dynamic object')
                pass
            #raise BfdErr('Failed to get dynamic syms')
            return

        syms = <asymbol**> malloc(size)
        if ( syms == NULL ):
            raise BfdErr('Failed to malloc static syms')

        num = bfd_canonicalize_dynamic_symtab(self.abfd, syms)
        self._add_syms(syms, num, True)
        free(syms)

    cdef _load_sections(self):
        bfd_map_over_sections(self.abfd, add_sections_callback, self);

    def raw_data(self, section, addr, size):

        cdef Section sec = section
        cdef char* buf
        cdef bytes raw
        global ctx

        if setjmp(ctx) != 0:
            raise BfdSegFault('Something very bad happened while trying to grab raw_data!')

        bufSize = size
        buf = <char*> malloc(bufSize)
        if buf == NULL:
            logger.info('Failed to allocate disassembly buffer')
            return

        sec.get_section_contents(<bfd_byte*>buf, addr - sec.vma, size)

        # cython will automiatically convert this to a python string
        raw = buf[:size]

        free(buf)

        return raw

    def disassemble(self, section, startAddr=None, endAddr=None, numLines=None, funcFmtAddr=None, funcFmtLine=None, funcFmtLineArgs=None, endian=ENDIAN_DEFAULT, options=b'', baseAddr=None):
        '''Disassemble the given section

           section - String specifying the name of the section to disassemble
           startAddr - The absolute address at which to start disassembling. The default of None means sec.vma.
           numLines - The maximum number of lines to disassemble.  The default of None means return all lines possible.
           endAddr - The address at which to stop disassembling.  The default of None means up to the end of the section.
           funcFmtAddr - Called to format address references
           funcFmtLine - Called to format entire lines of disassembly
           endian - Endian to use when disassembling
           options - Machine specific disassembly options
           baseAddr - Amount to adjust VMA (startAddr is always given without taking baseAddr into affect)

           returns a tuple containing (1. the disassembly text, 2. the next address at which disassembly should continue, 3. number of lines returned)
        '''

        global ctx
        cdef disassemble_info disasm_info
        cdef disassembler_ftype disassemble_fn
        cdef bufSize
        cdef bfd_byte* buf
        cdef Section sec
        cdef int i
        cdef FILE* stream
        cdef char* tmpBuffer
        cdef bfd_target* xvec_new
        cdef const bfd_target* xvec_orig
        #cdef char* coptions = <bytes>(options.encode('UTF-8'))

        if setjmp(ctx) != 0:
            raise BfdSegFault('Something very bad happened while trying to disassemble!')

        # this assignment is necessary to translate between C and Cython
        sec = section

        sec_vma = sec.vma
        if baseAddr:
            sec_vma += baseAddr
        else:
            baseAddr = 0

        # uncomment this to test our segmentation fault handler
        #cdef bfd_byte* test = NULL
        #test[0] = 2

        # make sure right away that we can disassemble this bfd
        disassemble_fn = <disassembler_ftype> disassembler(self.archId, False, self.mach, self.abfd)
        if NULL == disassemble_fn:
            raise BfdErr('Cannot disassemble for arch %s' % self.arch)

        xvec_new = NULL
        xvec_orig = self.abfd.xvec

        stream = tmpfile()
        #iostream = tempfile.TemporaryFile()
        #stream = <FILE*>iostream
        #if hasattr(iostream, 'file'):
        #    stream = PyFile_AsFile(iostream.file)
        #else:
        #    stream = PyFile_AsFile(iostream)


        self.funcFmtAddr = funcFmtAddr

        init_disassemble_info (&disasm_info, stream, <fprintf_ftype> fprintf)

        disasm_info.application_data = <void *> self
        disasm_info.print_address_func = print_address_func
        disasm_info.symbol_at_address_func = symbol_at_address_func
        disasm_info.flavour = bfd_get_flavour(self.abfd)
        disasm_info.arch = bfd_get_arch(self.abfd)
        disasm_info.mach = bfd_get_mach(self.abfd)
        disasm_info.disassembler_options = options
        disasm_info.octets_per_byte = bfd_octets_per_byte(self.abfd)
        disasm_info.skip_zeroes = 8 # DEFAULT_SKIP_ZEROES
        disasm_info.skip_zeroes_at_end = 3 # DEFAULT_SKIP_ZEROES_AT_END
        disasm_info.bytes_per_chunk = 0
        disasm_info.disassembler_needs_relocs = 0 # FALSE
        disasm_info.application_data = <void*> self

        if bfd_big_endian(self.abfd):
            disasm_info.display_endian = disasm_info.endian = BFD_ENDIAN_BIG
        elif (bfd_little_endian(self.abfd)):
            disasm_info.display_endian = disasm_info.endian = BFD_ENDIAN_LITTLE
        else:
            # ??? Aborting here seems too drastic.  We could default to big or little instead.
            disasm_info.endian = BFD_ENDIAN_UNKNOWN;

        if endian != ENDIAN_DEFAULT:
            xvec_new = <bfd_target*> malloc (sizeof (bfd_target))
            memcpy (xvec_new, self.abfd.xvec, sizeof(bfd_target))
            if endian == ENDIAN_BIG:
                xvec_new.byteorder = BFD_ENDIAN_BIG
                disasm_info.display_endian = disasm_info.endian = BFD_ENDIAN_BIG
            else:
                xvec_new.byteorder = BFD_ENDIAN_LITTLE
                disasm_info.display_endian = disasm_info.endian = BFD_ENDIAN_LITTLE
            self.abfd.xvec = xvec_new

        # get disassemble function again, since we modified xvec
        disassemble_fn = <disassembler_ftype> disassembler(self.archId, True if disasm_info.endian == BFD_ENDIAN_BIG else False, self.mach, self.abfd)
        if NULL == disassemble_fn:
            raise BfdErr('Cannot disassemble for arch %s' % self.arch)

            # TODO: set symbols?
        disasm_info.symtab = NULL
        disasm_info.symtab_size = 0
        disasm_info.symbols = NULL
        disasm_info.num_symbols = 0

        bufSize = sec.size
        buf = <bfd_byte*> malloc(bufSize)
        if buf == NULL:
            logger.info('Failed to allocate disassembly buffer')
            if xvec_new != NULL:
                free(xvec_new)
            self.abfd.xvec = xvec_orig
            return

        sec.get_section_contents(buf)

        disasm_info.buffer = buf
        disasm_info.buffer_vma = sec_vma
        disasm_info.buffer_length = bufSize

        # start address of None means from beginning of section
        if startAddr is None:
            startAddr = sec_vma

        # end address of None means everything in the section
        if endAddr is None:
            endAddr = sec_vma + sec.size

        # numLines of None means all available in the section
        if numLines is None:
            numLines = 2147483648

        #print 'Section: %s' % section.name
        #print 'Start Address: 0x%08x' % startAddr
        #print 'End Address: 0x%08x' % endAddr
        #print 'Num Lines: %d' % numLines
        #print 'funcFmtAddr: %s' % funcFmtAddr
        #print 'funcFmtLine: %s' % funcFmtLine
        #print 'Endian: %s' % endian
        #print 'Options: %s' % options
        #print 'Base Address: 0x%016x' % baseAddr

        addr = startAddr

        lineCnt = 0
        output = []

        # bytes per instruction, set by some architectures
        self.bpc = None
        self.endian = endian

        foffs = 0

        # Allow the target to customize the info structure
        disassemble_init_for_target(&disasm_info)

        while addr < endAddr and lineCnt < numLines:
            instrSize = disassemble_fn(addr, &disasm_info)

            if funcFmtLine != None:
                #iostream.flush()
                fflush(stream)

                #iostream.seek(foffs)
                fseek(stream, foffs, 0)

                #line = iostream.read()
                tmpBuffer = <char*>malloc(2048)
                memset(tmpBuffer, 0, 2048)
                fread(tmpBuffer, 2048, 1, stream)
                line = <bytes> tmpBuffer
                free(tmpBuffer)

                #foffs = iostream.tell()
                foffs = ftell(stream)

                #if hasattr(iostream, 'file'):
                # Keep Windows happy
                #    iostream.seek(foffs)
                rawData = []
                offset = addr - sec_vma

                # TODO: Let cython convert this to a python string
                for 0 <= i < instrSize:
                    rawData.append( buf[offset+i])

                # if we have not initialized bpc this time 'round
                if not self.bpc:
                    if disasm_info.bytes_per_chunk > 0:
                        self.bpc = disasm_info.bytes_per_chunk
                    else:
                        self.bpc = 1

                try:
                    line = funcFmtLine(addr, rawData, line.decode('ascii'), self, **funcFmtLineArgs)
                except BfdHaltDisassembly:
                    break

                if line is not None:
                    output.append(line)

            lineCnt += 1
            addr += instrSize
            if instrSize < 1:
                break

        #iostream.close()
        fclose(stream)
        free(buf)
        if xvec_new != NULL:
            free(xvec_new)
        self.abfd.xvec = xvec_orig

        # next address is returned without taking baseAddr into affect
        return (''.join(output), addr - baseAddr, lineCnt)

    def print_dis_options(self):
        cdef FILE* stream

        #iostream = tempfile.TemporaryFile()
        #if hasattr(iostream, 'file'):
        #    stream = PyFile_AsFile(iostream.file)
        #else:
        #    stream = PyFile_AsFile(iostream)

        #disassembler_usage(stream)
        #iostream.seek(0)
        #iostream.flush()
        #options = iostream.read()
        #print options


        # helper callback function used to interate over each section
cdef void add_sections_callback(bfd* abfd, asection* section, void* _bfd):
    cdef Section sec
    bfd = <object>_bfd

    sec = Section()
    sec.load(abfd, section)
    bfd.sections[sec.name] = sec

cdef void print_address_func(bfd_vma addr, disassemble_info *dinfo):
    cdef Bfd bfd
    bfd = <Bfd> dinfo.application_data
    addrStr = internalFuncFmtAddr(bfd, addr)
    dinfo.fprintf_func(dinfo.stream, addrStr, 0)

cdef int symbol_at_address_func(bfd_vma addr, disassemble_info *dinfo):
    return 0

profile_code='''
import bfd
b = bfd.Bfd('/bin/ls')
sec = b.sections['.text']
start = sec.vma
logger.info('about to disassemble')
(dis,nextAddr, lineCnt) = b.disassemble(sec, sec.vma, None, 3000000000, funcFmtAddr, funcFmtLine, funcFmtLineArgs, endian=bfd.ENDIAN_LITTLE)
with open('out', 'w') as f:
    f.write('Next Address: 0x%08x,\t' % nextAddr)
    f.write('Line Count: 0x%08x,\t' % lineCnt)
    f.write('Disassembly:%s' % dis)
'''

def profile(funcFmtAddr, funcFmtLine, funcFmtLineArgs):
    import cProfile
    logger.info('starting profiler')
    cProfile.runctx(profile_code, globals(), locals())
    logger.info('done profiling')

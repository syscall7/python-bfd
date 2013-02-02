#!/usr/bin/python
import bfd
import sys
import os

# Called each time there is an address referenced in an instruction,
#   such as move r0, 0x12345678
#
# We get a chance to format that value however we want.  In the example below,
#
def funcFmtAddr(bfd, addr):
    addrStr = '0x%08x' % addr
    if bfd.syms_by_addr.has_key(addr):
        addrStr += ' <%s>' % bfd.syms_by_addr[addr].name
    return addrStr

def funcFmtLine(addr, rawData, instr, abfd):
    ret = ''
    if abfd.syms_by_addr.has_key(addr):
        ret += '\n0%08x <%s>:\n' % (addr, abfd.syms_by_addr[addr].name)
    if abfd.bpc > 1 and abfd.endian is bfd.ENDIAN_LITTLE:
        bytes = ''.join(['%02x ' % i for i in reversed(rawData)])
    else:
        bytes = ''.join(['%02x ' % i for i in rawData])
        
    ret += ' %08x %-32s %s\n' % (addr, bytes, instr)
    return ret

def main():

    exe = '/bin/ls'

    if len(sys.argv) > 1:
        exe = sys.argv[1]

    length = 32 #os.path.getsize(exe)
    
    if len(sys.argv) > 2:
        length = int(sys.argv[2])

    #b=bfd.Bfd(exe, 'binary', 'mips')
    b=bfd.Bfd(exe)
    
    print '\nFile: %s' % exe
    print 'Architecture: %s' % b.arch
    print 'Target: %s' % b.target

    print '\nSections:\n'
    print 'Index %-32s %-10s %-10s %-10s %s' % ('Name', 'Size', 'VMA', 'Flags', 'Alignment')
    i = 0
    for sec in b.sections.values():
        print '   %2d %-32s 0x%08x 0x%08x %s 2**%d' % (i, sec.name, sec.size, sec.vma, ', '.join([f.abbrev for f in sec.flags]), sec.alignment)
        i += 1

    print '\nSymbols:\n'
    for sym in b.syms_by_name.values():
        print '  0x%08x %s %s' % (sym.value, sym.type, sym.name)

    if '.text' in b.sections:
        sec_name = '.text'
    elif '.data' in b.sections:
        sec_name = '.data'
    print '\nDisassembly of %s:\n' % sec_name
    sec = b.sections[sec_name]
    start = sec.vma
    numLines = 30
    (dis,nextAddr, lineCnt) = b.disassemble(sec, start, 0, numLines, funcFmtAddr, funcFmtLine, endian=bfd.ENDIAN_LITTLE)
    print 'disassembly is %s' % dis
    print 'Next address to disassemble is: 0x%08x' % nextAddr
    #print b.disassemble(sec, start, stop, funcFmtAddr, funcFmtLine, endian=bfd.ENDIAN_BIG)

    print '\nSupported Architectures:\n'
    print ' '.join(bfd.list_architectures())

    print '\nSupported Targets:\n'
    print ' '.join(bfd.list_targets())

if __name__ == '__main__':
    main()


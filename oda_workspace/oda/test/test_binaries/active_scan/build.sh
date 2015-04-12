#!/bin/sh
# This build script creates two active_scan outputs.  The first is an ELF file
# that is basically the .data section.  The second is a binary file with the
# contents of .data.
gcc -nostdlib -m32 -o active_scan.o active_scan.S
objcopy -O binary -j .data active_scan.o active_scan.bin

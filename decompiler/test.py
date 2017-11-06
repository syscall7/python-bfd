#!/usr/bin/python
import snowman
import binascii
ret = snowman.decompile("/home/anthony/oda/oda_workspace/oda/apps/odaweb/examples/whoami", "xstrdup")

if ret:
    print("Decompilation:\n%s" % ret)
elif ret == '':
    print("Decompliation not supported for this function")

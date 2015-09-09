'''
Created on November 7, 2012

@author: Owner
'''
from oda.libs.odb.bfd.analyzers.arm import arm

class armv4(arm):
    def __init__(self, odb_file):
        arm.__init__(self, odb_file)
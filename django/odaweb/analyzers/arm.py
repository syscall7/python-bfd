'''
Created on November 7, 2012

@author: Owner
'''
import re

from odaweb.analyzers.defaultAnalyzer import defaultAnalyzer
from odaweb.analyzers.instruction import instructionType, callType


class arm(defaultAnalyzer):
    '''
    classdocs
    '''

    def __init__(self):
        defaultAnalyzer.__init__(self)

        self.options = [
            ('Force Thumb Mode', 'Assume all insns are Thumb insns', 'CHOICE', ('DEFAULT','force-thumb', 'no-force-thumb'), False),
            ('Register Names', 'Select register names specified by ATPCS, APCS, ARM ISA, gcc, or raw', 'CHOICE', 
                ('DEFAULT','reg-names-special-atpcs', 'reg-names-atpcs', 'reg-names-apcs', 'reg-names-std', 'reg-names-gcc', 'reg-names-raw'), 'reg-names-gcc'),
        ]


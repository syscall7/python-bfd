'''
Created on November 7, 2012

@author: Owner
'''
import re

from odaweb.analyzers.defaultAnalyzer import defaultAnalyzer
from odaweb.analyzers.instruction import instructionType, callType


class powerpc(defaultAnalyzer):
    '''
    classdocs
    '''

    def __init__(self):
        defaultAnalyzer.__init__(self)

        self.options = [
            ('Mode', 'Processor mode', 'CHOICE', ('DEFAULT', '32', '64'), ''),
            ('CPU', 'CPU variant', 'CHOICE',
                ('DEFAULT', '403', '405', '440', '464', '476', '601', '603', '604',
                 '620', '7400', '7410', '7450', '7455', '750cl', 'a2', 
                 'altivec', 'any', 'booke', 'booke32', 'cell', 'com', 'e300',
                 'e500','e500mc','e500mc64', 'e5500', 'e6500', 'e500x2', 
                 'efs', 'power4', 'power5', 'power6', 'power7', 'ppc', 'ppc32', 
                 'ppc64', 'ppc64bridge', 'ppcps', 'pwr', 'pwr2', 'pwr4', 
                 'pwr5', 'pwr5x', 'pwr6', 'pwr7', 'pwrx', 'spe', 'titan', 
                 'vle', 'vsx'), ''),
        ]

          
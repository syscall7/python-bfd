__author__ = 'anthony'

from abc import ABCMeta

class InstDoc(object):
    __metaclass__ = ABCMeta

    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
        self.short = 'No help available'
        self.long = 'No help available'


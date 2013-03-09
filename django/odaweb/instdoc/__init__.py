__author__ = 'anthony'

from odaweb.instdoc.instdoc import InstDoc
from odaweb.instdoc.i386 import i386

def InstDocFactory(platform, mnemonic):

    # TODO: Raise exception if platform is not i386
    return i386(mnemonic)

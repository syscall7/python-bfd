
#import re


class DisChunk(object):
    MIN_CHUNK_SIZE_BYTES = 50
    def __init__(self, startAddr, endAddr, lines, sec_name, is_boundary=False):
        self.start = startAddr
        self.end = endAddr
        self.lines = lines
        self.sec_name = sec_name
        self.is_boundary = is_boundary

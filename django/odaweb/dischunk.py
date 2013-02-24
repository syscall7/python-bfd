
#import re

from odaweb.models import Comment

class DisChunk(object):
    MIN_CHUNK_SIZE_BYTES = 512
    def __init__(self, startAddr, endAddr, lines, sec_name, is_boundary=False):
        self.start = startAddr
        self.end = endAddr
        self.lines = lines
        self.sec_name = sec_name
        self.is_boundary = is_boundary


    def attach_comments(self, binary):
        comments = Comment.get_for_binary(binary)
        if len(comments) == 0:
            return
        for iu in self.instUnits:
            comments_for_address = filter( lambda c: c.offset == iu.offset, comments )
            if (len(comments_for_address) > 0):
                iu.comment = comments_for_address[0].comment


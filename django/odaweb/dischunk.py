
#import re


class DisChunk(object):
    def __init__(self,name,start):
        self.name = name
        self.start = start
        self.end = start
    def grow(self,size):
        self.end += size
        
class DisSuperChunk(object):
    MIN_SUPER_CHUNK_SIZE_BYTES = 2048
    def __init__(self, start=None, end=0, is_boundary=False):
        self.start = start
        self.end = end
        if start != None:
            self.byte_len = end-start
        else:
            self.byte_len = 0
        self.is_boundary = is_boundary
        self.chunks = {}

    def __len__(self):
        return self.byte_len

    def available_len(self):
        if self.byte_len >= DisSuperChunk.MIN_SUPER_CHUNK_SIZE_BYTES:
            return 0
        else:
            return DisSuperChunk.MIN_SUPER_CHUNK_SIZE_BYTES - self.byte_len

    def grow(self, sec_name, sec_addr, size):
        if self.start == None:
            self.start = sec_addr

        if self.available_len() > size:
            useable_size = size 
        else:
            useable_size = self.available_len()            

        if useable_size > 0:
            # Handle sections
            if sec_name not in self.chunks:
                # Add a new section
                self.chunks[sec_name] = DisChunk(sec_name,sec_addr)
                     
            # Grow the section        
            self.chunks[sec_name].grow(useable_size)
        
            # Grow the chunk
            self.end = sec_addr + useable_size
            self.byte_len += useable_size

        return size - useable_size
        


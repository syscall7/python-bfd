from abc import abstractmethod, abstractproperty, ABCMeta
import commands
import os
import hashlib
import tempfile
import types
from os import unlink
import magic

class Options(object):
    def __init__(self, target, architecture, base_address, selected_opts = []):
        self.target = target
        self.architecture = architecture
        self.base_address = base_address
        self.endian = 'DEFAULT'
        self.selected_opts = selected_opts

    def get_endian(self):
        return self.endian

    def get_extra_options(self):
        if hasattr(self, 'selected_opts'):
            return self.selected_opts

        return []


class Binary(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def file_handle(self):
        pass

    @abstractproperty
    def options(self):
        pass

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def size(self):
        pass

    def md5(self):
        f = self.file_handle()
        md5 = hashlib.md5(f.read()).hexdigest()
        f.close()
        Binary.done(f)
        return md5

    def sha1(self):
        f = self.file_handle()
        sha = hashlib.sha1(f.read()).hexdigest()
        f.close()
        Binary.done(f)
        return sha

    def desc(self):
        if os.name == 'nt':
            line = ''
        else:
            f = self.file_handle()
            with magic.Magic() as m:
                line = m.id_filename(f.name)
            f.close()
            Binary.done(f)

        return line.split(', ')

    @staticmethod
    def done(f):
        try:
            f.done()
        except AttributeError:
            pass


class BinaryFile(Binary):
    def __init__(self, filename, target, architecture):
        self.filename = filename
        self._options = Options(target, architecture, 0)
        self.arch = architecture

    def __str__(self):
        return "BinaryFile file:%s, arch:%s, size:%d" % (
            os.path.basename(self.filename), self.arch, os.path.getsize(self.filename))

    @property
    def options(self):
        return self._options

    @property
    def name(self):
        return os.path.split(self.filename)[-1]

    @property
    def size(self):
        return os.path.getsize(self.filename)

    @options.setter
    def options(self, options):
        self._options = options

    def file_handle(self):
        f = open(self.filename)
        return f


class BinaryString(Binary):
    def __init__(self, binary_string, arch):

        self.byte_array = ''
        self.binary_string = ''.join(binary_string.split())
        self.arch = arch
        self.is_live_mode = True
        self._options = Options('binary', arch, 0)

        # pad out with a 0 if odd length
        if len(self.binary_string) % 2 != 0:
            self.binary_string += '0'

        # this decode may throw TypeError or UnicodeEncodeError
        self.byte_array = self.binary_string.decode("hex")

        self.binary_string_display = ' '.join(['%02X' % ord(c) for c in self.byte_array])

    def __str__(self):
        return "BinaryString arch:%s, len:%d" % (self.arch, len(self.binary_string))

    @property
    def name(self):
        return 'raw'

    @property
    def size(self):
        return len(self.byte_array)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def file_handle(self):
        # Create a file containing the BinaryString for passing to BFD
        #  Must use delete=False because bfd expects a file name
        t = tempfile.NamedTemporaryFile(bufsize=0, delete=False)
        t.write(self.byte_array)

        # Dynamic function that deletes the temp file when we are done with it
        def done(self):
            # Close the file in case it isn't already closed
            self.close()

            # Delete the temporary file permanently
            unlink(self.name)

        # Add the done function dynamically to the File instance
        #f = open(t)
        t.done = types.MethodType(done, t)

        return t
from os import stat, unlink
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import os.path
from datetime import datetime
from utils import sha1_hash
import uuid
import tempfile
import hashlib
import json
import commands
import logging
import types

logger = logging.getLogger(__name__)

# where to store uploaded files on the server's filesystem
fs = FileSystemStorage(location='/tmp/odaweb2')

class OdaMaster(models.Model):
    ''' Complete representation of a disassembled entity '''

    ipAddress = models.CharField(max_length=64, default='')
    project_name = models.CharField(max_length=64, default='')
    short_name = models.CharField(max_length=12, db_index = True)
    revision = models.IntegerField(default=0)
    owner = models.ForeignKey(User, null=True)
    creation_date = models.DateTimeField(auto_now_add = True)
    copy = models.ForeignKey('OdaMaster', null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    binary = generic.GenericForeignKey()

    def file_handle(self):
        return self.content_object.file_handle()

    def next_revision(self):
        revisions = map(lambda m: m.revision, OdaMaster.objects.filter(short_name=self.short_name))
        return max(revisions) + 1

    def latest_revision(self):
        revisions = map(lambda m: m.revision, OdaMaster.objects.filter(short_name=self.short_name))
        return max(revisions)

    def details(self):
        return self.binary.options.target + " " + self.binary.options.architecture

class OdaOptions(models.Model):
    ''' Options that specify how the associated Binary is to be treated '''
    target = models.CharField(max_length=128)
    architecture = models.CharField(max_length=128)
    extra_options = models.CharField(max_length=256, default='{"flags" : [] }')
    base_address = models.CharField(max_length=18)

    def get_options_map(self):
        return json.loads(self.extra_options)

    def get_extra_options(self):
        return self.get_options_map()["flags"]

    def set_extra_options(self, options):
        o = self.get_options_map()
        o["flags"] = options
        self.extra_options = json.dumps(o)

    def reset_extra_options(self):
        self.extra_options = '{ "flags" : [] }'

    def get_endian(self):
        options = self.get_extra_options()
        endian = 'DEFAULT'
        if 'LITTLE' in options:
            endian = 'LITTLE'
        elif 'BIG' in options:
            endian = 'BIG'

        return endian

    def set_endian(self, endian):
        o = self.get_options_map()
        o["endian"] = endian
        self.extra_options = json.dumps(o)

class Binary(models.Model):
    ''' Parent class of BinaryFile and BinaryString containing the data of a single disassembled entity'''
    options = models.OneToOneField(OdaOptions, null=True)

    def md5(self):
        f = self.file_handle()
        f.open('rb')
        md5 = hashlib.md5(f.read()).hexdigest()
        f.close()
        f.done()
        return md5

    def sha1(self):
        f = self.file_handle()
        f.open('rb')
        md5 = hashlib.sha1(f.read()).hexdigest()
        f.close()
        f.done()
        return md5

    def desc(self):
        if os.name == 'nt':
            line = ''
        else:
            f = self.file_handle()
            line = commands.getoutput('file -b %s' % f.name)
            f.close()
            f.done()
        return line.split(', ')

    class Meta:
        abstract = True

class BinaryString(Binary):
    ''' Represents a disassembled binary that was entered as a string of hex characters via Live View'''
    binary_string = models.TextField()

    def file_handle(self):
        if len(self.binary_string) % 2 == 1:
            self.binary_string += '0'

        try:
            byte_array = self.binary_string.decode("hex")
        except TypeError:
            logger.exception("Failed to decode hex %s" % self.binary_string)

        # Create a file containing the BinaryString for passing to BFD
        #  Must use delete=False because bfd expects a file name
        t = tempfile.NamedTemporaryFile(bufsize = 0, delete = False)
        t.write(byte_array)

        # Dynamic function that deletes the temp file when we are done with it
        def done(self):
            # Close the file in case it isn't already closed
            self.close()

            # Delete the temporary file permanently
            unlink(self.name)

        # Add the done function dynamically to the File instance
        f = File(t)
        f.done = types.MethodType(done, f)

        return f

    def name(self):
        return 'Live Mode'

    def size(self):
        return len(self.binary_string) / 2

    def is_live_mode(self):
        return True

    def binary_string_display(self):
        return " ".join(self.binary_string[i:i+2] for i in range(0, len(self.binary_string), 2))

class BinaryFile(Binary):
    ''' Represents a disassembled entity that was uploaded as a file '''
    the_file = models.FileField(storage=fs, upload_to="uploads")
    filename = models.CharField(max_length=255)
    filesize = models.IntegerField()
    hash = models.CharField(max_length=128)

    def file_handle(self):

        # Add done function to the BinaryFile file object
        def done(self):
            # BinaryFiles need to exist indefinitely. Nothing to do here
            pass

        self.the_file.file.done = types.MethodType(done, self.the_file.file)
        return self.the_file.file

    def name(self):
        return self.filename

    def size(self):
        return self.filesize

    def create(f, options):
        u = BinaryFile()
        u.the_file = File(f)
        filename = u.the_file.name
        u.filename = os.path.basename(filename)
        u.filesize = u.the_file.size
        u.the_file.open('rb')
        u.hash = sha1_hash(u.the_file)
        u.options = options
        return u

    def is_live_mode(self):
        return False

    create = staticmethod(create)

class BinaryFeature(models.Model):
    ''' Represents a stored feature of a Binary '''
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    binary = generic.GenericForeignKey()

    @classmethod
    def get_for_binary(cls, binary):
        ctype = ContentType.objects.get_for_model(binary)
        return cls.objects.filter(content_type=ctype.id, object_id = binary.id)

    class Meta:
        abstract = True

class BinaryAddressFeature(BinaryFeature):
    ''' Represents a stored feature of a Binary, unique to a certain address '''
    offset = models.BigIntegerField()

    class Meta:
        abstract = True
        unique_together = ('offset', 'content_type', 'object_id')

class Comment(BinaryAddressFeature):
    ''' Comment on a line of disassembly '''
    comment = models.CharField(max_length=255)

class Function(BinaryAddressFeature):
    ''' Describes a disassembled function '''
    name = models.CharField(max_length=255)
    retval = models.CharField(max_length=255, default='unknown')
    args = models.CharField(max_length=255, default='unknown')

class Label(BinaryAddressFeature):
    ''' Describes a local label '''
    label = models.CharField(max_length=255)

class Symbol(BinaryAddressFeature):
    ''' Symbol of a function or chunk of data '''
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=1)

class BinaryParcel(BinaryFeature):
    ''' Represents a contiguous chunk of code or a single data '''
    start = models.BigIntegerField()
    end = models.BigIntegerField()
    is_code = models.NullBooleanField()

    class Meta:
        ordering = ['start']

class Xref(models.Model):
    ''' Reference to a symbol '''

    # location that references the symbol
    address = models.BigIntegerField()

    # symbol that is referenced
    symbol = models.ForeignKey(Symbol, related_name='xrefs_set')

    class Meta:
        unique_together = ('address', 'symbol')

class InstDoc(models.Model):
    ''' Help for an assembly instruction '''
    platform = models.TextField()
    mnemonic = models.TextField()
    short = models.TextField()
    long = models.TextField()


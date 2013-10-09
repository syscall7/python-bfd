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


fs = FileSystemStorage(location='/tmp/odaweb2')

# Create your models here.
class OdaFile(models.Model):
    the_file = models.FileField(storage=fs, upload_to="uploads")
    filename = models.CharField(max_length=255)
    filesize = models.IntegerField()
    hash = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    uuid = models.CharField(max_length=64)
    ipAddress = models.CharField(max_length=64, default='')
    creation_date = models.DateTimeField(auto_now_add = True)
    
    def generate_values(self):
        print((self.the_file.open('rb')))
        filename = self.the_file.name
        self.filename = os.path.basename(filename)
        self.filesize = self.the_file.size
        self.the_file.open('rb')
        self.hash = sha1_hash(self.the_file)
        self.creation_date = datetime.now()
        self.uuid = str(uuid.uuid4())

    @staticmethod
    def create(f, ip_address=''):
        u = OdaFile()
        u.ipAddress = ip_address
        u.the_file = File(f)  
        u.generate_values()
        return u; 
    
    def file_handle(self):
        return self.the_file.file

    @staticmethod
    def get_by_user(user):
        return OdaMaster.objects.filter(owner=user)


## TODO: Used by views.py. Delete when views.py is obsoleted
#class DisassemblyChunk(models.Model):
#    odafile = models.ForeignKey(OdaFile)
#
#    # TODO: Is this length too much? Not enough?    
#    #sec_name = models.CharField(max_length=128)
#    start = models.IntegerField()
#    end = models.IntegerField()
#    is_boundary = models.BooleanField()
#    class Meta:
#        ordering = ['start']

class OdaOptions(models.Model):
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

class BinaryDisassemblySuperChunk(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    binary = generic.GenericForeignKey()

    # TODO: Is this length too much? Not enough?
    start = models.BigIntegerField()
    end = models.BigIntegerField()
    is_boundary = models.BooleanField()
    class Meta:
        ordering = ['start']

    def chunks(self):
        chunks_temp = BinaryDisassemblyChunk.objects.filter(
            superchunk_id = self.id )
        return list(chunks_temp)

    def attach_comments(self, binary):
        comments = Comment.get_for_binary(binary)
        if len(comments) == 0:
            return
        for iu in self.instUnits:
            comments_for_address = filter( lambda c: c.offset == iu.offset, comments )
            if (len(comments_for_address) > 0):
                iu.comment = comments_for_address[0].comment

    @staticmethod
    def get_for_binary(binary):
        ctype = ContentType.objects.get_for_model(binary)
        return BinaryDisassemblySuperChunk.objects.filter(content_type=ctype.id, object_id = binary.id)


class BinaryDisassemblyChunk(models.Model):
    superchunk = models.ForeignKey(BinaryDisassemblySuperChunk)
    
    name = models.CharField(max_length=128)
    start = models.BigIntegerField()
    end = models.BigIntegerField()
    class Meta:
        ordering = ['start']
        

# TODO: Used by views.py. Delete when views.py is obsoleted
#class DisassemblyComment(models.Model):
#    chunk = models.ForeignKey(DisassemblyChunk)
#    comment_str = models.CharField(max_length=128)
#    offset = models.IntegerField()
#    class Meta:
#        ordering = ['offset']
class BinaryString(Binary):
    binary_string = models.TextField()
    
    def file_handle(self):
        if len(self.binary_string) % 2 == 1:
            self.binary_string += '0'

        try:
            byte_array = self.binary_string.decode("hex")
        except TypeError:
            logger.exception("Failed to decode hex")
        
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

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    binary = generic.GenericForeignKey()
    comment = models.CharField(max_length=255)
    offset = models.BigIntegerField()

    @staticmethod
    def get_for_binary(binary):
        ctype = ContentType.objects.get_for_model(binary)
        return Comment.objects.filter(content_type=ctype.id, object_id = binary.id)


class BinaryFile(Binary):
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

class OdaMaster(models.Model):

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


class InstDoc(models.Model):
    platform = models.TextField()
    mnemonic = models.TextField()
    short = models.TextField()
    long = models.TextField()


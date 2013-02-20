from os import stat
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import os.path
from datetime import datetime
from utils import sha1_hash
import uuid
import tempfile

fs = FileSystemStorage(location='/tmp/odaweb')

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
        
    def create(f, ip_address=''):
        u = OdaFile()
        u.ipAddress = ip_address
        u.the_file = File(f)  
        u.generate_values()
        return u; 
    
    def file_handle(self):
        return self.the_file.file

    create = staticmethod(create)

class DisassemblyChunk(models.Model):
    odafile = models.ForeignKey(OdaFile)

    # TODO: Is this length too much? Not enough?    
    sec_name = models.CharField(max_length=128)
    start = models.IntegerField()
    end = models.IntegerField()
    bfd_lines = models.IntegerField()
    is_boundary = models.BooleanField()
    class Meta:
        ordering = ['start', 'sec_name']




class OdaOptions(models.Model):
    target = models.CharField(max_length=128)
    architecture = models.CharField(max_length=128)

class Binary(models.Model):
    options = models.OneToOneField(OdaOptions, null=True)

    class Meta:
        abstract = True

class BinaryDisassemblyChunk(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    binary = generic.GenericForeignKey()

    # TODO: Is this length too much? Not enough?
    sec_name = models.CharField(max_length=128)
    start = models.IntegerField()
    end = models.IntegerField()
    bfd_lines = models.IntegerField()
    is_boundary = models.BooleanField()
    class Meta:
        ordering = ['start', 'sec_name']


class DisassemblyComment(models.Model):
    chunk = models.ForeignKey(DisassemblyChunk)
    comment_str = models.CharField(max_length=128)
    offset = models.IntegerField()
    class Meta:
        ordering = ['offset']

class BinaryString(Binary):
    binary_string = models.TextField()

    def file_handle(self):

        if len(self.binary_string) % 2 == 1:
            self.binary_string += '0'
        byte_array = self.binary_string.decode("hex")
        t = tempfile.NamedTemporaryFile(bufsize = 0, delete = False)
        t.write(byte_array)

        return File(t)

    def name(self):
        return 'hex string'

    def size(self):
        return len(self.binary_string)/2


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    binary = generic.GenericForeignKey()
    comment = models.CharField(max_length=255)
    offset = models.IntegerField()

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

    create = staticmethod(create)

class OdaMaster(models.Model):

    ipAddress = models.CharField(max_length=64, default='')
    short_name = models.CharField(max_length=12, db_index = True, unique = True)
    creation_date = models.DateTimeField(auto_now_add = True)
    copy = models.ForeignKey('OdaMaster', null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    binary = generic.GenericForeignKey()

    def file_handle(self):
        return self.content_object.file_handle()


        
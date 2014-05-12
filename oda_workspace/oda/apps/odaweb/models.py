from os import unlink
import os.path
import tempfile
import hashlib
import json
import commands
import logging
import types
import cPickle

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from oda.libs.odb.odb_file import DefaultOdbSerializer

from utils import sha1_hash


logger = logging.getLogger(__name__)

# where to store uploaded files on the server's filesystem
# fs = FileSystemStorage(location=settings.UPLOAD_LOCATION)

class OdaMaster(models.Model):
    ''' Complete representation of a disassembled entity '''

    ipAddress = models.CharField(max_length=64, default='')
    project_name = models.CharField(max_length=64, default='')
    short_name = models.CharField(max_length=12, db_index=True)
    revision = models.IntegerField(default=0)
    owner = models.ForeignKey(User, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    copy = models.ForeignKey('OdaMaster', null=True)
    odb_file = models.BinaryField(blank=False)


    @property
    def object_id(self):
        return 0

    @property
    def content_id(self):
        return 0

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

    def odb(self):
        return DefaultOdbSerializer().load(self.odb_file)


# this is where we'll cache the GoogleStorage files locally
LOCAL_CACHE_DIR=os.path.join(settings.MEDIA_ROOT, 'cache')

class BinaryFile(models.Model):
    ''' Represents a disassembled entity that was uploaded as a file '''
    the_file = models.FileField(upload_to="uploads")
    filename = models.CharField(max_length=255)
    filesize = models.IntegerField()
    hash = models.CharField(max_length=128)
    local_path = None

    target = models.CharField(max_length=128)
    architecture = models.CharField(max_length=128)
    extra_options = models.CharField(max_length=256, default='{"flags" : [] }')
    base_address = models.CharField(max_length=18)


    def file_handle(self):

        # Add done function to the BinaryFile file object
        def done(self):
            # BinaryFiles need to exist indefinitely. Nothing to do here
            pass

        # if we haven't written the file locally yet
        if not self.local_path:
            self.local_path = os.path.join(LOCAL_CACHE_DIR, self.hash)

            # if the file does not exist locally
            if not os.path.exists(self.local_path):

                # write it out
                with open(self.local_path, 'wb') as f:
                    self.the_file.open('rb')
                    f.write(self.the_file.read())
                    self.the_file.close()

        # return a reference to the local copy
        f = File(open(self.local_path))
        f.done = types.MethodType(done, f)
        return f

    def name(self):
        return self.filename

    def size(self):
        return self.filesize

    def create(f):
        u = BinaryFile()
        u.filename = f.name
        f.open('rb')
        u.hash = sha1_hash(f)
        f.close()
        f.name = u.hash

        u.the_file = File(f)
        u.the_file.open('rb')
        u.filesize = u.the_file.size

        u.target = ''
        u.architecture = ''

        return u

    def is_live_mode(self):
        return False

    def desc(self):
        if os.name == 'nt':
            line = ''
        else:
            f = self.file_handle()
            #this is a security hazard? f.name = ;rm -rf *
            line = commands.getoutput('file -b %s' % f.name)
            f.close()
            f.done()
        return line.split(', ')

    create = staticmethod(create)

class InstDoc(models.Model):
    ''' Help for an assembly instruction '''
    platform = models.TextField()
    mnemonic = models.TextField()
    short = models.TextField()
    long = models.TextField()


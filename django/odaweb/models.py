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

from utils import sha1_hash


logger = logging.getLogger(__name__)

# where to store uploaded files on the server's filesystem
fs = FileSystemStorage(location=settings.UPLOAD_LOCATION)

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

class InstDoc(models.Model):
    ''' Help for an assembly instruction '''
    platform = models.TextField()
    mnemonic = models.TextField()
    short = models.TextField()
    long = models.TextField()


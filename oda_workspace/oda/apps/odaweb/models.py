import os.path
import commands
import logging
import types

from django.db import models
from django.core.files import File
from django.contrib.auth.models import User
from django.conf import settings
from oda.libs.odb.binaries import Options, Binary

from oda.libs.odb.odb_file import DefaultOdbSerializer
from utils import sha1_hash, sha1_hash_contents


logger = logging.getLogger(__name__)

# where to store uploaded files on the server's filesystem
# fs = FileSystemStorage(location=settings.UPLOAD_LOCATION)

class SandboxServer(models.Model):
    ''' Represents a sandbox server instance '''
    ip = models.CharField(max_length=255)
    port = models.IntegerField()

class SandboxJob(models.Model):
    ''' Represents a sandbox job '''
    server = models.ForeignKey(SandboxServer, null=True)
    task_id = models.IntegerField()

    # use to track whether or not we've reloaded the odb file after running the job
    reloaded = models.BooleanField(default=False)

class OdbFileLoader(object):
    def load_odb_file(self, oda_master):
        logger.info("load_odb_file odb_master:%s" % (oda_master.id))
        return DefaultOdbSerializer().load(oda_master.odb_file_storage.pickled_odb_file)

    def store_odb_file(self, oda_master, odb_file):
        logger.info("store_odb_file odb_master:%s %s" % (oda_master.id, type(odb_file.binary)))


        odb_file_storage = oda_master.odb_file_storage
        if odb_file_storage is None:
            odb_file_storage = OdbFileStorage()

        odb_file_storage.pickled_odb_file = DefaultOdbSerializer().dumps(odb_file)

        if isinstance(odb_file.binary, BinaryFileModel):
            logger.info("uses binary_file_id: %d" % (odb_file.binary.binary_file_id))
            odb_file_storage.binary_file_id = odb_file.binary.binary_file_id

        odb_file_storage.save()
        oda_master.odb_file_storage = odb_file_storage
        oda_master.save()

odb_file_system = OdbFileLoader()

# this is where we'll cache the GoogleStorage files locally
LOCAL_CACHE_DIR=os.path.join(settings.MEDIA_ROOT, 'cache')

class BinaryFileModel(Binary):
    def __init__(self, id):
        self.binary_file_id = id
        self._options = BinaryFile.objects.get(id=self.binary_file_id).options

    def file_handle(self):
        return BinaryFile.objects.get(id=self.binary_file_id).file_handle()

    @property
    def options(self):
        return self._options

    @property
    def name(self):
        return os.path.split(BinaryFile.objects.get(id=self.binary_file_id).filename)[-1]

    @property
    def size(self):
        BinaryFile.objects.get(id=self.binary_file_id).size


    @options.setter
    def options(self, options):
        binary_file = BinaryFile.objects.get(id=self.binary_file_id)
        binary_file.target = options.target
        binary_file.architecture = options.architecture
        binary_file.extra_options = options.get_extra_options()
        binary_file.base_address = options.base_address
        binary_file.save()
        self._options = binary_file.options
        logger.info("Setting Options...")


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

    @property
    def options(self):
        return Options(self.target, self.architecture, self.base_address, self.extra_options)


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

    def create_from_byte_array(filename, path,  data):
        u = BinaryFile()
        u.filename = filename
        u.hash = sha1_hash_contents(data)

        u.the_file = path
        u.filesize = len(data)

        return u

    def create(f):
        u = BinaryFile()
        u.filename = f.name
        u.hash = sha1_hash(f)

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

    create_from_byte_array = staticmethod(create_from_byte_array)
    create = staticmethod(create)

class OdbFileStorage(models.Model):
    binary_file = models.ForeignKey(BinaryFile, null=True)
    pickled_odb_file = models.BinaryField(blank=False)

class OdaMaster(models.Model):
    ''' Complete representation of a disassembled entity '''

    ipAddress = models.CharField(max_length=64, default='')
    project_name = models.CharField(max_length=64, default='')
    short_name = models.CharField(max_length=12, db_index=True)
    revision = models.IntegerField(default=0)
    owner = models.ForeignKey(User, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    copy = models.ForeignKey('OdaMaster', null=True)

    sandbox_job = models.ForeignKey(SandboxJob, null=True)

    odb_file_storage = models.ForeignKey(OdbFileStorage, null=True)

    @property
    def object_id(self):
        return 0

    @property
    def content_id(self):
        return 0

    @property
    def odb_file(self):
        return odb_file_system.load_odb_file(self)

    @odb_file.setter
    def odb_file(self, val):
        odb_file_system.store_odb_file(self, val)


    def file_handle(self):
        return self.content_object.file_handle()

    def next_revision(self):
        revisions = map(lambda m: m.revision, OdaMaster.objects.filter(short_name=self.short_name))
        return max(revisions) + 1

    def latest_revision(self):
        revisions = map(lambda m: m.revision, OdaMaster.objects.filter(short_name=self.short_name))
        return max(revisions)

    def details(self):
        return self.odb_file.get_options().target + " " + self.odb_file.get_options().architecture


class InstDoc(models.Model):
    ''' Help for an assembly instruction '''
    platform = models.TextField()
    mnemonic = models.TextField()
    short = models.TextField()
    long = models.TextField()

class Share(models.Model):
    odaMaster = models.ForeignKey(OdaMaster, null=False)
    name = models.CharField(db_index=True, max_length=16)
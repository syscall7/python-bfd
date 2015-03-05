from sets import Set
import traceback
import bfd
from django.core.management.base import BaseCommand

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

from boto.gs.connection import GSConnection
from oda.apps.odaweb.models import OdaMaster, BinaryFileModel, BinaryFile, OdbFileStorage, BinaryOptions
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation

import collections

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return None

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

metadata = MetaData()


oda_masters = Table('odaweb_odamaster', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('project_name', String),
                     Column('short_name', String),
                     Column('content_type_id', Integer),
                     Column('object_id', None, ForeignKey('odaweb_binaryfile.id')),
                     Column('creation_date', Date),
                     Column('ipAddress', String))


binaries = Table('odaweb_binaryfile', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('the_file', String),
                 Column('filename', String),
                 Column('options_id', None, ForeignKey('odaweb_odaoptions.id')),
                 Column('hash', String))

strings = Table('odaweb_binarystring', metadata,
                Column('id', String, primary_key=True),
                Column('options_id', None, ForeignKey('odaweb_odaoptions.id')),
                Column('binary_string', String))

oda_options = Table('odaweb_odaoptions', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('target', String),
                    Column('architecture', String),
                    Column('extra_options', String))

content_types = Table('django_content_type', metadata,
    Column('id', Integer, primary_key=True),
    Column('model', String),
    Column('name', String))

class Migrator(object):
    def __init__(self):
        connection = GSConnection('GOOGVILB3OU772HKZS7J', 'rqXIOK8TSSPP4XJ991edCsgIf+3eT/NFE/VJf5ZN')
        self.bucket = connection.get_bucket('oda', validate=True)

        self.number_processed = 0

        self.odb_file_cache = LRUCache(500)

    def migrate_row(self, row):

        self.number_processed += 1

        print("%d: (%s) (Architecture %s) (target: %s) " % (self.number_processed, row.short_name, row.architecture, row.target))

        #print("  file: %s" % (str(file_object)))

        oda_master = OdaMaster(short_name=row.short_name, project_name=row.project_name,
                               ipAddress=row.ipAddress)
        #the_file = file_object.read()
        options = BinaryOptions(architecture=row.architecture, target=row.target, extra_options=row.extra_options)
        options.save()

        binary_file = BinaryFile(the_file=row.the_file, hash=row.hash, filename=row.filename,
                                 filesize=0, binary_options=options)
        binary_file.save()
        #binary_file = BinaryFile.create_from_byte_array('uploads/' + row.hash, row.the_file, the_file)
        odb_file_storage = OdbFileStorage(binary_file=binary_file)
        odb_file_storage.save()

        oda_master.odb_file_storage = odb_file_storage
        oda_master.save()


        return


    def create_query(self, db_url, type="binaryfile"):
        print("Connecting: %s" % db_url)

        engine = create_engine(db_url, pool_recycle=3600)

        Session = sessionmaker()
        Session.configure(bind=engine)  # once engine is available
        session = Session()

        content_id = session.query(content_types).filter(content_types.c.model == type).first().id

        query = session.query(oda_masters, binaries, oda_options).join(binaries).join(oda_options).filter(oda_masters.c.content_type_id == content_id)

        return query

    def migrate_binary_files(self, db_url = "mysql://root:password@localhost/odapython2"):

        query = self.create_query(db_url, 'binaryfile')

        for row in query:
            existing = OdaMaster.objects.filter(short_name=row.short_name).count()
            if existing > 0:
                print("Master Exists %s" % (row.short_name))
                continue

            self.migrate_row(row)

    def migrate_binary_strings(self, db_url = "mysql://root:password@localhost/odapython2"):
        query = self.create_query(db_url, 'binaryfile')

        for row in query:
            existing = OdaMaster.objects.filter(short_name=row.short_name).count()
            if existing > 0:
                print("Master Exists %s" % (row.short_name))
                continue

            self.migrate_row(row)


    def unused(self, row):
        binary_file = []
        file_object = self.bucket.get_key('uploads/' + row.hash)

        if file_object:
            print("%s: Project Name: %s, ipAddress: %s, short_name: %s, creation_date: %s, the_file: %s" % (
                str(self.number_processed), row.project_name, row.ipAddress, row.short_name, row.creation_date, row.the_file
            ))


            the_filename = "/var/oda/uploads/%s" % (row.hash)
            f = open(the_filename, 'w+')
            f.write(the_file)
            f.close()

            binary_file.target = row.target
            binary_file.architecture = row.architecture
            binary_file.save()

            cached_value = self.odb_file_cache.get(row.hash)
            if cached_value is not None:
                print ("Using Cached Value: %s: %s" % (row.hash, row.short_name))
                cached_value.binary = BinaryFileModel(binary_file.id)
                oda_master.odb_file = cached_value
                oda_master.save()
            else:
                try:
                    odb_file = OdbFile(BinaryFileModel(binary_file.id))
                    odb_file.execute(LoadOperation())
                    odb_file.execute(PassiveScanOperation())

                    oda_master.odb_file = odb_file
                    self.odb_file_cache.set(row.hash, odb_file)
                    oda_master.save()
                except bfd.BfdFileFormatException as e:
                    traceback.print_exc()
                    print("Error")
                except AssertionError as e:
                    traceback.print_exc()
                    print("Error")


                print("  new hash: %s" % binary_file.hash)


class Command(BaseCommand):
    args = '<url>'
    help = 'Setup ODA'

    def handle(self, *args, **options):
        Migrator().migrate_binary_files(args[0])
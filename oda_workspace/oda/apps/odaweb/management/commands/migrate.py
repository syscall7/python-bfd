import traceback
from django.core.management.base import BaseCommand

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

from boto.gs.connection import GSConnection
from oda.apps.odaweb.models import OdaMaster, BinaryFileModel, BinaryFile
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

def migrate(db_url = "mysql://root:password@localhost/odapython2"):
    print("Connecting: %s" % db_url)

    engine = create_engine(db_url, pool_recycle=3600)
    conn = engine.connect()

    connection = GSConnection('GOOGVILB3OU772HKZS7J', 'rqXIOK8TSSPP4XJ991edCsgIf+3eT/NFE/VJf5ZN')
    bucket = connection.get_bucket('oda', validate=True)

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

    oda_options = Table('odaweb_odaoptions', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('target', String),
                        Column('architecture', String))

    Session = sessionmaker()
    Session.configure(bind=engine)  # once engine is available
    session = Session()

    #s = select([oda_masters, binaries]).select_from(oda_masters.join(binaries)).where(oda_masters.c.content_type_id == 19)
    #result = conn.execute(s)
    #row = result.fetchone()

    query = session.query(oda_masters, binaries, oda_options).join(binaries).join(oda_options).filter(oda_masters.c.content_type_id == 19)

    #import os
    #if not os.path.exists('uploads'):
    #    os.makedirs('uploads')

    skipped_ids = [ 'ETFIPt' ]

    odb_file_cache = LRUCache(500)

    for row in query:
        file_object = bucket.get_key('uploads/' + row.hash)

        if file_object:
            print("Project Name: %s, ipAddress: %s, short_name: %s, creation_date: %s, the_file: %s" % (
                row.project_name, row.ipAddress, row.short_name, row.creation_date, row.the_file
            ))
            print("  Architecture %s, target: %s" % (row.architecture, row.target))

            print("  file: %s" % (str(file_object)))

            if row.short_name in skipped_ids:
                print('Skipping %s' % (row.short_name))
                continue

            existing_master = OdaMaster.objects.filter(short_name=row.short_name).first()
            if existing_master:
                print("Master Exists %s" % (row.short_name))
                continue

            oda_master = OdaMaster(short_name=row.short_name, project_name=row.project_name,
                                   ipAddress=row.ipAddress)
            the_file = file_object.read()
            binary_file = BinaryFile.create_from_byte_array(row.filename, row.the_file, the_file)

            the_filename = "/var/oda/uploads/%s" % (row.hash)
            f = open(the_filename, 'w+')
            f.write(the_file)
            f.close()

            binary_file.target = row.target
            binary_file.architecture = row.architecture
            binary_file.save()

            cached_value = odb_file_cache.get(row.hash)
            if cached_value is not None:
                print ("Using Cached Value: %s: %s" % row.hash, row.short_name)
                cached_value.binary = binary_file
                oda_master.odb_file = cached_value
                oda_master.save()
            else:
                try:
                    odb_file = OdbFile(BinaryFileModel(binary_file.id))
                    odb_file.execute(LoadOperation())
                    odb_file.execute(PassiveScanOperation())

                    oda_master.odb_file = odb_file
                    odb_file_cache.set(row.hash, odb_file)
                    oda_master.save()
                except:
                    traceback.print_exc()
                    print("Error")


                print("  new hash: %s" % binary_file.hash)

class Command(BaseCommand):
    args = '<url>'
    help = 'Setup ODA'

    def handle(self, *args, **options):
        migrate(args[0])
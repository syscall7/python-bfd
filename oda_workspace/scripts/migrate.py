#from django.db import connection

#cursor = connection.cursor()

#cursor.execute('SELECT m.project_name, m.short_name, m.object_id, b.the_file, b.hash, b.filename FROM odaweb_odamaster m INNER JOIN odaweb_binaryfile b ON m.object_id = b.id WHERE content_type_id = 19')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

from boto.gs.connection import GSConnection
from boto.gs.key import Key
from oda.apps.odaweb.models import OdaMaster, BinaryFileModel, BinaryFile
from oda.libs.odb.odb_file import OdbFile

engine = create_engine("mysql://root:password@localhost/odapython2", pool_recycle=3600)
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

import os
if not os.path.exists('uploads'):
    os.makedirs('uploads')

for row in query:
    file_object = bucket.get_key('uploads/' + row.hash)

    if file_object:
        print "Project Name: %s, ipAddress: %s, short_name: %s, creation_date: %s, the_file: %s" % (
            row.project_name, row.ipAddress, row.short_name, row.creation_date, row.the_file
        )
        print "  Architecture %s, target: %s" % (row.architecture, row.target)

        print "  file: %s" % (str(file_object))




        oda_master = OdaMaster(short_name=row.short_name, project_name=row.project_name,
                               ipAddress=row.ipAddress)
        binary_file = BinaryFile.create_from_byte_array(row.filename, row.the_file, file_object.read())
        binary_file.target = row.target
        binary_file.architecture = row.architecture
        binary_file.save()
        odb_file = OdbFile(BinaryFileModel(binary_file.id))
        oda_master.odb_file = odb_file
        oda_master.save()





desc = cursor.description
for row in cursor:
    m = dict(zip([col[0] for col in desc], row))
    print m
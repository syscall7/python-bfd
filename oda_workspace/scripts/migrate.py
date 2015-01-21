from django.db import connection

cursor = connection.cursor()

cursor.execute('SELECT m.project_name, m.short_name, m.object_id, b.the_file, b.hash, b.filename FROM odaweb_odamaster m INNER JOIN odaweb_binaryfile b ON m.object_id = b.id WHERE content_type_id = 19')

from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

from boto.gs.connection import GSConnection
from boto.gs.key import Key

engine = create_engine("mysql://root:password@localhost/odapython2", pool_recycle=3600)
conn = engine.connect()

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
                 Column('hash', String))

s = select([oda_masters, binaries]).select_from(oda_masters.join(binaries)).where(oda_masters.c.content_type_id == 19)

result = conn.execute(s)

connection = GSConnection('GOOGVILB3OU772HKZS7J', 'rqXIOK8TSSPP4XJ991edCsgIf+3eT/NFE/VJf5ZN')
bucket = connection.get_bucket('oda', validate=True)

row = result.fetchone()
for row in conn.execute(s):
    print row
    a = bucket.get_key('uploads/' + row[binaries.c.hash])
    print a


desc = cursor.description
for row in cursor:
    m = dict(zip([col[0] for col in desc], row))
    print m
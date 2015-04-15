import traceback
import bfd
from django.core.management.base import BaseCommand

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

from boto.gs.connection import GSConnection
from oda.apps.odaweb.models import BinaryFileModel
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation

metadata_binaries = MetaData()
metadata_strings = MetaData()

oda_master_files = Table('odaweb_odamaster', metadata_binaries,
                     Column('id', Integer, primary_key=True),
                     Column('project_name', String),
                     Column('short_name', String),
                     Column('content_type_id', Integer),
                     Column('object_id', None, ForeignKey('odaweb_binaryfile.id')),
                     Column('owner_id', Integer),
                     Column('creation_date', Date),
                     Column('ipAddress', String))

binaries = Table('odaweb_binaryfile', metadata_binaries,
                 Column('id', Integer, primary_key=True),
                 Column('the_file', String),
                 Column('filename', String),
                 Column('filesize', Integer),
                 Column('options_id', None, ForeignKey('odaweb_odaoptions.id')),
                 Column('hash', String))

oda_master_strings = Table('odaweb_odamaster', metadata_strings,
                     Column('id', Integer, primary_key=True),
                     Column('project_name', String),
                     Column('short_name', String),
                     Column('content_type_id', Integer),
                     Column('object_id', None, ForeignKey('odaweb_binarystring.id')),
                     Column('creation_date', Date),
                     Column('owner_id', Integer),
                     Column('ipAddress', String))

strings = Table('odaweb_binarystring', metadata_strings,
                Column('id', String, primary_key=True),
                Column('options_id', None, ForeignKey('odaweb_odaoptions.id')),
                Column('binary_string', String))

oda_options_strings = Table('odaweb_odaoptions', metadata_strings,
                    Column('id', Integer, primary_key=True),
                    Column('target', String),
                    Column('architecture', String),
                    Column('extra_options', String))

oda_options_binaries = Table('odaweb_odaoptions', metadata_binaries,
                    Column('id', Integer, primary_key=True),
                    Column('target', String),
                    Column('architecture', String),
                    Column('extra_options', String))

content_types = Table('django_content_type', metadata_binaries,
    Column('id', Integer, primary_key=True),
    Column('model', String),
    Column('name', String))

class Migrator(object):
    def __init__(self):
        connection = GSConnection('GOOGVILB3OU772HKZS7J', 'rqXIOK8TSSPP4XJ991edCsgIf+3eT/NFE/VJf5ZN')
        self.bucket = connection.get_bucket('oda', validate=True)

        self.number_processed = 0

    def create_session(self, db_url):
        print("Connecting: %s" % db_url)

        engine = create_engine(db_url, pool_recycle=3600)

        Session = sessionmaker()
        Session.configure(bind=engine)  # once engine is available
        session = Session()

        return session

    def find_match(self, query_results, terms):
        matches = []
        for row in query_results:
            match = True
            for term in terms:
                if term[1] not in getattr(row, term[0]):
                    match = False
                    break
            if match:
                matches.append(row)

        return matches

    def find_binary_files(self, terms, db_url = "mysql://root:password@127.0.0.1:1234/odapython2"):

        session = self.create_session(db_url)
        content_id = session.query(content_types).filter(content_types.c.model == 'binaryfile').first().id
        query = session.query(oda_master_files, binaries, oda_options_binaries).join(binaries).join(oda_options_binaries).filter(oda_master_files.c.content_type_id == content_id)
        print 'Searching through %d binary file records' % query.count()
        matches = self.find_match(query, terms)
        print '%d matches found:' % len(matches)
        print '--------------------------------------------------------------------------------'
        for match in matches:
            print match


    def find_binary_strings(self, terms, db_url = "mysql://root:password@127.0.0.1:1234/odapython2"):
        session = self.create_session(db_url)
        content_id = session.query(content_types).filter(content_types.c.model == 'binarystring').first().id
        query = session.query(oda_master_strings, strings, oda_options_strings).join(strings).join(oda_options_strings).filter(oda_master_strings.c.content_type_id == content_id)
        print 'Searching through %d binary string records' % query.count()
        matches = self.find_match(query, terms)
        print '%d matches found:' % len(matches)
        print '--------------------------------------------------------------------------------'
        for match in matches:
            print match

class Command(BaseCommand):
    args = 'search1=term1 search2=term2 ...'
    help = 'Example: ./migrate.py find architecture=mips target=pe'

    def handle(self, *args, **options):
        search_terms = []
        for arg in args:
            search_terms.append(arg.split('='))

        print "Searching for the following terms %s" % search_terms
        Migrator().find_binary_files(search_terms)
        #Migrator().find_binary_strings(search_terms)

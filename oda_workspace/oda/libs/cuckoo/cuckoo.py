import datetime
import hashlib
import logging
from oda.libs.cuckoo import api

from oda.apps.odaweb.models import BinaryFile, BinaryFileModel
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation

logger = logging.getLogger(__name__)

# TODO: Persist this info in the database in case we have to restart the server
jobs = {}

def submit_job(oda_master):
    # submit a new job to the Cuckoo server and get the job ID
    job = CuckooJob(oda_master)
    jobs[str(job.id)] = job
    return job

def get_job(job_id):
    return jobs[job_id]


class CuckooJob(object):

    def __init__(self, oda_master):
        self.oda_master = oda_master

        # use to track whether or not we've reloaded the odb file after running the job
        self.reloaded = False

        self.name = oda_master.odb_file.binary.name

        self.started = datetime.datetime.now()
        self.elapsed_seconds = 0

        # TODO: Select the server instance from a set of available cuckoo servers
        self.server = api.CuckooServer('localhost', 8090)

        # submit the job
        self.submit()

        # create unique string to identify this cuckoo job
        unique = '{time}{ip}{port}{task}'.format(
                    time=self.started,
                    ip=self.server.ip,
                    port=self.server.port,
                    task=self.task_id)
        self.id = hashlib.sha256(unique).hexdigest()

    def submit(self):
        logger.info('submitting cuckoo job for file %s' % self.name)
        self.task_id = api.submit_task(
                    self.server,
                    self.oda_master.odb_file.binary.name,
                    self.oda_master.odb_file.binary.file_handle())

        return self.task_id

    def status(self):

        status = api.get_status(self.server, self.task_id)

        now = datetime.datetime.now()
        self.elapsed_seconds = (now - self.started).total_seconds()
        status['elapsed_time'] = str(datetime.timedelta(seconds=self.elapsed_seconds))

        # if the job completed
        if status['status'] == 'reported':
            # get run-time data from cuckoo and reconstruct the odb_file
            self.reload_odb()

        return status

    # internal function to create a new odb_file based on runtime info from cuckoo
    def reload_odb(self):

        if self.reloaded:
            return
        # ensure we only do this once
        self.reloaded = True

        logger.info('Reloading odb for job %s' % self.name)
        orig_binary_file = self.oda_master.odb_file.binary

        # get the procdump file
        f = api.get_procdump(self.server, self.task_id)
        f.name = self.oda_master.odb_file.binary.name

        binary_file = BinaryFile.create(f)
        binary_file.save()
        bfm = BinaryFileModel(binary_file.id)
        options = orig_binary_file.options

        # TODO: set the target to a new target type called 'cuckoo' or something and add support in ofd
        options.target = 'lime'
        bfm.options = options

        odb_file = OdbFile(bfm)
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        self.oda_master.odb_file = odb_file
        self.oda_master.save()


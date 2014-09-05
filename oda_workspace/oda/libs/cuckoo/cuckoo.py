import datetime

jobs = {}

def submit_job(odb_file):
    # submit a new job to the Cuckoo server and get the job ID
    id = 0
    server = 'localhost'
    job = CuckooJob(server, id)
    jobs[str(id)] = job
    return job

def get_job(job_id):
    return jobs[job_id]

class CuckooJob(object):

    def __init__(self, server, id):
        self.started = datetime.datetime.now()
        self.server = server
        self.id = id

    def status(self):
        now = datetime.datetime.now()
        elapsed_seconds = (now - self.started).total_seconds()
        # make RESTful query using server/id
        return "PROCESSING " + str(elapsed_seconds)
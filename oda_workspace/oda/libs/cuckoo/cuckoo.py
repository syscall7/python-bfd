import datetime
import requests

jobs = {}

def submit_job(odb_file):
    # submit a new job to the Cuckoo server and get the job ID
    server = 'localhost'
    job = CuckooJob(server, odb_file.file_handle, odb_file.name)
    jobs[str(id)] = job
    return job

def get_job(job_id):
    return jobs[job_id]

class CuckooJob(object):

    def __init__(self, server, file_handle, file_name):
        self.started = datetime.datetime.now()
        self.elapsed_seconds = 0
        self.server = server
        self.id = id
        self.port = 8090
        self.file_handle = file_handle
        self.file_name = file_name

    def submit(self):
        url = 'http://{server}:{port}/tasks/create/file'.format(server=self.server, port=self.port)
        files = {'file': (self.file_name, self.file_handle)}
        data = {
            'options' : 'procmemdump=yes',
            'package' : 'exe',
            'timeout' : 10,
            'enforce_timeout' : 10,
        }
        response = requests.post(url, files=files, data=data)
        self.task_id = response.json()['task_id']

    def status(self):
        url = 'http://{server}:{port}/tasks/view/{task_id}'.format(server=self.server, port=self.port, task_id=self.task_id)
        response = requests.get(url)

        now = datetime.datetime.now()
        self.elapsed_seconds = (now - self.started).total_seconds()

        return response.json()['task']


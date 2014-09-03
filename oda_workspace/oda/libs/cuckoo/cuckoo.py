
def submit_job(path):
    # submit a new job to the Cuckoo server and get the job ID
    id = 0
    server = 'localhost'
    return CuckooJob(server, id)

class CuckooJob(object):
    def __init__(self, server, id):
        self.server = server
        self.id = id

    def status(self):
        # make RESTful query using server/id
        pass

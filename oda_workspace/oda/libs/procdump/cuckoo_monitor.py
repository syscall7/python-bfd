class CuckooMonitor:
    instances = {}

    @staticmethod
    def getMonitor(id):
        return CuckooMonitor.instances[id]

    @staticmethod
    def create(id):
        cm = CuckooMonitor(id)
        CuckooMonitor.instances[cm.id] = cm

    def __init__(self, id):
        self.status='PROCESSING'
        self.id = id

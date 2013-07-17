from time import time
from logging import getLogger

class LoggingMiddleware(object):
    def __init__(self):
        # arguably poor taste to use django's logger
        self.requestNum = 0
        self.logger = getLogger(__file__)

    def process_request(self, request):
        request.timer = time()
        request.requestNum = self.requestNum
        self.requestNum+=1
        self.logger.info("%5d|%s", self.requestNum, request.get_full_path())
        return None

    def process_response(self, request, response):
        self.logger.info(
            '%5d|%s [%s] (%.1fs)',
            self.requestNum,
            request.get_full_path(),
            response.status_code,
            time() - request.timer
        )
        return response
from time import time
from logging import getLogger
from itertools import count

class LoggingMiddleware(object):
    def __init__(self):
        # arguably poor taste to use django's logger
        self.requestNum = count()
        self.logger = getLogger(__file__)

    def process_request(self, request):
        request.timer = time()
        request.requestNum = int(self.requestNum.next())
        self.logger.info("%5d|%s", request.requestNum, request.get_full_path())
        return None

    def process_response(self, request, response):
        self.logger.info(
            '%5d|%s [%s] (%.1fs)',
            request.requestNum,
            request.get_full_path(),
            response.status_code,
            time() - request.timer
        )
        return response
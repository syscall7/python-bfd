from time import time
from logging import getLogger
from itertools import count
from django.db import connection

logger = getLogger(__name__)

class LoggingMiddleware(object):
    def __init__(self):
        # arguably poor taste to use django's logger
        self.requestNum = count()
        self.logger = getLogger(__file__)

    def process_request(self, request):
        request.timer = time()
        request.requestNum = int(self.requestNum.next())
        self.logger.info("%5d/%s|%s", request.requestNum, request.META.get('REMOTE_ADDR'), request.get_full_path())
        return None

    def process_response(self, request, response):
        requestNum = -1
        requestTime = -1
        if hasattr(request, 'requestNum'):
            requestNum = request.requestNum
        if hasattr(request, 'timer'):
            requestTime = time() - request.timer

        self.logger.info(
            '%5d|%s [%s] (%.1fs)',
            requestNum,
            request.get_full_path(),
            response.status_code,
            requestTime
        )
        return response

class QueryCountDebugMiddleware(object):
    """
    This middleware will log the number of queries run
    and the total time taken for each request (with a
    status code of 200). It does not currently support
    multi-db setups.
    """
    def process_response(self, request, response):
        if response.status_code == 200:
            total_time = 0

            for query in connection.queries:
                query_time = query.get('time')
                if query_time is None:
                    # django-debug-toolbar monkeypatches the connection
                    # cursor wrapper and adds extra information in each
                    # item in connection.queries. The query time is stored
                    # under the key "duration" rather than "time" and is
                    # in milliseconds, not seconds.
                    query_time = query.get('duration', 0) / 1000
                total_time += float(query_time)

            logger.debug('%s queries run, total %s seconds' % (len(connection.queries), total_time))
        return response
"""Safe request observability at the backend composition boundary."""

import logging
from time import perf_counter


request_logger = logging.getLogger("nexetl.request")


class RequestLoggingMiddleware:
    """Log only method, path, status, and duration for every HTTP request."""

    def __init__(self, get_response) -> None:  # type: ignore[no-untyped-def]
        self.get_response = get_response

    def __call__(self, request):  # type: ignore[no-untyped-def]
        started = perf_counter()
        response = self.get_response(request)
        request_logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.path,
            response.status_code,
            (perf_counter() - started) * 1000,
        )
        return response

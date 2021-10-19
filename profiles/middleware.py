import time
from structlog import get_logger
from profiles.verifier import get_key_from_request

logger = get_logger("openstates")


def structlog_middleware(get_response):
    def middleware(request):
        msg = None

        if request.path.startswith("/graphql"):
            msg = "graphql"

        if msg:
            log = logger.bind(
                user_agent=request.META.get("HTTP_USER_AGENT", "UNKNOWN"),
                remote_addr=request.META.get("REMOTE_ADDR"),
                api_key=get_key_from_request(request),
                url=request.path_info,
                params=request.GET if request.method == "GET" else request.body,
            )
            start = time.time()

        response = get_response(request)

        if msg:
            log = log.bind(
                status_code=response.status_code,
                duration=time.time() - start,
            )
            log.info(msg)

        return response

    return middleware

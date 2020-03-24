import time
from graphene_django.views import GraphQLView
from profiles.verifier import verify_request, get_key_from_request
from structlog import get_logger


logger = get_logger("openstates")


class KeyedGraphQLView(GraphQLView):
    def get_response(self, request, data, show_graphiql=False):
        log = logger.bind(
            user_agent=request.META.get("HTTP_USER_AGENT", "UNKNOWN"),
            remote_addr=request.META.get("REMOTE_ADDR"),
            api_key=get_key_from_request(request),
            query=data.get("query") or request.GET.get("query"),
        )
        start = time.time()

        internal = request.get_host() in request.META.get("HTTP_ORIGIN", "")

        # check key only if we're not handling a graphiql request
        if not show_graphiql and not internal:
            error = verify_request(request, "v2")
            if error:
                log = log.bind(
                    error=error,
                    status_code=error.status_code,
                    duration=time.time() - start,
                )
                log.info("graphql")
                return error, error.status_code

        resp = super().get_response(request, data, show_graphiql)
        log = log.bind(duration=time.time() - start)
        log.info("graphql")
        return resp

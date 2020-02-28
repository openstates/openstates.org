import time
from simplekeys.verifier import verify_request
from graphene_django.views import GraphQLView
from django.conf import settings
import newrelic
from structlog import get_logger


logger = get_logger("openstates")


class KeyedGraphQLView(GraphQLView):
    graphiql_template = "graphene/graphiql-keyed.html"

    def get_response(self, request, data, show_graphiql=False):
        log = logger.bind(
            user_agent=request.META.get("HTTP_USER_AGENT", "UNKNOWN"),
            remote_addr=request.META.get("REMOTE_ADDR"),
            api_key=request.META.get(
                getattr(settings, "SIMPLEKEYS_HEADER", "HTTP_X_API_KEY")
            ),
            query=data.get("query") or request.GET.get("query"),
        )
        start = time.time()

        # check key only if we're not handling a graphiql request
        if not show_graphiql:
            newrelic.agent.add_custom_parameter(
                "key",
                request.META.get(
                    getattr(settings, "SIMPLEKEYS_HEADER", "HTTP_X_API_KEY")
                ),
            )
            newrelic.agent.add_custom_parameter("request-data", data)
            error = verify_request(request, "graphapi")
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

    def render_graphiql(self, request, **data):
        data["demo_key"] = settings.GRAPHQL_DEMO_KEY
        return super().render_graphiql(request, **data)

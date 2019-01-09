from django.http import Http404, HttpResponse
from django.shortcuts import redirect
import boto3
from botocore.errorfactory import ClientError
from ..models import PersonProxy


def fallback(request):
    BUCKET_NAME = "legacy.openstates.org"

    key = request.path.lstrip("/") + "index.html"
    s3 = boto3.client("s3")

    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        return HttpResponse(obj["Body"].read())
    except ClientError:
        raise Http404(request.path + "index.html")


def legislator_fallback(request, legislator_id):
    try:
        p = PersonProxy.objects.get(
            identifiers__scheme="legacy_openstates",
            identifiers__identifier=legislator_id,
        )
        return redirect(p.pretty_url(), permanent=True)
    except PersonProxy.DoesNotExist:
        return fallback(request)

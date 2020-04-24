from django.http import Http404, HttpResponse
from django.shortcuts import redirect
import boto3
from botocore.errorfactory import ClientError
from openstates.data.models import Person
from utils.common import pretty_url


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
        p = Person.objects.get(
            identifiers__scheme="legacy_openstates",
            identifiers__identifier=legislator_id,
        )
        return redirect(pretty_url(p), permanent=True)
    except Person.DoesNotExist:
        return fallback(request)

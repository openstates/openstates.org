from django.http import Http404, HttpResponse
import boto3
from botocore.errorfactory import ClientError


def fallback(request):
    BUCKET_NAME = 'legacy.openstates.org'

    key = request.path.lstrip('/') + 'index.html'
    s3 = boto3.client('s3')

    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        return HttpResponse(obj['Body'].read())
    except ClientError:
        raise Http404(request.path + 'index.html')

import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.gis.geos import Point
from opencivicdata.core.models import Division

DATE_FORMAT = "%Y-%m-%d"


def division_list(request):
    today = datetime.datetime.strftime(datetime.datetime.now(), DATE_FORMAT)

    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    date = datetime.datetime.strptime(
        request.GET.get("date", today), DATE_FORMAT
    ).date()

    if not (lat and lon):
        return JsonResponse({"error": "Must provide lat & lon"}, status_code=400)

    divisions = Division.objects.filter(
        Q(geometries__boundary__set__start_date__lte=date)
        | Q(geometries__boundary__set__start_date=None),
        Q(geometries__boundary__set__end_date__gte=date)
        | Q(geometries__boundary__set__end_date=None),
        geometries__boundary__shape__contains=Point(float(lon), float(lat)),
    )

    return JsonResponse({"results": [{"id": d.id, "name": d.name} for d in divisions]})


def serialize_geometry(geometry):
    return {
        "boundary_set": {
            "name": geometry.boundary.set.name,
            "start_date": geometry.boundary.set.start_date,
            "end_date": geometry.boundary.set.end_date,
        },
        "metadata": geometry.boundary.metadata,
        "extent": geometry.boundary.extent,
        "external_id": geometry.boundary.external_id,
        "name": geometry.boundary.name,
        "centroid": tuple(geometry.boundary.centroid),
    }


def division_detail(request, pk):
    division = get_object_or_404(Division, pk=pk)
    data = {
        "id": division.id,
        "country": division.country,
        "name": division.name,
        "geometries": [serialize_geometry(g) for g in division.geometries.all()],
    }
    return JsonResponse(data)

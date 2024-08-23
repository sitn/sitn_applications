from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest
from djgeojson.serializers import Serializer as GeoJSONSerializer
from django.contrib.gis.geos import Point
from django.conf import settings
from cadastre.models import Mo9Immeubles

def is_valid_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def get_estate(request):
    if "east" not in request.GET or "north" not in request.GET:
        return HttpResponseBadRequest("east and north coordinates should be provided")
    
    east = request.GET.get('east')
    north = request.GET.get('north')

    if not is_valid_number(east) or not is_valid_number(north):
        return HttpResponseBadRequest("Invalid parameters: east and north must be valid numbers.")

    intersector = Point(float(east), float(north), srid=settings.DEFAULT_SRID)

    if "buffer" in request.GET:
        buffer = request.GET.get('buffer')
        if not is_valid_number(buffer):
            return HttpResponseBadRequest("Invalid parameters: buffer must be a valid number.")
        intersector = intersector.buffer(float(buffer))

    intersected_estate = Mo9Immeubles.objects.filter(geom__intersects=intersector)

    serializer = GeoJSONSerializer()
    response_data = serializer.serialize(
        intersected_estate,
        srid=settings.DEFAULT_SRID
    )

    return HttpResponse(
        response_data,
        headers={
            "Content-Type": "application/json",
        },
    )


class HelpView(TemplateView):
    template_name = "help_ecap.html"

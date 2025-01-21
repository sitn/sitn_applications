from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest
from djgeojson.serializers import Serializer as GeoJSONSerializer
from django.contrib.gis.geos import Point
from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework_gis.pagination import GeoJsonPagination

from cadastre.models import Mo9Immeubles
from ecap_intra.models import ObjetImmobilise
from ecap_intra.serializers import ObjetImmobiliseSerializer

def is_valid_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

@api_view(['GET'])
def get_estate(request):
    """
    Retrieves estates found at east and north params.
    If provided, a buffer is applied to the coordinates before intersecting
    Maximum 200 estates can be queried per query.
    """
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

    intersected_estate = Mo9Immeubles.objects.filter(geom__intersects=intersector)[:200]

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


class ObjetImmobiliseViewSet(viewsets.ModelViewSet):
    serializer_class = ObjetImmobiliseSerializer
    pagination_class = GeoJsonPagination
    queryset = ObjetImmobilise.objects.order_by('peggi_id').all()

    @action(detail=False)
    def download(self, request):
        data = ObjetImmobilise.as_geojson()
        return JsonResponse(
            data, 
            safe=False,
            json_dumps_params={'ensure_ascii': False}
        )

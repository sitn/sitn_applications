import json
from itertools import chain

from django.conf import settings
from django.db.models import CharField, Value
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal.error import GDALException

from djgeojson.serializers import Serializer as GeoJSONSerializer

from forest_forpriv.models import Fo01Arrondissement, Fo02Cantonnement, Fo11UniteGestionForprivee


@csrf_exempt
@require_http_methods(["POST"])
def forpriv_intersection(request):
    """
    Accepts a POST of a GeoJSON that must contain one Polygon that will be used as a clipper
    on Fo01Arrondissement, Fo02Cantonnement and Fo11UniteGestionForprivee.

    Replies with a GeoJSON containing one or more Multipolygons inside the given clipper for each
    layer.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})
    try:
        first_geometry_json = data.get('features')[0].get('geometry')
    except TypeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid GeoJSON or GeoJSON is empty'})
    try:
        clipper = GEOSGeometry(str(first_geometry_json))
        clipper.srid = settings.DEFAULT_SRID
    except GDALException:
        return JsonResponse({'status': 'error', 'message': 'Invalid Geometry'})

    if clipper.geom_type not in ['Polygon', 'MultiPolygon']:
        return JsonResponse({'status': 'error', 'message': 'Invalid geometry type.'})

    # Intersect all layers and annotate them with a simple value in order
    # to be able to distinguish the features returned in the Geojson response
    intersected_f01 = Fo01Arrondissement.objects.filter(geom__intersects=clipper).annotate(
        table_name=Value('fo01_arrondissements', CharField())
    )
    intersected_f02 = Fo02Cantonnement.objects.filter(geom__intersects=clipper).annotate(
        table_name=Value('fo02_cantonnements', CharField())
    )
    intersected_f11 = Fo11UniteGestionForprivee.objects.filter(geom__intersects=clipper).annotate(
        table_name=Value('fo11_unite_gestion_forprivees', CharField())
    )

    combined_queryset = list(chain(
        intersected_f01,
        intersected_f02,
        intersected_f11,
    ))

    serializer = GeoJSONSerializer()
    response_data = serializer.serialize(
        combined_queryset,
        srid=settings.DEFAULT_SRID,
        properties=('table_name', 'inspecteur', 'titulaire', 'email'),
    )

    return HttpResponse(
        response_data,
        headers={
            "Content-Type": "application/json",
        },
    )


class HelpView(TemplateView):
    template_name = "help_forest_forpriv.html"

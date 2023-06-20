import json

from django.conf import settings
from django.core.serializers import serialize
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Intersection
from django.contrib.gis.gdal.error import GDALException
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from stationnement.models import Mob20TypeLocalisation

@csrf_exempt
def stationnement_intersection(request):
    """
    Accepts a POST of a GeoJSON that must contain one Polygon or Multipolygon that will be used as a clipper
    on Mob20TypeLocalisation.

    Replies with a GeoJSON containing on or more Multipolygons inside the given clipper.
    """
    if request.method == 'POST':
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
        
        if clipper.geom_type in ['Poylgon', 'MultiPolygon']:
            intersected = Mob20TypeLocalisation.objects.filter(geom__intersects=clipper)
            clipped_mob20 = intersected.annotate(intersected_geom=Intersection('geom', clipper))

            response_data = serialize(
                "geojson",
                clipped_mob20,
                srid=2056,
                geometry_field="geom",
                fields=["type_localisation"]
            )

            return HttpResponse(
                response_data,
                headers={
                    "Content-Type": "application/json",
                },
            )
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid geometry type.'})
    else:
        return HttpResponseNotAllowed(['POST'])

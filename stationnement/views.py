import json

from django.conf import settings
from djgeojson.serializers import Serializer as GeoJSONSerializer
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models import GeometryField, Union
from django.contrib.gis.db.models.functions import Intersection, Area
from django.contrib.gis.gdal.error import GDALException
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from stationnement.models import Mob20TypeLocalisation

@csrf_exempt
def stationnement_intersection(request):
    """
    Accepts a POST of a GeoJSON that must contain one Polygon or Multipolygon that will be used as a clipper
    on Mob20TypeLocalisation.

    Replies with a GeoJSON containing on or more Multipolygons inside the given clipper.
    Multipolygons are grouped by type_localisation and the intersection area is calculated for each group.
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
            # Group by type_localisation, Union polygons and get area of multipolygon
            intersected = Mob20TypeLocalisation.objects.filter(geom__intersects=clipper).values("type_localisation")
            clipped_mob20 = intersected.annotate(
                geom=Union(Intersection('geom', clipper), output_field=GeometryField()),
                intersection_area=Cast(Area(F('geom')), output_field=FloatField()),
            )

            serializer = GeoJSONSerializer()
            response_data = serializer.serialize(
                clipped_mob20,
                srid=settings.DEFAULT_SRID,
                properties=('type_localisation', 'intersection_area'),
                with_modelname=False
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

import json

from django.conf import settings
from django.db.models import IntegerField
from django.contrib.gis.db.models.functions import Intersection, Area
from django.contrib.gis.gdal.error import GDALException
from django.contrib.gis.geos import GEOSGeometry
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from djgeojson.serializers import Serializer as GeoJSONSerializer
from gsr.models import Gsr001Search


class HelpView(TemplateView):
    template_name = "help_gsr.html"

@csrf_exempt
@require_http_methods(["POST"])
def gsr_intersection(request):
    """
    Makes a spatial intersection between the GSR layer and
    the given Geojson sent feature.

    This view takes only the first received feature in the
    Geojson feature collection into account.
    
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
        geom_type = first_geometry_json.get('type')
    except GDALException:
        return JsonResponse({'status': 'error', 'message': 'Invalid Geometry'})

    properties= [
        'comnom',
        'nom_gsr',
        'numero_telephone',
        'email',
        'form_prise_contact',
        'adresse',
        'google_maps',
    ]

    objs = Gsr001Search.objects.filter(geom__intersects=clipper)

    if geom_type == 'Polygon':
        objs = objs.annotate(
            intersection_sq_m=Area(Intersection('geom', clipper), output_field=IntegerField())
        )
        properties.append('intersection_sq_m')

    serializer = GeoJSONSerializer()
    response_data = serializer.serialize(
        objs,
        srid=settings.DEFAULT_SRID,
        properties=tuple(properties),
        with_modelname=False
    )

    return HttpResponse(
        response_data,
        headers={
            "Content-Type": "application/json",
        },
    )

import json

from django.conf import settings
from django.db.models import Case, When, Value, FloatField, F, Func, CharField
from django.contrib.gis.db.models.functions import Intersection, Area
from django.contrib.gis.gdal.error import GDALException
from django.contrib.gis.geos import GEOSGeometry
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from djgeojson.serializers import Serializer as GeoJSONSerializer
from action_sociale.models import Gsr001Search


class GeometryType(Func):
    function = "ST_GeometryType"
    output_field = CharField()


class HelpView(TemplateView):
    template_name = "help_action_sociale.html"


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
        return JsonResponse({"status": "error", "message": "Invalid JSON format"})
    try:
        first_geometry_json = data.get("features")[0].get("geometry")
    except TypeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid GeoJSON or GeoJSON is empty"}
        )

    try:
        clipper = GEOSGeometry(str(first_geometry_json))
        clipper.srid = settings.DEFAULT_SRID
    except GDALException:
        return JsonResponse({"status": "error", "message": "Invalid Geometry"})

    if clipper.geom_type in ("Polygon", "MultiPolygon"):
        zone = (
            Gsr001Search.objects
            .annotate(inter=Intersection("geom", clipper))
            .annotate(
                geom_type=GeometryType(F("inter")),
                inter_area=Case(
                    When(geom_type__in=["ST_Polygon", "ST_MultiPolygon"], then=Area("inter")),
                    default=Value(0.0),
                    output_field=FloatField(),
                ),
            )
            .order_by("-inter_area")
            .select_related("guichet")
            .first()
        )
    else:
        zone = (
            Gsr001Search.objects
            .filter(geom__intersects=clipper)
            .select_related("guichet")
            .first()
        )

    if not zone:
        return JsonResponse({"status": "error", "message": "No intersecting zone found"})

    properties = [
        "comnom",
        "nom_gsr",
        "numero_telephone",
        "email",
        "form_prise_contact",
        "adresse",
        "informations",
        "google_maps",
    ]
    serializer = GeoJSONSerializer()
    response_data = serializer.serialize(
        [zone.guichet],
        srid=settings.DEFAULT_SRID,
        properties=tuple(properties),
        with_modelname=False,
    )

    return HttpResponse(
        response_data,
        headers={
            "Content-Type": "application/json",
        },
    )

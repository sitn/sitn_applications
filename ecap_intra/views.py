from django.http import HttpResponse, HttpResponseBadRequest
from djgeojson.serializers import Serializer as GeoJSONSerializer
from django.contrib.gis.geos import Point
from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework.response import Response

from cadastre.models import Mo9Immeubles
from sitn.mixins import MultiSerializerMixin
from ecap_intra.models import (
    ObjetImmobilise,
    RepartitionExpert,
    PlanSpecial,
    PlanQuartier,
    Ecap90RepartitionExpertsSinistre,
    Ecap06Preavis,
)
from ecap_intra.serializers import (
    ObjetImmobiliseSerializer,
    RepartitionExpertSerializer,
    RepartitionExpertDigestSerializer,
    PlanQuartierSerializer,
    PlanSpecialSerializer,
)


def is_valid_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


@api_view(["GET"])
def get_estate(request):
    """
    Retrieves estates found at east and north params.
    If provided, a buffer is applied to the coordinates before intersecting
    Maximum 200 estates can be queried per query.
    """
    if "east" not in request.GET or "north" not in request.GET:
        return HttpResponseBadRequest("east and north coordinates should be provided")

    east = request.GET.get("east")
    north = request.GET.get("north")

    if not is_valid_number(east) or not is_valid_number(north):
        return HttpResponseBadRequest(
            "Invalid parameters: east and north must be valid numbers."
        )

    intersector = Point(float(east), float(north), srid=settings.DEFAULT_SRID)

    if "buffer" in request.GET:
        buffer = request.GET.get("buffer")
        if not is_valid_number(buffer):
            return HttpResponseBadRequest(
                "Invalid parameters: buffer must be a valid number."
            )
        intersector = intersector.buffer(float(buffer))

    intersected_estate = Mo9Immeubles.objects.filter(geom__intersects=intersector)[:200]

    serializer = GeoJSONSerializer()
    response_data = serializer.serialize(intersected_estate, srid=settings.DEFAULT_SRID)

    return HttpResponse(
        response_data,
        headers={
            "Content-Type": "application/json",
        },
    )


class ObjetImmobiliseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Objects immobilisés actifs
    """

    serializer_class = ObjetImmobiliseSerializer
    pagination_class = GeoJsonPagination
    queryset = ObjetImmobilise.objects.order_by("no_obj").all()

    @action(detail=False)
    def download(self, request):
        data = ObjetImmobilise.as_geojson()
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})


class RepartitionExpertViewSet(MultiSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    Répartition générale des experts
    """

    queryset = RepartitionExpert.objects.order_by("ini_expert").all()
    serializers = {
        "default": RepartitionExpertSerializer,
        "list": RepartitionExpertDigestSerializer,
    }

    @action(detail=False)
    def download(self, request):
        data = RepartitionExpert.as_geojson()
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})


class PlanQuartierViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Périmètres de plan de quartier
    """

    serializer_class = PlanQuartierSerializer
    queryset = PlanQuartier.objects.order_by("identifiant_unique_ct").all()

    @action(detail=False)
    def download(self, request):
        data = PlanSpecial.as_geojson()
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})


class PlanSpecialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Périmètres de plan spécial
    """

    serializer_class = PlanSpecialSerializer
    queryset = PlanSpecial.objects.order_by("identifiant_unique_ct").all()

    @action(detail=False)
    def download(self, request):
        data = PlanSpecial.as_geojson()
        return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False})


@api_view(["GET"])
def get_sinistres(request):
    """
    Retrieves a list of available "secteurs d'intervention" related to a "sinistre"
    """
    sinistres = (
        Ecap90RepartitionExpertsSinistre.objects.values_list("name_sinistre", flat=True)
        .order_by("name_sinistre")
        .distinct()
    )

    return Response(sinistres)


@api_view(["GET"])
def get_preavis(request):
    """
    Retrieves a list of available "preavis". "Preavis" are preliminary geometries drawn on intranet
    geoportal. They refer to future "plans de quartier" or "plans spéciaux"
    """
    preavis = (
        Ecap06Preavis.objects.values_list("document_name", flat=True)
        .order_by("document_name")
        .distinct()
    )

    return Response(preavis)

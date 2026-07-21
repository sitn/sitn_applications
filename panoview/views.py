from django.contrib.gis.db.models.functions import Transform
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from . import stac
from .models import PanoramaItem, Sequence


def _json(data):
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})


def catalog_view(request):
    return _json(stac.build_catalog(request))


def collections_view(request):
    return _json(stac.build_collections(request))


def collection_view(request, seq_id):
    sequence = get_object_or_404(Sequence, pk=seq_id)
    return _json(stac.build_collection(request, sequence))


def item_view(request, seq_id, item_id):
    queryset = PanoramaItem.objects.select_related("sequence").annotate(geom_wgs84=Transform("geom", 4326))
    item = get_object_or_404(queryset, pk=item_id, sequence_id=seq_id)
    return _json(stac.build_item(request, item))


def search_view(request):
    try:
        return _json(stac.build_search(request, request.GET))
    except ValueError:
        return HttpResponseBadRequest("Invalid query parameters")


def panorama_view(request, item_id):
    """Serves the streetview-style HTML page for a given picture id."""
    item = get_object_or_404(PanoramaItem, pk=item_id)
    return render(request, "panoview/panorama.html", {
        "picture_id": item.id,
        "sequence_id": item.sequence_id,
        "stac_endpoint": stac.catalog_url(request),
    })

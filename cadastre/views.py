from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity, SearchQuery
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from djgeojson.serializers import Serializer as GeoJSONSerializer
from cadastre.models import Cadastre, ImmeublesAdressesSearch

import re

def get_cadastre(request):

    cadastres = Cadastre.objects.values('numcad', 'cadnom').all().order_by('cadnom')

    return JsonResponse(list(cadastres), safe=False)

def search_parcel(request):
    """
      Extended properties on search estates by address.
      This is an adapted and simplified copy from here:
      https://github.com/camptocamp/c2cgeoportal/blob/2.6/geoportal/c2cgeoportal_geoportal/views/fulltextsearch.py
    """

    IGNORED_CHARS_RE = re.compile(r"[()&|!:<>\t]")
    IGNORED_STARTUP_CHARS_RE = re.compile(r"^[']*")

    if "query" not in request.GET:
        return HttpResponseBadRequest("No query")

    terms = request.GET["query"]
    
    terms_array = [
        IGNORED_STARTUP_CHARS_RE.sub("", elem) for elem in IGNORED_CHARS_RE.sub(" ", terms).split(" ")
    ]

    terms_ts = "&".join(w + ":*" for w in terms_array if w != "")

    query = ImmeublesAdressesSearch.objects.annotate(
        similarity=TrigramSimilarity("label", terms)
    ).filter(
        _ts=SearchQuery(terms_ts, config="fr", search_type='raw')
    ).order_by("-similarity")

    objs = query.all()

    serializer = GeoJSONSerializer()
    response_data = serializer.serialize(
        objs,
        srid=settings.DEFAULT_SRID,
        properties=(
            'label',
            'idmai',
            'comnum',
            'comnom',
            'cadnum',
            'cadnom',
            'adresse'
        ),
        with_modelname=False
    )

    return HttpResponse(
        response_data,
        headers={
            "Content-Type": "application/json",
        },
    )

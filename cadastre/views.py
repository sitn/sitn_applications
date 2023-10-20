from django.http import JsonResponse
from django.shortcuts import render
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

    settings = request.registry.settings.get("fulltextsearch", {})
#    fts_normaliser = Normalize(settings)  


    return {}
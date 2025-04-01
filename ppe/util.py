import requests
from functools import wraps

from .forms import GeolocalisationForm
from .models import DossierPPE
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

# BOUNDING BOX CANTON NEUCHATEL
NE_MIN_EST = 2515000
NE_MAX_EST = 2585000
NE_MIN_NORD = 1180000
NE_MAX_NORD = 1230000

# Geolocalisation service
GEOLOC_SERVICE_URL = 'https://sitn.ne.ch/satac_localisation?'

def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if 'login_code' in request.session : 
            try:
                return func(request, DossierPPE.objects.get(login_code=request.session['login_code']), *args, **kwargs)
            except:
                pass
        return redirect('/ppe/login')
    return wrapper

def get_localisation(localisation):

    try:
        coords = localisation['coordinates']
        coord_est = round(coords[0],1)
        coord_nord = round(coords[1],1)
    except KeyError:
        # Redisplay the question voting form.
        return render(
            "ppe/geolocalisation.html",
            {
                "error_message": "Les coordonnées n'ont pas pu être récupérées.",
                "form": GeolocalisationForm
            },
        )

    if (NE_MIN_EST < coord_est < NE_MAX_EST) and (NE_MIN_NORD < coord_nord < NE_MAX_NORD):
        url = GEOLOC_SERVICE_URL+"X="+str(coord_est)+"&Y="+str(coord_nord)

        headers = {
            'cache-control': "no-cache",
            'postman-token': "c71c65a6-07f4-a2a4-a6f8-dca3fd706a7a"
            }

        response = requests.request("GET", url, headers=headers)
        data = response.json()
        
        # THERE MIGHT BE DDP's ...
        # TODO: Establish a list to select from

        if isinstance(data, dict) and 'bien_fonds' in data:
            idemai = data['bien_fonds']
            nummai = data['nummai']
            numcad = data['numcad']
            cadastre = data['nomcad']
            commune = data['nomcom']
        else:
            return HttpResponseBadRequest("Une erreur inconnue s'est produite. La localisation a échouée.")

    else:
        return HttpResponseBadRequest("La localisation semble se situer en dehors du canton.")

    geoloc = {
        "egrid": 'ToDo',
        "idemai": idemai,
        "nummai": nummai,
        "numcad": numcad,
        "cadastre": cadastre,
        "commune": commune,
        "coord_est": coord_est,
        "coord_nord": coord_nord
    }

    return(geoloc)

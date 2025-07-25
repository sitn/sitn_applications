import requests, logging
from functools import wraps

from .forms import GeolocalisationForm
from .models import DossierPPE
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.db import connections

logger = logging.getLogger(__name__)

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
            logger.debug('== Trying to log in with code')
            try:
                return func(request, DossierPPE.objects.get(login_code=request.session['login_code']), *args, **kwargs)
            except Exception as e:
                print(f"Exception : {repr(e)}")
                pass
        return redirect('/ppe/login')
    return wrapper

def get_localisation(localisation):

    try:
        coords = localisation['coordinates']
        coord_est = round(coords[0],1)
        coord_nord = round(coords[1],1)
    except KeyError:
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
        if isinstance(data, dict) and 'bien_fonds' in data:
            if isinstance(data['bien_fonds'], list):
                bf = None
                bf_list = []
                for i in range(len(data['nummai'])):
                    for k,v in data['bien_fonds'][i].items():
                        bf_type = k
                    bf_list.append({
                        "bf_type" : bf_type,
                        "nummai" : data["nummai"][i]
                    })
            else:
                bf_list = None
                bf = {
                "bf_type" : 'bien_fonds',
                "nummai" : data["nummai"]
                }
            numcad = data["numcad"]
            cadastre = data["nomcad"]
        else:
            return HttpResponseBadRequest("Une erreur inconnue s'est produite. La localisation a échouée.")

    else:
        return HttpResponseBadRequest("La localisation semble se situer en dehors du canton.")

    geoloc = {
        "egrid": "ToDo",
        "bf_list": bf_list,
        "bien_fonds": bf,
        "numcad": numcad,
        "cadastre": cadastre,
        "coord_est": coord_est,
        "coord_nord": coord_nord,
        "coordinates": coords
    }

    return(geoloc)

def check_geoshop_ref(ref):
    """ Function de validation of the provided geoshop reference """
    ref_ok = False

    if ref is None:
        return False
    
    try:
        if not ref.isnumeric():
            ref = ref.split('_')
            if len(ref) != 2:
                return False
            else:
                if not ref[0].isnumeric():
                    return False

        with connections["geoshop"].cursor() as cursor:
            cursor.execute("SELECT * FROM geoshop.order WHERE id = %s", [ref])
            row = cursor.fetchone()
            if row:
                ref_ok = True
            
    except Exception as e:
        print(f"Exception : {repr(e)}")
        pass
    return ref_ok
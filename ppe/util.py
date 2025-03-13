from .forms import GeolocalisationForm
from django.shortcuts import render
from django.http import HttpResponseBadRequest

import requests
from json import loads

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

    if (coord_est > 2515000 and coord_est < 2585000) and (coord_nord > 1180000 and coord_nord < 1230000):
        url = "https://sitn.ne.ch/satac_localisation?X="+str(coord_est)+"&Y="+str(coord_nord)


        headers = {
            'cache-control': "no-cache",
            'postman-token': "c71c65a6-07f4-a2a4-a6f8-dca3fd706a7a"
            }

        response = requests.request("GET", url, headers=headers)
        data = response.json()

        if isinstance(data, dict) and 'bien_fonds' in data:
            idemai = data['bien_fonds']
            nummai = data['nummai']
            numcad = data['numcad']
            cadastre = data['nomcad']
            commune = data['nomcom']

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

def get_immeubles(coordinates):

    # SEARCH: Get real estate nb and EGRID for this coordinates
    results = []
    if (coord_est > 2515000 and coord_est < 2585000) and (coord_nord > 1180000 and coord_nord < 1230000):
        results = [{"egrid": "CH848749790063", "idemai": "1_14127", "cadastre": "Neuchâtel"}]

    if len(results) >= 1:
        # THERE MIGHT BE DDP's ...
        # TODO: Establish a list to select from
        for result in results:
            egrid = result["egrid"]
            idemai = result["idemai"]
            cadastre = result["cadastre"]

            ppe.append({
                "coord_est": coord_est,
                "coord_nord": coord_nord,
                "egrid": egrid,
                "idemai": idemai,
                "cadastre": cadastre
            })
    else:
        ppe =  {"error_message": "Aucun résultat trouvé."}

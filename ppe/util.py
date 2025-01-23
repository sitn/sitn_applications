from .forms import GeolocalisationForm

def get_localisation(localisation):
    
    try:
        coordinates = localisation["coordinates"]
        coord_est = round(coordinates[0],1)
        coord_nord = round(coordinates[1],1)
    except KeyError:
        # Redisplay the question voting form.
        return render(
            request,
            "ppe/geolocalisation.html",
            {
                "error_message": "Les coordonnées n'ont pas pu être récupérées.",
                "form": GeolocalisationForm
            },
        )

    # SEARCH: Get real estate nb and EGRID for this coordinates
    results = [{"egrid": "CH848749790063", "idemai": "1_14127", "cadastre": "Neuchâtel"}]
    if len(results) > 1:
        # THERE MIGHT BE DDP's ...
        # TODO: Establish a list to select from
        return render(
            request,
            "ppe/geolocalisation.html",
            {
                "error_message": "Plusieurs résultats trouvé" + {{ results }},
                "form": GeolocalisationForm
            },
        )
    else:
        result = results[0]
        egrid = result["egrid"]
        idemai = result["idemai"]
        cadastre = result["cadastre"]

    ppe = {
        "coord_est": coord_est,
        "coord_nord": coord_nord,
        "egrid": egrid,
        "idemai": idemai,
        "cadastre": cadastre
    }

    return(ppe)
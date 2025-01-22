from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
import json

from .models import DossierPPE
from .forms import DossierPPEForm, GeolocalisationForm, ContactPrincipalForm
from .forms import DocumentForm, AdresseFacturationForm, NotaireForm, SignataireForm

def index(request):
    latest_dossiers_list = DossierPPE.objects.order_by("-date_creation")[:5]
    template = loader.get_template("ppe/index.html")
    context = {
        "latest_dossiers_list": latest_dossiers_list,
    }
    return HttpResponse(template.render(context, request))

def detail(request, id):
    dossier_ppe = get_object_or_404(DossierPPE, pk=id)
    return render(request, "ppe/detail.html", {"dossier_ppe": dossier_ppe})

def geolocalisation(request):

    try:
        localisation = json.loads(request.GET["geom"])
    except KeyError:
        # Redisplay the question voting form.
        return render(
            request,
            "ppe/geolocalisation.html",
            {
                "error_message": "Aucune localisation trouvée",
                "form": GeolocalisationForm
            },
        )
    
    if localisation:
        coordinates = localisation["coordinates"]
        coord_est = round(coordinates[0],1)
        coord_nord = round(coordinates[1],1)
        # SEARCH: Get real estate nb and EGRID for this coordinates

    results = [{"egrid": "CH848749790063", "idemai": "1_14127"}]
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

    return render(
        request, 
        "ppe/contact_principal.html", {
        "contact_form": ContactPrincipalForm,
        "notaire_form": NotaireForm,
        "signataire_form": SignataireForm,
        "facturation_form": AdresseFacturationForm,
        "document_form": DocumentForm,
        "localisation": localisation,
        "coord_est": coord_est,
        "coord_nord": coord_nord,
        "egrid": egrid,
        "idemai": idemai
            })

def modification(request):

    return render(request, "ppe/modification.html", {"form": GeolocalisationForm})

def contact_principal(request):

    return render(request, "ppe/contact_principal.html", {"form": ContactPrincipalForm})
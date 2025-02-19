from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
import json

from .models import DossierPPE
from .forms import DossierPPEForm, GeolocalisationForm, ContactPrincipalForm
from .forms import DocumentForm, AdresseFacturationForm, NotaireForm, SignataireForm

from .util import get_localisation

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
    # initialising a dict collecting the necessary information by step
    ppe = {}

    try:
        localisation = request.GET["geom"]
        if isinstance(localisation, str) and localisation != '':
            localisation = json.loads(localisation)
        else:
         # Redisplay the question voting form.
            return render(
                request,
                "ppe/geolocalisation.html",
                {
                    "error_message": "Aucune localisation trouvée",
                    "form": GeolocalisationForm
                },
            )                      
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
        ppe.update(get_localisation(localisation))

    return render(
        request, 
        "ppe/contact_principal.html", {
        "contact_form": ContactPrincipalForm,
        "notaire_form": NotaireForm,
        "signataire_form": SignataireForm,
        "facturation_form": AdresseFacturationForm,
        "document_form": DocumentForm,
        "localisation": localisation,
        "ppe": ppe
#        "coord_est": coord_est,
#        "coord_nord": coord_nord,
#        "cadastre": cadastre,
#        "egrid": egrid,
#        "idemai": idemai
            })

def modification(request):

    return render(request, "ppe/modification.html", {"form": GeolocalisationForm})

def contact_principal(request):

    return render(request, "ppe/contact_principal.html", {"form": ContactPrincipalForm})
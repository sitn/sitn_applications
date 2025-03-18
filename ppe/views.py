import datetime
import json

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.gis.geos import Point

from .models import DossierPPE, ContactPrincipal, Notaire, Signataire, AdresseFacturation
from .models import AccordFrais, Geolocalisation
from .forms import GeolocalisationForm, ContactPrincipalForm
from .forms import AccordFraisForm, AdresseFacturationForm, NotaireForm, SignataireForm

from .util import get_localisation

def index(request):
    # A list for the PPE admins to see the latest demands
    latest_dossiers_list = DossierPPE.objects.order_by("-date_creation")[:5]
    template = loader.get_template("ppe/index.html")
    context = {
        "latest_dossiers_list": latest_dossiers_list,
    }
    return HttpResponse(template.render(context, request))


def detail(request, id):
    # detail view of a specific ppe
    dossier_ppe = get_object_or_404(DossierPPE, pk=id)
    return render(request, "ppe/detail.html", {"dossier_ppe": dossier_ppe})


def geolocalisation(request):
    localisation = None
    # if this is a POST request we need to process the form data

    try:
        # Check if a localisation exists
        localisation = request.GET["geom"]
        geoloc = Geolocalisation(localisation)

        # Convert an existing localisation to a JSON dict
        if isinstance(localisation, str) and localisation != '':
            localisation = json.loads(localisation)
        # Fetch geolocalisation calling the satac service
        if localisation is not None and 'coordinates' in localisation:
            geolocalisation_ppe = get_localisation(localisation)
            return contact_principal(request, geolocalisation_ppe)
        else:
            error_message = "La localisation n'a pas donné de résultat"
    except KeyError:
        # Redisplay the question voting form.
        return render(
            request,
            "ppe/geolocalisation.html",
            {
                "error_message": "Aucune localisation définie.",
                "form": GeolocalisationForm
            },
        )


def modification(request):
    
    try:
        id = request.GET["id_dossier"]
        if isinstance(id, str) and id != '':
            return detail(request, id)
        else:
            return render(request, "ppe/modification.html", {"error_message" : "Il manque l'identifiant du dossier."})
    except:
        return render(request, "ppe/modification.html")


def contact_principal(request, geolocalisation_ppe):

    if request.method == 'POST':
        notaire_form = NotaireForm(request.POST, prefix='notaire')
        contact_form = ContactPrincipalForm(request.POST, prefix='contact')
        signataire_form = SignataireForm(request.POST, prefix='signataire')
        facturation_form = AdresseFacturationForm(request.POST, prefix='facturation')
        accord_form = AccordFraisForm(request.POST, request.FILES, prefix='accord')

        if (contact_form.is_valid() and
           notaire_form.is_valid() and
           signataire_form.is_valid() and
           facturation_form.is_valid()
           and accord_form.is_valid()):

            new_contact = ContactPrincipalForm(contact_form.cleaned_data)
            new_contact.save()
            new_notaire = NotaireForm(notaire_form.cleaned_data)
            new_notaire.save()
            new_signataire = SignataireForm(signataire_form.cleaned_data)
            new_signataire.save()
            new_adresse = AdresseFacturationForm(facturation_form.cleaned_data)
            new_adresse.save()
            #new_accord = AccordFraisForm(accord_form.cleaned_data)
            #new_accord.save()
            new_geom = Geolocalisation()
            new_geom = json.loads(request.GET["geom"])

            new_dossier_ppe = DossierPPE()
            new_dossier_ppe.egrid = geolocalisation_ppe["egrid"]
            new_dossier_ppe.cadastre = geolocalisation_ppe["cadastre"]
            new_dossier_ppe.commune = geolocalisation_ppe["commune"]
            new_dossier_ppe.numcad = geolocalisation_ppe["numcad"]
            new_dossier_ppe.nummai = geolocalisation_ppe["nummai"]
            new_dossier_ppe.coord_E = geolocalisation_ppe["coord_est"]
            new_dossier_ppe.coord_N = geolocalisation_ppe["coord_nord"]
            new_dossier_ppe.contact_principal = ContactPrincipal(pk=new_contact.instance.id)
            new_dossier_ppe.notaire = Notaire(pk=new_notaire.instance.id)
            new_dossier_ppe.signataire = Signataire(pk=new_signataire.instance.id)
            new_dossier_ppe.adresse_facturation = AdresseFacturation(pk=new_adresse.instance.id)
            # TODO: replace hard coded pk for accord frais
            new_dossier_ppe.accord_frais = AccordFrais(pk=1)
            new_dossier_ppe.statut = 'P'
            new_dossier_ppe.type_dossier = "C"
            new_dossier_ppe.date_creation = datetime.datetime.now()
            new_dossier_ppe.geom = Point(new_geom["coordinates"])
            new_dossier_ppe.save()

            # Get all the elements from the freshly created dossier ppe
            dossierppe = get_object_or_404(DossierPPE, pk=new_dossier_ppe.id)  

            return overview_nouveau_depot(request, dossierppe)
        else:
            return render(
                request, 
                "ppe/contact_principal.html", 
                {
                "error_message": "Un formulaire n'a pas été renseigné correctement.",
                "contact_form": ContactPrincipalForm(prefix='contact'),
                "notaire_form": NotaireForm(prefix='notaire'),
                "signataire_form": SignataireForm(prefix='signataire'),
                "facturation_form": AdresseFacturationForm(prefix='facturation'),
                "accord_form": AccordFraisForm(prefix='accord'),
                "localisation_ppe": geolocalisation_ppe
                    })
    return render(
        request, 
        "ppe/contact_principal.html", 
        {
        "contact_form": ContactPrincipalForm(prefix='contact'),
        "notaire_form": NotaireForm(prefix='notaire'),
        "signataire_form": SignataireForm(prefix='signataire'),
        "facturation_form": AdresseFacturationForm(prefix='facturation'),
        "accord_form": AccordFraisForm(prefix='accord'),
        "localisation_ppe": geolocalisation_ppe
            })

def overview_nouveau_depot(request, new_dossier_ppe):
    
    return render(request, "ppe/overview_nouveau_depot.html", {"overview": new_dossier_ppe})


def soumission(request, id):
    dossier_ppe = get_object_or_404(DossierPPE, pk=id)    
    return render(request, "ppe/soumission.html", {"dossier_ppe": dossier_ppe})


def definition_type_dossier(request, id, type_dossier=None):
    if id is not None and type_dossier is None:
        dossier_ppe = get_object_or_404(DossierPPE, pk=id)
        type_dossier = dossier_ppe.type_dossier
    # TODO: handle other cases

    return render(request, "ppe/definition_type_dossier.html", {"dossier_ppe": dossier_ppe, "type_dossier": type_dossier })
import datetime, random, string, json, logging, ast
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.gis.geos import Point
from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import FileSystemStorage

# INDIVIDUAL ELEMENTS
from .models import DossierPPE, ContactPrincipal, Notaire, Signataire, AdresseFacturation, Geolocalisation, ZipFile
from .forms import AdresseFacturationForm, NotaireForm, SignataireForm, GeolocalisationForm, ContactPrincipalForm, ZipFileForm

from .util import get_localisation, login_required

logger = logging.getLogger(__name__)

def index(request):
    # A list for the PPE admins to see the latest demands
    # TODO : This should only be visible to admins
    latest_dossiers_list = DossierPPE.objects.order_by("-date_creation")[:5]
    template = loader.get_template("ppe/index.html")
    return HttpResponse(template.render({"latest_dossiers_list": latest_dossiers_list}, request))

def geolocalisation(request):
    # if this is a POST request we need to process the form data
    error_message = None
    localisation_ppe = None
    geo_form = GeolocalisationForm()
    form_action = 'geolocalisation'

    if 'geom' in request.POST:
        localisation = request.POST['geom']
        geo_form = GeolocalisationForm(request.POST)
        if geo_form.is_valid():
            geo_form.save()
        # Convert an existing localisation to a JSON dict
        if isinstance(localisation, str) and localisation != '':
            localisation = json.loads(localisation)
            localisation_ppe = get_localisation(localisation)
        form_action = 'contact_principal'
    else:
        logger.warning(f"Error during geoloc. decoding")


    return render(
        request,
        "ppe/geolocalisation.html",
        {
            "error_message": error_message,
            "localisation_ppe": localisation_ppe,
            "form": geo_form,
            "form_action": form_action,
        }
    )


@login_required
def modification(request, doc):
    error_message = None
    notaire_form = NotaireForm(request.POST, prefix='notaire')
    contact_form = ContactPrincipalForm(request.POST, prefix='contact')
    signataire_form = SignataireForm(request.POST, prefix='signataire')
    facturation_form = AdresseFacturationForm(request.POST, request.FILES or None, prefix='facturation')

    try:
        if isinstance(doc, object):
            if 'modification' in request.POST:
                dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
                contact_form = ContactPrincipalForm(
                    request.POST, 
                    instance=dossier_ppe.contact_principal, 
                    prefix='contact'
                    )
                notaire_form = NotaireForm(
                    request.POST, 
                    instance=dossier_ppe.notaire, 
                    prefix='notaire'
                    )
                signataire_form = SignataireForm(
                    request.POST, dossier_ppe.signataire,
                    prefix='signataire'
                    )
                facturation_form = AdresseFacturationForm(
                    request.POST, 
                    request.FILES, 
                    instance=dossier_ppe.adresse_facturation,
                    prefix='facturation'
                    )

                if (contact_form.is_valid() and
                    notaire_form.is_valid() and
                    signataire_form.is_valid() and
                    facturation_form.is_valid()):

                    contact_form.save()
                    notaire_form.save()
                    signataire_form.save()
                    facturation_form.save()

                    dossier_ppe.contact_principal = ContactPrincipal(pk=contact_form.instance.id)
                    dossier_ppe.notaire = Notaire(pk=notaire_form.instance.id)
                    dossier_ppe.signataire = Signataire(pk=signataire_form.instance.id)
                    dossier_ppe.adresse_facturation = AdresseFacturation(pk=facturation_form.instance.id)
                    dossier_ppe.save()

                    return redirect(f'/ppe/definition_type_dossier', dossier_ppe)
                else:
                    error_message = "Une valeur modifiée ne semble pas avoir été conforme."

        else:
            error_message = "Une erreur de chargement du dossier est survenue."

        return render(request, "ppe/modification.html", {
            "error_mesage": error_message,
            "dossier": doc,
            "contact_form": ContactPrincipalForm(instance=doc.contact_principal, prefix='contact'),
            "notaire_form": NotaireForm(instance=doc.notaire, prefix='notaire'),
            "signataire_form": SignataireForm(instance=doc.signataire, prefix='signataire'),
            "facturation_form": AdresseFacturationForm(instance=doc.adresse_facturation, prefix='facturation'),
            "cadastre": doc.cadastre,
            "nummai": doc.nummai,
            "geolocalisation_ppe": doc.geom})

    except:
        return render(request, "ppe/modification.html", {"error_message": "Il manque l'identifiant du dossier."})


def contact_principal(request):
    error_message = None
    notaire_form = NotaireForm(request.POST, prefix='notaire')
    contact_form = ContactPrincipalForm(request.POST, prefix='contact')
    signataire_form = SignataireForm(request.POST, prefix='signataire')
    facturation_form = AdresseFacturationForm(request.POST, request.FILES, prefix='facturation')

    if (contact_form.is_valid() and
        notaire_form.is_valid() and
        signataire_form.is_valid() and
        facturation_form.is_valid()):

        geolocalisation_ppe = ast.literal_eval(request.POST["localisation_ppe"])

        login_code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + '._-') for _ in range(16))

        contact_form.save()
        notaire_form.save()
        signataire_form.save()
        facturation_form.save()

        new_dossier_ppe = DossierPPE()
        new_dossier_ppe.login_code = login_code
        new_dossier_ppe.cadastre = geolocalisation_ppe["cadastre"]
        new_dossier_ppe.numcad = geolocalisation_ppe["numcad"]
        new_dossier_ppe.nummai = geolocalisation_ppe["nummai"]
        new_dossier_ppe.coord_E = geolocalisation_ppe["coord_est"]
        new_dossier_ppe.coord_N = geolocalisation_ppe["coord_nord"]
        new_dossier_ppe.contact_principal = ContactPrincipal(pk=contact_form.instance.id)
        new_dossier_ppe.notaire = Notaire(pk=notaire_form.instance.id)
        new_dossier_ppe.signataire = Signataire(pk=signataire_form.instance.id)
        new_dossier_ppe.adresse_facturation = AdresseFacturation(pk=facturation_form.instance.id)
        new_dossier_ppe.statut = 'P'
        new_dossier_ppe.type_dossier = "C"
        new_dossier_ppe.date_creation = datetime.datetime.now()
        new_dossier_ppe.geom = Point(geolocalisation_ppe["coordinates"])
        new_dossier_ppe.save()

        request.session['login_code'] = login_code
        return redirect(f'/ppe/definition_type_dossier', new_dossier_ppe)

    if 'geom' in request.POST:
        try:
            # Check if a localisation exists
            localisation = request.POST["geom"]

            # Convert an existing localisation to a JSON dict
            if isinstance(localisation, str) and localisation != '':
                localisation = json.loads(localisation)
            # Fetch geolocalisation calling the satac service
            if (localisation is not None) and ('coordinates' in localisation):
                return render(
                    request, 
                    "ppe/contact_principal.html", 
                    {
                        "contact_form": ContactPrincipalForm(prefix='contact'),
                        "notaire_form": NotaireForm(prefix='notaire'),
                        "signataire_form": SignataireForm(prefix='signataire'),
                        "facturation_form": AdresseFacturationForm(prefix='facturation'),
                        "localisation_ppe": get_localisation(localisation)
                    }
                )
            else:
                error_message = "La localisation n'a pas donné de résultat"
        except Exception as e:
            # Redisplay the geolocalisation form.
            logger.warning(f"Error during geoloc. decoding : {repr(e)}")
            error_message = "Une erreur est survenue lors de la création du formulaire."

    return redirect(f'/ppe/geolocalisation', {"error_message": error_message})


def login(request):
    if 'login_code' in request.POST:
        request.session['login_code'] = request.POST['login_code']
        try:
            doc = DossierPPE.objects.get(login_code=request.session['login_code'])
            return redirect(f"/ppe/modification", {"dossier_ppe": doc})
        except:
            pass
    return render(request, "ppe/login.html")

@login_required
def detail(request, doc):
    return render(request, "ppe/detail.html", {"dossier_ppe": doc})

@login_required
def overview(request, doc):
    return render(request, "ppe/overview.html", {"dossier_ppe": doc})

@login_required
def soumission(request, doc):
    return render(request, "ppe/soumission.html", {"dossier_ppe": doc})

@login_required
def definition_type_dossier(request, doc, type_dossier=None):
    error_message = None

    try:
        # We get the current entry of the dossier ppe if it exists
        dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
    except:
        # ELSE we return an error
        error_message = "Aucun dossier avec ce code n'a pu être trouvé."
        return render(request, "ppe/definition_type_dossier.html", {"error_message": error_message})  

    type_dossier = request.POST["type_dossier"] if 'type_dossier' in request.POST else dossier_ppe.type_dossier
    ref_geoshop = request.POST["ref_geoshop"] if 'ref_geoshop' in request.POST else None
    situation_bati = request.POST["situation_bati"] if 'situation_bati' in request.POST else None

    if type_dossier == 'C' and situation_bati in ['bati_existant','nouveau_batiment']:
        dossier_ppe.type_dossier = type_dossier

        if situation_bati == 'bati_existant':
            dossier_ppe.save()
            return redirect("/ppe/overview")
        # if changes to buildings are planned or under way check for ref
        elif situation_bati == 'nouveau_batiment' and ref_geoshop != '':
            #TODO: implement ref validation in geoshop db
            dossier_ppe.save()
            return redirect("/ppe/overview")
        else:
            return render(request, "ppe/definition_type_dossier.html", {"error_message": 'Type ou référence invalide.'}) 
    elif type_dossier in ['M','R'] and 'login_code' in request.POST:
        login_code = request.POST['login_code']
        if type_dossier == 'R':
            return redirect(f"/ppe/overview")
        else:
            return redirect(f"/ppe/modification")

    return render(
        request,
        "ppe/definition_type_dossier.html", 
        {
            "dossier_ppe": doc, 
            "type_dossier": type_dossier, 
            "error_message": error_message
        }
    )

@login_required
def load_ppe_files(request, doc):
    """ Function to load the zip file with the PPE documents"""
    error_message = None

    zip_form = ZipFileForm(request.POST, request.FILES or None, prefix='zip')
    doc = DossierPPE.objects.get(login_code=doc.login_code)
    if zip_form.is_valid():
        zipfile = ZipFile(pk=zip_form.instance.id)
        print(zipfile)
        zip_form.save()
        return render(request, "ppe/load_ppe_files.html", {"dossier_ppe" : doc, "zipfile": zipfile })

    return render(request, "ppe/load_ppe_files.html", {"dossier_ppe" : doc, "zip_form": zip_form })

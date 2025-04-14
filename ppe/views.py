import datetime, random, string, json, logging, ast
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.gis.geos import Point
from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import FileSystemStorage

# INDIVIDUAL ELEMENTS
from .models import DossierPPE, ContactPrincipal, Notaire, Signataire, AdresseFacturation, AccordFrais, Geolocalisation
from .forms import AccordFraisForm, AdresseFacturationForm, NotaireForm, SignataireForm, GeolocalisationForm, ContactPrincipalForm

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

    return render(
        request,
        "ppe/geolocalisation.html",
        {
            "error_message": error_message,
            "form": GeolocalisationForm
        }
    )


def modification(request):
    try:
        id = request.GET["id_dossier"]
        if isinstance(id, str) and id != '':
            dossier_ppe = get_object_or_404(DossierPPE, pk=id)
            geolocalisation_ppe = dossier_ppe.geom
            dossier = {
                "contact_form": ContactPrincipalForm(instance=dossier_ppe.contact_principal, prefix='contact'),
                "notaire_form": NotaireForm(instance=dossier_ppe.notaire, prefix='notaire'),
                "signataire_form": SignataireForm(instance=dossier_ppe.signataire, prefix='signataire'),
                "facturation_form": AdresseFacturationForm(instance=dossier_ppe.adresse_facturation, prefix='facturation'),
                #"accord_form": AccordFraisForm(instance=dossier_ppe.accord_frais, prefix='accord')
            }
            return render(request, "ppe/modification.html", {
                "dossier_ppe" : dossier_ppe, 
                "dossier": dossier,
                "geolocalisation_ppe": geolocalisation_ppe})
        else:
            return render(request, "ppe/modification.html", {"error_message" : "Il manque l'identifiant du dossier."})
    except:
        return render(request, "ppe/modification.html")


def contact_principal(request):
    error_message = None
    notaire_form = NotaireForm(request.POST, prefix='notaire')
    contact_form = ContactPrincipalForm(request.POST, prefix='contact')
    signataire_form = SignataireForm(request.POST, prefix='signataire')
    facturation_form = AdresseFacturationForm(request.POST, prefix='facturation')
    accord_form = AccordFraisForm(request.POST, request.FILES, prefix='accord')

    if (contact_form.is_valid() and
        notaire_form.is_valid() and
        signataire_form.is_valid() and
        facturation_form.is_valid() and 
        accord_form.is_valid()):

        geolocalisation_ppe = ast.literal_eval(request.POST["localisation_ppe"])

        login_code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + '._-') for _ in range(16))

        contact_form.save()
        notaire_form.save()
        signataire_form.save()
        facturation_form.save()
        accord_form.save()

        new_dossier_ppe = DossierPPE()
        new_dossier_ppe.login_code = login_code
        new_dossier_ppe.egrid = geolocalisation_ppe["egrid"]
        new_dossier_ppe.cadastre = geolocalisation_ppe["cadastre"]
        new_dossier_ppe.commune = geolocalisation_ppe["commune"]
        new_dossier_ppe.numcad = geolocalisation_ppe["numcad"]
        new_dossier_ppe.nummai = geolocalisation_ppe["nummai"]
        new_dossier_ppe.coord_E = geolocalisation_ppe["coord_est"]
        new_dossier_ppe.coord_N = geolocalisation_ppe["coord_nord"]
        new_dossier_ppe.contact_principal = ContactPrincipal(pk=contact_form.instance.id)
        new_dossier_ppe.notaire = Notaire(pk=notaire_form.instance.id)
        new_dossier_ppe.signataire = Signataire(pk=signataire_form.instance.id)
        new_dossier_ppe.adresse_facturation = AdresseFacturation(pk=facturation_form.instance.id)
        new_dossier_ppe.accord_frais = AccordFrais(pk=accord_form.instance.id)
        new_dossier_ppe.statut = 'P'
        new_dossier_ppe.type_dossier = "C"
        new_dossier_ppe.date_creation = datetime.datetime.now()
        new_dossier_ppe.geom = Point(geolocalisation_ppe["coordinates"])
        new_dossier_ppe.save()

        request.session['login_code'] = login_code
        return redirect(f'/ppe/overview')

    if 'geom' in request.POST:
        try:
            # Check if a localisation exists
            localisation = request.POST["geom"]
            print(localisation)
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
                        "accord_form": AccordFraisForm(prefix='accord'),
                        "localisation_ppe": get_localisation(localisation)
                    }
                )
            else:
                error_message = "La localisation n'a pas donné de résultat"
        except Exception as e:
            # Redisplay the question voting form.
            logger.warning(f"Error during geoloc. decoding : {repr(e)}")
            error_message = "Une erreur est survenue lors de la création du formulaire."

    return redirect(f'/ppe/geolocalisation', {"error_message": error_message})
    
        

def login(request):
    if 'login_code' in request.POST:
        request.session['login_code'] = request.POST['login_code']
        return redirect("/ppe/detail")
    return render(request, "ppe/login.html")

@login_required
def detail(request, doc):
    return render(request, "ppe/detail.html", {"dossier_ppe": doc})

@login_required
def overview(request, doc):
    return render(request, "ppe/overview.html", {"overview": doc})

@login_required
def soumission(request, doc):
    return render(request, "ppe/soumission.html", {"dossier_ppe": doc})

@login_required
def definition_type_dossier(request, doc, type_dossier=None):
    if type_dossier is None:
        type_dossier = doc.type_dossier

    try:
        id_unique = request.GET["id_unique"] if 'id_unique' in request.GET else id_dossier
        type_dossier = request.GET["type_dossier"] if 'type_dossier' in request.GET else dossier_ppe.type_dossier
        ref_geoshop = request.GET["ref_geoshop"] if 'ref_geoshop' in request.GET else None
    except:
        error_message = "Veuillez saisir le type de dossier PPE"

    # TODO: handle other cases
    results = {
        "id_unique": id_unique,
        "type_dossier": type_dossier,
        "ref_geoshop": ref_geoshop
    }

    if type_dossier != '':
        #if type_dossier == 'M':
    
        return load_ppe_files(request, id, results)
    else:
        return render(request, "ppe/definition_type_dossier.html", {"dossier_ppe": doc, "type_dossier": type_dossier })

@login_required
def load_ppe_files(request, doc, results):
    """ Function to load the zip file with the PPE documents"""
    results = results
    return render(request, "ppe/load_ppe_files.html", {"dossier_ppe": doc, "results": results})

    

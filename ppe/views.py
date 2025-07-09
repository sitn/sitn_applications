import datetime, random, string, json, logging, ast
from django.shortcuts import render, redirect, get_list_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.gis.geos import Point
from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import FileSystemStorage

# INDIVIDUAL ELEMENTS
from .models import DossierPPE, ContactPrincipal, Notaire, Signataire, AdresseFacturation, Geolocalisation, Zipfile
from .forms import AdresseFacturationForm, NotaireForm, SignataireForm, GeolocalisationForm, ContactPrincipalForm, ZipfileForm, WMTSWithSearchWidget

from .util import get_localisation, login_required, check_geoshop_ref

logger = logging.getLogger(__name__)

def index(request):
    # A list for the PPE admins to see the latest demands
    # TODO : This should only be visible to admins
    request.session['login_code'] = None
    latest_dossiers_list = DossierPPE.objects.order_by("-date_creation")[:5]
    template = loader.get_template("ppe/index.html")
    return HttpResponse(template.render({"latest_dossiers_list": latest_dossiers_list}, request))

def geolocalisation(request):
    # if this is a POST request we need to process the form data
    error_message = None
    localisation_ppe = None
    geo_form = GeolocalisationForm(request.POST)
    form_action = 'geolocalisation'

    if 'geom' in request.POST:
        localisation = request.POST['geom']
        #geo_form = GeolocalisationForm(request.POST)
        if geo_form.is_valid():
            geo_form.save(commit=False)
        # Convert an existing localisation to a JSON dict
        if isinstance(localisation, str) and localisation != '':
            localisation = json.loads(localisation)
            localisation_ppe = get_localisation(localisation)
        form_action = 'contact_principal'

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
        request.session['login_code'] = None
        request.session['login_code'] = request.POST['login_code'].strip()
        try:
            doc = DossierPPE.objects.get(login_code=request.session['login_code'])
            return redirect(f"/ppe/overview", {"dossier_ppe": doc})
        except Exception as e:
            # Redisplay the geolocalisation form.
            logger.warning(f"Error fetching the file : {repr(e)}")
    return render(request, "ppe/login.html")

@login_required
def detail(request, doc):
    return render(request, "ppe/detail.html", {"dossier_ppe": doc})

@login_required
def overview(request, doc):

    try: 
        zips =  Zipfile.objects.filter(dossier_ppe_id=doc.id).order_by('-upload_date')
    except Exception as e:
        logger.warning(f"Error finding a zip : {repr(e)}")

    if len(zips) > 0:
        doc.zipfiles = zips

    return render(request, "ppe/overview.html", {"dossier_ppe": doc})

@login_required
def soumission(request, doc):
    return render(request, "ppe/soumission.html", {"dossier_ppe": doc})

@login_required
def definition_type_dossier(request, doc, type_dossier=None):
    error_message = None
    type_dossier = request.POST["type_dossier"] if 'type_dossier' in request.POST else None
    ref_geoshop = request.POST["ref_geoshop"] if 'ref_geoshop' in request.POST else None
    revision_jouissances = request.POST["droits_jouissance"] if 'droits_jouissance' in request.POST else None 
    elements_rf_identiques = request.POST["elements_rf"] if 'elements_rf' in request.POST else None
    nouveaux_droits = request.POST["new_jouissance"] if 'new_jouissance' in request.POST else None

    try:
        # We get the current entry of the dossier ppe if it exists
        dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
    except:
        # ELSE we return an error
        error_message = "Aucun dossier avec ce code n'a pu être trouvé."
        return render(request, "ppe/definition_type_dossier.html", {"error_message": error_message})  

    if type_dossier == 'C' and ref_geoshop is not None:
        dossier_ppe.type_dossier = type_dossier

        #TODO: Check geoshop_ref is existing
        ref_exists = check_geoshop_ref(ref_geoshop)
        if ref_exists == True:
            #dossier_ppe.elements_rf_identiques = None
            #dossier_ppe.nouveaux_droits = None
            #dossier_ppe.revision_jouissances = None
            dossier_ppe.save()
            return redirect("/ppe/overview")
        else:
            error_message = "La référence de la commande géoshop contient une erreur ou n'existe pas."
    
    elif type_dossier in ['M','R'] and 'login_code' in request.POST:
        login_code = request.POST['login_code']
        dossier_ppe.elements_rf_identiques = elements_rf_identiques
        dossier_ppe.nouveaux_droits = nouveaux_droits
        dossier_ppe.revision_jouissances = revision_jouissances
        dossier_ppe.save()
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
    zipfile = None
    
    zip_form = ZipfileForm(request.POST, request.FILES or None)
    doc = DossierPPE.objects.get(login_code=doc.login_code)
    init_data = {"dossier_ppe": DossierPPE(pk=doc.id)}

    if zip_form.is_valid():
        zip_form.save()
        zipfile = Zipfile(pk=zip_form.instance.id)

        return render(request, "ppe/load_ppe_files.html", {"dossier_ppe" : doc, "zipfile": zipfile })

    zip_form = ZipfileForm(initial=init_data)

    return render(request, "ppe/load_ppe_files.html", {"dossier_ppe" : doc, "zip_form": zip_form})

@login_required
def edit_geolocalisation(request, doc):
    error_message = None
    localisation_ppe = None

    try:
        # We get the current entry of the dossier ppe if it exists
        dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
    except:
        # ELSE we return an error
        error_message = "Aucun dossier avec ce code n'a pu être trouvé. "+ doc.login_code
        return render(request, "ppe/geolocalisation.html", {"dossier_ppe": doc, "error_message": error_message})  

    if 'geom' in request.POST:
        localisation = request.POST['geom']
        geo_form = GeolocalisationForm(request.POST)
        if geo_form.is_valid():
            geo_form.save(commit=False)
            # Convert an existing localisation to a JSON dict
            if isinstance(localisation, str) and localisation != '':
                localisation = json.loads(localisation)
                localisation_ppe = get_localisation(localisation)
                #geolocalisation_ppe = ast.literal_eval(localisation_ppe)
                dossier_ppe.cadastre = localisation_ppe["cadastre"]
                dossier_ppe.numcad = localisation_ppe["numcad"]
                dossier_ppe.nummai = localisation_ppe["nummai"]
                dossier_ppe.coord_E = localisation_ppe["coord_est"]
                dossier_ppe.coord_N = localisation_ppe["coord_nord"]
                dossier_ppe.date_creation = datetime.datetime.now()
                dossier_ppe.geom = Point(localisation_ppe["coordinates"])
                dossier_ppe.save()
            form_action = 'overview'
            return redirect(f"/ppe/overview")
    else:
        if doc.geom is not None:
            init_data={"geom": doc.geom}
            geo_form = GeolocalisationForm(initial=init_data)

    return render(
        request,
        "ppe/geolocalisation.html",
        {
            "error_message": error_message,
            "localisation_ppe": localisation_ppe,
            "form": geo_form,
            "form_action": 'edit_geolocalisation',
            "doc": doc
        }
    )

@login_required
def edit_contacts(request, doc):
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

                return redirect(f'/ppe/overview', dossier_ppe)

        return render(request, "ppe/modification.html", {
            "error_message": error_message,
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

@login_required
def edit_ppe_type(request, doc):
    error_message = None

    try:
        # We get the current entry of the dossier ppe if it exists
        dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
        elements_rf_identiques = request.POST["elements_rf_identiques"] if 'elements_rf_identiques' in request.POST else dossier_ppe.elements_rf_identiques
        print(elements_rf_identiques)
        nouveaux_droits = request.POST["nouveaux_droits"] if 'nouveaux_droits' in request.POST else dossier_ppe.nouveaux_droits
        revision_jouissances = request.POST["revision_jouissances"] if 'revision_jouissances' in request.POST else dossier_ppe.revision_jouissances
    except:
        # ELSE we return an error
        error_message = "Aucun dossier avec ce code n'a pu être trouvé."
        return render(request, "ppe/definition_type_dossier.html", {"error_message": error_message})  

    if 'type_dossier' in request.POST and request.POST["type_dossier"] in ('C','M','R'):
        type_dossier = request.POST["type_dossier"]
        dossier_ppe.elements_rf_identiques = elements_rf_identiques
        dossier_ppe.nouveaux_droits = nouveaux_droits
        dossier_ppe.revision_jouissances = revision_jouissances
        dossier_ppe.type_dossier = type_dossier
        print('=== IF ===')
        print(elements_rf_identiques)
        print(dossier_ppe.revision_jouissances)
        dossier_ppe.save()
        
        return redirect(f"/ppe/overview")
    else: 
        return render(request, "ppe/definition_type_dossier.html", {"dossier_ppe": doc})
    

@login_required
def edit_zipfile(request, doc):
    """ Replace the zip file with PPE documents by a newer version """
    error_message = None
    zipfile = None
    
    zip_form = ZipfileForm(request.POST, request.FILES or None)
    doc = DossierPPE.objects.get(login_code=doc.login_code)
    init_data = {"dossier_ppe": DossierPPE(pk=doc.id)}

    if zip_form.is_valid():
        zip_form.save()
        zipfile = Zipfile(pk=zip_form.instance.id)

        return render(request, "ppe/load_ppe_files.html", {"dossier_ppe" : doc, "zipfile": zipfile })

    zip_form = ZipfileForm(initial=init_data)

    return render(request, "ppe/load_ppe_files.html", {"dossier_ppe" : doc, "zip_form": zip_form})
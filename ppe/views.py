import datetime, random, string, json, logging, ast
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.gis.geos import Point
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.core.mail import EmailMultiAlternatives

# INDIVIDUAL ELEMENTS
from .models import DossierPPE, ContactPrincipal, Notaire, Signataire, AdresseFacturation, Zipfile
from .forms import AdminLoginForm, AdresseFacturationForm, NotaireForm, SignataireForm, GeolocalisationForm, ContactPrincipalForm, ZipfileForm
from urllib.request import urlopen
from .util import get_localisation, login_required, check_geoshop_ref

logger = logging.getLogger(__name__)

ZIP_STATUS_LABELS = {
    "CAA": "Contrôle automatique : dossier archivé",
    "CAC": "Contrôle automatique : en cours",
    "CAE": "Contrôle automatique : erreurs à corriger",
    "ERR": "Contrôle automatique : erreur interne",
    "CAV": "Contrôle automatique : validé",
    "CMS": "Contrôle manuel : en cours (S)",
    "CMC": "Contrôle manuel : en cours",
    "CME": "Contrôle manuel : erreurs à corriger",
    "CMV": "Contrôle manuel : validé",
    "DPV": "Dossier papier validé",
}

def index(request):
    # A list for the PPE admins to see the latest demands
    request.session['login_code'] = None

    if request.user.is_authenticated:
        latest_dossiers_list = DossierPPE.objects.order_by("-date_creation")[:15]
    else:
        latest_dossiers_list = None

    template = loader.get_template("ppe/index.html")
    return HttpResponse(template.render({"latest_dossiers_list": latest_dossiers_list}, request))


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('ppe:index')

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('ppe:index')
        else:
            return render(request, 'ppe/admin_login.html', {
                'form': form,
                'error_message': "Identifiants incorrects"
            })
    else:
        form = AdminLoginForm()

    return render(request, 'ppe/admin_login.html', {'form': form})


def admin_logout(request):
    auth_logout(request)
    return redirect('ppe:index')


def set_geolocalisation(request):
    # if this is a POST request we need to process the form data
    error_message = None
    localisation_ppe = None
    geo_form = GeolocalisationForm(request.POST)
    form_action = 'set_geolocalisation'
    mode = 'init'

    if 'geom' in request.POST:
        localisation = request.POST['geom']
        #geo_form = GeolocalisationForm(request.POST)
        if geo_form.is_valid():
            geo_form.save(commit=False)
        # Convert an existing localisation to a JSON dict
        if isinstance(localisation, str) and localisation != '':
            localisation = json.loads(localisation)
            localisation_ppe = get_localisation(localisation)
        check_geolocalisation(request)
        if request.POST['geom'] == '':
            form_action = 'set_geolocalisation'
            mode = 'reset'
        else:
            form_action = 'contact_principal'

    return render(
        request,
        "ppe/geolocalisation.html",
        {
            "error_message": error_message,
            "localisation_ppe": localisation_ppe,
            "form": geo_form,
            "form_action": form_action,
            "mode": mode
        }
    )

def check_geolocalisation(request):
    # TODO: Validate that the selected point is inside the cantonal border
    return

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

                    return redirect('ppe:definition_type_dossier')
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
            "geolocalisation_ppe": doc.geom
        })

    except:
        return render(request, "ppe/modification.html", {"error_message": "Il manque l'identifiant du dossier."})


def contact_principal(request):
    """ Checks the geolocation and if ok handles the contact information """

    if 'geom' in request.POST:
        nummai = request.POST.get("nummai")
        if nummai is None:
            raise BadRequest("Aucun numéro de bien-fonds n'a été trouvé")
        # Check if a localisation exists
        localisation = request.POST["geom"]
        # Convert an existing localisation to a JSON dict
        if isinstance(localisation, str) and localisation != '':
            localisation = json.loads(localisation)
        # Fetch geolocalisation calling the satac service
        if (localisation is not None) and ('coordinates' in localisation):
            localisation_ppe = get_localisation(localisation)
            localisation_ppe['nummai'] = nummai
            return render(
                request, 
                "ppe/contact_principal.html", 
                {
                    "contact_form": ContactPrincipalForm(prefix='contact'),
                    "notaire_form": NotaireForm(prefix='notaire'),
                    "signataire_form": SignataireForm(prefix='signataire'),
                    "facturation_form": AdresseFacturationForm(prefix='facturation'),
                    "localisation_ppe": localisation_ppe
                }
            )
        else:
            raise BadRequest("La localisation n'a pas donné de résultat")
    
    notaire_form = NotaireForm(request.POST, prefix='notaire')
    contact_form = ContactPrincipalForm(request.POST, prefix='contact')
    signataire_form = SignataireForm(request.POST, prefix='signataire')
    facturation_form = AdresseFacturationForm(request.POST, request.FILES, prefix='facturation')

    if not contact_form.is_valid():
        raise BadRequest(contact_form.errors)
    
    if not notaire_form.is_valid():
        raise BadRequest(notaire_form.errors)
    
    if not signataire_form.is_valid():
        raise BadRequest(signataire_form.errors)
    
    if not facturation_form.is_valid():
        raise BadRequest(facturation_form.errors)

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
    new_dossier_ppe.type_dossier = 'I'
    new_dossier_ppe.aff_infolica = 0
    new_dossier_ppe.date_creation = datetime.datetime.now()
    new_dossier_ppe.geom = Point(geolocalisation_ppe["coordinates"])
    new_dossier_ppe.save()
    request.session['login_code'] = login_code
    return redirect('ppe:definition_type_dossier')


def login(request):
    if 'login_code' in request.POST:
        request.session['login_code'] = request.POST['login_code']
        try:
            doc = DossierPPE.objects.get(login_code=request.session['login_code'])
            return redirect("ppe:overview")
        except Exception as e:
            # Redisplay the geolocalisation form.
            logger.warning(f"Error fetching the file : {repr(e)}")
    return render(request, "ppe/login.html")

@login_required
def detail(request, doc):
    return render(request, "ppe/detail.html", {"dossier_ppe": doc})

@login_required
def overview(request, doc):
    error_message = None
    dossier_initial = None
    # GET initial PPE Dossier data if type is modification
    if doc.type_dossier == 'M':
        try:
            dossier_initial = get_object_or_404(DossierPPE, pk=doc.ref_dossier_initial)
        except:
            error_message = "Aucun dossier PPE de référence n\'a été trouvé pour cette demande de modification."
            return render(request, "ppe/overview.html", {"dossier_ppe": doc, "error_message": error_message})

    return render(request, "ppe/overview.html", {"dossier_ppe": doc, "dossier_initial": dossier_initial, "error_message": error_message})

@login_required
def soumission(request, doc):
    # Set the mail subject
    mail_subject = "Nouveau dossier PPE : création réussie"
    default_sender = settings.DEFAULT_FROM_EMAIL if settings.DEFAULT_FROM_EMAIL else 'no-reply-ppe@ne.ch'

    # First, render the plain text content.
    text_content = f"Vous venez de créer un nouveau dossier PPE sur l'application PETITNOMJOLIATROUVER \
        \nCadastre {doc.cadastre} \nBien-fonds : {doc.nummai} \nType de dossier : {doc.get_type_dossier_display}\n \
        Son identifiant unique est : {doc.login_code} \
        \nAttention : Gardez bien ce code, vous en avez besoin pour tout changement.\
        \nRendez-vous sur https://sitn.ne.ch/apps/ppe pour modifier votre \
        dossier."

    # Secondly, render the HTML content.
    html_content = f"<p>Vous venez de créer un nouveau dossier PPE sur l'application PETITNOMJOLIATROUVER</p> \
        <p>Cadastre : {doc.cadastre}<br> \
            Bien-fonds : {doc.nummai}<br> \
            Type de dossier : {doc.get_type_dossier_display}</p> \
        <p>Son identifiant unique est :</p> <h2 id=\"login_code\">{doc.login_code}</h2> <p><b>Attention :</b> \
        Gardez bien ce code, vous en avez besoin pour tout changement.</p> \
        <p>Rendez-vous sur <a href=\"https://sitn.ne.ch/apps/ppe\" target=\"_blank\">https://sitn.ne.ch/apps/ppe</a> \
        pour modifier votre dossier."

    # Then, create a multipart email instance.
    msg = EmailMultiAlternatives(
        mail_subject,
        text_content,
        default_sender,
        [doc.contact_principal.email, "francois.voisard@ne.ch"],    )
    print(msg)
    # Lastly, attach the HTML content to the email instance and send.
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return render(request, "ppe/soumission.html", {"dossier_ppe": doc})

@login_required
def definition_type_dossier(request, doc, type_dossier=None):
    """ Definition of the PPE submission type """
    error_message = None
    type_dossier = request.POST["type_dossier"] if 'type_dossier' in request.POST else None
    code_initial = request.POST["initial_code"] if 'initial_code' in request.POST else None
    ref_geoshop = request.POST["ref_geoshop"] if 'ref_geoshop' in request.POST else None
    revision_jouissances = request.POST["droits_jouissance"] if 'droits_jouissance' in request.POST else None 
    elements_rf_identiques = request.POST["elements_rf"] if 'elements_rf' in request.POST else None
    nouveaux_droits = request.POST["new_jouissance"] if 'new_jouissance' in request.POST else None

    try:
        # We get the current entry of the dossier ppe if it exists
        dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
        logger.debug('CHECK for existing dossier ppe %s', doc.login_code)
    except:
        # ELSE we return an error
        error_message = "Aucun dossier avec ce code n'a pu être trouvé."
        logger.debug('DID NOT FIND a dossier ppe with code: %s. Error was: %s', doc.login_code, error_message)
        return render(request, "ppe/definition_type_dossier.html", {"error_message": error_message})  

    if ref_geoshop is not None:
        # Check geoshop_ref is existing
        logger.debug('CHECK if given geoshop ref %s exists and is valid for this real estate')
        ref_exists, ref_error = check_geoshop_ref(ref_geoshop, doc.geom)
        if ref_exists == False:
            error_message = ref_error
    else:
        ref_exists = False

    if type_dossier == 'C' and ref_exists == True:
        dossier_ppe.type_dossier = type_dossier
        dossier_ppe.elements_rf_identiques = None
        dossier_ppe.nouveaux_droits = None
        dossier_ppe.revision_jouissances = None
        dossier_ppe.ref_geoshop = ref_geoshop
        dossier_ppe.save()
        return redirect('ppe:overview')

    elif type_dossier == 'M' and code_initial is not None:
        # GET the inital DossierPPE to be replaced or return an error
        try: 
            dossier_ppe_initial = DossierPPE.objects.get(login_code=code_initial)
        except:
            error_message = "La référence de commande indiquée n'existe pas."

        # Check if the geolocation of the new submission is the same as the initial one
        if (dossier_ppe.cadastre == dossier_ppe_initial.cadastre and dossier_ppe.nummai == dossier_ppe_initial.nummai):
            dossier_ppe.ref_geoshop = None
            dossier_ppe.type_dossier = type_dossier
            dossier_ppe.ref_dossier_initial = dossier_ppe_initial.id
            dossier_ppe.save()
            return redirect("ppe:overview")
        else:
            error_message = "Le numéro de bien-fonds n'est pas le même que dans le dossier d'origine."    

    elif type_dossier == 'R':
        dossier_ppe.type_dossier = type_dossier
        dossier_ppe.elements_rf_identiques = elements_rf_identiques
        dossier_ppe.nouveaux_droits = nouveaux_droits
        dossier_ppe.revision_jouissances = revision_jouissances
        if ref_exists == False:
            error_message = "La référence de commande indiquée n\'existe pas."
        if elements_rf_identiques == 'non' and ref_exists == True:
            dossier_ppe.ref_geoshop = ref_geoshop
        dossier_ppe.save()
        return redirect("ppe:overview")
    
    else:
        error_message = 'Le type de dossier PPE ne semble pas encore défini.'

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
def load_zipfile(request, doc):
    """ Function to load the zip file with the PPE documents"""
    zip_form = ZipfileForm(request.POST, request.FILES or None)
    doc = DossierPPE.objects.get(login_code=doc.login_code)
    init_data = {"dossier_ppe": DossierPPE(pk=doc.id)}
    if zip_form.is_valid():
        zip_form.save()
        Zipfile(pk=zip_form.instance.id)
        return render(request, "ppe/submited.html", {"dossier_ppe" : doc})
    # TODO VCRON ajouter un trigger sur statut CAC
    # TODO: zip_form.errors probablement intéressant pour l'utilisateur
    zip_form = ZipfileForm(initial=init_data)
    return render(request, "ppe/load_zipfile.html", {"dossier_ppe" : doc, "zip_form": zip_form})

@login_required
def submit_for_validation(request, doc):
    # TODO VCRON ajouter un trigger sur statut CMC
    """ Function to start the manual validation process by a employee """
    logger.debug('Submitting dossier %s for manual check', doc.id)
    # GET all the zipfiles and set the automatically validated 'CAV' to manual check status 'CMC'
    try: 
        zip =  Zipfile.objects.filter(dossier_ppe_id=doc.id,file_statut='CAV').order_by('-upload_date').first()
    except Exception as e:
        logger.warning(f"Error finding a zip : {repr(e)}")

    zip.file_statut = 'CMS'
    zip.save()

    # Set the application's status to submitted for manual validation 'S'
    doc.statut = 'S'
    doc.date_soumission = datetime.datetime.now()
    doc.save()
    return redirect("ppe:overview")

@login_required
def edit_geolocalisation(request, doc):
    """ Modify the geolocation of an existing submission"""
    error_message = None
    localisation_ppe = None

    try:
        # We get the current entry of the dossier ppe if it exists
        dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
    except:
        # ELSE we return an error
        error_message = "Aucun dossier avec ce code n'a pu être trouvé. "+ doc.login_code
        return render(request, "ppe/geolocalisation.html", {"dossier_ppe": doc, "error_message": error_message})  

    # When the function is first called geom and nummai are None
    # When the function is called to reset location geom and nummai are empty strings
    # When the function is called to validate a new location geom has a value nummai is empty
    # Lastly, when geom and nummai have values we set the new location and continue
    if 'geom' in request.POST:
        localisation = request.POST['geom']
        geo_form = GeolocalisationForm(request.POST)
        if isinstance(localisation, str) and localisation != '':
            localisation = json.loads(localisation)
            localisation_ppe = get_localisation(localisation)

        if 'nummai' in request.POST and localisation != '':
            localisation_ppe["nummai"] = request.POST['nummai']
            if geo_form.is_valid():
                geo_form.save(commit=False)
                # Convert an existing localisation to a JSON dict
                dossier_ppe.cadastre = localisation_ppe["cadastre"]
                dossier_ppe.numcad = localisation_ppe["numcad"]
                dossier_ppe.nummai = localisation_ppe["nummai"]
                dossier_ppe.coord_E = localisation_ppe["coord_est"]
                dossier_ppe.coord_N = localisation_ppe["coord_nord"]
                dossier_ppe.date_creation = datetime.datetime.now()
                dossier_ppe.geom = Point(localisation_ppe["coordinates"])
                dossier_ppe.save()
                return redirect("ppe:overview")
        else:
            return render(request, "ppe/geolocalisation.html", {
                "error_message": error_message,
                "localisation_ppe": localisation_ppe,
                "form": geo_form,
                "form_action": 'edit_geolocalisation',
                "doc": doc,
                "mode": 'edit' if localisation != '' else 'reset'
            })
    else:
        if doc.geom is not None:
            init_data={"geom": doc.geom}
            geo_form = GeolocalisationForm(initial=init_data)
            localisation_ppe = {'bien_fonds': {'nummai': doc.nummai}, 'cadastre': doc.cadastre}

    return render(request, "ppe/geolocalisation.html", {
        "error_message": error_message,
        "localisation_ppe": localisation_ppe,
        "form": geo_form,
        "form_action": 'edit_geolocalisation',
        "doc": doc,
        "mode": 'edit'
    })

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

                return redirect('ppe:overview', dossier_ppe)

        return render(request, "ppe/modification.html", {
            "error_message": error_message,
            "dossier": doc,
            "contact_form": ContactPrincipalForm(instance=doc.contact_principal, prefix='contact'),
            "notaire_form": NotaireForm(instance=doc.notaire, prefix='notaire'),
            "signataire_form": SignataireForm(instance=doc.signataire, prefix='signataire'),
            "facturation_form": AdresseFacturationForm(instance=doc.adresse_facturation, prefix='facturation'),
            "cadastre": doc.cadastre,
            "nummai": doc.nummai,
            "geolocalisation_ppe": doc.geom
        })
    except:
        return render(request, "ppe/modification.html", {"error_message": "Il manque l'identifiant du dossier."})

@login_required
def edit_ppe_type(request, doc):
    error_message = None
    ref_exists = False
    ref_error = None
    
    try:
        # We get the current entry of the dossier ppe if it exists
        dossier_ppe = DossierPPE.objects.get(login_code=doc.login_code)
        code_initial = request.POST["initial_code"].strip() if 'initial_code' in request.POST else None
        type_dossier = request.POST["type_dossier"] if 'type_dossier' in request.POST else None
        ref_geoshop = request.POST["ref_geoshop"] if 'ref_geoshop' in request.POST else None
        revision_jouissances = request.POST["droits_jouissance"] if 'droits_jouissance' in request.POST else None 
        elements_rf_identiques = request.POST["elements_rf"] if 'elements_rf' in request.POST else None
        nouveaux_droits = request.POST["new_jouissance"] if 'new_jouissance' in request.POST else None
    except:
        # ELSE we return an error
        error_message = "Aucun dossier avec ce code n'a pu être trouvé."
        return render(request, "ppe/definition_type_dossier.html", {"error_message": error_message})

    request.session['type_dossier'] = type_dossier

    if ref_geoshop:
        ref_error = None
        logger.info('> CHECK REF GEOSHOP: %s', ref_geoshop)
        ref_exists, ref_error = check_geoshop_ref(ref_geoshop, doc.geom)
        if ref_error:
            error_message = ref_error
            logger.debug("GEOSHOP_REF check failed with error %s", error_message)

    logger.info("GEOSHOP_REF %s exists: %s", ref_geoshop, ref_exists)

    logger.info("> Submission type is %s, ref_exists is %s, elements_rf_identiques is %s",
                 type_dossier, ref_exists, elements_rf_identiques
                 )
    
    if type_dossier == 'C' and ref_exists == True:
        dossier_ppe.elements_rf_identiques = None
        dossier_ppe.nouveaux_droits = None
        dossier_ppe.revision_jouissances = None
        dossier_ppe.type_dossier = type_dossier
        dossier_ppe.ref_geoshop = ref_geoshop
        dossier_ppe.save()
        return redirect("ppe:overview")

    if type_dossier == 'R':
        # Be sure to set back the different values on changes
        dossier_ppe.ref_geoshop = None
        dossier_ppe.ref_dossier_initial = None
        dossier_ppe.elements_rf_identiques = None
        dossier_ppe.nouveaux_droits = None
        dossier_ppe.revision_jouissances = None

        dossier_ppe.type_dossier = type_dossier
        dossier_ppe.elements_rf_identiques = elements_rf_identiques
        dossier_ppe.nouveaux_droits = nouveaux_droits
        dossier_ppe.revision_jouissances = revision_jouissances

        if ref_exists == False and not ref_error is None :
            error_message = ref_error
        if elements_rf_identiques == 'non' and ref_exists == True:
            dossier_ppe.ref_geoshop = ref_geoshop
        dossier_ppe.save()
        return redirect("ppe:overview")

    if type_dossier == 'M' and code_initial is not None:
        # GET the inital DossierPPE to be replaced or return an error
        try:
            dossier_ppe_initial = DossierPPE.objects.get(login_code=code_initial)
            if dossier_ppe.id == dossier_ppe_initial.id :
                error_message = "Le dossier actuel et le dossier initial ne peuvent pas être identiques."
                return render(
                    request, 
                    "ppe/definition_type_dossier.html", 
                    {"dossier_ppe": doc, "mode": 'edit', "error_message" : error_message}
                    )

            # Check if the geolocation of the new submission is the same as the initial one,
            # if so, save the modification with the initial reference
            if (dossier_ppe.cadastre == dossier_ppe_initial.cadastre and dossier_ppe.nummai == dossier_ppe_initial.nummai):
                dossier_ppe.ref_geoshop = None
                dossier_ppe.elements_rf_identiques = None
                dossier_ppe.nouveaux_droits = None
                dossier_ppe.revision_jouissances = None
                dossier_ppe.type_dossier = type_dossier
                dossier_ppe.ref_dossier_initial = dossier_ppe_initial.id
                dossier_ppe.save()
                return redirect("ppe:overview")
            else:
                error_message = "Le numéro de bien-fonds n'est pas le même que dans le dossier d'origine." 

        except ObjectDoesNotExist:
            error_message = "Ce numéro de dossier n\'existe pas."

    if not error_message is None:
        doc.type_dossier = request.session['type_dossier']
    return render(
        request, 
        "ppe/definition_type_dossier.html", 
        {"dossier_ppe": doc, "mode": 'edit', "error_message" : error_message}
    )
    

@login_required
def edit_zipfile(request, doc):
    """ Replace the zip file with PPE documents by a newer version """
    zip_form = ZipfileForm(request.POST, request.FILES or None)
    doc = DossierPPE.objects.get(login_code=doc.login_code)
    init_data = {"dossier_ppe": DossierPPE(pk=doc.id)}

    if zip_form.is_valid():
        zip_form.save()
        Zipfile(pk=zip_form.instance.id)
        return render(request, "ppe/submited.html", {"dossier_ppe" : doc})
    
    # TODO zip_form.errors?

    zip_form = ZipfileForm(initial=init_data)

    return render(request, "ppe/load_zipfile.html", {"dossier_ppe" : doc, "zip_form": zip_form})


@login_required
def zip_status(request, doc):
    dossier_ppe = get_object_or_404(DossierPPE, pk=doc.id)
    zip = doc.zipfiles.order_by('-upload_date').first()
    zip.label = ZIP_STATUS_LABELS.get(
        zip.file_statut,
        "Erreur inconnue sur le statut des fichiers zip"
    )

    return render(
        request,
        "ppe/zip_status.html",
        {
            "zip": zip,
            "dossier_ppe": dossier_ppe,
            "refreshed_at": datetime.datetime.now(),
        },
    )
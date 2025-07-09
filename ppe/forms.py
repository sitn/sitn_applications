from django.contrib.gis import forms
from django_extended_ol.forms.widgets import WMTSWithSearchWidget

from .models import DossierPPE, Geolocalisation, AdresseFacturation, Zipfile
from .models import ContactPrincipal, Notaire, Signataire

from django.utils.translation import gettext_lazy as _


class ZipfileForm(forms.ModelForm):
    class Meta:
        model = Zipfile
        prefix = "zip"
        fields = "__all__"
        widgets = {
            'upload_date': forms.HiddenInput(),
            'file_statut': forms.HiddenInput(),
            'dossier_ppe': forms.HiddenInput()
            }
        labels = {
            "zipfile": _("Dossier zip des plans"),
        }


class GeolocalisationForm(forms.ModelForm):
    geom = forms.PointField(widget=WMTSWithSearchWidget(attrs={"geom": ""}))
    class Meta: 
        model = Geolocalisation
        fields = "__all__"
        labels = {
           # "geom": _(""),
        }

class AdresseFacturationForm(forms.ModelForm):
    class Meta:
        model = AdresseFacturation
        prefix = "facturation"
        fields = fields = "__all__"
        labels = {
            "nom_raison_sociale": _("Nom / raison sociale *"),
            "prenom": _("Prénom / à l'att. *"),
            "complement": _("Complément/Réf."),
            "rue": _("Rue *"),
            "no_rue": _("No. rue"),
            "npa": _("NPA *"),
            "localite": _("Localité *"),
            "file": _("Accord de prise en charge *"),
        }
        #help_texts = {
        #    "complement": _("Case postale, appt., unité, etc."),
        #    "file": _("Document"),
        #}
        error_messages = {
            "complement": {
                "max_length": _("Le contenu du champ est trop long."),
            },
        }

class ContactPrincipalForm(forms.ModelForm):
    class Meta:
        model = ContactPrincipal
        prefix="contact"
        fields = fields = "__all__"
        labels = {
            "nom": _("Nom *"),
            "prenom": _("Prénom *"),
            "complement": _("Complément"),
            "email": _("Courriel *"),
            "no_tel": _("No. tél *"),
        }

class NotaireForm(forms.ModelForm):
    class Meta:
        model = Notaire
        prefix="notaire"
        fields = fields = "__all__"
        labels = {
            "nom": _("Nom *"),
            "prenom": _("Prénom *"),
            "complement": _("Complément"),
            "rue": _("Rue *"),
            "no_rue": _("No. rue"),
            "npa": _("NPA *"),
            "localite": _("Localité *"),
        }

class SignataireForm(forms.ModelForm):
    class Meta:
        model = Signataire
        prefix="signataire"
        fields = fields = "__all__"
        labels = {
            "nom": _("Nom *"),
            "prenom": _("Prénom *"),
            "complement": _("Complément"),
            "rue": _("Rue *"),
            "no_rue": _("No. rue"),
            "npa": _("NPA *"),
            "localite": _("Localité *"),
        }

class DossierPPEForm(forms.ModelForm):
    geom = forms.PointField(widget=WMTSWithSearchWidget())
    class Meta: 
        model = DossierPPE
        fields = [
            'cadastre',
            'numcad',
            'nummai',
            'coord_E',
            'coord_N',
            'statut',
            'type_dossier',
            'contact_principal',
            'signataire',
            'notaire',
            'adresse_facturation',
            #'date_creation',
            #'date_soumission',
            #'date_validation,
        ]
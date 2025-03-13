from django.contrib.gis import forms
from django_extended_ol.forms.widgets import WMTSWidget

from .models import DossierPPE, Geolocalisation, AccordFrais, AdresseFacturation
from .models import ContactPrincipal, Notaire, Signataire

from django.utils.translation import gettext_lazy as _

class GeolocalisationForm(forms.ModelForm):
    geom = forms.PointField(widget=WMTSWidget())
    class Meta: 
        model = Geolocalisation
        fields = "__all__"
        labels = {
            "geom": _(""),
        }

class AccordFraisForm(forms.ModelForm):
    class Meta:
        model = AccordFrais
        fields = "__all__"

class AdresseFacturationForm(forms.ModelForm):
    class Meta:
        model = AdresseFacturation
        prefix = "facturation"
        fields = fields = "__all__"
        labels = {
            "nom_raison_sociale": _("Nom / raison sociale"),
            "prenom": _("Prénom / à l'att."),
            "complement": _("Complément"),
        }
        #help_texts = {
        #    "complement": _("Case postale, appt., unité, etc."),
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
            "prenom": _("Prénom"),
            "complement": _("Complément"),
            "no_tel": _("No. tél"),
        }

class NotaireForm(forms.ModelForm):
    class Meta:
        model = Notaire
        prefix="notaire"
        fields = fields = "__all__"

class SignataireForm(forms.ModelForm):
    class Meta:
        model = Signataire
        prefix="signataire"
        fields = fields = "__all__"

class DossierPPEForm(forms.ModelForm):
    geom = forms.PointField(widget=WMTSWidget())
    class Meta: 
        model = DossierPPE
        fields = [
            'egrid',
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
            'accord_frais',
            #'date_creation',
            #'date_soumission',
            #'date_validation,
        ]
from django.contrib.gis import forms
from django_extended_ol.forms.widgets import WMTSWidget

from .models import DossierPPE, Geolocalisation, Document, AdresseFacturation
from .models import ContactPrincipal, Notaire, Signataire

class GeolocalisationForm(forms.ModelForm):
    geom = forms.PointField(widget=WMTSWidget())
    class Meta: 
        model = Geolocalisation
        fields = []

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = fields = "__all__"

class AdresseFacturationForm(forms.ModelForm):
    class Meta:
        model = AdresseFacturation
        prefix = "facturation"
        fields = fields = "__all__"

class ContactPrincipalForm(forms.ModelForm):
    class Meta:
        model = ContactPrincipal
        prefix="contact"
        fields = fields = "__all__"

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
            'id_unique',
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
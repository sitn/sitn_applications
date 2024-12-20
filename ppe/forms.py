from django.contrib.gis.db import models
from django_extended_ol.forms.widgets import WMTSWidget
from django.forms import ModelForm

from .models import DossierPPE

class DossierPPEForm(ModelForm, WMTSWidget):
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
            #'date_validation',
            'geom']
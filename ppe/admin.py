from django.contrib import admin
from django_extended_ol.admin import WMTSGISModelAdmin

from .models import DossierPPE, AccordFrais, AdresseFacturation, ContactPrincipal, Notaire, Signataire, Geolocalisation

admin.site.register(AdresseFacturation)
admin.site.register(ContactPrincipal)
admin.site.register(AccordFrais)
admin.site.register(DossierPPE, WMTSGISModelAdmin)
admin.site.register(Notaire)
admin.site.register(Signataire)
admin.site.register(Geolocalisation)

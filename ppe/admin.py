from django.contrib import admin
from django_extended_ol.admin import WMTSGISModelAdmin

from .models import DossierPPE, Document, AdresseFacturation, ContactPrincipal, Notaire, Signataire

admin.site.register(AdresseFacturation)
admin.site.register(ContactPrincipal)
admin.site.register(Document)
admin.site.register(DossierPPE, WMTSGISModelAdmin)
admin.site.register(Notaire)
admin.site.register(Signataire)

from django.contrib import admin
from django_extended_ol.admin import WMTSGISModelAdmin

from .models import DossierPPE, AdresseFacturation, ContactPrincipal, Notaire, Signataire, Geolocalisation

class DossierPPEAdmin(admin.ModelAdmin):
    list_display = (
        'nummai',
        'cadastre',
        'contact_principal',
        'login_code',
        'statut',
        'type_dossier',
        'date_creation'
    )

admin.site.register(AdresseFacturation)
admin.site.register(ContactPrincipal)
admin.site.register(DossierPPE, DossierPPEAdmin)
admin.site.register(Notaire)
admin.site.register(Signataire)
admin.site.register(Geolocalisation, WMTSGISModelAdmin)

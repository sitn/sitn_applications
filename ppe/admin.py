from django.contrib import admin
from django_extended_ol.admin import WMTSGISModelAdmin

from .models import DossierPPE, AdresseFacturation, ContactPrincipal, Notaire, Signataire, Geolocalisation, Zipfile


class ZipfileInline(admin.TabularInline):
     model = Zipfile

class DossierPPEAdmin(admin.ModelAdmin):
    search_fields = [
        'nummai',
        'cadastre',
        'contact_principal',
        'login_code',
        'statut',
        'type_dossier',
        'date_creation'
    ]
    list_filter = [
        'statut', 
        'type_dossier',
        'date_creation'
    ]
    list_display = (
        'nummai',
        'cadastre',
        'contact_principal',
        'login_code',
        'statut',
        'type_dossier',
        'date_creation'
    )
    inlines = [
         ZipfileInline
    ]

class ZipfileAdmin(admin.ModelAdmin):
     search_fields = [
        'dossier_ppe'
    ]
     list_filter = [
        'dossier_ppe',
        'file_statut', 
        'upload_date'
    ]
     list_display = (
        'id',
        'dossier_ppe',
        'file_statut',
        'zipfile',
        'upload_date'
     )

admin.site.register(AdresseFacturation)
admin.site.register(ContactPrincipal)
admin.site.register(DossierPPE, DossierPPEAdmin)
admin.site.register(Notaire)
admin.site.register(Signataire)
admin.site.register(Geolocalisation, WMTSGISModelAdmin)
admin.site.register(Zipfile, ZipfileAdmin)

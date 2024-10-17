from django.contrib import admin

from .models import DossierPPE, Document, AdresseFacturation, ContactPrincipal, Notaire, Signataire

admin.site.register(AdresseFacturation)
admin.site.register(ContactPrincipal)
admin.site.register(Document)
admin.site.register(DossierPPE)
admin.site.register(Notaire)
admin.site.register(Signataire)

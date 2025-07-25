from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "ppe"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("detail", views.detail, name="detail"),
    path("set_geolocalisation", views.set_geolocalisation, name="geolocalisation"),
    path("check_geolocalisation", views.check_geolocalisation, name="check_geolocalisation"),
    path("contact_principal", views.contact_principal, name="contact_principal"),
    path("modification", views.modification, name="modification"),
    path("edit_geolocalisation", views.edit_geolocalisation, name="edit_geolocalisation"),
    path("edit_contacts", views.edit_contacts, name="edit_contacts"),
    path("edit_ppe_type", views.edit_ppe_type, name="edit_ppe_type"),
    path("edit_zipfile", views.edit_zipfile, name="edit_zipfile"),
    path("soumission", views.soumission, name="soumission"),
    path("definition_type_dossier", views.definition_type_dossier, name="definition_type_dossier"),
    path("overview", views.overview, name="overview"),
    path("load_ppe_files", views.load_ppe_files, name="load_ppe_files"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import views

app_name = "ppe"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("detail", views.detail, name="detail"),
    path("geolocalisation", views.geolocalisation, name="geolocalisation"),
    path("contact_principal", views.contact_principal, name="contact_principal"),
    path("modification", views.modification, name="modification"),
    path("soumission", views.soumission, name="soumission"),
    path("definition_type_dossier", views.definition_type_dossier, name="definition_type_dossier"),
    path("overview", views.overview, name="overview"),
    #path("<id_unique>/contacts/", views.contacts, name="contacts"),
]
from django.urls import path

from . import views


app_name = "ppe"
urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<id>/", views.detail, name="detail"),
    path("geolocalisation", views.geolocalisation, name="geolocalisation"),
    path("contact_principal", views.contact_principal, name="contact_principal"),
    path("modification", views.modification, name="modification"),
    path("soumission/<id>/", views.soumission, name="soumission"),
    path("definition_type_dossier/<id>", views.definition_type_dossier, name="definition_type_dossier"),
    #path("resumee_nouveau_depot", views.resumee_nouveau_depot, name="resumee_nouveau_depot"),
    #path("<id_unique>/contacts/", views.contacts, name="contacts"),
]
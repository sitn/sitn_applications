from django.urls import path

from . import views


app_name = "ppe"
urlpatterns = [
    path("", views.index, name="index"),
    path("<id>/", views.detail, name="detail"),
    path("geolocalisation", views.geolocalisation, name="geolocalisation"),
    path("contact_principal", views.contact_principal, name="contact_principal"),
    path("modification", views.modification, name="modification"),
    #path("<id_unique>/contacts/", views.contacts, name="contacts"),
]
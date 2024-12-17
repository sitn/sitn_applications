from django.urls import path

from . import views


app_name = "ppe"
urlpatterns = [
    path("", views.index, name="index"),
    path("<id>/", views.detail, name="detail"),
    path("confirmation", views.confirmation, name="confirmation"),
    #path("<id_unique>/contacts/", views.contacts, name="contacts"),
]
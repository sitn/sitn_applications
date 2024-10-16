from django.urls import path

from . import views


app_name = "ppe"
urlpatterns = [
    path("", views.index, name="index"),
    path("<id_dossier>/", views.detail, name="detail"),
]
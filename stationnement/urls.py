from django.urls import path

from . import views

urlpatterns = [
    path('', views.stationnement_intersection, name='intersection'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('intersection', views.forpriv_intersection, name='forpriv-intersection'),
]

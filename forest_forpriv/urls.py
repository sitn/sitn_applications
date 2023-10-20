from django.urls import path

from . import views

urlpatterns = [
    path('forpriv/intersection', views.forpriv_intersection, name='intersection'),
]

from django.urls import path

from . import views
from cadastre.views import search_parcel

urlpatterns = [
    path('', views.HelpView.as_view(), name='forpriv'),
    path('intersection', views.forpriv_intersection, name='forpriv-intersection'),
    path('search', search_parcel, name='forpriv-search'),
]

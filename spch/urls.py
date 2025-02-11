from django.urls import path
from cadastre.views import search_parcel
from . import views

urlpatterns = [
    path('', views.HelpView.as_view(), name='ecap'),
    path('search', search_parcel, name='spch-search'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.HelpView.as_view(), name='forpriv'),
    path('intersection', views.forpriv_intersection, name='forpriv-intersection'),
]

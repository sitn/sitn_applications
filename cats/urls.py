from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_activity', views.get_activity, name='cats-get-activity'),
]
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^metadata/(?P<path>.*)$', views.get_metadata, name='metadata_proxy'),
]
from django.urls import re_path, path

from . import views

urlpatterns = [
    re_path(r'^metadata/(?P<path>.*)$', views.get_metadata, name='metadata_proxy'),
    path('', views.vcron_proxy_index, name='vcron-proxy-index'),
    re_path(r'^run/(?P<task_name>.*)$', views.vcron_proxy_run, name='vcron-proxy-run'),
    re_path(
        r'^status/(?P<task_guid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.vcron_proxy_status,
        name='vcron-proxy-status'
    ),
]

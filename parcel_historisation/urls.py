from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_docs_list', views.get_docs_list, name='get_docs_list'),
    path('get_download_path', views.get_download_path, name='get_download_path'),
    path('download/<path:name>', views.file_download),
    path('submit_saisie', views.submit_saisie),
]

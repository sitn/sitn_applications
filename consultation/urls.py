from django.urls import path

from . import views

app_name = "consultation"
urlpatterns = [
    path("", views.consultation_list, name="list"),
    path("<slug:slug>/", views.consultation_detail, name="detail"),
    path("<slug:slug>/chapitres/<int:chapter_id>/questionnaire/", views.questionnaire, name="questionnaire"),
    path("<slug:slug>/banniere/", views.banner_file, name="banner_file"),
    path("<slug:slug>/documents/<int:pk>/", views.document_file, name="document_file"),
    path("<slug:slug>/mesures/", views.proposal_list, name="proposals"),
    path("<slug:slug>/mesures/<int:pk>/", views.proposal_detail, name="proposal"),
    path("<slug:slug>/mesures/<int:pk>/document/", views.proposal_file, name="proposal_file"),
]

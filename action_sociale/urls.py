from django.urls import include, path, re_path
from . import views
from sitn import router

router = router.SitnRouter()

urlpatterns = [
    path('', views.HelpView.as_view(), name='action_sociale'),
    path('intersection', views.gsr_intersection, name='gsr_intersection'),
]

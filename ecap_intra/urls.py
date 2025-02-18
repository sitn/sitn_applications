from django.urls import include, path
from cadastre.views import search_parcel
from . import views

from sitn.router import SitnRouter

router = SitnRouter()
router.register(r'ois', views.ObjetImmobiliseViewSet)
router.register(r'experts', views.RepartitionExpertViewSet)
router.register(r'plansquartiers', views.PlanQuartierViewSet)
router.register(r'planspeciaux', views.PlanSpecialViewSet)
router.register_additional_route_to_root('estate', 'ecap-intra-estate')
router.register_additional_route_to_root('search', 'ecap-intra-search')

urlpatterns = [
    path('', include(router.urls)),
    path('estate/', views.get_estate, name='ecap-intra-estate'),
    path('search/', search_parcel, name='ecap-intra-search'),
]

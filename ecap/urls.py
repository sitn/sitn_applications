from django.urls import include, path
from cadastre.views import search_parcel
from . import views

from sitn import router

router = router.SitnRouter()
router.register(r'ois', views.ObjetImmobiliseViewSet)
router.register_additional_route_to_root('estate', 'ecap-estate')
router.register_additional_route_to_root('search', 'ecap-search')

urlpatterns = [
    path('', include(router.urls)),
    path('help', views.HelpView.as_view(), name='ecap'),
    path('estate/', views.get_estate, name='ecap-estate'),
    path('search/', search_parcel, name='ecap-search'),
]

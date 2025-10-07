from django.urls import include, path, re_path
from . import views
from sitn import router

router = router.SitnRouter()
router.register(r'doctors', views.St20AvailableDoctorsViewSet)
router.register(r'sites', views.St23HealthSiteViewSet)
router.register_additional_view('doctors/edit', 'doctors-by-token-detail')
router.register_additional_view('doctors/suggest', 'doctors-suggest')

urlpatterns = [
    path('', include(router.urls)),
    path('doctors/edit',
            views.DoctorsByTokenView.as_view(), name='doctors-by-token-detail'),
    re_path(r'^doctors/edit/(?P<token>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)/$',
            views.DoctorsByTokenView.as_view(), name='doctors-by-token-detail'),
    path('doctors/suggest',
            views.St22DoctorChangeSuggestionView.as_view(), name='doctors-suggest'),
]

from django.urls import include, path
from . import views
from . import router

router = router.DoctorRouter()
router.register(r'doctors', views.St20AvailableDoctorsViewSet)
router.register_additional_route_to_root('doctor/change/request/', 'doctor_request')

urlpatterns = [
    path('', include(router.urls)),
    path('doctor/change/request/', views.GenerateMagicLinkView.as_view(), name='doctor_request'),
]

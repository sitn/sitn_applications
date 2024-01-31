from django.urls import include, path
from . import views
from . import router

router = router.DoctorRouter()
router.register(r'doctors', views.St20AvailableDoctorsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

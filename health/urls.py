from django.urls import include, path, re_path
from . import views
from . import router

router = router.DoctorRouter()
router.register(r'doctors', views.St20AvailableDoctorsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^doctors/(?P<token>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)$',
            views.St20DoctorsByTokenView.as_view(), name='doctors_update'),
]

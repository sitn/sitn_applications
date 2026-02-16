from django.urls import include, path
from sitn import router
from . import views

router = router.SitnRouter()
router.register_additional_view('vmdeport-export', 'vmdeport-export')

urlpatterns = [
    path("", include(router.urls)),
    path("vmdeport_export/", views.VmDeportExportView.as_view(), name="vmdeport-export"),
]

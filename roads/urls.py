from django.urls import include, path
from sitn import router
from . import views

router = router.SitnRouter()
router.register(r"axissegments", views.AxisSegmentsViewSet, basename="axissegments")
router.register_additional_view('vmdeport-export', 'vmdeport-export')

urlpatterns = [
    path("", include(router.urls)),
    path(
        "axissegments/<str:asg_iliid>/sectors/",
        views.SectorViewSet.as_view({"get": "list"}),
        name="axis-sectors",
    ),
    path("vmdeport_export/", views.VmDeportExportView.as_view(), name="vmdeport-export"),
]

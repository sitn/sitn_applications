from django.urls import include, path
from sitn import router
from . import views

router = router.SitnRouter()
router.register(r"axis", views.AxisViewSet, basename="axis")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "axis/<str:asg_iliid>/sectors/",
        views.SectorViewSet.as_view({"get": "list"}),
        name="axis-sectors",
    ),
    path("vmdeport_export/", views.vmdeport_export, name="vmdeport-export"),
]

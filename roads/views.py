from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from .models import AxisSegment, Sector
from .serializers import AxisSegmentSerializer, SectorSerializer
from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse


class AxisViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AxisSegmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["asg_name"]
    ordering_fields = ["asg_name"]
    lookup_field = "asg_iliid"

    def get_queryset(self):
        return AxisSegment.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        result = []
        for axis in queryset:
            result.append(
                {
                    "asg_iliid": axis.asg_iliid,
                    "asg_name": axis.asg_name,
                    "sectors": reverse(
                        "axis-sectors",
                        kwargs={"asg_iliid": axis.asg_iliid},
                        request=request,
                    ),
                }
            )
        return Response(result)


class SectorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SectorSerializer

    def get_queryset(self):
        asg_iliid = self.kwargs.get("asg_iliid")
        axis_segment = get_object_or_404(AxisSegment, asg_iliid=asg_iliid)
        return Sector.objects.filter(sec_asg_iliid=axis_segment.asg_iliid).order_by(
            "sec_name"
        )

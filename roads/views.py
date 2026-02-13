import logging
from .models import AxisSegment, Sector
from .serializers import AxisSegmentSerializer, SectorSerializer, VmDeportExportSerializer
from sitn.functions import LineSubstring, LineMerge, OffsetCurve

from django.db.models import Subquery, OuterRef, Case, When, Value, F, ExpressionWrapper, FloatField
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.db.models.functions import LineLocatePoint, Length, AsWKT, Reverse
from django.shortcuts import get_object_or_404

from rest_framework import filters, viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


LOGGER = logging.getLogger(__name__)


class VmDeportExportView(APIView):

    def get(self, request):
        """
        test avec NE 1161 = 5+200 7+300
        f_prop="NE"
        f_axe="1161"
        f_sens="="
        f_pr_d="5"
        f_pr_f="7"
        f_dist_d=200.0
        f_dist_f=300.0
        f_ecart_d=0.0
        f_ecart_f=0.0
        f_usaneg=True

        Let's represent an Axis composed of 4 segments:
        [38]----d-----[39]-------[40]  [50]----[51]  [120]----f---[121]  [150]----[151]

        [##] Are the PR with their number
        d is the depart and f the finish points of extraction

        This method will extract the geometry between d and f, in this case we will end up with:
        d-----[39]-------[40]  [50]----[51]  [120]----f
        A MULTILINESTRING with 3 parts
        """
        serializer = VmDeportExportSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        f_prop = params["f_prop"]
        f_axe = params["f_axe"]
        f_sens = params["f_sens"]
        f_pr_d = params["f_pr_d"]
        f_pr_f = params["f_pr_f"]

        f_dist_d = round(params["f_dist_d"], 3)
        f_dist_f = round(params["f_dist_f"], 3)
        f_ecart_d = round(params["f_ecart_d"], 3)

        f_usaneg = params["f_usaneg"]

        # Point geometry of starting PR and ending PR
        start_geom_subquery = Subquery(
            Sector.objects
            .filter(sec_name=f_pr_d, sec_asg=OuterRef("asg_iliid"))
            .values("sec_geom")[:1]
        )
        finish_geom_subquery = Subquery(
            Sector.objects
            .filter(sec_name=f_pr_f, sec_asg=OuterRef("asg_iliid"))
            .values("sec_geom")[:1]
        )

        # AxiSegments are ordered by asg_sequence, we need that range of sequence to filter
        # only the segments that intersect with the starting and ending PR, including the segments between
        start_sequence_subquery = Subquery(
            AxisSegment.objects.filter(
                asg_axe__axe_owner=f_prop,
                asg_axe__axe_name=f_axe,
                asg_axe__axe_positioncode=f_sens,
                asg_geom__intersects=start_geom_subquery,
            )
            .values("asg_sequence")[:1]
        )
        finish_sequence_subquery = Subquery(
            AxisSegment.objects.filter(
                asg_axe__axe_owner=f_prop,
                asg_axe__axe_name=f_axe,
                asg_axe__axe_positioncode=f_sens,
                asg_geom__intersects=finish_geom_subquery,
            )
            .values("asg_sequence")[:1]
        )

        # We need to calculate the fractions of the segment where we will cut them
        segments = AxisSegment.objects.filter(
            asg_axe__axe_owner=f_prop,
            asg_axe__axe_name=f_axe,
            asg_axe__axe_positioncode=f_sens,
        ).annotate(
            start_seq=start_sequence_subquery,
            finish_seq=finish_sequence_subquery,
        ).filter(
            asg_sequence__gte=F("start_seq"),
            asg_sequence__lte=F("finish_seq"),
        ).distinct().annotate(
            seg_length=Length("asg_geom"),
            start_geom=start_geom_subquery,
            finish_geom=finish_geom_subquery,
        ).annotate(
            start_proj=LineLocatePoint(F("asg_geom"), F("start_geom")),
            end_proj=LineLocatePoint(F("asg_geom"), F("finish_geom")),
        ).annotate(
            start_frac=ExpressionWrapper(
                F("start_proj") + (Value(f_dist_d) / F("seg_length")),
                output_field=FloatField()
            ),
            end_frac=ExpressionWrapper(
                F("end_proj") + (Value(f_dist_f) / F("seg_length")),
                output_field=FloatField()
            ),
        )

        segments = segments.annotate(
            cut_geom=Case(
                # Start and finish are on the same segment? A substring is sufficient
                When(
                    start_geom__isnull=False,
                    finish_geom__isnull=False,
                    then=LineSubstring(F("asg_geom"), F("start_frac"), F("end_frac"))
                ),
                # Otherwise starting segment must be cut from cutting point until its ending extremity
                When(
                    start_geom__isnull=False,
                    then=LineSubstring(F("asg_geom"), F("start_frac"), Value(1.0))
                ),
                # Ending segment must be cut from its starting extremity until cutting point
                When(
                    finish_geom__isnull=False,
                    then=LineSubstring(F("asg_geom"), Value(0.0), F("end_frac"))
                ),
                # Intermediate segments are kept like they are
                default=F("asg_geom"),
            )
        )

        # Apply an offset if requested
        if f_ecart_d != 0.0:
            segments = segments.annotate(
                cut_geom=OffsetCurve(
                    F("cut_geom"),
                    Value(-f_ecart_d),
                    Value("quad_segs=1 join=mitre mitre_limit=9"),
                )
            )

        # Reverse geometry if requested
        if f_usaneg:
            segments = segments.annotate(
                cut_geom=Reverse("cut_geom")
            )

        final_wkt = (
            segments
            .aggregate(
                merged=AsWKT(
                    LineMerge(
                        Union("cut_geom")
                    )
                )
            )
        )["merged"]
        return Response(final_wkt, status=200)


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

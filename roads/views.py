import logging
from .models import AxisSegment, Sector
from .serializers import VmDeportExportSerializer
from sitn.functions import LineSubstring, LineMerge, OffsetCurve

from django.http import Http404
from django.db.models import Subquery, OuterRef, Case, When, Value, F, ExpressionWrapper, FloatField
from django.db.models.functions import Least
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.db.models.functions import LineLocatePoint, Length, AsWKT, Reverse

from rest_framework.response import Response
from rest_framework.views import APIView


LOGGER = logging.getLogger(__name__)


class VmDeportExportView(APIView):
    """
        Transforms SRB based coordinates into geometries.

        Let's represent an Axis composed of 4 segments:
        [38]----d-----[39]-------[40]  [50]----[51]  [120]----f---[121]  [150]----[151]

        Legend:
        [##] Sectors (also called PR) with their numbers
        d is the depart and f the finish points of extraction

        This method will extract the geometry between d and f, in this case we will end up with:
        d-----[39]-------[40]  [50]----[51]  [120]----f
        A MULTILINESTRING with 3 parts
        
        Example: ?f_prop=NE&f_axe=H10&f_sens=%3D&f_pr_d=38&f_pr_f=120&f_dist_d=20&f_dist_f=50
    """
    def get_serializer(self):
        return VmDeportExportSerializer()
    
    def get(self, request):
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
                sectors__sec_name=f_pr_d,
            )
            .values("asg_sequence")[:1]
        )
        finish_sequence_subquery = Subquery(
            AxisSegment.objects.filter(
                asg_axe__axe_owner=f_prop,
                asg_axe__axe_name=f_axe,
                asg_axe__axe_positioncode=f_sens,
                sectors__sec_name=f_pr_f,
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
                    then=LineSubstring(F("asg_geom"), F("start_frac"), Least(F("end_frac"), Value(1.0)))
                ),
                # Otherwise starting segment must be cut from cutting point until its ending extremity
                When(
                    start_geom__isnull=False,
                    then=LineSubstring(F("asg_geom"), F("start_frac"), Value(1.0))
                ),
                # Ending segment must be cut from its starting extremity until cutting point
                When(
                    finish_geom__isnull=False,
                    then=LineSubstring(F("asg_geom"), Value(0.0), Least(F("end_frac"), Value(1.0)))
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
        
        if not final_wkt:
            raise Http404("No geometry found.")
        return Response(final_wkt, status=200)

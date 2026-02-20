import logging

from .models import AxisSegment, Sector
from .serializers import VmDeportExportSerializer
from sitn.functions import OffsetCurve, LineSubstring, LineInterpolatePoint

from django.db.models import FloatField, ExpressionWrapper, F, Value, Func
from django.contrib.gis.db.models.functions import Reverse, LineLocatePoint, Length, Azimuth, Translate, AsWKT
from django.contrib.gis.geos import MultiLineString

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
    
    # Factor to correct measured distance with geographic planar distance
    def _compute_elastic_factor(self, sector):
        if not sector.sec_length:
            return 1.0

        next_sector = (
            Sector.objects
            .filter(
                sec_asg=sector.sec_asg,
                sec_sequence__gt=sector.sec_sequence
            )
            .order_by("sec_sequence")
            .first()
        )

        if not next_sector or not sector.sec_length:
            return 1.0

        segment = AxisSegment.objects.filter(
            pk=sector.sec_asg.pk
        ).annotate(
            start_proj=LineLocatePoint("asg_geom", Value(sector.sec_geom)),
            end_proj=LineLocatePoint("asg_geom", Value(next_sector.sec_geom)),
            subgeom=LineSubstring(
                "asg_geom",
                F("start_proj"),
                F("end_proj")
            ),
            #real_length=Length("subgeom", spheroid=False),
        )
        segment = segment.first()
        if not segment or not segment.subgeom.length:
            return 1.0
        
        factor = segment.subgeom.length / sector.sec_length
        LOGGER.info(f'Factor is {factor}')

        return factor
    
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


        # Get the sectors
        try:
            start_sector = Sector.objects.select_related("sec_asg").get(
                sec_name=f_pr_d,
                sec_asg__asg_axe__axe_owner=f_prop,
                sec_asg__asg_axe__axe_name=f_axe,
                sec_asg__asg_axe__axe_positioncode=f_sens,
            )
            finish_sector = Sector.objects.select_related("sec_asg").get(
                sec_name=f_pr_f,
                sec_asg__asg_axe__axe_owner=f_prop,
                sec_asg__asg_axe__axe_name=f_axe,
                sec_asg__asg_axe__axe_positioncode=f_sens,
            )
        except Sector.DoesNotExist:
            return Response(
                {"The sector does not exist"},
                status=400,
            )

        f_dist_d *= self._compute_elastic_factor(start_sector)
        f_dist_f *= self._compute_elastic_factor(finish_sector)

        # Get the related segments
        segments = AxisSegment.objects.filter(
            asg_axe__axe_owner=f_prop,
            asg_axe__axe_name=f_axe,
            asg_axe__axe_positioncode=f_sens,
            asg_sequence__gte=start_sector.sec_asg.asg_sequence,
            asg_sequence__lte=finish_sector.sec_asg.asg_sequence,
        ).order_by("asg_sequence")

        # Cut the segments
        cut_geoms = []
        
        for seg in segments:
            seg_qs = AxisSegment.objects.filter(pk=seg.pk)

            is_start = seg.pk == start_sector.sec_asg.pk
            is_finish = seg.pk == finish_sector.sec_asg.pk
            
            LOGGER.info(f'Start sector {start_sector.sec_name}, Finish sector {finish_sector.sec_name}')
            LOGGER.info(f'Processing segment {seg.asg_name}, is_start? {is_start}, is_finish? {is_finish}')
            if is_start:
                seg_qs = seg_qs.annotate(
                    start_proj=LineLocatePoint("asg_geom", Value(start_sector.sec_geom)),
                    start_frac=ExpressionWrapper(
                        F("start_proj") + (Value(f_dist_d) / Length("asg_geom")),
                        output_field=FloatField()
                    )
                )

                # If a point is requested
                if f_pr_d == f_pr_f and f_dist_d == f_dist_f:
                    seg_qs = seg_qs.annotate(
                        interpolated_point=LineInterpolatePoint(
                            F("asg_geom"),
                            F("start_frac")
                        )
                    )
                    
                    # Apply an offset if requested
                    if f_ecart_d != 0.0:
                        seg_qs = seg_qs.annotate(
                            pt=LineInterpolatePoint(F("asg_geom"), F("start_frac")),
                            pt2=LineInterpolatePoint(F("asg_geom"), F("start_frac") + Value(0.1)),
                        ).annotate(
                            az=Azimuth(F("pt"), F("pt2"))
                        ).annotate(
                            interpolated_point=Translate(
                                F("pt"),
                                Value(-f_ecart_d) * Func(F("az") + Value(1.57079632679), function="cos"),
                                Value(-f_ecart_d) * Func(F("az") + Value(1.57079632679), function="sin"),
                            )
                        )
                    
                    final_wkt = seg_qs.annotate(
                            point_wkt=AsWKT(F("interpolated_point"))
                        ).values_list("point_wkt", flat=True).first()

                    if not final_wkt:
                        return Response(
                            {"No point found"},
                            status=400,
                        )
                    return Response(final_wkt, status=200)
            else:
                seg_qs = seg_qs.annotate(start_frac=Value(0.0))

            if is_finish:
                seg_qs = seg_qs.annotate(
                    end_proj=LineLocatePoint("asg_geom", Value(finish_sector.sec_geom)),
                    end_frac=ExpressionWrapper(
                        F("end_proj") + (Value(f_dist_f) / Length("asg_geom")),
                        output_field=FloatField()
                    )
                )
            else:
                seg_qs = seg_qs.annotate(end_frac=Value(1.0))

            seg_qs = seg_qs.annotate(
                subgeom=LineSubstring(
                    "asg_geom",
                    F("start_frac"),
                    F("end_frac")
                )
            )

            if f_ecart_d != 0.0:
                seg_qs = seg_qs.annotate(
                    subgeom=OffsetCurve(
                        "subgeom",
                        Value(-f_ecart_d),
                        Value("quad_segs=1 join=mitre mitre_limit=9"),
                    )
                )

            if f_usaneg:
                seg_qs = seg_qs.annotate(
                    subgeom=Reverse("subgeom")
                )
            
            geom = seg_qs.values_list("subgeom", flat=True).first()
            LOGGER.info(geom.length)
            if geom:
                cut_geoms.append(geom)

        final_geom = MultiLineString(cut_geoms)

        return Response(final_geom.wkt, status=200)

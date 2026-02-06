from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from .models import AxisSegment, Sector
from .serializers import AxisSegmentSerializer, SectorSerializer
from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse
from django.http import JsonResponse
import logging
logger = logging.getLogger(__name__)
@api_view(["GET"])
def vmdeport_export(request):
    """
    Migration Django de la route Pyramid vmdeport_export.
    Cette version ne fait PAS de traitement géométrique, mais structure la logique et les contrôles de paramètres.
    """
    logger.info(f"Début traitement de la requête: {request.build_absolute_uri()}")

    # Contrôle des paramètres obligatoires
    required_params = ["f_prop", "f_axe", "f_sens", "f_pr_d", "f_pr_f", "f_dist_d", "f_dist_f"]
    for param in required_params:
        if param not in request.GET:
            return JsonResponse({"detail": f"no {param}"}, status=400)

    f_prop = request.GET["f_prop"].strip().upper()
    f_axe = request.GET["f_axe"].strip().upper()
    f_sens = request.GET["f_sens"].strip()
    if f_sens not in ["+", "-", "="]:
        f_sens = "="
    f_pr_d = request.GET["f_pr_d"].strip().upper()
    f_pr_f = request.GET["f_pr_f"].strip().upper()

    try:
        f_dist_d = round(float(request.GET["f_dist_d"].strip()), 3)
        if f_dist_d < 0.0:
            raise ValueError
    except Exception:
        return JsonResponse({"detail": "Problème de saisie: la distance depuis le PR début doit être un nombre supérieur ou égal à 0.0"}, status=400)

    try:
        f_dist_f = round(float(request.GET["f_dist_f"].strip()), 3)
        if f_dist_f < 0.0:
            raise ValueError
    except Exception:
        return JsonResponse({"detail": "Problème de saisie: la distance depuis le PR de fin doit être un nombre supérieur ou égal à 0.0"}, status=400)

    # Optionnels
    try:
        f_ecart_d = round(float(request.GET.get("f_ecart_d", 0.0)), 3)
    except Exception:
        return JsonResponse({"detail": "Problème de saisie: l'écart au début doit être un nombre"}, status=400)
    try:
        f_ecart_f = round(float(request.GET.get("f_ecart_f", 0.0)), 3)
    except Exception:
        return JsonResponse({"detail": "Problème de saisie: l'écart à la fin doit être un nombre"}, status=400)
    if f_ecart_d != f_ecart_f:
        return JsonResponse({"detail": "Le calcul d'un déport biais n'est pas encore implémenté !"}, status=400)

    f_usaneg = request.GET.get("f_usaneg", "false").strip().upper() == "TRUE"
    f_recalcM = request.GET.get("f_recalcM", "false").strip().upper() == "TRUE"
    f_reprojZ = request.GET.get("f_reprojZ", "false").strip().upper() == "TRUE"
    f_geomAsBin = request.GET.get("f_geomAsBin", "false").strip().upper() == "TRUE"

    if f_reprojZ:
        return JsonResponse({"detail": "La reprojection 3D (recalcul du Z) n'est pas encore implémentée !"}, status=400)

    # Recherche de l'axe
    axes = AxisSegment.objects.filter(
        asg_axe_iliid=f_prop, asg_name=f_axe
    )
    if not axes.exists():
        return JsonResponse({"detail": f"Problème d'axe: cet axe [{f_prop}:{f_axe}:{f_sens}] est inconnu !"}, status=400)

    # Recherche des segments et secteurs avec géométrie
    from django.contrib.gis.db.models.functions import LineLocatePoint, LineSubstring, Length, Transform
    from django.contrib.gis.geos import GEOSGeometry
    from django.db.models import F

    # On suppose que l'axe est unique (clé composite dans la base)
    axis = axes.first()
    segments = AxisSegment.objects.filter(asg_axe_iliid=axis.asg_axe_iliid, asg_name=axis.asg_name).order_by('asg_sequence')
    geom_result = None
    pr_debut = None
    pr_fin = None
    for seg in segments:
        sectors = Sector.objects.filter(sec_asg_iliid=seg.asg_iliid).order_by('sec_sequence')
        for sc in sectors:
            # Trouver le PR début
            if sc.sec_name == f_pr_d and pr_debut is None:
                pr_debut = sc
            # Trouver le PR fin
            if sc.sec_name == f_pr_f:
                pr_fin = sc
    if not pr_debut or not pr_fin:
        return JsonResponse({"detail": f"Le PR début ({f_pr_d}) et/ou le PR fin ({f_pr_f}) n'existe pas sur cet axe."}, status=400)

    # Récupérer la géométrie du segment
    seg_geom = segments.first().asg_geom
    if not seg_geom:
        return JsonResponse({"detail": "Pas de géométrie pour ce segment."}, status=400)

    # Interpolation sur la ligne (simplifié)
    # On suppose que sec_geom est un point sur la ligne
    try:
        # Calcul de la position du PR début et fin sur la ligne
        pr_debut_geom = pr_debut.sec_geom
        pr_fin_geom = pr_fin.sec_geom
        if not pr_debut_geom or not pr_fin_geom:
            return JsonResponse({"detail": "Pas de géométrie pour le PR début ou fin."}, status=400)
        # Calcul de la fraction le long de la ligne (0-1)
        from django.contrib.gis.db.models.functions import LineLocatePoint
        start_frac = seg_geom.line_locate_point(pr_debut_geom)
        end_frac = seg_geom.line_locate_point(pr_fin_geom)
        # Décalage par la distance demandée
        # (ici, on suppose que la longueur du segment est en mètres)
        seg_length = seg_geom.length
        start_dist = f_dist_d / seg_length if seg_length else 0
        end_dist = f_dist_f / seg_length if seg_length else 0
        start = float(start_frac) + start_dist
        end = float(end_frac) + end_dist
        if start > end:
            start, end = end, start
        # Découper la ligne
        subline = seg_geom.line_substring(start, end)
        # Offset si demandé
        if f_ecart_d != 0.0:
            # Décalage latéral (buffer négatif pour un offset à gauche, positif à droite)
            subline = subline.parallel_offset(f_ecart_d, 'left')
        # Inversion du sens si demandé
        if f_usaneg:
            subline = subline.reverse()
        # Format de sortie
        if f_geomAsBin:
            result = subline.wkb
        else:
            result = subline.wkt
        return JsonResponse({"geometry": result})
    except Exception as e:
        logger.error(f"Erreur géométrique: {e}")
        return JsonResponse({"detail": f"Erreur géométrique: {e}"}, status=500)


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

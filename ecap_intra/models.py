from django.contrib.gis.db import models
from django.conf import settings

from sitn.mixins import GeoJSONModelMixin

class ObjetImmobilise(models.Model, GeoJSONModelMixin):
    no_obj = models.BigIntegerField(unique=True, primary_key=True)
    statut_obj = models.CharField(max_length=3)
    peggi_id = models.IntegerField()
    geom = models.PointField(srid=settings.DEFAULT_SRID)

    PUBLIC_FIELDS = [
        'no_obj',
        'peggi_id',
    ]

    class Meta:
        db_table = 'ecap\".\"ecap05_objets_immobilises_actifs'
        managed = False


class RepartitionExpert(models.Model, GeoJSONModelMixin):
    idobj = models.CharField(max_length=40, primary_key=True)
    nom_expert = models.CharField(max_length=50)
    ini_expert = models.CharField(max_length=5)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    PUBLIC_FIELDS = [
        'idobj',
        'nom_expert',
        'ini_expert',
    ]

    class Meta:
        db_table = 'ecap\".\"ecap04_experts_sinistre_statistique'
        managed = False


class PlanQuartier(models.Model, GeoJSONModelMixin):
    identifiant_unique_ct = models.CharField(max_length=15, primary_key=True)
    commune_ct = models.CharField(max_length=25)
    type_instrument_ct = models.CharField(max_length=20)
    designation_specifique_ct = models.CharField(max_length=180, null=True)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    PUBLIC_FIELDS = [
        'identifiant_unique_ct',
        'designation_specifique_ct',
        'type_instrument_ct',
        'commune_ct',
    ]

    class Meta:
        db_table = 'amenagement\".\"at204_plans_quartier'
        managed = False


class PlanSpecial(models.Model, GeoJSONModelMixin):
    identifiant_unique_ct = models.CharField(max_length=15, primary_key=True)
    commune_ct = models.CharField(max_length=25)
    type_instrument_ct = models.CharField(max_length=20)
    designation_specifique_ct = models.CharField(max_length=180, null=True)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    PUBLIC_FIELDS = [
        'identifiant_unique_ct',
        'designation_specifique_ct',
        'type_instrument_ct',
        'commune_ct',
    ]

    class Meta:
        db_table = 'amenagement\".\"at205_plans_speciaux'
        managed = False
from django.contrib.gis.db import models
from django.conf import settings

from sitn.mixins import GeoJSONModelMixin

class ObjetImmobilise(models.Model, GeoJSONModelMixin):
    idobj = models.CharField(max_length=40, primary_key=True)
    no_obj = models.BigIntegerField(unique=True)
    statut_obj = models.CharField(max_length=3)
    peggi_id = models.IntegerField()
    geom = models.PointField(srid=settings.DEFAULT_SRID)

    PUBLIC_FIELDS = [
        'idobj',
        'no_obj',
        'geom',
    ]

    class Meta:
        db_table = 'ecap\".\"ecap05_objets_immobilises_actifs'
        managed = False


class RepartitionExpert(models.Model):
    idobj = models.CharField(max_length=40, primary_key=True)
    nom_expert = models.CharField(max_length=50)
    ini_expert = models.CharField(max_length=5)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        db_table = 'ecap\".\"ecap04_experts_sinistre_statistique'
        managed = False

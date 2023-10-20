from django.conf import settings
from django.contrib.gis.db import models

class Fo01Arrondissement(models.Model):
    idobj = models.UUIDField(primary_key=True)
    inspecteur = models.CharField(max_length=50)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'foret\".\"fo_arrondissements'

class Fo02Cantonnement(models.Model):
    idobj = models.UUIDField(primary_key=True)
    titulaire = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'foret\".\"fo_cantonnements'

class Fo11UniteGestionForprivee(models.Model):
    idobj = models.CharField(max_length=40, primary_key=True)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'foret\".\"fo11_unite_gestion_forprivees'

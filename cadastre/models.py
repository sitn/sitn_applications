from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.search import SearchVectorField

class Cadastre(models.Model):
    idobj = models.UUIDField(primary_key=True)
    numcad = models.BigIntegerField()
    cadnom = models.CharField(max_length=50)
    numcom = models.BigIntegerField()
    nufeco = models.BigIntegerField()
    comnom = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'general\".\"la02_cadastres'


class ImmeublesAdressesSearch(models.Model):
    noobj = models.IntegerField(primary_key=True)
    numcom = models.IntegerField()
    cadastre = models.CharField(max_length=100)
    nummai = models.CharField(max_length=7)
    idemai = models.CharField(max_length=50)
    typimm = models.CharField(max_length=17)
    mutcou = models.CharField(max_length=8)
    mutmai = models.CharField(max_length=8)
    srfmai = models.IntegerField()
    valide = models.CharField(max_length=1)
    datedt = models.DateField()
    nufeco = models.CharField(max_length=5)
    source = models.CharField(max_length=50)
    url_terris = models.CharField(max_length=250)
    adresse = models.CharField(max_length=250)
    nom_localite = models.CharField(max_length=250)
    search_immeuble = models.CharField(max_length=250)
    geom = models.PolygonField(srid=settings.DEFAULT_SRID)
    _ts = SearchVectorField()

    class Meta:
        managed = False
        db_table = 'searchtables\".\"search_immeubles_adresses'

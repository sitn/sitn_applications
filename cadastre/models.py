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

class Commune(models.Model):
    idobj = models.CharField(max_length=40, primary_key=True)
    comnom = models.CharField(max_length=100)
    numcom = models.BigIntegerField()
    nufeco = models.BigIntegerField()
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'general\".\"la3_limites_communales'

class ImmeublesAdressesSearch(models.Model):
    noobj = models.IntegerField(primary_key=True)
    cadnum = models.IntegerField()
    cadnom = models.CharField(max_length=100)
    nummai = models.CharField(max_length=7)
    idemai = models.CharField(max_length=50)
    typimm = models.CharField(max_length=17)
    comnum = models.IntegerField()
    comnom= models.CharField(max_length=80)
    adresse_partielle = models.CharField(max_length=250)
    adresse = models.CharField(max_length=500)
    nom_localite = models.CharField(max_length=250)
    label = models.CharField(max_length=250)
    geom = models.PolygonField(srid=settings.DEFAULT_SRID)
    _ts = SearchVectorField()

    @property
    def idmai(self):
        return "{}_{}".format(self.cadnum, self.nummai)

    class Meta:
        managed = False
        db_table = 'searchtables\".\"search_immeubles_adresses_new'

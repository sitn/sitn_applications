from django.contrib.gis.db import models
from django.conf import settings

class Gsr001Search(models.Model):
    """Guichet social régional"""
    idobj = models.CharField(max_length=40, primary_key=True)
    comnom = models.CharField(max_length=100)
    nom_gsr = models.CharField(max_length=60)
    numero_telephone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    form_prise_contact = models.CharField(max_length=100)
    adresse = models.CharField(max_length=60)
    google_maps= models.CharField(max_length=100)
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'action_sociale\".\"gsr001_search'

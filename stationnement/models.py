from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Mob20TypeLocalisation(models.Model):
    idobj = models.TextField(primary_key=True)
    type_localisation = models.TextField()
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'mobilite\".\"mob20_type_localisation'

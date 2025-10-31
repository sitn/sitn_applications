from django.contrib.gis.db import models
from django.conf import settings


class AxisSegment(models.Model):
    """
    A road is represented by an Axis which has a unique name (asg_name).
    Each axis can have multiple AxisSegments.
    """

    asg_iliid = models.TextField(primary_key=True)
    asg_axe_iliid = models.TextField()
    asg_name = models.CharField(max_length=64, unique=True)
    asg_sequence = models.IntegerField()
    asg_geom = models.MultiLineStringField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'mistra_complet"."t_axissegments'


class Sector(models.Model):
    """
    A sector is a part of an AxisSegment, also called PR (point de repérage)
    """

    sec_iliid = models.TextField(primary_key=True)
    sec_sequence = models.FloatField(null=True)
    sec_name = models.CharField(max_length=64, null=True)
    sec_length = models.FloatField(null=True)
    sec_km = models.FloatField(null=True)
    sec_asg_iliid = models.TextField(null=True)
    sec_geom = models.PointField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'mistra_complet"."t_sectors'

from django.contrib.gis.db import models
from django.conf import settings


class Axis(models.Model):
    """
    A road is represented by an Axis which has a unique name (asg_name).
    """

    axe_iliid = models.TextField(primary_key=True)
    axe_name = models.CharField(max_length=64)
    axe_owner = models.CharField(max_length=12)
    axe_positioncode = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'mistra_complet"."t_axis'


class AxisSegment(models.Model):
    """
    Each Axis can have multiple AxisSegments.
    """

    asg_iliid = models.TextField(primary_key=True)
    asg_axe = models.ForeignKey(
        Axis,
        to_field="axe_iliid",
        db_column="asg_axe_iliid",
        related_name="segments",
        on_delete=models.DO_NOTHING,
    )
    asg_name = models.CharField(max_length=64, unique=True)
    asg_sequence = models.IntegerField()
    asg_geom = models.LineStringField(srid=settings.DEFAULT_SRID)

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
    sec_asg = models.ForeignKey(
        AxisSegment,
        to_field="asg_iliid",
        db_column="sec_asg_iliid",
        related_name="sectors",
        on_delete=models.DO_NOTHING,
    )
    sec_geom = models.PointField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'mistra_complet"."t_sectors'

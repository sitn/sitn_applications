from django.db import models


class AxisSegment(models.Model):
    """
    A road is represented by an Axis which has a unique name (asg_name).
    Each axis can have multiple AxisSegments.
    """

    asg_iliid = models.TextField(primary_key=True)
    asg_axe_iliid = models.TextField(null=True)
    asg_name = models.CharField(max_length=64, unique=True)

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

    class Meta:
        managed = False
        db_table = 'mistra_complet"."t_sectors'

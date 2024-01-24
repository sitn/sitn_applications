from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db import connection


class AbstractDoctors(models.Model):

    class Avalability(models.TextChoices):
        UNKNOWN = "Unknow"
        AVAILABLE = "Available"
        NOT_AVAILABLE = "Not available"
        AVAILABLE_WITH_CONDITIONS = "Available with conditions"

    id_person_address = models.TextField(primary_key=True)
    login_email = models.TextField(blank=True)
    availability_conditions = models.TextField(blank=True)
    has_parking = models.BooleanField(null=True),
    has_disabled_access = models.BooleanField(null=True),
    has_lift = models.BooleanField(null=True),
    spoken_languages = ArrayField(models.TextField())
    is_rsn_member = models.BooleanField(null=True),
    availability = models.TextField(choices=Avalability.choices, default=Avalability.UNKNOWN)

    class Meta:
        abstract = True


class St20AvailableDoctors(AbstractDoctors):
    """Doctor availability infos, without geom"""

    class Meta:
        db_table = 'sante\".\"st20_available_doctors'


class St21AvailableDoctorsWithGeom(AbstractDoctors):
    geom = models.PointField(srid=settings.DEFAULT_SRID)

    class Meta:
        db_table = 'sante\".\"st21_available_doctors_with_geom'

    @classmethod
    def as_geojson(cls):
        sql_query = f"""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(t.*)::json)
            )::text FROM "{cls._meta.db_table}" as t
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchone()

        return result[0]

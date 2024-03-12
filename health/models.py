import uuid

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
    availability_conditions = models.TextField(blank=True, null=True)
    has_parking = models.BooleanField(null=True),
    has_disabled_access = models.BooleanField(null=True),
    has_lift = models.BooleanField(null=True),
    spoken_languages = ArrayField(models.TextField())
    is_rsn_member = models.BooleanField(null=True),
    availability = models.TextField(choices=Avalability.choices, default=Avalability.UNKNOWN)
    edit_guid = models.UUIDField(null=True)
    guid_requested_when = models.DateTimeField(null=True)
    last_edit = models.DateTimeField(null=True)

    def prepare_for_edit(self):
        self.edit_guid = uuid.uuid4()

    class Meta:
        abstract = True


class St19Cabinets(models.Model):
    """Geom for cabinets"""

    class Meta:
        db_table = 'sante\".\"st19_cabinets'
        managed=False


class St18Independants(models.Model):
    """Geom for independants"""

    class Meta:
        db_table = 'sante\".\"st18_independants'
        managed=False


class St20AvailableDoctors(AbstractDoctors):
    """Doctor availability infos, without geom"""

    class Meta:
        db_table = 'sante\".\"st20_available_doctors'
        managed=False


class St21AvailableDoctorsWithGeom(AbstractDoctors):
    PUBLIC_FIELDS = [
        'id_person_address',
        'nom',
        'prenoms',
        'profession',
        'specialites',
        'notel',
        'address',
        'nopostal',
        'localite',
        'availability',
        'availability_conditions',
        'has_parking',
        'has_disabled_access',
        'has_lift',
        'spoken_languages',
        'is_rsn_member',
        'geom',
    ]
    geom = models.PointField(srid=settings.DEFAULT_SRID)

    class Meta:
        db_table = 'sante\".\"st21_available_doctors_with_geom'
        managed=False

    @classmethod
    def as_geojson(cls):
        """
        Custom database GeoJSON serializer rendering only PUBLIC_FIELDS
        """

        sql_query = f"""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(t.*)::json)
            )::text FROM (
                SELECT {', '.join(cls.PUBLIC_FIELDS)} FROM "{cls._meta.db_table}") t
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchone()

        return result[0]

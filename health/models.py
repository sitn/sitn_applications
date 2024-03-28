from datetime import timedelta
import uuid
import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class AbstractDoctors(models.Model):

    class Avalability(models.TextChoices):
        UNKNOWN = "Unknown", _("Unknown")
        AVAILABLE = "Available", _("Available")
        NOT_AVAILABLE = "Not available", _("Not available")
        AVAILABLE_WITH_CONDITIONS = "Available with conditions", _("Available with conditions")

    availability = models.TextField(_("availability"), choices=Avalability.choices, default=Avalability.UNKNOWN)
    availability_conditions = models.TextField(_("availability_conditions"), blank=True, null=True)
    has_parking = models.BooleanField(_("has_parking"), null=True)
    has_disabled_access = models.BooleanField(_("has_disabled_access"), null=True)
    has_lift = models.BooleanField(_("has_lift"), null=True)
    spoken_languages = ArrayField(models.TextField(), verbose_name=_("spoken_languages"))
    is_rsn_member = models.BooleanField(_("is_rsn_member"), null=True)

    class Meta:
        abstract = True


class St21AvailableDoctorsWithGeom(AbstractDoctors):
    id_person_address = models.TextField(_("id_person_address"), primary_key=True)
    nom = models.TextField()
    prenoms = models.TextField()
    profession = models.TextField()
    specialites = models.TextField()
    notel = models.TextField(null=True)
    address = models.TextField()
    nopostal = models.TextField()
    localite = models.TextField()

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
    
    def __str__(self):
        return "%s %s (%s)" % (
            self.nom,
            self.prenoms,
            self.id_person_address
        )


class St20AvailableDoctors(AbstractDoctors):
    """Doctor availability infos, without geom"""
    doctor = models.OneToOneField(
        St21AvailableDoctorsWithGeom,
        db_column="id_person_address",
        on_delete=models.CASCADE,
        verbose_name=_("doctor_nemedreg"),
        primary_key=True
    )
    login_email = models.CharField(blank=True, max_length=255)
    edit_guid = models.UUIDField(blank=True, null=True)
    guid_requested_when = models.DateTimeField(blank=True, null=True)
    last_edit = models.DateTimeField(blank=True, null=True)

    def prepare_for_edit(self):
        self.edit_guid = uuid.uuid4()

    @property
    def has_been_requested_recently(self):
        now = timezone.now()
        ten_minutes_ago = now - timedelta(minutes=10)
        if self.guid_requested_when == None:
            return False
        if self.guid_requested_when < ten_minutes_ago:
            logger.info('10 minutes cooldown')
            return False
        return True

    @property
    def is_edit_guid_valid(self):
        if not bool(self.edit_guid):
            logger.info('Edit guid is empty or null')
            return False
        now = timezone.now()
        three_days_ago = now - timedelta(days=3)
        if self.guid_requested_when == None:
            return False
        if self.guid_requested_when < three_days_ago:
            logger.info('Edit guid is older than three days ago')
            return False
        return True
    
    # TODO: Find a way when there's no nemedreg
    #def __str__(self):
    #    if self.doctor:
    #        return "%s %s (%s)" % (
    #            self.doctor.nom,
    #            self.doctor.prenoms,
    #            self.pk
    #        )
    #    return self.pk


    class Meta:
        db_table = 'sante\".\"st20_available_doctors'
        verbose_name = _("St20AvailableDoctors")
        managed=False
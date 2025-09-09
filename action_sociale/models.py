from django.contrib.gis.db import models
from django.conf import settings


class Gsr001Search(models.Model):
    """Zones de desserte du guichet social régional"""

    idobj = models.CharField(max_length=40, primary_key=True)
    guichet = models.ForeignKey(
        "Gsr002GuichetSocialRegional",
        to_field="nom_gsr",
        db_column="nom_gsr",
        on_delete=models.DO_NOTHING,
        related_name="zones",
    )
    geom = models.MultiPolygonField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'action_sociale\".\"gsr001_search'


class Gsr002GuichetSocialRegional(models.Model):
    """Guichet social régional"""

    idobj = models.CharField(max_length=40, primary_key=True)
    comnom = models.CharField(max_length=100)
    nom_gsr = models.CharField(max_length=60, unique=True)
    numero_telephone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    form_prise_contact = models.CharField(max_length=100)
    adresse = models.CharField(max_length=60)
    google_maps = models.CharField(max_length=100)
    geom = models.PointField(srid=settings.DEFAULT_SRID)

    class Meta:
        managed = False
        db_table = 'action_sociale\".\"gsr002_guichet_social_regional'

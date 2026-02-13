from django.db import models

# Create your models here.
class RfcenAdresse(models.Model):
    """
    Global table containing all needed information concerning
    owners and people referenced in the RF DB.
    akt_ase_typ enables to check if it is a moral or physcial
    person or even some kind of wonership group (hoirie, société simple,
    indivision familiale).
    """

    ase_id = models.BigIntegerField(primary_key=True, null=False)
    akt_name = models.CharField(max_length=256)
    akt_vorname = models.CharField(max_length=256)
    akt_ase_typ = models.CharField(max_length=1)

    class Meta:
        db_table = 'RFCEN\".\"ADRESSE'
        managed = False


class Recht(models.Model):
    """
    Global table containing all needed information concerning
    owners and people referenced in the RF DB.
    akt_ase_typ enables to check if it is a moral or physcial
    person or even some kind of wonership group (hoirie, société simple,
    indivision familiale).
    """

    rht_id = models.CharField(max_length=10, primary_key=True, null=False)
    lst_id = models.CharField(max_length=8)
    lst_typ = models.CharField(max_length=1)
    gdk_last = models.CharField(max_length=12)
    esta_last = models.CharField(max_length=4)
    art_last = models.CharField(max_length=1)
    gdk_recht = models.CharField(max_length=12)
    esta_recht = models.CharField(max_length=4)
    loesch_status = models.CharField(max_length=1)

    class Meta:
        db_table = 'RF_SITN\".\"RECHT'
        managed = False
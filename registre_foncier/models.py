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
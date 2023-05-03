from django.db import models

class Cadastre(models.Model):
    idobj = models.UUIDField(primary_key=True)
    numcad = models.BigIntegerField()
    cadnom = models.CharField(max_length=50)
    numcom = models.BigIntegerField()
    nufeco = models.BigIntegerField()
    comnom = models.CharField(max_length=50)

    class Meta:
        db_table = 'general\".\"la02_cadastres'
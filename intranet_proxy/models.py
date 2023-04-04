from django.db import models
from django.core.validators import RegexValidator

class VcronRoute(models.Model):
    url = models.CharField(max_length=120, null=False, unique=True)
    vcron_guid = models.CharField(max_length=36, null=False, validators=[
        RegexValidator(
            regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
            message=('VCRON guid is not valid'),
        ),
    ])

    class Meta:
        db_table = 'sitn_applications\".\"vcron_route'

    def __str__(self):
        return self.url

from django.db import models
from django.contrib.postgres.fields import ArrayField

class State(models.Model):
    name = models.CharField(max_length=1000)

    class Meta:
        db_table = 'parcel_historisation\".\"state'

class Designation(models.Model):
    name = models.CharField(max_length=1000)
    class Meta:
        db_table = 'parcel_historisation\".\"designation'
    @property
    def filename(self):
        return self.name.split('/')[-1]


class Plan(models.Model):
    name = models.CharField(max_length=1000)
    link = models.CharField(max_length=1000)
    plan_number = models.BigIntegerField()
    index = models.IntegerField()
    scale = models.IntegerField(null=True)
    date_plan = models.DateField(null=True)
    cadastre = models.IntegerField()
    id_plan_old = models.BigIntegerField()
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, verbose_name='designation', null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, verbose_name='state', null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"plan'

class Operation(models.Model):
    date = models.DateField(null=True)
    user = models.CharField(max_length=200, null=True)
    complement = models.CharField(max_length=5000, null=True)
    old_system = models.BooleanField(default=False)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, verbose_name='plan', blank=True, null=True)
    infolica_no = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'parcel_historisation\".\"operation'

class OtherOperation(models.Model):
    type = models.IntegerField()
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, verbose_name='operation', related_name="operations", null=True)
    bfs_list = ArrayField(models.CharField(max_length=200, null=True), null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"other_operation'

class DivisonReunion(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, verbose_name='operation', null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"division_operation'

class Balance(models.Model):
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    source_rp = models.BooleanField(null=True)
    destination_rp = models.BooleanField(null=True)
    source_origin = models.BooleanField(null=True)
    current_destination = models.BooleanField(null=True)
    division = models.ForeignKey(Operation, on_delete=models.SET_NULL, verbose_name='division', null=True)
    destination_ddp = models.BooleanField(default=False)

    class Meta:
        db_table = 'parcel_historisation\".\"balance'

class VBalanceSourceNoDest(models.Model):
    source = models.CharField(max_length=200, primary_key=True)
    class Meta:
        db_table = 'parcel_historisation\".\"v_source_no_destination'
        managed = False


class VBalanceDestNoSource(models.Model):
    destination = models.CharField(max_length=200, primary_key=True)
    class Meta:
        db_table = 'parcel_historisation\".\"v_destination_no_source'
        managed = False

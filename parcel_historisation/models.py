from django.db import models

class State(models.Model):
    name = models.CharField(max_length=1000)
  
    class Meta:
        db_table = 'parcel_historisation\".\"state'


class Plan(models.Model):
    name = models.CharField(max_length=1000)
    link = models.CharField(max_length=1000)
    plan_number = models.BigIntegerField()
    index = models.IntegerField()
    scale = models.IntegerField()
    id_state = models.ForeignKey(State, verbose_name='id_state')

    class Meta:
        db_table = 'parcel_historisation\".\"plan'

class Designation(models.Model):
    name = models.CharField(max_length=1000)
    id_state = models.ForeignKey(State, verbose_name='id_state')

    class Meta:
        db_table = 'parcel_historisation\".\"designation'

class DesignationPlan(models.Model):
    date_plan = models.DateField()
    cadastre = models.IntegerField()
    id_designation = models.ForeignKey(Designation, models.SET_NULL, verbose_name='id_designation', blank=True, null=True)
    id_plan = models.ForeignKey(Plan, verbose_name=_('id_plan'))

    class Meta:
        db_table = 'parcel_historisation\".\"designation_plan'

class Operation(models.Model):
    date = models.DateField()
    user = models.CharField(max_length=200, null=False)
    complement = models.CharField(max_length=5000)
    id_designation_plan = models.ForeignKey(DesignationPlan, models.SET_NULL, verbose_name='id_designation_plan', blank=True, null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"operation'

class OtherOperation(models.Model):
    type = models.IntegerField()
    id_operation = models.ForeignKey(Operation, verbose_name='id_operation')

    class Meta:
        db_table = 'parcel_historisation\".\"other_operation'

class DivisonReunion(models.Model):
    id_operation = models.ForeignKey(Operation, verbose_name='id_operation')

    class Meta:
        db_table = 'parcel_historisation\".\"division_operation'

class Balance(models.Model):
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    source_rp = models.BooleanField()
    destination_rp = models.BooleanField()
    source_origin = models.BooleanField()
    current_destination = models.BooleanField()
    id_division = models.ForeignKey(Operation, verbose_name='id_division')

    class Meta:
        db_table = 'parcel_historisation\".\"other_operation'

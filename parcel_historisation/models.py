from django.db import models

class State(models.Model):
    name = models.CharField(max_length=1000)
  
    class Meta:
        db_table = 'parcel_historisation\".\"state'

class Designation(models.Model):
    name = models.CharField(max_length=1000)
    class Meta:
        db_table = 'parcel_historisation\".\"designation'

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
    date = models.DateField()
    user = models.CharField(max_length=200, null=False)
    complement = models.CharField(max_length=5000)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, verbose_name='plan', blank=True, null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"operation'

class OtherOperation(models.Model):
    type = models.IntegerField()
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, verbose_name='operation', null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"other_operation'

class DivisonReunion(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, verbose_name='operation', null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"division_operation'

class Balance(models.Model):
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    source_rp = models.BooleanField()
    destination_rp = models.BooleanField()
    source_origin = models.BooleanField()
    current_destination = models.BooleanField()
    id_division = models.ForeignKey(Operation, on_delete=models.SET_NULL, verbose_name='id_division', null=True)

    class Meta:
        db_table = 'parcel_historisation\".\"balance'

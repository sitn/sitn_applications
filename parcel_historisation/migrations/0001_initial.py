# Generated by Django 4.0.5 on 2023-03-28 07:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
            sql=[("CREATE SCHEMA IF NOT EXISTS parcel_historisation;")],
            reverse_sql=[("DROP SCHEMA parcel_historisation CASCADE;")],
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'parcel_historisation"."designation',
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('user', models.CharField(max_length=200)),
                ('complement', models.CharField(max_length=5000)),
            ],
            options={
                'db_table': 'parcel_historisation"."operation',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'parcel_historisation"."state',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('link', models.CharField(max_length=1000)),
                ('plan_number', models.BigIntegerField()),
                ('index', models.IntegerField()),
                ('scale', models.IntegerField(null=True)),
                ('date_plan', models.DateField(null=True)),
                ('cadastre', models.IntegerField()),
                ('id_plan_old', models.BigIntegerField()),
                ('designation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='parcel_historisation.designation', verbose_name='designation')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='parcel_historisation.state', verbose_name='state')),
            ],
            options={
                'db_table': 'parcel_historisation"."plan',
            },
        ),
        migrations.CreateModel(
            name='OtherOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField()),
                ('id_operation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='parcel_historisation.operation', verbose_name='id_operation')),
            ],
            options={
                'db_table': 'parcel_historisation"."other_operation',
            },
        ),
        migrations.AddField(
            model_name='operation',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='parcel_historisation.plan', verbose_name='plan'),
        ),
        migrations.CreateModel(
            name='DivisonReunion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_operation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='parcel_historisation.operation', verbose_name='id_operation')),
            ],
            options={
                'db_table': 'parcel_historisation"."division_operation',
            },
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=200)),
                ('destination', models.CharField(max_length=200)),
                ('source_rp', models.BooleanField()),
                ('destination_rp', models.BooleanField()),
                ('source_origin', models.BooleanField()),
                ('current_destination', models.BooleanField()),
                ('id_division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='parcel_historisation.operation', verbose_name='id_division')),
            ],
            options={
                'db_table': 'parcel_historisation"."balance',
            },
        ),
    ]

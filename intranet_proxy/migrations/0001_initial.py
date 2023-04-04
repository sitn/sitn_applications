# Generated by Django 4.0.5 on 2023-02-20 17:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL('CREATE SCHEMA IF NOT EXISTS sitn_applications;'),
        migrations.CreateModel(
            name='VcronRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=120, unique=True)),
                ('vcron_guid', models.CharField(max_length=36, validators=[django.core.validators.RegexValidator(message='VCRON guid is not valid', regex='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$')])),
            ],
            options={
                'db_table': 'vcron_route',
            },
        ),
    ]

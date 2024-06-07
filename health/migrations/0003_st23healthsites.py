# Generated by Django 4.0.5 on 2024-06-07 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0002_st18independants_st19cabinets_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='St23HealthSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=120, verbose_name='site_name')),
                ('public_link', models.URLField(blank=True, max_length=255, verbose_name='public_link')),
                ('address', models.CharField(max_length=255, verbose_name='address')),
            ],
            options={
                'verbose_name': 'St23HealthSite',
                'db_table': 'sante"."st23_health_site',
                'managed': False,
            },
        ),
    ]
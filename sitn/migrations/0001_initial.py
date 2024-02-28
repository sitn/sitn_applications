# Generated by Django 4.0.5 on 2024-02-28 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunSQL('CREATE TEXT SEARCH CONFIGURATION public.fr (PARSER=default)'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR asciihword WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR asciiword WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR email WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR file WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR float WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR host WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR hword WITH simple, public.unaccent'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR hword_asciipart WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR hword_numpart WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR hword_part WITH simple, public.unaccent'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR int WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR numhword WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR numword WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR sfloat WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR uint WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR url WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR url_path WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR version WITH simple'),
        migrations.RunSQL('ALTER TEXT SEARCH CONFIGURATION public.fr ADD MAPPING FOR word WITH simple, public.unaccent')
    ]
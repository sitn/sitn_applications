from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parcel_historisation", "0006_create_balance_view"),
    ]

    operations = [
        # Existing DDP relations were all immatriculations: renaming keeps their value.
        migrations.RenameField(
            model_name="balance",
            old_name="destination_ddp",
            new_name="immatriculation_ddp",
        ),
        migrations.AddField(
            model_name="balance",
            name="exmatriculation_ddp",
            field=models.BooleanField(default=False),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0001_initial"),
        ("records", "0003_record_main_emotion"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="place",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="records",
                to="locations.place",
            ),
        ),
    ]

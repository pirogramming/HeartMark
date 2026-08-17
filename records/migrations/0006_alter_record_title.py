from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("records", "0005_record_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="title",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]

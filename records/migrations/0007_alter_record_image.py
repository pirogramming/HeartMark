from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("records", "0006_alter_record_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="image",
            field=models.ImageField(blank=True, upload_to="records/%Y/%m/%d/"),
        ),
    ]

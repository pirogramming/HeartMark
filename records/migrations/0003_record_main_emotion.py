from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


def set_existing_main_emotions(apps, schema_editor):
    Record = apps.get_model("records", "Record")
    for record in Record.objects.all().iterator():
        emotions = record.emotions if isinstance(record.emotions, list) else []
        if not emotions:
            emotions = [1]
            record.emotions = emotions
        record.main_emotion = int(emotions[0])
        record.save(update_fields=["emotions", "main_emotion"])


class Migration(migrations.Migration):
    dependencies = [
        ("records", "0002_alter_record_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="main_emotion",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[MinValueValidator(1), MaxValueValidator(20)],
            ),
        ),
        migrations.RunPython(
            set_existing_main_emotions,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="record",
            name="main_emotion",
            field=models.PositiveSmallIntegerField(
                validators=[MinValueValidator(1), MaxValueValidator(20)],
            ),
        ),
    ]

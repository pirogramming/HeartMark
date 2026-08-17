from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("record_sharing", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecordShareComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.CharField(max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="record_share_comments", to=settings.AUTH_USER_MODEL)),
                ("share", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="record_sharing.recordshare")),
            ],
            options={"ordering": ["created_at"]},
        ),
    ]

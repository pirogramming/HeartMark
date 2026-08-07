# Generated manually for the friendships app.

import friendships.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Invitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(default=friendships.models.make_invitation_code, max_length=32, unique=True)),
                ("status", models.CharField(choices=[("pending", "대기"), ("accepted", "수락"), ("rejected", "거절"), ("cancelled", "취소")], default="pending", max_length=12)),
                ("message", models.CharField(blank=True, max_length=120)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invitee", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="received_friend_invitations", to=settings.AUTH_USER_MODEL)),
                ("inviter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sent_friend_invitations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Friendship",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user1", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="friendships_as_user1", to=settings.AUTH_USER_MODEL)),
                ("user2", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="friendships_as_user2", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="invitation",
            constraint=models.CheckConstraint(condition=(models.Q(("invitee__isnull", True)) | ~models.Q(("inviter", django.db.models.expressions.F("invitee")))), name="invitation_prevent_self_request"),
        ),
        migrations.AddConstraint(
            model_name="friendship",
            constraint=models.CheckConstraint(condition=~models.Q(("user1", django.db.models.expressions.F("user2"))), name="friendship_prevent_self_relation"),
        ),
        migrations.AddConstraint(
            model_name="friendship",
            constraint=models.UniqueConstraint(fields=("user1", "user2"), name="friendship_unique_user_pair"),
        ),
    ]

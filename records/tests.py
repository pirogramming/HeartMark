from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import RecordForm
from .models import Record


def uploaded_image(name="record.gif"):
    return SimpleUploadedFile(
        name,
        b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        content_type="image/gif",
    )


class RecordFormTests(TestCase):
    def test_image_weather_content_and_emotion_are_required(self):
        form = RecordForm(data={})
        self.assertFalse(form.is_valid())
        for field in ("image", "weather", "content", "emotions", "main_emotion"):
            self.assertIn(field, form.errors)

    def test_more_than_three_emotions_are_rejected(self):
        form = RecordForm(data={
            "weather": "sunny",
            "content": "오늘의 마음",
            "emotions": ["1", "2", "3", "4"],
            "main_emotion": "1",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("emotions", form.errors)

    def test_main_emotion_must_be_one_of_selected_emotions(self):
        form = RecordForm(
            data={
                "weather": "sunny",
                "content": "오늘의 마음",
                "emotions": ["2", "5"],
                "main_emotion": "9",
            },
            files={"image": uploaded_image()},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("main_emotion", form.errors)


class RecordCreateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="records-user", password="test-password"
        )

    def test_login_is_required(self):
        response = self.client.post(reverse("records:create"), {})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_valid_record_is_saved_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("records:create"), {
            "weather": "cloudy",
            "content": "기록 생성 테스트",
            "emotions": ["2", "5", "9"],
            "main_emotion": "5",
            "place_name": "테스트 장소",
            "latitude": "37.5665000",
            "longitude": "126.9780000",
            "image": uploaded_image(),
        })

        record = Record.objects.get()
        self.assertRedirects(response, reverse("records:detail", args=[record.pk]))
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.emotions, [2, 5, 9])
        self.assertEqual(record.main_emotion, 5)


class RecordCrudViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user("owner", password="password")
        self.other_user = user_model.objects.create_user("other", password="password")
        self.record = Record.objects.create(
            user=self.owner,
            weather="sunny",
            content="수정 전 기록",
            emotions=[1],
            main_emotion=1,
            image=uploaded_image("existing.gif"),
        )

    def test_owner_can_view_and_update_record(self):
        self.client.force_login(self.owner)
        detail_response = self.client.get(
            reverse("records:detail", args=[self.record.pk])
        )
        self.assertContains(detail_response, "수정 전 기록")

        edit_response = self.client.get(
            reverse("records:update", args=[self.record.pk])
        )
        self.assertEqual(edit_response.status_code, 200)
        self.assertContains(edit_response, "수정 완료")
        self.assertEqual(edit_response.context["selected_emotions"], [1])

        update_response = self.client.post(
            reverse("records:update", args=[self.record.pk]),
            {
                "weather": "rainy",
                "content": "수정한 기록",
                "emotions": ["3"],
                "main_emotion": "3",
            },
        )
        self.assertRedirects(
            update_response, reverse("records:detail", args=[self.record.pk])
        )
        self.record.refresh_from_db()
        self.assertEqual(self.record.content, "수정한 기록")
        self.assertEqual(self.record.main_emotion, 3)

    def test_other_user_cannot_view_record(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse("records:detail", args=[self.record.pk]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_delete_record(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("records:delete", args=[self.record.pk])
        )
        self.assertRedirects(response, reverse("records:modal_preview"))
        self.assertFalse(Record.objects.filter(pk=self.record.pk).exists())

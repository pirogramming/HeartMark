from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


EMOTION_NAMES = {
    1: "슬픔",
    2: "사랑",
    3: "따분",
    4: "예민",
    5: "만족",
    6: "슬픔",
    7: "짝사랑",
    8: "심술",
    9: "당황",
    10: "슬픔",
    11: "화남",
    12: "신남",
    13: "아픔",
    14: "놀람",
    15: "행운",
    16: "기쁨",
    17: "질투",
    18: "맛있어!",
    19: "냉철",
    20: "졸림",
}


class Record(models.Model):
    class Weather(models.TextChoices):
        SUNNY = "sunny", "해"
        CLOUDY = "cloudy", "구름"
        RAINY = "rainy", "비"
        THUNDER = "thunder", "천둥"
        DUST = "dust", "미세먼지"
        SNOWY = "snowy", "눈"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="heartmark_records",
    )
    weather = models.CharField(max_length=10, choices=Weather.choices)
    title = models.CharField(max_length=20, blank=True)
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to="records/%Y/%m/%d/", blank=True)
    emotions = models.JSONField(default=list)
    main_emotion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
    )

    place = models.ForeignKey(
        "locations.Place",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="records",
    )

    # Legacy snapshot fields are kept so existing records and diary views remain compatible.
    place_name = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}의 기록 ({self.created_at:%Y-%m-%d})"

    @property
    def weather_image_name(self):
        return f"{self.weather}.png"

    @property
    def emotion_image_names(self):
        return [f"emotion-{int(number):02d}.png" for number in self.emotions]

    @property
    def emotion_items(self):
        numbers = [int(number) for number in self.emotions]
        numbers.sort(key=lambda number: number != self.main_emotion)
        return [
            {
                "number": number,
                "image_name": f"emotion-{number:02d}.png",
                "name": EMOTION_NAMES.get(number, f"감정 {number}"),
                "is_main": number == self.main_emotion,
            }
            for number in numbers
        ]

    def clean(self):
        super().clean()
        if not isinstance(self.emotions, list):
            raise ValidationError({"emotions": "감정은 목록 형태여야 합니다."})
        if not self.emotions:
            raise ValidationError({"emotions": "감정을 1개 이상 선택해 주세요."})
        if len(self.emotions) > 3:
            raise ValidationError({"emotions": "감정은 최대 3개까지 선택할 수 있습니다."})
        if self.main_emotion not in self.emotions:
            raise ValidationError({
                "main_emotion": "선택한 감정 중에서 대표 감정을 골라주세요."
            })

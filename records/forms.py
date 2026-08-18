from django import forms

from .models import Record


class RecordForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    emotions = forms.MultipleChoiceField(
        choices=[(str(number), f"감정 {number}") for number in range(1, 21)],
        required=True,
        error_messages={"required": "감정을 1개 이상 선택해 주세요."},
    )
    main_emotion = forms.ChoiceField(
        choices=[
            ("", "메인 감정 선택"),
            *[
                (str(number), f"감정 {number}")
                for number in range(1, 21)
            ],
        ],
        required=True,
        error_messages={"required": "대표 감정을 선택해 주세요."},
    )

    class Meta:
        model = Record
        fields = [
            "weather", "title", "content", "image", "emotions", "main_emotion",
            "place_name", "latitude", "longitude",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not self.is_bound:
            self.initial["emotions"] = [
                str(emotion) for emotion in self.instance.emotions
            ]
            self.initial["main_emotion"] = str(self.instance.main_emotion)

    def clean_emotions(self):
        emotions = self.cleaned_data.get("emotions", [])
        if len(emotions) > 3:
            raise forms.ValidationError("감정은 최대 3개까지 선택할 수 있습니다.")
        return [int(emotion) for emotion in emotions]

    def clean_image(self):
        uploaded_images = self.files.getlist("image")
        if len(uploaded_images) > 1:
            raise forms.ValidationError("사진은 한 장만 선택할 수 있어요.")
        return self.cleaned_data.get("image")

    def clean_main_emotion(self):
        return int(self.cleaned_data["main_emotion"])

    def clean(self):
        cleaned_data = super().clean()
        emotions = cleaned_data.get("emotions", [])
        main_emotion = cleaned_data.get("main_emotion")
        if main_emotion is not None and main_emotion not in emotions:
            self.add_error(
                "main_emotion",
                "선택한 감정 중에서 대표 감정을 골라주세요.",
            )
        return cleaned_data

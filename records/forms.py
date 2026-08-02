from django import forms

from .models import Record


class RecordForm(forms.ModelForm):
    emotions = forms.MultipleChoiceField(
        choices=[(str(number), f"감정 {number}") for number in range(1, 21)],
        required=True,
        error_messages={"required": "감정을 1개 이상 선택해 주세요."},
    )

    class Meta:
        model = Record
        fields = [
            "weather", "content", "image", "emotions",
            "place_name", "latitude", "longitude",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not self.is_bound:
            self.initial["emotions"] = [
                str(emotion) for emotion in self.instance.emotions
            ]

    def clean_emotions(self):
        emotions = self.cleaned_data.get("emotions", [])
        if len(emotions) > 3:
            raise forms.ValidationError("감정은 최대 3개까지 선택할 수 있습니다.")
        return [int(emotion) for emotion in emotions]

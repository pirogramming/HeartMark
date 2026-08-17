"""공유 대상 친구를 고르는 폼."""

from django import forms

from friendships.services import get_friends
from records.models import Record


class RecordShareForm(forms.Form):
    """기록 상세의 '공유하기' 모달에서 넘어오는 값을 검증한다.

    ModelForm 이 아니라 그냥 Form 인 이유:
    이 폼이 만드는 건 RecordShare 한 개가 아니라 "고른 친구 수만큼" 여러 개다.
    실제 생성은 services.share_record_with_friends() 가 하고,
    이 폼은 '입력값이 올바른가'만 본다.
    """

    # 공유할 친구들. 체크박스로 여러 명 고를 수 있다.
    # queryset 은 아래 __init__ 에서 "이 사용자의 친구"로 좁힌다.
    # ModelMultipleChoiceField 는 넘어온 id 가 queryset 안에 없으면 자동으로 걸러내므로,
    # 남의 id 를 손으로 끼워 넣어도 여기서 막힌다. (1차 방어)
    friends = forms.ModelMultipleChoiceField(
        queryset=None,
        error_messages={
            "required": "공유할 친구를 선택해 주세요.",
            "invalid_choice": "친구가 아닌 사용자에게는 공유할 수 없습니다.",
        },
    )

    record_ids = forms.ModelMultipleChoiceField(queryset=Record.objects.none(), required=True)

    # '장소도 함께 공유' 체크박스.
    # required=False 가 중요하다. 체크박스는 체크를 안 하면 아예 값이 안 넘어오는데,
    # required=True 면 "체크 안 함"이 오류가 되어버린다.
    # 체크를 안 하면 False → 장소 비공개. 이게 기본값이다.
    share_location = forms.BooleanField(required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # 선택 가능한 대상을 "지금 이 사용자의 친구"로 제한한다.
        # 폼을 만들 때마다 친구 목록을 다시 계산하므로, 방금 친구를 끊었다면
        # 그 사람은 바로 선택지에서 사라진다.
        self.fields["friends"].queryset = get_friends(user) if user else None
        self.fields["record_ids"].queryset = Record.objects.filter(user=user).order_by("-created_at") if user else Record.objects.none()

# 담당 신은아: RecordShare

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class RecordShare(models.Model):
    """
    "이 기록(record)을 내가(sender) 이 친구에게(receiver) 공유했다" 라는 사실 하나를 저장하는 모델.

    기록 자체는 records.Record가 이미 갖고 있으므로 여기서 기록 내용을 복사해오지 않는다.
    이 모델은 오직 "누가 누구에게 무엇을 공유했고, 장소까지 보여줄지" 만 기록한다.

    한 기록을 친구 3명에게 공유하면 이 모델의 행(row)이 3개 생긴다.
    친구마다 장소 공개 여부(share_location)를 다르게 줄 수 있기 때문에
    "기록 1개 = 공유 1개"가 아니라 "기록 1개 + 받는 사람 1명 = 공유 1개"가 기본 단위다.

    기본 원칙: 모든 기록은 '나만 보기'다. 이 모델에 행이 생긴 경우에만 그 친구가 볼 수 있다.
    """

    # ------------------------------------------------------------------
    # 관계 필드
    # ------------------------------------------------------------------

    # 공유 대상 기록.
    # on_delete=CASCADE: 원본 기록이 삭제되면 그 기록에 대한 공유도 함께 사라져야 한다.
    #   공유 기록만 남아 있으면 존재하지 않는 기록을 가리키게 되므로 반드시 같이 지운다.
    # related_name="shares": 기록 쪽에서 record.shares.all() 로 이 기록의 공유 목록을 볼 수 있다.
    #   (records 앱을 수정하지 않고도 역참조가 생긴다 — 기존 앱 수정 금지 규칙을 지키는 방법)
    record = models.ForeignKey(
        "records.Record",
        on_delete=models.CASCADE,
        related_name="shares",
    )

    # 공유한 사람 = 기록 작성자.
    # 이론상 record.user 와 항상 같은 값이라 중복처럼 보이지만, 일부러 따로 저장한다.
    #   1) "내가 보낸 공유 목록"을 record 테이블까지 join 하지 않고 바로 조회할 수 있다.
    #   2) 나중에 '친구가 대신 공유' 같은 기능이 생겨도 모델을 갈아엎지 않아도 된다.
    # settings.AUTH_USER_MODEL: User 모델을 직접 import 하지 않고 settings 를 통해 가리키는 게
    #   Django 표준이다. 나중에 프로젝트가 커스텀 User 모델로 바뀌어도 이 코드는 안 고쳐도 된다.
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_record_shares",
    )

    # 공유받은 친구.
    # 이 사람이 로그인했을 때 '공유받은 기록' 목록에 이 기록이 뜬다.
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_record_shares",
    )

    # ------------------------------------------------------------------
    # 값 필드
    # ------------------------------------------------------------------

    # 장소까지 같이 공개할지 여부.
    # default=False 가 핵심이다. 사용자가 '장소도 함께 공유'를 직접 체크했을 때만 True 가 된다.
    #   → 실수로 위치가 새는 방향이 아니라, 실수하면 위치가 가려지는 방향으로 기본값을 잡았다.
    # 이 값이 False 면 3단계의 get_shared_place_data() 가 장소명·주소·구·좌표를 전부 숨긴다.
    share_location = models.BooleanField(default=False)

    # 공유한 시각. auto_now_add=True 라서 행이 처음 저장될 때 자동으로 채워지고 이후 안 바뀐다.
    created_at = models.DateTimeField(auto_now_add=True)

    # 공유를 취소한 시각. 아직 취소 안 했으면 None.
    #
    # [설계 결정] 공유 취소를 행 삭제(delete)가 아니라 '취소 시각 기록'으로 처리한다.
    #   기획서의 RecordShare 에 '공유 취소일'이 필드로 잡혀 있기 때문이다.
    #   즉 취소해도 행은 남고, revoked_at 에 시각만 찍힌다. (= 소프트 삭제)
    #   덕분에 "언제 공유했다가 언제 취소했는지" 이력이 남는다.
    #
    # 이 방식의 대가: "지금 유효한 공유"를 찾을 때 항상 revoked_at__isnull=True 를 붙여야 한다.
    #   이걸 빼먹으면 취소된 공유가 그대로 보이는 버그가 된다. 3단계 services.py 에서 이 조건을
    #   한 곳에 모아두고 뷰에서는 그 함수만 쓰도록 해서 실수를 막는다.
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # 최근에 공유한 것이 목록 위로 오도록 정렬한다.
        ordering = ["-created_at"]

        constraints = [
            # (1) 자기 자신에게 공유 방지.
            #     CheckConstraint 는 DB 자체에 거는 규칙이라, 코드에서 검사를 빠뜨려도 DB가 막아준다.
            #     condition= 은 "이 조건을 만족해야만 저장 허용"이라는 뜻이다.
            #     ~Q(sender=receiver) = "sender 와 receiver 가 같지 않을 것".
            #     (Django 5.1 부터 check= 대신 condition= 을 쓴다. friendships 앱과 같은 문법)
            models.CheckConstraint(
                condition=~Q(sender=models.F("receiver")),
                name="record_share_prevent_self_share",
            ),
            # (2) 중복 공유 방지 — 단, '아직 취소되지 않은 공유'끼리만.
            #
            #     그냥 UniqueConstraint(record, receiver) 로 걸면 문제가 생긴다.
            #     위에서 취소를 소프트 삭제로 정했기 때문에, 취소된 행이 계속 남아 있어서
            #     같은 친구에게 다시 공유하려 할 때 "이미 있음" 으로 막혀버린다.
            #
            #     그래서 condition 을 붙여서 revoked_at 이 비어 있는(=살아있는) 행에만
            #     유일성을 적용한다. 이렇게 하면
            #       - 살아있는 공유는 (기록, 받는사람) 조합당 최대 1개  → 중복 공유 차단
            #       - 취소된 공유는 몇 개든 남을 수 있음               → 이력 보존 + 재공유 가능
            #     둘 다 만족한다. (부분 인덱스라고 부르고 SQLite/PostgreSQL 모두 지원한다)
            models.UniqueConstraint(
                fields=["record", "receiver"],
                condition=Q(revoked_at__isnull=True),
                name="record_share_unique_active_per_receiver",
            ),
        ]

        indexes = [
            # "나에게 공유된 살아있는 기록 목록"(get_shared_records)은 가장 자주 실행될 쿼리다.
            # receiver 로 걸러내는 인덱스를 미리 만들어 두면 친구·공유가 늘어나도 느려지지 않는다.
            models.Index(fields=["receiver", "-created_at"], name="record_share_receiver_idx"),
        ]

    def __str__(self):
        # admin 목록에서 한 줄로 알아볼 수 있게. 취소된 건 뒤에 표시를 붙인다.
        state = "" if self.is_active else " (취소됨)"
        return f"{self.sender} → {self.receiver}: 기록 {self.record_id}{state}"

    @property
    def is_active(self):
        """지금 유효한 공유인지. revoked_at 이 비어 있으면 살아있는 공유다."""
        return self.revoked_at is None

    def revoke(self):
        """공유를 취소한다. 이미 취소된 공유를 또 취소해도 처음 취소한 시각을 덮어쓰지 않는다."""
        if self.is_active:
            self.revoked_at = timezone.now()
            self.save(update_fields=["revoked_at"])
        return self

    def clean(self):
        """
        모델 단위 검증.

        DB의 CheckConstraint 는 IntegrityError 라는 투박한 에러를 내기 때문에,
        여기서 먼저 걸러서 사람이 읽을 수 있는 한국어 메시지를 준다.

        주의: 여기서 '친구인지'는 검사하지 않는다.
        친구 여부는 friendships 앱을 조회해야 알 수 있는데, 모델의 clean() 안에서 다른 앱을
        조회하면 두 앱이 서로 얽혀버린다. 친구 검사·권한 검사는 3단계 services.py 에서 한다.
        모델은 "이 데이터 자체가 말이 되는가"만 본다.
        """
        super().clean()

        if self.sender_id and self.receiver_id and self.sender_id == self.receiver_id:
            raise ValidationError("자기 자신에게는 기록을 공유할 수 없습니다.")

        # 공유는 기록 작성자만 할 수 있다.
        # record_id 만 있고 아직 record 객체를 안 불러온 경우도 있어서 record_id 로 먼저 확인한다.
        if self.record_id and self.sender_id and self.record.user_id != self.sender_id:
            raise ValidationError("자신이 작성한 기록만 공유할 수 있습니다.")

    def save(self, *args, **kwargs):
        # full_clean() 을 호출해 저장 직전에 위 clean() 검증을 반드시 거치게 한다.
        # (Django 는 기본적으로 save() 시 검증을 하지 않는다. friendships.Friendship 도 같은 방식)
        self.full_clean()
        return super().save(*args, **kwargs)


class RecordShareComment(models.Model):
    """공유된 기록에 남기는 짧은 댓글."""

    share = models.ForeignKey(
        RecordShare,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="record_share_comments",
    )
    content = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author}: {self.content[:20]}"

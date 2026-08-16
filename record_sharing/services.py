"""
기록 공유 공통 함수.

다른 앱(social_hub 화면, record_sharing 뷰)은 RecordShare 모델을 직접 조회하지 않고
반드시 이 파일의 함수만 사용한다. 이유는 두 가지다.

1) "살아있는 공유"의 정의가 한 곳에만 있어야 한다.
   2단계에서 공유 취소를 소프트 삭제(revoked_at 에 시각 기록)로 정했기 때문에,
   유효한 공유를 찾으려면 항상 revoked_at__isnull=True 를 붙여야 한다.
   이 조건을 화면마다 따로 쓰면 언젠가 한 곳에서 빠뜨리고, 그러면 취소한 기록이
   친구에게 계속 보이는 버그가 된다. 그래서 이 파일 안에만 조건을 둔다.

2) 장소 공개 여부 판단이 한 곳에만 있어야 한다.
   장소는 아래 get_shared_place_data() 를 거쳐서만 밖으로 나간다.
   화면에서 record.place 나 record.latitude 를 직접 읽으면 비공개 장소가 그대로 샌다.

용어:
    sender   = 공유한 사람 = 기록 작성자
    receiver = 공유받은 친구
    viewer   = 지금 화면을 보고 있는 사람 (작성자일 수도, 공유받은 친구일 수도 있다)


[친구 해제 정책]

친구를 끊으면 그 전에 공유했던 기록도 더 이상 볼 수 없다.
"친구니까 보여준 것"이므로 친구가 아니게 되면 근거가 사라진다고 본다.

구현 방식: 친구를 끊는 시점에 RecordShare 를 손대지 않고, **볼 때마다 친구인지 확인**한다.
검사는 can_view_shared_record() 와 get_shared_records() 두 곳에서 한다.

왜 이렇게 했나 (친구 삭제 시 공유를 같이 지우는 방식과 비교):

  1) friendships 앱을 수정하지 않아도 된다.
     친구 삭제 시점에 공유를 지우려면 friendships 의 delete_friend() 에 손을 대거나
     시그널을 걸어야 하는데, 팀 규칙상 남의 앱은 건드리지 않는다.

  2) 다시 친구가 되면 예전 공유가 자연스럽게 되살아난다.
     싸웠다가 화해한 경우 다시 공유해달라고 하지 않아도 된다.
     (지웠다면 영영 복구 불가능하다)

  3) 데이터가 한쪽으로만 흐른다.
     friendships 가 진실이고 record_sharing 이 그걸 참조할 뿐이라, 두 앱의 상태가
     어긋날 일이 없다. 지우는 방식은 삭제가 한 번이라도 실패하면 계속 어긋난 채로 남는다.

대가: 조회할 때마다 친구 여부를 확인하는 비용이 든다.
     목록 조회는 친구 id 를 한 번에 가져와서 처리하므로 쿼리가 늘어나지 않는다.
"""

from django.db import IntegrityError, transaction

from friendships.services import are_friends, get_friends

from .models import RecordShare


class RecordShareError(ValueError):
    """공유가 규칙에 어긋날 때 발생. 메시지를 그대로 사용자에게 보여줄 수 있게 한국어로 쓴다.

    friendships 앱의 FriendshipError 와 같은 패턴이다.
    ValueError 를 상속해서, 호출하는 쪽에서 except RecordShareError 로만 잡으면 된다.
    """


# ----------------------------------------------------------------------
# 조회 (읽기)
# ----------------------------------------------------------------------


def _active_shares():
    """'아직 취소되지 않은 공유'의 기본 QuerySet.

    이 파일 안의 모든 조회는 여기서 출발한다.
    revoked_at__isnull=True 라는 조건이 코드 전체에서 오직 이 한 줄에만 존재하게 만드는 게 목적이다.
    """
    return RecordShare.objects.filter(revoked_at__isnull=True)


def get_shared_records(user):
    """`user` 가 공유받은 기록 목록. RecordShare 객체들의 QuerySet 을 돌려준다.

    Record 가 아니라 RecordShare 를 돌려주는 이유:
    같은 기록이라도 받는 사람에 따라 share_location 값이 다를 수 있다.
    화면에서 장소를 보여줄지 판단하려면 "어떤 공유 건으로 보고 있는지"를 알아야 하므로
    기록이 아니라 공유 자체를 넘긴다. 기록은 share.record 로 꺼내 쓰면 된다.

    친구 관계가 끊긴 사람이 보낸 공유는 목록에서 빠진다.
    (맨 아래 '친구 해제 정책' 설명 참고)

    select_related: 목록에서 각 항목마다 작성자·기록·장소를 출력하게 되는데, 그냥 두면
    항목 수만큼 추가 쿼리가 나간다(N+1 문제). 미리 JOIN 해서 쿼리 한 번으로 가져온다.
    """
    # 지금 내 친구인 사람들의 id 만 뽑아서, 그 사람들이 보낸 공유만 남긴다.
    # 공유 1건마다 are_friends() 를 호출하면 목록 길이만큼 쿼리가 나가므로(N+1),
    # 친구 id 목록을 한 번에 구해서 조건 하나로 거른다.
    friend_ids = get_friends(user).values_list("pk", flat=True)

    return (
        _active_shares()
        .filter(receiver=user, sender__in=friend_ids)
        .select_related("record", "sender", "record__place")
    )


def get_sent_records(user):
    """`user`가 친구들에게 보낸, 아직 취소하지 않은 마음 편지 목록."""
    return (
        _active_shares()
        .filter(sender=user)
        .select_related("record", "receiver", "record__place")
        .order_by("-created_at")
    )


def get_active_shares_for_record(record, sender):
    """`sender` 가 이 기록을 지금 누구에게 공유 중인지.

    공유 모달에서 "이미 공유한 친구"를 체크 표시하거나 공유 취소 버튼을 그릴 때 쓴다.
    (서영은 화면용)

    여기서는 친구 여부를 따지지 않는다. 이건 '내가 보낸 공유'의 목록이고,
    친구가 끊긴 상대에게 남아 있는 공유도 작성자에게는 보여야 취소할 수 있기 때문이다.
    (친구가 아니면 상대는 어차피 못 본다 — can_view_shared_record 가 막는다)
    """
    if record.user_id != sender.pk:
        return RecordShare.objects.none()
    return _active_shares().filter(record=record, sender=sender).select_related("receiver")


def can_view_shared_record(user, record):
    """`user` 가 이 기록을 볼 권한이 있는지 판단하는 단 하나의 관문.

    공유받은 기록을 화면에 그리기 전에 반드시 이 함수를 통과시킨다.
    records 앱의 상세 뷰는 `user=request.user` 로 잠겨 있어서 남의 기록을 아예 못 여는데,
    공유 기능에서는 "남의 기록이지만 나에게 공유된 것"을 열어줘야 하므로 판단 기준이 필요하다.

    True 가 되는 경우는 두 가지뿐이다.
      1) 내가 그 기록의 작성자다 (내 기록은 언제나 볼 수 있다)
      2) 나에게 온 살아있는 공유가 있고, **지금도 그 사람과 친구다**

    2번의 뒷조건이 '친구 해제 정책'이다. 맨 아래 설명 참고.
    """
    if not user or not user.is_authenticated:
        return False

    # 1) 작성자 본인
    if record.user_id == user.pk:
        return True

    # 2) 나에게 온 살아있는 공유가 있는지
    if not _active_shares().filter(record=record, receiver=user).exists():
        return False

    # 3) 친구 해제 정책 — 공유는 살아 있어도, 친구가 아니면 못 본다.
    #    친구를 끊는 순간 RecordShare 를 건드리지 않고, '볼 때마다' 친구인지 확인한다.
    #    이렇게 하는 이유는 아래 설명 참고.
    return are_friends(record.user, user)


# ----------------------------------------------------------------------
# 장소 공개 (이 앱에서 제일 조심해야 하는 부분)
# ----------------------------------------------------------------------


def _read_place(record):
    """기록에서 장소 정보를 긁어모은다. 공개 여부는 여기서 판단하지 않는다.

    ⚠️ 이 프로젝트의 기록은 장소를 **두 군데**에 갖고 있다.
        (1) record.place        → locations.Place 를 가리키는 FK (지금 방식)
        (2) record.place_name / record.latitude / record.longitude
            → 예전에 좌표를 기록에 직접 박아두던 시절의 스냅샷 필드.
              records/models.py 에 "legacy" 라고 주석까지 달려서 아직 남아 있고,
              지금도 기록을 저장할 때 값이 같이 채워진다.

    그래서 (1)만 가리고 (2)를 놓치면 좌표가 그대로 새어나간다.
    두 경로를 이 함수 한 곳에서 모두 읽어서, 밑의 get_shared_place_data() 가
    한 번에 가릴 수 있게 만든다.

    반환값이 None 이면 그 기록에는 애초에 장소가 없다는 뜻이다.
    """
    place = record.place  # FK. 장소가 지워졌으면(SET_NULL) None 일 수 있다.

    if place is not None:
        return {
            "name": place.name,
            "address": place.address,
            "district": place.district,
            "latitude": place.latitude,
            "longitude": place.longitude,
        }

    # FK 가 비어 있어도 레거시 스냅샷에 값이 남아 있을 수 있다. 여기가 누수 지점이다.
    if record.place_name or record.latitude is not None:
        return {
            "name": record.place_name,
            "address": "",       # 레거시 필드에는 상세 주소가 없다
            "district": "",      # 구 정보도 없다
            "latitude": record.latitude,
            "longitude": record.longitude,
        }

    return None


def get_shared_place_data(record_share, viewer):
    """공유받은 기록의 장소를 화면에 넘겨도 되는 형태로 가공한다.

    화면(social_hub 포함)은 record.place / record.latitude 를 직접 읽지 말고
    **반드시 이 함수의 결과만** 사용한다. 그래야 비공개 장소가 샐 수 없다.

    돌려주는 값:
        None                         → 볼 권한이 아예 없음 (화면에 아무것도 그리지 않는다)
        dict                         → 아래 형태

        {
            "has_place":  True/False,   원본 기록에 장소가 있는지
            "is_visible": True/False,   그 장소를 지금 보여줘도 되는지
            "name": ..., "address": ..., "district": ...,
            "latitude": ..., "longitude": ...,
        }

    has_place 와 is_visible 을 나눈 이유:
        화면에서 "장소 없이 쓴 기록"과 "장소는 있지만 친구가 비공개로 둔 기록"은
        다른 안내를 보여줘야 한다. (기획서의 '비공개 장소 안내 UI')
        어디에 있는지는 안 알려주고, 장소가 있다는 사실만 알려주는 정도는 안전하다.

    is_visible 이 False 면 name/address/district/latitude/longitude 는 전부 None 이다.
    즉 화면이 실수로 좌표를 출력하려 해도 출력할 값 자체가 없다.
    """
    # 1) 권한부터 확인. 권한이 없으면 장소가 있는지 없는지조차 알려주지 않는다.
    if not can_view_shared_record(viewer, record_share.record):
        return None

    place = _read_place(record_share.record)
    has_place = place is not None

    # 2) 보여줘도 되는지 판단.
    #    - 작성자 본인은 자기 장소니까 항상 볼 수 있다.
    #    - 공유받은 친구는 작성자가 share_location 을 켰을 때만 볼 수 있다.
    #    - 공유가 취소됐으면(is_active False) 볼 수 없다.
    is_author = record_share.record.user_id == viewer.pk
    is_visible = has_place and (
        is_author or (record_share.is_active and record_share.share_location)
    )

    # 3) 비공개면 값을 지운 껍데기를 돌려준다.
    #    빈 dict 가 아니라 키는 다 있고 값만 None 인 형태로 맞춘다.
    #    그래야 템플릿에서 키가 없어서 나는 오류 없이 그냥 빈 값으로 렌더된다.
    if not is_visible:
        return {
            "has_place": has_place,
            "is_visible": False,
            "name": None,
            "address": None,
            "district": None,
            "latitude": None,
            "longitude": None,
        }

    return {
        "has_place": True,
        "is_visible": True,
        **place,
    }


# ----------------------------------------------------------------------
# 공유하기 / 취소하기 (쓰기)
# ----------------------------------------------------------------------


def share_record(record, sender, receiver, share_location=False):
    """기록 하나를 친구 한 명에게 공유한다.

    통과해야 하는 조건 4개를 순서대로 검사한다. 하나라도 어기면 RecordShareError.
        1) sender 가 그 기록의 작성자인가
        2) 자기 자신에게 공유하는 건 아닌가
        3) 두 사람이 실제로 친구인가
        4) 이미 살아있는 공유가 있진 않은가

    2단계 모델에도 비슷한 검증(clean)이 있지만 역할이 다르다.
        모델      = 데이터 자체가 말이 되는가 (자기 공유 금지, 작성자 여부)
        여기      = 서비스 규칙 (친구인가, 중복인가) — 다른 앱을 조회해야 알 수 있는 것들
    모델은 friendships 앱을 몰라야 두 앱이 안 얽히므로, 친구 검사는 여기서만 한다.

    share_location: 기본값 False. 사용자가 '장소도 함께 공유'를 직접 체크했을 때만 True 로 넘어온다.
    """
    # (1) 작성자 본인만 공유할 수 있다.
    if record.user_id != sender.pk:
        raise RecordShareError("자신이 작성한 기록만 공유할 수 있습니다.")

    # (2) 자기 자신에게는 공유할 수 없다.
    if sender.pk == receiver.pk:
        raise RecordShareError("자기 자신에게는 기록을 공유할 수 없습니다.")

    # (3) 친구가 아니면 공유할 수 없다. 여기가 이 앱과 friendships 앱이 만나는 유일한 지점이다.
    if not are_friends(sender, receiver):
        raise RecordShareError("친구인 사용자에게만 기록을 공유할 수 있습니다.")

    # (4) 이미 공유 중이면 또 공유하지 않는다.
    #     취소된 공유는 여기 안 걸린다(_active_shares 가 살아있는 것만 보므로) → 재공유 가능.
    if _active_shares().filter(record=record, receiver=receiver).exists():
        raise RecordShareError("이미 이 친구에게 공유한 기록입니다.")

    # 위 (4) 검사와 실제 저장 사이의 아주 짧은 순간에 같은 요청이 두 번 들어오면
    # 검사를 둘 다 통과해버릴 수 있다(더블 클릭 등). 그때는 2단계에서 걸어둔 DB 제약이
    # IntegrityError 로 막아주므로, 그걸 잡아서 같은 한국어 메시지로 바꿔준다.
    try:
        with transaction.atomic():
            return RecordShare.objects.create(
                record=record,
                sender=sender,
                receiver=receiver,
                share_location=share_location,
            )
    except IntegrityError:
        raise RecordShareError("이미 이 친구에게 공유한 기록입니다.")


def share_record_with_friends(record, sender, receivers, share_location=False):
    """여러 친구에게 한 번에 공유한다. (공유 모달에서 친구를 복수 선택하는 경우)

    한 명이 실패했다고 전체를 취소하지 않는다.
    예를 들어 3명을 골랐는데 그중 1명에게 이미 공유한 상태라면,
    나머지 2명에게는 공유가 되고 1명만 실패로 보고한다.
    화면에서 "2명에게 공유했어요 / OO님은 이미 공유한 기록이에요" 처럼 안내할 수 있다.

    반환값:
        {
            "shared": [RecordShare, ...],       성공한 공유들
            "failed": [(user, "실패 이유"), ...]  실패한 친구와 이유
        }
    """
    shared = []
    failed = []

    for receiver in receivers:
        try:
            shared.append(share_record(record, sender, receiver, share_location))
        except RecordShareError as exc:
            failed.append((receiver, str(exc)))

    return {"shared": shared, "failed": failed}


def revoke_share(record, sender, receiver):
    """공유를 취소한다.

    행을 지우지 않고 revoked_at 에 현재 시각을 찍는다(2단계에서 정한 소프트 삭제).
    취소된 뒤에는
        - get_shared_records() 에 안 나오고
        - can_view_shared_record() 가 False 가 되고
        - 같은 친구에게 다시 공유할 수 있다

    취소에는 친구 여부를 요구하지 않는다. 친구를 끊은 뒤에도 작성자가 남은 공유를
    정리할 수 있어야 하기 때문이다. (공유할 때만 친구여야 한다)
    """
    if record.user_id != sender.pk:
        raise RecordShareError("자신이 작성한 기록의 공유만 취소할 수 있습니다.")

    share = _active_shares().filter(record=record, sender=sender, receiver=receiver).first()
    if share is None:
        raise RecordShareError("취소할 공유를 찾을 수 없습니다.")

    # 실제로 시각을 찍는 일은 2단계에서 모델에 만들어 둔 revoke() 가 한다.
    # 여기(서비스)는 "취소할 자격이 있는가"만 판단하고, 저장 방식은 모델에 맡긴다.
    return share.revoke()

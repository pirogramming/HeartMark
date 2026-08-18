"""
기록 공유 화면.

이 파일의 뷰는 권한 판단을 직접 하지 않는다.
"누가 무엇을 볼 수 있는가"는 전부 services.py 가 정하고, 뷰는 그 결과를 화면에 넘기기만 한다.
그래야 판단 기준이 한 곳에만 있고, 화면을 늘려도 규칙이 흔들리지 않는다.

특히 장소는 반드시 get_shared_place_data() 를 거쳐서만 context 에 넣는다.
record.place 나 record.latitude 를 그대로 넘기면 비공개 장소가 화면으로 새어나간다.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from records.models import Record

from .forms import RecordShareForm
from .models import RecordShare, RecordShareComment
from .services import (
    RecordShareError,
    can_view_shared_record,
    get_active_shares_for_record,
    get_shared_place_data,
    get_shared_records,
    revoke_share,
    share_record_with_friends,
)


def _back_to_record(request, record_id):
    """작업이 끝난 뒤 원래 보던 기록 상세로 돌려보낸다.

    폼에 next 값이 들어 있으면 그쪽을 우선한다. 어디서 공유 모달을 열었든
    (기록 상세든 다이어리 목록이든) 그 자리로 돌아가게 하려는 것이다.

    ⚠️ next 는 사용자가 보낸 값이라 그대로 믿으면 안 된다.
    외부 주소를 넣어두면 우리 사이트에서 엉뚱한 사이트로 튕겨 보내는 통로가 된다
    (open redirect). 그래서 '/'로 시작하는 내부 경로만 허용한다.
    """
    next_url = request.POST.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return HttpResponseRedirect(next_url)
    return redirect("records:detail", pk=record_id)


# ----------------------------------------------------------------------
# 공유하기 / 취소하기
# ----------------------------------------------------------------------


@login_required(login_url="accounts:login")
@require_POST
def share_create(request, record_id):
    """선택한 친구들에게 기록을 공유한다.

    @require_POST: 데이터를 바꾸는 동작이라 GET 으로는 못 들어오게 막는다.
    주소창에 URL 을 치거나 링크를 잘못 눌러서 공유가 되는 일을 방지한다.

    공유 대상 검증은 3중으로 걸린다.
        1) 폼        — 내 친구 목록 안에 있는 id 인지
        2) 서비스     — 작성자인지, 친구인지, 중복인지
        3) DB 제약   — 동시 요청으로 검사를 빠져나간 경우
    """
    # 내 기록이 아니면 여기서 404. 남의 기록을 공유하려는 시도를 입구에서 끊는다.
    record = get_object_or_404(Record, pk=record_id, user=request.user)

    # user=request.user 를 넘겨야 폼의 선택지가 '내 친구'로 좁혀진다.
    form = RecordShareForm(request.POST, user=request.user)
    if not form.is_valid():
        # 폼 오류를 메시지로 바꿔서 원래 화면에 그대로 보여준다.
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return _back_to_record(request, record_id)

    records = list(form.cleaned_data["record_ids"])
    results = [share_record_with_friends(record_item, request.user, form.cleaned_data["friends"], share_location=form.cleaned_data["share_location"]) for record_item in records]
    result = {"shared": [item for result_item in results for item in result_item["shared"]], "failed": [item for result_item in results for item in result_item["failed"]]}

    # 성공한 사람과 실패한 사람을 나눠서 안내한다.
    # 3명을 골랐는데 1명만 실패했다면, 나머지 2명은 공유된 상태다.
    if result["shared"]:
        count = len(result["shared"])
        if form.cleaned_data["share_location"]:
            messages.success(request, f"{count}명에게 기록과 장소를 공유했어요.")
        else:
            messages.success(request, f"{count}명에게 기록을 공유했어요. (장소는 비공개)")

    for user, reason in result["failed"]:
        messages.error(request, f"{user.username}: {reason}")

    return _back_to_record(request, record_id)


@login_required(login_url="accounts:login")
@require_POST
def share_revoke(request, record_id):
    """공유를 취소한다. 취소할 상대는 POST 의 receiver 값으로 받는다.

    URL 에 receiver 를 넣지 않고 POST 본문으로 받는 이유는,
    '누구에게서 회수할지'가 주소가 아니라 폼에서 고르는 값이기 때문이다.
    """
    record = get_object_or_404(Record, pk=record_id, user=request.user)

    receiver_id = request.POST.get("receiver")
    if not receiver_id:
        messages.error(request, "공유를 취소할 친구를 찾을 수 없습니다.")
        return _back_to_record(request, record_id)

    # 취소 대상은 '이 기록의 살아있는 공유' 안에서만 찾는다.
    # 아무 사용자 id 나 받아서 조회하지 않으므로, 남의 공유를 건드릴 수 없다.
    share = get_active_shares_for_record(record, request.user).filter(
        receiver_id=receiver_id
    ).first()
    if share is None:
        messages.error(request, "이미 취소되었거나 존재하지 않는 공유입니다.")
        return _back_to_record(request, record_id)

    try:
        revoke_share(record, request.user, share.receiver)
        messages.info(request, f"{share.receiver.username}님과의 공유를 취소했어요.")
    except RecordShareError as exc:
        messages.error(request, str(exc))

    return _back_to_record(request, record_id)


# ----------------------------------------------------------------------
# 공유받은 기록 보기
# ----------------------------------------------------------------------


@login_required(login_url="accounts:login")
def shared_list(request):
    """나에게 공유된 기록 목록.

    get_shared_records() 가 이미
        - 취소된 공유
        - 친구가 끊긴 사람이 보낸 공유
    를 걸러서 주므로, 여기서 따로 거르지 않는다.
    """
    shares = get_shared_records(request.user)

    # 목록에서도 장소를 보여줄 수 있으므로(예: "OO에서 남긴 기록"),
    # 각 공유마다 공개 가능한 장소 정보를 미리 만들어서 넘긴다.
    # 템플릿에서 share.record.place 를 직접 읽지 못하게 하려는 것이다.
    items = [
        {"share": share, "record": share.record, "place": get_shared_place_data(share, request.user)}
        for share in shares
    ]

    return render(
        request,
        "record_sharing/shared_list.html",
        {"items": items},
    )


@login_required(login_url="accounts:login")
def shared_detail(request, pk):
    """공유받은 기록 상세.

    records 앱의 상세 뷰는 `get_object_or_404(Record, pk=pk, user=request.user)` 라서
    남의 기록은 아예 열리지 않는다. 공유 기능에서는 "남의 기록이지만 나에게 공유된 것"을
    열어야 하므로 상세 화면을 이 앱에 따로 둔다. (records 앱은 수정하지 않는다)

    pk 는 Record 가 아니라 RecordShare 의 pk 다.
    같은 기록이라도 받는 사람마다 share_location 이 다를 수 있어서,
    '어떤 공유 건으로 보고 있는지'를 알아야 장소 공개 여부를 판단할 수 있기 때문이다.
    """
    share = get_object_or_404(
        RecordShare.objects.select_related("record", "sender", "record__place"),
        pk=pk,
    )

    # 볼 자격이 없으면 404 로 답한다. 403(권한 없음)이 아니라 404 인 이유는,
    # 403 은 "그 공유는 존재한다"는 사실을 알려주는 셈이기 때문이다.
    # 존재 여부 자체를 숨기는 편이 안전하다.
    if not can_view_shared_record(request.user, share.record):
        raise Http404

    # 취소된 공유는 링크를 직접 열어도 안 보이게 한다.
    # (can_view_shared_record 는 '다른 살아있는 공유'가 있으면 True 를 줄 수 있으므로
    #  이 공유 건 자체가 살아있는지는 여기서 따로 확인한다)
    if not share.is_active and share.record.user_id != request.user.pk:
        raise Http404

    is_sender = request.user.pk == share.sender_id

    return render(
        request,
        "record_sharing/shared_detail.html",
        {
            "share": share,
            "record": share.record,
            # 장소는 반드시 이 함수를 거친 결과만 넘긴다.
            "place": get_shared_place_data(share, request.user),
            "shared_list_url": reverse("record_sharing:shared_list"),
            "mailbox_url": reverse(
                "social_hub:sent_records" if is_sender else "social_hub:shared_records"
            ),
            "mailbox_label": "보낸 편지함으로" if is_sender else "받은 편지함으로",
        },
    )


@login_required(login_url="accounts:login")
@require_POST
def comment_create(request, pk):
    """공유 당사자만 해당 마음 편지에 댓글을 남길 수 있다."""
    share = get_object_or_404(RecordShare, pk=pk, revoked_at__isnull=True)
    if request.user.pk not in {share.sender_id, share.receiver_id}:
        raise Http404

    content = request.POST.get("content", "").strip()
    if not content:
        messages.error(request, "댓글 내용을 입력해 주세요.")
    elif len(content) > 300:
        messages.error(request, "댓글은 300자 이내로 입력해 주세요.")
    else:
        RecordShareComment.objects.create(share=share, author=request.user, content=content)
        messages.success(request, "마음 한마디를 남겼어요.")

    mailbox = "social_hub:sent_records" if request.user.pk == share.sender_id else "social_hub:shared_records"
    return redirect(f"{reverse(mailbox)}?comments={share.pk}#shared-record-{share.pk}")


@login_required(login_url="accounts:login")
@require_POST
def comment_delete(request, pk, comment_id):
    """댓글 작성자 본인만 댓글을 삭제할 수 있다."""
    share = get_object_or_404(RecordShare, pk=pk, revoked_at__isnull=True)
    comment = get_object_or_404(
        RecordShareComment,
        pk=comment_id,
        share=share,
        author=request.user,
    )
    comment.delete()
    messages.success(request, "댓글을 삭제했어요.")

    mailbox = "social_hub:sent_records" if request.user.pk == share.sender_id else "social_hub:shared_records"
    return redirect(f"{reverse(mailbox)}?comments={share.pk}#shared-record-{share.pk}")

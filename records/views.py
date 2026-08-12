from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from locations.services import clear_verified_place, get_verified_place

from .forms import RecordForm
from .models import Record


def has_verified_location(request):
    """TODO: locations 앱의 인증 규격이 확정되면 실제 검사로 교체합니다."""
    return get_verified_place(request) is not None


@login_required(login_url="accounts:login")
def record_create(request):
    # GET으로 이 URL에 들어오는 건 "기록을 쓰겠다"는 진입 시도다.
    # 기록은 매번 그 순간의 장소에 남기는 것이므로, 오늘 이미 인증했더라도
    # 예외 없이 화면 1(위치 선택)부터 다시 시작시킨다.
    # 실제 작성 모달은 위치 확정 후 지도 화면에서 열리고, 그 폼이 여기로 POST한다.
    if request.method == "GET":
        return redirect("locations:place_select")

    verified_place = get_verified_place(request)
    if verified_place is None:
        # 인증이 만료됐거나 세션이 끊긴 채로 폼이 제출된 경우.
        return redirect("locations:place_select")

    form = RecordForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        record = form.save(commit=False)
        record.user = request.user
        record.place = verified_place
        record.place_name = verified_place.name or verified_place.address
        record.latitude = verified_place.latitude
        record.longitude = verified_place.longitude
        record.save()
        # 저장이 끝난 인증은 여기서 소진시킨다. 남겨두면 다음 기록이 사용자가
        # 다시 고르지 않은 이 장소로 저장될 수 있다.
        clear_verified_place(request)
        return redirect("records:detail", pk=record.pk)
    return render(request, "records/record_form.html", {"form": form, "mode": "create"})


@login_required(login_url="accounts:login")
def record_detail(request, pk):
    record = get_object_or_404(Record, pk=pk, user=request.user)
    return render(request, "records/record_detail.html", {"record": record})


@login_required(login_url="accounts:login")
def record_update(request, pk):
    record = get_object_or_404(Record, pk=pk, user=request.user)
    if request.method == "POST":
        form = RecordForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            return redirect("records:detail", pk=record.pk)
    else:
        form = RecordForm(instance=record)
    selected_emotions = (
        [int(value) for value in request.POST.getlist("emotions") if value.isdigit()]
        if request.method == "POST"
        else record.emotions
    )
    return render(request, "records/record_form.html", {
        "form": form,
        "record": record,
        "mode": "update",
        "emotion_numbers": range(1, 21),
        "selected_emotions": selected_emotions,
        "weather_choices": Record.Weather.choices,
    })


@login_required(login_url="accounts:login")
def record_delete(request, pk):
    record = get_object_or_404(Record, pk=pk, user=request.user)
    if request.method == "POST":
        record.delete()
        return redirect("diary:list")
    return render(request, "records/record_confirm_delete.html", {"record": record})

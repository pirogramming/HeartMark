from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from locations.services import get_verified_place

from .forms import RecordForm
from .models import Record


def record_modal_preview(request):
    """메인 화면 완성 전 기록 작성 모달을 독립적으로 확인하는 임시 화면."""
    return redirect(f"{reverse('common:home')}?open_record=1")


def has_verified_location(request):
    """TODO: locations 앱의 인증 규격이 확정되면 실제 검사로 교체합니다."""
    return get_verified_place(request) is not None


@login_required(login_url="accounts:login")
def record_create(request):
    verified_place = get_verified_place(request)
    if verified_place is None:
        return redirect("locations:place_select")

    if request.method == "GET":
        return redirect(f"{reverse('common:home')}?open_record=1")

    form = RecordForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        record.user = request.user
        record.place = verified_place
        record.place_name = verified_place.name or verified_place.address
        record.latitude = verified_place.latitude
        record.longitude = verified_place.longitude
        record.save()
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

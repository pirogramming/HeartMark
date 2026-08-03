from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RecordForm
from .models import Record


def record_modal_preview(request):
    """메인 화면 완성 전 기록 작성 모달을 독립적으로 확인하는 임시 화면."""
    return render(request, "records/record_modal_preview.html")


def has_verified_location(request):
    """TODO: locations 앱의 인증 규격이 확정되면 실제 검사로 교체합니다."""
    return True


@login_required
def record_create(request):
    if request.method == "POST" and not has_verified_location(request):
        return redirect("/locations/")

    form = RecordForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        record.user = request.user
        record.save()
        return redirect("records:detail", pk=record.pk)
    return render(request, "records/record_form.html", {"form": form, "mode": "create"})


@login_required
def record_detail(request, pk):
    record = get_object_or_404(Record, pk=pk, user=request.user)
    return render(request, "records/record_detail.html", {"record": record})


@login_required
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


@login_required
def record_delete(request, pk):
    record = get_object_or_404(Record, pk=pk, user=request.user)
    if request.method == "POST":
        record.delete()
        return redirect("records:modal_preview")
    return render(request, "records/record_confirm_delete.html", {"record": record})

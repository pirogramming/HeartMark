# 담당 D: 캘린더 및 다이어리 목록 조회

from django.shortcuts import render


def diary_list(request):
    return render(request, "diary/list.html")
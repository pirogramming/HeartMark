from django.urls import path

from . import views


app_name = "diary"


urlpatterns = [
    # 전체 / 감정별 / 장소별 다이어리 목록
    path(
        "",
        views.diary_list,
        name="list",
    ),

    # 감정 캘린더
    path(
        "calendar/",
        views.emotion_calendar,
        name="calendar",
    ),

    # 다이어리 기록 상세
    #
    # 예:
    # /diary/2/
    path(
        "<int:pk>/",
        views.diary_detail,
        name="detail",
    ),
]
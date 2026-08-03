from django.urls import path

from . import views


app_name = "diary"


urlpatterns = [
    # 기록 목록 페이지
    path(
        "",
        views.diary_list,
        name="list",
    ),

    # 감정 캘린더 페이지
    #
    # 접속 주소:
    # /diary/calendar/
    path(
        "calendar/",
        views.emotion_calendar,
        name="calendar",
    ),
    
    path(
        "<int:pk>/",
        views.diary_detail,
        name="detail",
    ),
]
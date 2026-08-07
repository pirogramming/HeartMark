from django.shortcuts import render


def friend_management(request):
    """친구 백엔드 연결 전 UI 확인을 위한 임시 화면."""
    context = {
        "invite_url": request.build_absolute_uri("/accounts/invite/HEART24/"),
        "friends": [
            {
                "id": 1,
                "name": "홍연우",
                "character_static": "accounts/images/1.png",
                "message": "12일째 함께 마음자국을 나누는 중",
            },
            {
                "id": 2,
                "name": "신은아",
                "character_static": "accounts/images/3.png",
                "message": "오늘 친구가 되었어요",
            },
            {
                "id": 3,
                "name": "한지수",
                "character_static": "accounts/images/5.png",
                "message": "5일째 함께 마음자국을 나누는 중",
            },
        ],
        "received_requests": [
            {
                "id": 11,
                "name": "마음이",
                "character_static": "accounts/images/2.png",
                "message": "마음자국 친구가 되고 싶대요!",
            },
            {
                "id": 12,
                "name": "구름이",
                "character_static": "accounts/images/4.png",
                "message": "새로운 친구 요청이 도착했어요.",
            },
        ],
        "sent_requests": [
            {
                "id": 21,
                "name": "별이",
                "character_static": "accounts/images/2.png",
                "message": "친구의 답장을 기다리고 있어요.",
            },
        ],
    }
    return render(request, "social_hub/friend_management.html", context)


def shared_records(request):
    """공유 백엔드 연결 전 목록 UI 확인을 위한 임시 화면."""
    context = {
        "shared_records": [
            {
                "share_id": 1,
                "sender_name": "홍연우",
                "sender_character_static": "accounts/images/1.png",
                "record_id": 15,
                "record_date": "2026년 8월 7일",
                "main_emotion": "16",
                "main_emotion_name": "기쁨",
                "image_static": "records/images/main-character-writing.png",
                "content_preview": "오늘은 천천히 걸으며 좋아하는 풍경을 오래 바라봤어요.",
                "share_location": True,
                "place_name": "서울숲",
            },
            {
                "share_id": 2,
                "sender_name": "신은아",
                "sender_character_static": "accounts/images/3.png",
                "record_id": 16,
                "record_date": "2026년 8월 6일",
                "main_emotion": "15",
                "main_emotion_name": "행운",
                "image_static": "accounts/images/tutorial-record-write.png",
                "content_preview": "우연히 예쁜 골목을 발견해서 마음자국을 남겼어요.",
                "share_location": False,
                "place_name": "",
            },
            {
                "share_id": 3,
                "sender_name": "한지수",
                "sender_character_static": "accounts/images/5.png",
                "record_id": 17,
                "record_date": "2026년 8월 3일",
                "main_emotion": "05",
                "main_emotion_name": "만족",
                "image_static": "accounts/images/tutorial-calendar.png",
                "content_preview": "기다리던 일을 마무리해서 뿌듯했던 하루였어요.",
                "share_location": True,
                "place_name": "북서울꿈의숲",
            },
        ]
    }
    return render(request, "social_hub/shared_records.html", context)

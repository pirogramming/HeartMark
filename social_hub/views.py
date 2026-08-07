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

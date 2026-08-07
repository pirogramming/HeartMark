# Friendships backend

친구 초대, 친구 요청, 친구 목록을 담당하는 백엔드 앱입니다.

## 연결할 때 필요한 설정

`config/settings.py`

```python
INSTALLED_APPS = [
    ...
    "friendships",
]
```

`config/urls.py`

```python
urlpatterns = [
    ...
    path("friendships/", include("friendships.urls")),
]
```

## 주요 URL

- `friendships:invite_link`: 내 초대 링크 생성/조회
- `friendships:invite_detail`: 초대 링크 접속, 수락/거절
- `friendships:list`: 받은 요청, 보낸 요청, 친구 목록
- `friendships:send_request`: 특정 사용자에게 친구 요청 보내기
- `friendships:respond_request`: 친구 요청 수락/거절
- `friendships:friend_delete`: 친구 삭제

## 다른 앱에서 쓰는 공용 함수

```python
from friendships.services import (
    are_friends,
    get_friends,
    get_received_requests,
    get_sent_requests,
)
```

- `are_friends(user1, user2)`: 두 사용자가 친구인지 확인
- `get_friends(user)`: 친구 목록 QuerySet 반환
- `get_received_requests(user)`: 받은 친구 요청 QuerySet 반환
- `get_sent_requests(user)`: 보낸 친구 요청 QuerySet 반환

## 모델

- `Friendship`: 수락 완료된 친구 관계
- `Invitation`: 초대 링크 및 친구 요청 상태

`Invitation.status` 값은 `pending`, `accepted`, `rejected`, `cancelled`입니다.

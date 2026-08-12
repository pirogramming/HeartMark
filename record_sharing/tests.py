"""
기록 공유 테스트.

이 앱에서 제일 중요한 건 '장소가 새지 않는가'다.
좌표는 한 번 새면 되돌릴 수 없는 정보라, PlaceVisibilityTests 를 가장 촘촘하게 짰다.

구성:
    RecordShareModelTests   모델 제약 (DB 가 막아주는 것)
    ShareRecordTests        공유 규칙
    RevokeTests             공유 취소
    VisibilityTests         누가 볼 수 있는가
    PlaceVisibilityTests    장소 공개 여부  ← 핵심
    UnfriendPolicyTests     친구를 끊었을 때
    ShareViewTests          공유/취소 화면
    SharedPageTests         받은 편지 목록·상세 화면
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse

from friendships.models import Friendship
from friendships.services import delete_friend
from locations.models import Place
from records.models import Record

from .models import RecordShare
from .services import (
    RecordShareError,
    can_view_shared_record,
    get_active_shares_for_record,
    get_shared_place_data,
    get_shared_records,
    revoke_share,
    share_record,
    share_record_with_friends,
)


class SharingTestBase(TestCase):
    """모든 테스트가 함께 쓰는 준비물.

    author 는 friend, friend2 와 친구고 stranger 와는 남남이다.
    record 에는 장소(서울숲)가 붙어 있고, 레거시 스냅샷 필드에도 같은 값이 들어 있다.
    """

    def setUp(self):
        user_model = get_user_model()
        self.author = user_model.objects.create_user(
            username="author", password="pass", first_name="연우"
        )
        self.friend = user_model.objects.create_user(
            username="friend", password="pass", first_name="은아"
        )
        self.friend2 = user_model.objects.create_user(username="friend2", password="pass")
        self.stranger = user_model.objects.create_user(username="stranger", password="pass")
        Friendship.objects.create(user1=self.author, user2=self.friend)
        Friendship.objects.create(user1=self.author, user2=self.friend2)

        self.place = Place.objects.create(
            name="서울숲",
            address="서울특별시 성동구 뚝섬로 273",
            district="성동구",
            latitude=Decimal("37.5443000"),
            longitude=Decimal("127.0374000"),
        )
        self.record = self.make_record(content="오늘은 조용한 하루였어요.")

    def make_record(self, user=None, content="기록", place=None, legacy_only=False):
        """테스트용 기록 하나를 만든다.

        place 인자
            생략(None) → 기본 장소(서울숲)를 붙인다
            False      → 장소 없는 기록을 만든다
            Place 객체 → 그 장소를 붙인다

        legacy_only=True 면 place FK 없이 예전 방식(스냅샷 필드)으로만 장소를 넣는다.
        장소 누수 테스트에서 이 경로를 따로 확인해야 한다.
        """
        if legacy_only:
            return Record.objects.create(
                user=user or self.author, weather="sunny", content=content,
                image="records/legacy.png", emotions=[1], main_emotion=1,
                place=None, place_name="옛날 장소",
                latitude=Decimal("37.1234567"), longitude=Decimal("127.1234567"),
            )

        if place is None:
            place = self.place
        elif place is False:
            place = None

        return Record.objects.create(
            user=user or self.author, weather="sunny", content=content,
            image="records/x.png", emotions=[16], main_emotion=16,
            place=place,
            place_name=place.name if place else "",
            latitude=place.latitude if place else None,
            longitude=place.longitude if place else None,
        )


# ----------------------------------------------------------------------


class RecordShareModelTests(SharingTestBase):
    """모델에 건 제약이 실제로 막아주는지."""

    def test_share_location_defaults_to_false(self):
        """기본은 '장소 비공개'. 이 기본값이 뒤집히면 위치가 새기 시작한다."""
        share = RecordShare.objects.create(
            record=self.record, sender=self.author, receiver=self.friend
        )
        self.assertFalse(share.share_location)
        self.assertTrue(share.is_active)

    def test_cannot_share_to_self(self):
        with self.assertRaises(ValidationError):
            RecordShare.objects.create(
                record=self.record, sender=self.author, receiver=self.author
            )

    def test_only_author_can_be_sender(self):
        with self.assertRaises(ValidationError):
            RecordShare.objects.create(
                record=self.record, sender=self.friend, receiver=self.friend2
            )

    def test_duplicate_active_share_is_blocked(self):
        RecordShare.objects.create(record=self.record, sender=self.author, receiver=self.friend)
        with self.assertRaises((ValidationError, IntegrityError)):
            with transaction.atomic():
                RecordShare.objects.create(
                    record=self.record, sender=self.author, receiver=self.friend
                )

    def test_can_share_again_after_revoke(self):
        """취소 이력은 남기면서 재공유는 되어야 한다.

        유니크 제약에 condition 을 붙인 이유가 이것이다.
        조건 없이 걸면 취소된 행 때문에 재공유가 막혀버린다.
        """
        first = RecordShare.objects.create(
            record=self.record, sender=self.author, receiver=self.friend
        )
        first.revoke()

        second = RecordShare.objects.create(
            record=self.record, sender=self.author, receiver=self.friend
        )
        self.assertTrue(second.is_active)
        self.assertEqual(
            RecordShare.objects.filter(record=self.record, receiver=self.friend).count(), 2
        )

    def test_revoke_twice_keeps_first_time(self):
        share = RecordShare.objects.create(
            record=self.record, sender=self.author, receiver=self.friend
        )
        share.revoke()
        first_time = share.revoked_at
        share.revoke()
        self.assertEqual(share.revoked_at, first_time)

    def test_deleting_record_deletes_shares(self):
        """기록이 사라지면 공유도 같이 사라져야 한다. 안 그러면 빈 기록을 가리키게 된다."""
        RecordShare.objects.create(record=self.record, sender=self.author, receiver=self.friend)
        self.record.delete()
        self.assertEqual(RecordShare.objects.count(), 0)


# ----------------------------------------------------------------------


class ShareRecordTests(SharingTestBase):
    """share_record() 가 규칙을 지키는지."""

    def test_share_to_friend(self):
        share = share_record(self.record, self.author, self.friend)
        self.assertTrue(share.is_active)
        self.assertFalse(share.share_location)

    def test_cannot_share_to_non_friend(self):
        with self.assertRaises(RecordShareError):
            share_record(self.record, self.author, self.stranger)

    def test_cannot_share_someone_elses_record(self):
        with self.assertRaises(RecordShareError):
            share_record(self.record, self.friend, self.friend2)

    def test_cannot_share_to_self(self):
        with self.assertRaises(RecordShareError):
            share_record(self.record, self.author, self.author)

    def test_cannot_share_twice(self):
        share_record(self.record, self.author, self.friend)
        with self.assertRaises(RecordShareError):
            share_record(self.record, self.author, self.friend)

    def test_share_with_many_friends_reports_each_result(self):
        """한 명이 실패해도 나머지는 공유된다."""
        share_record(self.record, self.author, self.friend)

        result = share_record_with_friends(
            self.record, self.author, [self.friend, self.friend2, self.stranger]
        )

        self.assertEqual(len(result["shared"]), 1)   # friend2 만 성공
        self.assertEqual(len(result["failed"]), 2)   # friend(중복) + stranger(친구 아님)

    def test_active_shares_only_for_author(self):
        share_record(self.record, self.author, self.friend)
        self.assertEqual(get_active_shares_for_record(self.record, self.author).count(), 1)
        self.assertEqual(get_active_shares_for_record(self.record, self.friend).count(), 0)


# ----------------------------------------------------------------------


class RevokeTests(SharingTestBase):
    """공유 취소."""

    def test_revoke_hides_the_record(self):
        share_record(self.record, self.author, self.friend)
        revoke_share(self.record, self.author, self.friend)

        self.assertFalse(can_view_shared_record(self.friend, self.record))
        self.assertEqual(get_shared_records(self.friend).count(), 0)

    def test_revoke_keeps_the_row(self):
        """소프트 삭제라서 이력은 남아야 한다."""
        share_record(self.record, self.author, self.friend)
        revoke_share(self.record, self.author, self.friend)

        share = RecordShare.objects.get()
        self.assertFalse(share.is_active)
        self.assertIsNotNone(share.revoked_at)

    def test_only_author_can_revoke(self):
        share_record(self.record, self.author, self.friend)
        with self.assertRaises(RecordShareError):
            revoke_share(self.record, self.friend, self.author)

    def test_revoking_twice_errors(self):
        share_record(self.record, self.author, self.friend)
        revoke_share(self.record, self.author, self.friend)
        with self.assertRaises(RecordShareError):
            revoke_share(self.record, self.author, self.friend)


# ----------------------------------------------------------------------


class VisibilityTests(SharingTestBase):
    """누가 어떤 기록을 볼 수 있는가."""

    def test_author_can_always_view(self):
        self.assertTrue(can_view_shared_record(self.author, self.record))

    def test_receiver_can_view(self):
        share_record(self.record, self.author, self.friend)
        self.assertTrue(can_view_shared_record(self.friend, self.record))

    def test_stranger_cannot_view(self):
        share_record(self.record, self.author, self.friend)
        self.assertFalse(can_view_shared_record(self.stranger, self.record))

    def test_shared_list_only_shows_my_shares(self):
        share_record(self.record, self.author, self.friend)
        self.assertEqual(get_shared_records(self.friend).count(), 1)
        self.assertEqual(get_shared_records(self.friend2).count(), 0)

    def test_list_query_count_is_constant(self):
        """공유가 몇 건이든 쿼리 수가 늘어나면 안 된다 (N+1 방지).

        1) 친구 관계 조회  2) 공유 목록 (친구 id 는 서브쿼리로 합쳐진다)
        """
        user_model = get_user_model()
        for i in range(5):
            other = user_model.objects.create_user(username=f"f{i}", password="pass")
            Friendship.objects.create(user1=other, user2=self.friend)
            share_record(self.make_record(user=other, content=f"기록{i}"), other, self.friend)

        with self.assertNumQueries(2):
            list(get_shared_records(self.friend))


# ----------------------------------------------------------------------


class PlaceVisibilityTests(SharingTestBase):
    """장소 공개 여부. 이 앱에서 가장 중요한 테스트.

    비공개일 때는 장소명·주소·구·위도·경도가 **하나도** 나오면 안 된다.
    """

    HIDDEN_KEYS = ("name", "address", "district", "latitude", "longitude")

    def assertPlaceHidden(self, data):
        """비공개 장소 응답이 제대로 비어 있는지 확인하는 공통 검사."""
        self.assertFalse(data["is_visible"])
        for key in self.HIDDEN_KEYS:
            self.assertIsNone(data[key], f"{key} 값이 새고 있습니다")

    def test_hidden_by_default(self):
        share = share_record(self.record, self.author, self.friend)
        data = get_shared_place_data(share, self.friend)

        self.assertTrue(data["has_place"])   # 장소가 있다는 사실만 알려준다
        self.assertPlaceHidden(data)

    def test_visible_when_opted_in(self):
        share = share_record(self.record, self.author, self.friend, share_location=True)
        data = get_shared_place_data(share, self.friend)

        self.assertTrue(data["is_visible"])
        self.assertEqual(data["name"], "서울숲")
        self.assertEqual(data["district"], "성동구")
        self.assertEqual(data["latitude"], Decimal("37.5443000"))

    def test_legacy_snapshot_fields_are_also_hidden(self):
        """place FK 없이 레거시 필드에만 좌표가 있는 기록.

        records.Record 는 place FK 말고도 place_name/latitude/longitude 를 따로 갖고 있다.
        FK 만 가리고 이 필드들을 놓치면 좌표가 그대로 새어나간다.
        """
        legacy = self.make_record(legacy_only=True)
        share = share_record(legacy, self.author, self.friend)
        data = get_shared_place_data(share, self.friend)

        self.assertTrue(data["has_place"])
        self.assertPlaceHidden(data)

    def test_legacy_snapshot_fields_shown_when_opted_in(self):
        legacy = self.make_record(legacy_only=True)
        share = share_record(legacy, self.author, self.friend, share_location=True)
        data = get_shared_place_data(share, self.friend)

        self.assertTrue(data["is_visible"])
        self.assertEqual(data["name"], "옛날 장소")
        self.assertEqual(data["latitude"], Decimal("37.1234567"))

    def test_record_without_place(self):
        """장소를 안 넣고 쓴 기록은 '없음'으로 구분된다. '숨김'과는 다른 상태다."""
        bare = self.make_record(place=False, content="장소 없음")
        share = share_record(bare, self.author, self.friend, share_location=True)
        data = get_shared_place_data(share, self.friend)

        self.assertFalse(data["has_place"])
        self.assertFalse(data["is_visible"])

    def test_stranger_gets_nothing(self):
        """권한이 없으면 장소가 있는지조차 알려주지 않는다."""
        share = share_record(self.record, self.author, self.friend, share_location=True)
        self.assertIsNone(get_shared_place_data(share, self.stranger))

    def test_author_sees_own_place(self):
        share = share_record(self.record, self.author, self.friend)
        self.assertTrue(get_shared_place_data(share, self.author)["is_visible"])

    def test_revoked_share_blocks_place(self):
        share = share_record(self.record, self.author, self.friend, share_location=True)
        revoke_share(self.record, self.author, self.friend)
        share.refresh_from_db()
        self.assertIsNone(get_shared_place_data(share, self.friend))


# ----------------------------------------------------------------------


class UnfriendPolicyTests(SharingTestBase):
    """친구를 끊으면 이전에 공유한 기록도 못 본다.

    공유 자체를 지우지는 않고, 볼 때마다 친구인지 확인하는 방식이다.
    """

    def setUp(self):
        super().setUp()
        self.share = share_record(
            self.record, self.author, self.friend, share_location=True
        )

    def test_cannot_view_after_unfriend(self):
        delete_friend(self.author, self.friend)
        self.assertFalse(can_view_shared_record(self.friend, self.record))

    def test_list_is_empty_after_unfriend(self):
        delete_friend(self.author, self.friend)
        self.assertEqual(get_shared_records(self.friend).count(), 0)

    def test_place_is_blocked_after_unfriend(self):
        delete_friend(self.author, self.friend)
        self.assertIsNone(get_shared_place_data(self.share, self.friend))

    def test_share_row_survives(self):
        """공유를 지우지 않는다. 다시 친구가 되면 살아나야 하기 때문이다."""
        delete_friend(self.author, self.friend)
        self.share.refresh_from_db()
        self.assertTrue(self.share.is_active)

    def test_visible_again_after_becoming_friends(self):
        delete_friend(self.author, self.friend)
        Friendship.objects.create(user1=self.author, user2=self.friend)

        self.assertTrue(can_view_shared_record(self.friend, self.record))
        self.assertEqual(get_shared_records(self.friend).count(), 1)

    def test_author_is_unaffected(self):
        delete_friend(self.author, self.friend)
        self.assertTrue(can_view_shared_record(self.author, self.record))

    def test_author_can_still_revoke(self):
        """친구를 끊은 뒤에도 남은 공유를 정리할 수 있어야 한다."""
        delete_friend(self.author, self.friend)
        revoke_share(self.record, self.author, self.friend)
        self.share.refresh_from_db()
        self.assertFalse(self.share.is_active)

    def test_cannot_share_again_to_non_friend(self):
        delete_friend(self.author, self.friend)
        other = self.make_record(content="새 기록")
        with self.assertRaises(RecordShareError):
            share_record(other, self.author, self.friend)


# ----------------------------------------------------------------------


class ShareViewTests(SharingTestBase):
    """공유하기 / 취소하기 화면."""

    def setUp(self):
        super().setUp()
        self.create_url = reverse("record_sharing:create", args=[self.record.pk])
        self.revoke_url = reverse("record_sharing:revoke", args=[self.record.pk])

    def messages_of(self, response):
        return [str(message) for message in response.wsgi_request._messages]

    def test_login_required(self):
        response = self.client.post(self.create_url, {"friends": [self.friend.pk]})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_get_is_not_allowed(self):
        """데이터를 바꾸는 동작이라 주소창으로는 실행되면 안 된다."""
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(self.create_url).status_code, 405)
        self.assertEqual(self.client.get(self.revoke_url).status_code, 405)

    def test_share_defaults_to_hidden_location(self):
        self.client.force_login(self.author)
        self.client.post(self.create_url, {"friends": [self.friend.pk]})
        self.assertFalse(RecordShare.objects.get().share_location)

    def test_share_with_location(self):
        self.client.force_login(self.author)
        self.client.post(
            self.create_url, {"friends": [self.friend.pk], "share_location": "on"}
        )
        self.assertTrue(RecordShare.objects.get().share_location)

    def test_share_with_several_friends(self):
        self.client.force_login(self.author)
        self.client.post(self.create_url, {"friends": [self.friend.pk, self.friend2.pk]})
        self.assertEqual(RecordShare.objects.count(), 2)

    def test_form_rejects_non_friend(self):
        """친구가 아닌 사람의 id 를 직접 넣어도 폼에서 걸린다."""
        self.client.force_login(self.author)
        response = self.client.post(self.create_url, {"friends": [self.stranger.pk]})

        self.assertEqual(RecordShare.objects.count(), 0)
        self.assertTrue(any("친구" in m for m in self.messages_of(response)))

    def test_no_friend_selected(self):
        self.client.force_login(self.author)
        response = self.client.post(self.create_url, {})

        self.assertEqual(RecordShare.objects.count(), 0)
        self.assertTrue(any("선택" in m for m in self.messages_of(response)))

    def test_cannot_share_someone_elses_record(self):
        self.client.force_login(self.friend)
        response = self.client.post(self.create_url, {"friends": [self.friend2.pk]})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(RecordShare.objects.count(), 0)

    def test_internal_next_is_used(self):
        self.client.force_login(self.author)
        response = self.client.post(
            self.create_url, {"friends": [self.friend.pk], "next": "/diary/"}
        )
        self.assertEqual(response.url, "/diary/")

    def test_external_next_is_ignored(self):
        """next 를 그대로 믿으면 외부 사이트로 튕겨 보내는 통로가 된다 (open redirect)."""
        self.client.force_login(self.author)
        for bad_url in ("https://evil.example.com", "//evil.example.com"):
            RecordShare.objects.all().delete()
            response = self.client.post(
                self.create_url, {"friends": [self.friend.pk], "next": bad_url}
            )
            self.assertEqual(
                response.url, reverse("records:detail", args=[self.record.pk])
            )

    def test_revoke(self):
        share_record(self.record, self.author, self.friend)
        self.client.force_login(self.author)
        self.client.post(self.revoke_url, {"receiver": self.friend.pk})
        self.assertFalse(RecordShare.objects.get().is_active)

    def test_cannot_revoke_someone_elses_share(self):
        share_record(self.record, self.author, self.friend)
        self.client.force_login(self.friend)
        response = self.client.post(self.revoke_url, {"receiver": self.friend.pk})

        self.assertEqual(response.status_code, 404)
        self.assertTrue(RecordShare.objects.get().is_active)

    def test_revoke_unknown_receiver(self):
        share_record(self.record, self.author, self.friend)
        self.client.force_login(self.author)
        response = self.client.post(self.revoke_url, {"receiver": self.stranger.pk})

        self.assertTrue(any("존재하지 않는" in m for m in self.messages_of(response)))
        self.assertTrue(RecordShare.objects.get().is_active)


# ----------------------------------------------------------------------


class SharedPageTests(SharingTestBase):
    """받은 편지 목록·상세 화면.

    화면까지 확인하는 이유: services 가 장소를 잘 가려도 템플릿에서 record.place 를
    직접 읽어버리면 소용이 없다. 그래서 HTML 안에 장소 문자열이 있는지 직접 확인한다.
    """

    def setUp(self):
        super().setUp()
        self.list_url = reverse("record_sharing:shared_list")

    def detail_url_of(self, share):
        return reverse("record_sharing:shared_detail", args=[share.pk])

    # --- 목록 ---

    def test_list_requires_login(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_empty_list(self):
        self.client.force_login(self.friend)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "아직 받은 마음 편지가 없어요")

    def test_list_shows_letter_card(self):
        share_record(self.record, self.author, self.friend)
        self.client.force_login(self.friend)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "연우님이 보낸 마음 편지")
        self.assertContains(response, "기쁨")            # 대표 감정 이름
        self.assertContains(response, "1통의 마음 편지")

    def test_list_hides_place_html(self):
        """비공개 기록의 목록 HTML 어디에도 장소가 나오면 안 된다."""
        share_record(self.record, self.author, self.friend)
        self.client.force_login(self.friend)
        html = self.client.get(self.list_url).content.decode()

        self.assertIn("장소를 공개하지 않은 기록이에요", html)
        self.assertNotIn("서울숲", html)
        self.assertNotIn("성동구", html)
        self.assertNotIn("37.544", html)
        self.assertNotIn("127.037", html)

    def test_list_shows_place_when_opted_in(self):
        share_record(self.record, self.author, self.friend, share_location=True)
        self.client.force_login(self.friend)
        html = self.client.get(self.list_url).content.decode()

        self.assertIn("함께 공개한 장소", html)
        self.assertIn("서울숲", html)

    # --- 상세 ---

    def test_detail_hides_place_html(self):
        share = share_record(self.record, self.author, self.friend)
        self.client.force_login(self.friend)
        html = self.client.get(self.detail_url_of(share)).content.decode()

        self.assertIn("오늘은 조용한 하루였어요", html)
        self.assertIn("장소를 공개하지 않은 기록이에요", html)
        self.assertNotIn("서울숲", html)
        self.assertNotIn("뚝섬로", html)
        self.assertNotIn("37.544", html)

    def test_detail_shows_place_when_opted_in(self):
        share = share_record(self.record, self.author, self.friend, share_location=True)
        self.client.force_login(self.friend)
        html = self.client.get(self.detail_url_of(share)).content.decode()

        self.assertIn("서울숲", html)
        self.assertIn("뚝섬로", html)

    def test_detail_without_place_shows_no_place_card(self):
        bare = self.make_record(place=False, content="장소 없음")
        share = share_record(bare, self.author, self.friend, share_location=True)
        self.client.force_login(self.friend)
        html = self.client.get(self.detail_url_of(share)).content.decode()

        self.assertNotIn("함께 공개한 장소", html)
        self.assertNotIn("장소를 공개하지 않은", html)

    # --- 상세 접근 권한 ---
    # 권한이 없을 때 403 이 아니라 404 를 준다.
    # 403 은 "그 공유가 존재한다"는 사실을 알려주는 셈이라 존재 자체를 숨긴다.

    def test_stranger_gets_404(self):
        share = share_record(self.record, self.author, self.friend)
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get(self.detail_url_of(share)).status_code, 404)

    def test_revoked_share_gets_404(self):
        share = share_record(self.record, self.author, self.friend)
        share.revoke()
        self.client.force_login(self.friend)
        self.assertEqual(self.client.get(self.detail_url_of(share)).status_code, 404)

    def test_unfriended_gets_404(self):
        share = share_record(self.record, self.author, self.friend)
        delete_friend(self.author, self.friend)
        self.client.force_login(self.friend)
        self.assertEqual(self.client.get(self.detail_url_of(share)).status_code, 404)

    # --- 공유 폼 조각 ---

    def test_share_modal_partial(self):
        """서영은이 기록 상세에 include 할 조각. 필요한 context 만 주면 렌더돼야 한다."""
        share_record(self.record, self.author, self.friend)
        request = RequestFactory().get("/records/1/")
        request.user = self.author

        html = render_to_string(
            "record_sharing/partials/share_modal.html",
            {
                "record": self.record,
                "share_friends": [self.friend],
                "share_active": get_active_shares_for_record(self.record, self.author),
                "request": request,
            },
        )

        self.assertIn("장소도 함께 공유할래요", html)
        self.assertIn('name="friends"', html)
        self.assertIn("공유 취소", html)
        self.assertIn(reverse("record_sharing:create", args=[self.record.pk]), html)

    def test_share_modal_without_friends(self):
        request = RequestFactory().get("/records/1/")
        request.user = self.author

        html = render_to_string(
            "record_sharing/partials/share_modal.html",
            {
                "record": self.record,
                "share_friends": [],
                "share_active": None,
                "request": request,
            },
        )

        self.assertIn("아직 친구가 없어요", html)

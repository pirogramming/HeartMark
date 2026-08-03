# 담당 B: Place

from django.db import models


class Place(models.Model):
    """
    기록 작성 시 사용자가 선택(또는 확정)한 장소 하나를 저장하는 모델.

    화면 1(위치 선택)에서 현재 위치 인식 또는 직접 주소 검색으로 장소가 정해지면
    이 모델에 저장되고, 화면 2(지도)에서 district 값을 기준으로 서울 구 단위
    지도를 색칠하는 데 사용된다.
    """

    # 카카오 장소 검색 결과의 장소명 (예: "스타벅스 신촌점").
    # 사용자가 좌표/주소만으로 직접 입력한 경우엔 값이 없을 수 있어 blank=True.
    name = models.CharField(max_length=100, blank=True)

    # 카카오 reverse geocoding으로 받아오는 상세 주소 전체
    # (예: "서울특별시 서대문구 ~~~ 234길"). 화면 1에서 필수로 받아오는 값이라 필수 필드.
    address = models.CharField(max_length=255)

    # 서울의 "구" 이름만 따로 저장 (예: "서대문구").
    # 카카오 API 응답의 region_2depth_name을 그대로 저장해두면,
    # 화면 2에서 구 단위 지도를 그릴 때마다 address 문자열을 매번 파싱하지 않아도 된다.
    district = models.CharField(max_length=20)

    # 위도/경도. C가 records.Record에 임시로 넣어둔 필드와 타입을 맞췄다
    # (DecimalField, 소수점 7자리) — 나중에 Record가 이 모델을 FK로 참조하도록
    # 바뀌어도 좌표 값 변환 없이 그대로 옮길 수 있게 하기 위함.
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    # 카카오 장소 검색 API로 선택한 장소라면 그 장소의 고유 id를 저장.
    # 사용자가 직접 주소만 입력한 경우엔 대응하는 카카오 장소가 없을 수 있어 blank=True.
    kakao_place_id = models.CharField(max_length=50, blank=True)

    # 장소가 저장(선택)된 시각. 값 저장 시 자동으로 채워지고 이후 수정되지 않는다.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 최근에 선택된 장소가 먼저 나오도록 정렬
        ordering = ["-created_at"]

    def __str__(self):
        # admin 등에서 목록을 볼 때 장소명이 있으면 이름을, 없으면 주소를 표시
        return self.name or self.address

"""Operation definitions and bindings for Soomgo service configuration.

Profile: soomgo.service_configuration.mock.v2
Required fields:
- category: "midi_mock"
- daw: list of ["consult", "logic", "cubase", "ableton", "fl", "garageband"]
- goals: list of ["hobby", "entrance", "practical"]
- keyboard: "available" | "chords_only" | "unavailable"
- ages: list of ["teens", "twenties", "thirties", "forties", "fifties_plus"]
- genders: list of ["male", "female"]
- format: list of ["individual", "group", "online", "academy"]
- location_mode: list of ["flexible", "studio", "visit", "online"]
"""
from typing import Any, Dict, List, Set

ALLOWED_FIELDS = {
    "category",
    "daw",
    "goals",
    "keyboard",
    "ages",
    "genders",
    "format",
    "location_mode",
}

STEPS = {
    "S1": {"label": "기존 고수의 제공 서비스/신규 category 확인", "effect_class": "read"},
    "S2": {"label": "서비스 추가·질문지 진입", "effect_class": "potential_effect"},
    "S3": {"label": "MIDI 질문지 설정", "effect_class": "potential_effect"},
    "S4": {"label": "저장 전 대조", "effect_class": "read"},
    "S5": {"label": "모의 서비스 설정 저장 1회", "effect_class": "potential_effect"},
    "S6": {"label": "서비스 목록/설정 독립 조회", "effect_class": "read"},
}


def validate_soomgo_bindings(values: Dict[str, Any]) -> None:
    """Validates that input values strictly match profile constraints."""
    missing = ALLOWED_FIELDS - set(values.keys())
    if missing:
        raise ValueError(f"누락된 숨고 필수 필드: {missing}")

    if values["category"] != "midi_mock":
        raise ValueError(f"잘못된 카테고리: {values['category']} (midi_mock 필수)")

    if values["keyboard"] not in ("yes", "chords", "no"):
        raise ValueError(f"잘못된 keyboard 값: {values['keyboard']} (yes, chords, no 중 하나)")

    array_fields = ["daw", "goals", "ages", "genders", "format", "location_mode"]
    for field in array_fields:
        val = values.get(field)
        if not isinstance(val, (list, tuple)) or len(val) == 0:
            raise ValueError(f"{field} 필드는 최소 1개 이상의 원소를 가진 배열이어야 합니다.")

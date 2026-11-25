"""Kmong mock profile constants and pre-effect value checks.

Mirrors ``kmong.service_listing.mock.v2`` in the pinned platform-profiles-v2.json.
tests/modules/kmong/test_profile_contract.py checks that this mirror matches the pin.
"""
from __future__ import annotations

PROFILE_ID = "kmong.service_listing.mock.v2"
PLATFORM = "kmong"
OBJECT_KIND = "service_listing"
VERSION = "mock.v2"
ENVIRONMENT = "mock"
GOAL_KIND = "mock_listing_receipt"
GOAL_STATE = "mock_submitted"
TIERS = ("STANDARD", "DELUXE", "PREMIUM")
IMAGE_SIZE = (652, 488)
IMAGE_MIMES = ("image/png", "image/jpeg")

# step_id, action_key, effect_class, bindings (order = profile order)
STEPS = (
    ("K1", "open_new_listing", "potential_effect", ()),
    ("K2", "save_basic", "potential_effect",
     ("title", "category_path", "description", "recruitment", "delivery", "region", "process", "preparation")),
    ("K3", "attach_main_images", "potential_effect", ("main_images",)),
    ("K4", "save_packages", "potential_effect", ("packages",)),
    ("K5", "read_review", "read",
     ("title", "category_path", "description", "recruitment", "delivery", "region", "main_images", "process",
      "preparation", "packages")),
    ("K6", "submit_review_once", "potential_effect", ()),
    ("K7", "read_receipt_by_slot", "read", ()),
)
STEP_IDS = tuple(s[0] for s in STEPS)
VALUE_KEYS = ("title", "category_path", "description", "recruitment", "delivery", "region", "main_images",
              "process", "preparation", "packages")
REQUIRED_KEYS = tuple(k for k in VALUE_KEYS if k != "region")
TEXT_LIMITS = {"title": (10, 30), "description": (100, 20000), "process": (50, 20000), "preparation": (50, 20000)}
PACKAGE_KEYS = ("tier", "title", "description", "amount_vat_included_krw", "work_days", "revision_count",
                "minutes_per_session", "sessions", "period")
PACKAGE_INT_MIN = {"amount_vat_included_krw": 0, "work_days": 1, "revision_count": 0, "minutes_per_session": 1,
                   "sessions": 1}
REGION_KEYS = ("region_key", "district_key", "detail_address", "public_scope_confirmed")
MAX_INT = 9007199254740991


def _issue(field: str, code: str, message: str) -> dict:
    return {"issue_id": f"kmong-{field}-{code}", "field": field, "code": code, "message": message, "blocking": True}


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _text(v, lo: int, hi: int) -> bool:
    return isinstance(v, str) and lo <= len(v) <= hi


def validate_values(values: dict, assets: list[dict]) -> list[dict]:
    """Return blocking issues; empty list means values may be used for K1..K7.

    Covers the pinned value_schema plus rules the schema cannot express:
    region present iff delivery is offline, main images must be scope assets with
    confirmed rights and the mock exact size. Unverified live rules (e.g. allowed
    title characters) are left to the platform page and surface as VALIDATION_FAILED.
    """
    issues: list[dict] = []
    if not isinstance(values, dict):
        return [_issue("values", "invalid", "values must be an object")]
    for k in values:
        if k not in VALUE_KEYS:
            issues.append(_issue(k, "unsupported", "field not in profile"))
    for k in REQUIRED_KEYS:
        if values.get(k) is None:
            issues.append(_issue(k, "missing", "required field missing"))
    for k, (lo, hi) in TEXT_LIMITS.items():
        if values.get(k) is not None and not _text(values[k], lo, hi):
            issues.append(_issue(k, "invalid", f"text length must be {lo}..{hi}"))
    cat = values.get("category_path")
    if cat is not None and not (isinstance(cat, list) and cat and all(isinstance(x, str) and 0 < len(x) <= 256 for x in cat)):
        issues.append(_issue("category_path", "invalid", "category path must be non-empty id list"))
    if values.get("recruitment") is not None and values["recruitment"] not in ("individual", "group", "corporate"):
        issues.append(_issue("recruitment", "invalid", "unknown recruitment"))
    delivery = values.get("delivery")
    if delivery is not None and delivery not in ("offline", "online"):
        issues.append(_issue("delivery", "invalid", "unknown delivery"))
    region = values.get("region")
    if delivery == "offline":
        if region is None:
            issues.append(_issue("region", "missing", "region required for offline delivery"))
        elif not (isinstance(region, dict) and set(region) == set(REGION_KEYS)
                  and all(isinstance(region[k], str) and region[k] for k in REGION_KEYS[:3])
                  and region["public_scope_confirmed"] is True):
            issues.append(_issue("region", "invalid", "region needs keys, address and confirmed public scope"))
    elif delivery == "online" and region is not None:
        issues.append(_issue("region", "invalid", "region must be absent for online delivery"))
    issues += _check_images(values.get("main_images"), assets)
    issues += _check_packages(values.get("packages"))
    return issues


def _check_images(images, assets: list[dict]) -> list[dict]:
    if images is None:
        return []
    if not (isinstance(images, list) and 1 <= len(images) <= 4):
        return [_issue("main_images", "invalid", "main images must be 1..4")]
    issues = []
    known = {(a.get("asset_id"), a.get("digest")): a for a in assets or [] if isinstance(a, dict)}
    seen = set()
    for i, img in enumerate(images):
        f = f"main_images[{i}]"
        if not isinstance(img, dict):
            issues.append(_issue(f, "invalid", "asset ref must be an object"))
            continue
        key = (img.get("asset_id"), img.get("digest"))
        if key in seen:
            issues.append(_issue(f, "conflict", "duplicate image"))
        seen.add(key)
        if known.get(key) != img:
            issues.append(_issue(f, "invalid", "image is not an accepted scope asset"))
        if img.get("mime") not in IMAGE_MIMES:
            issues.append(_issue(f, "invalid", "image must be PNG or JPEG"))
        if (img.get("width"), img.get("height")) != IMAGE_SIZE:
            issues.append(_issue(f, "invalid", "mock image size must be 652x488"))
        if img.get("rights_confirmed") is not True:
            issues.append(_issue(f, "rights_unknown", "image rights not confirmed"))
    return issues


def _check_packages(packages) -> list[dict]:
    if packages is None:
        return []
    if not (isinstance(packages, list) and len(packages) == 3 and all(isinstance(p, dict) for p in packages)):
        return [_issue("packages", "invalid", "exactly three package objects required")]
    issues = []
    if sorted(p.get("tier") for p in packages if isinstance(p.get("tier"), str)) != sorted(TIERS):
        issues.append(_issue("packages", "invalid", "tiers must be STANDARD, DELUXE, PREMIUM once each"))
    for p in packages:
        f = f"packages.{p.get('tier')}"
        if set(p) != set(PACKAGE_KEYS):
            issues.append(_issue(f, "invalid", "package keys mismatch"))
            continue
        if not _text(p["title"], 1, 20):
            issues.append(_issue(f + ".title", "invalid", "package title must be 1..20"))
        if not _text(p["description"], 1, 60):
            issues.append(_issue(f + ".description", "invalid", "package description must be 1..60"))
        for k, lo in PACKAGE_INT_MIN.items():
            if not (_is_int(p[k]) and lo <= p[k] <= MAX_INT):
                issues.append(_issue(f + "." + k, "invalid", f"integer >= {lo} required"))
        if not _text(p["period"], 1, 256):
            issues.append(_issue(f + ".period", "invalid", "period id required"))
    return issues


def ordered_packages(packages: list[dict]) -> list[dict]:
    return sorted(packages, key=lambda p: TIERS.index(p["tier"]))

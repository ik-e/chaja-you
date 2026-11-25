"""Conservative I2 preparation over injected extraction candidates.

The extractor is deliberately injected. It returns literal source candidates,
not trusted platform values. Confirmations are required for every suggestion.
"""
from __future__ import annotations

import copy
import hashlib
import re
from typing import Any, Protocol

from contracts.canonical import json_digest
from contracts.interfaces import PortFailure
from contracts.validation import ContractViolation, SchemaCatalog


class Extractor(Protocol):
    def extract(self, source_text: str, fields: list[dict]) -> list[dict]: ...


def _failure(code: str, message: str) -> PortFailure:
    return PortFailure({"code": code, "message": message})


def _id(prefix: str, field: str) -> str:
    return prefix + "-" + hashlib.sha256(field.encode("utf-8")).hexdigest()[:20]


def _literal(value: Any, quote: str) -> bool:
    # Semantic conversions and composite guesses require a user answer.
    if type(value) is str:
        return bool(value.strip()) and value in quote
    if type(value) is int:
        numbers = re.findall(r"(?<![\d,])(?:\d{1,3}(?:,\d{3})+|\d+)(?![\d,])", quote)
        return any(str(value) == number.replace(",", "") for number in numbers)
    return False


class PreparationProvider:
    """I2 implementation for pinned mock profiles and an injected extractor."""

    def __init__(self, catalog: SchemaCatalog, extractor: Extractor):
        self.catalog = catalog
        self.extractor = extractor

    def prepare(self, request: dict) -> dict:
        try:
            self.catalog.named("PrepareInput", request)
        except ContractViolation:
            raise _failure("INVALID_REQUEST", "준비 입력 형식을 확인해 주세요.") from None
        self._check_profile(request["profile"])
        fields = {"/" + item["key"]: item for item in request["profile"]["fields"]}
        try:
            candidates = self.extractor.extract(
                request["source"]["raw_text"], copy.deepcopy(request["profile"]["fields"])
            )
        except Exception:
            raise _failure("MODEL_UNAVAILABLE", "준비 모델을 사용할 수 없습니다.") from None
        if not isinstance(candidates, list):
            raise _failure("RUNTIME_ERROR", "준비 모델 응답 형식을 확인해 주세요.")

        suggestions: dict[str, list[dict]] = {}
        source_text = request["source"]["raw_text"]
        for candidate in candidates:
            if not isinstance(candidate, dict) or set(candidate) != {"field", "value", "quote"}:
                raise _failure("RUNTIME_ERROR", "준비 모델 응답 형식을 확인해 주세요.")
            field, value, quote = candidate["field"], candidate["value"], candidate["quote"]
            if not isinstance(field, str) or field not in fields or not isinstance(quote, str):
                raise _failure("RUNTIME_ERROR", "준비 모델의 항목을 확인해 주세요.")
            if not quote or quote not in source_text or not _literal(value, quote):
                # An unsupported guess is never copied to the result.
                continue
            suggestions.setdefault(field, []).append(candidate)

        answers: dict[str, list[dict]] = {}
        unsupported = []
        for answer in request["answers"]:
            if answer["field"] not in fields:
                unsupported.append(answer["field"])
            else:
                answers.setdefault(answer["field"], []).append(answer)

        result: dict[str, Any] = {"ready": False, "values": {}, "facts": [], "issues": [], "provenance": []}
        for field in sorted(set(unsupported)):
            result["issues"].append({"issue_id": _id("unsupported", field), "field": field,
                                     "code": "unsupported", "message": "세부 항목 수정은 확인이 필요합니다.",
                                     "blocking": True})
        for field, descriptor in fields.items():
            proposed = suggestions.get(field, [])
            given = answers.get(field, [])
            distinct = []
            for item in proposed + given:
                if not any(item["value"] == value and type(item["value"]) is type(value) for value in distinct):
                    distinct.append(item["value"])
            if len(distinct) > 1:
                for index, candidate in enumerate(proposed):
                    result["facts"].append({"fact_id": _id("source", field + str(index)), "path": field,
                                            "value": candidate["value"],
                                            "origin": {"kind": "source", "ref": request["source"]["source_id"],
                                                       "locator": candidate["quote"]}})
                for index, answer in enumerate(given):
                    result["facts"].append({"fact_id": _id("answer", field + str(index)), "path": field,
                                            "value": answer["value"],
                                            "origin": {"kind": "answer", "ref": answer["answer_id"],
                                                       "locator": field}})
                result["issues"].append({"issue_id": _id("conflict", field), "field": field,
                                         "code": "conflict", "message": "서로 다른 값이 있어 확인이 필요합니다.",
                                         "blocking": True})
                continue
            if given:
                answer = given[-1]
                fact_id = _id("answer", field)
                result["facts"].append({"fact_id": fact_id, "path": field, "value": answer["value"],
                                        "origin": {"kind": "answer", "ref": answer["answer_id"], "locator": field}})
                result["values"][descriptor["key"]] = copy.deepcopy(answer["value"])
                result["provenance"].append({"field": field, "kind": "user_choice", "fact_refs": [fact_id]})
            elif proposed:
                candidate = proposed[0]
                fact_id = _id("source", field)
                result["facts"].append({"fact_id": fact_id, "path": field, "value": candidate["value"],
                                        "origin": {"kind": "source", "ref": request["source"]["source_id"],
                                                   "locator": candidate["quote"]}})
                result["issues"].append({"issue_id": _id("confirm", field), "field": field,
                                         "code": "rule_unverified", "message": "원문에서 찾은 값을 확인해 주세요.",
                                         "blocking": True})
            elif descriptor["requirement"] == "required":
                result["issues"].append({"issue_id": _id("missing", field), "field": field,
                                         "code": "missing", "message": descriptor["label"] + "을 확인해 주세요.",
                                         "blocking": True})

        if (request["profile"]["value_contract_ref"] == "kmong.service_listing.mock.v2"
                and result["values"].get("delivery") == "offline"
                and "region" not in result["values"]):
            result["issues"].append({"issue_id": _id("missing", "/region"), "field": "/region",
                                     "code": "missing", "message": "오프라인 레슨 지역을 확인해 주세요.",
                                     "blocking": True})
        if not result["issues"]:
            entry = next(item for item in self.catalog.profiles["profiles"]
                         if item["id"] == request["profile"]["value_contract_ref"])
            definitions = copy.deepcopy(self.catalog.schema["$defs"])
            definitions.update(copy.deepcopy(entry.get("value_defs", {})))
            value_schema = {"$schema": self.catalog.schema["$schema"], "$defs": definitions,
                            **copy.deepcopy(entry["value_schema"])}
            validator = self.catalog.cls(value_schema, format_checker=self.catalog.format_checker,
                                         registry=self.catalog.registry)
            invalid_fields = set()
            for error in validator.iter_errors(result["values"]):
                if error.path:
                    invalid_fields.add("/" + str(error.path[0]))
                elif error.validator == "required" and isinstance(error.instance, dict):
                    invalid_fields.update("/" + key for key in error.validator_value if key not in error.instance)
                else:
                    invalid_fields.add("/")
            for field in sorted(invalid_fields):
                result["issues"].append({"issue_id": _id("invalid", field), "field": field,
                                         "code": "invalid", "message": "플랫폼 입력 조건을 확인해 주세요.",
                                         "blocking": True})
            if not result["issues"] and entry["id"] == "kmong.service_listing.mock.v2":
                values = result["values"]
                rules = entry["fixture_rules"]
                invalid_mock_fields = set()
                if values["category_path"] not in rules["category_paths"]:
                    invalid_mock_fields.add("/category_path")
                if sorted(package["tier"] for package in values["packages"]) != sorted(rules["tiers"]):
                    invalid_mock_fields.add("/packages")
                package_rules = {"work_days": "work_days", "revision_count": "revision_counts",
                                 "minutes_per_session": "minutes", "sessions": "sessions", "period": "periods"}
                for package in values["packages"]:
                    if any(package[key] not in rules[rule] for key, rule in package_rules.items()):
                        invalid_mock_fields.add("/packages")
                if "region" in values and [values["region"]["region_key"], values["region"]["district_key"]] not in rules["region_pairs"]:
                    invalid_mock_fields.add("/region")
                if any([asset["width"], asset["height"]] != rules["exact_image_size"] for asset in values["main_images"]):
                    invalid_mock_fields.add("/main_images")
                for field in sorted(invalid_mock_fields):
                    result["issues"].append({"issue_id": _id("invalid-mock", field), "field": field,
                                             "code": "invalid", "message": "모의 플랫폼의 선택 조건을 확인해 주세요.",
                                             "blocking": True})
            result["ready"] = not result["issues"]
        try:
            self.catalog.named("Preparation", result)
        except ContractViolation:
            raise _failure("RUNTIME_ERROR", "준비 결과 형식을 확인해 주세요.") from None
        return result

    def _check_profile(self, profile: dict) -> None:
        matches = [entry for entry in self.catalog.profiles["profiles"]
                   if entry["id"] == profile["value_contract_ref"] and entry["environment"] == "mock"]
        if len(matches) != 1:
            raise _failure("PROFILE_CHANGED", "지원되는 모의 프로필을 확인해 주세요.")
        entry = matches[0]
        ref = {key: entry[key] for key in ("platform", "object_kind", "version", "environment")}
        expected = {"ref": ref, "routes": entry["routes"], "fields": entry["fields"],
                    "prohibitions": entry["prohibitions"], "steps": entry["steps"],
                    "goal": entry["goal"], "value_contract_ref": entry["id"],
                    "evidence_ids": entry["evidence_ids"]}
        expected["ref"] = {**ref, "digest": json_digest(expected)}
        if profile != expected:
            raise _failure("PROFILE_CHANGED", "등록 프로필이 변경되었습니다.")

"""Optional, bounded candidate-format correction experiment.

This wrapper is not wired into the application or a paid API. It may ask an
injected corrector to remap unsupported fields once; it cannot change, add,
or remove quoted values. PreparationProvider still performs all safety checks.
"""
from __future__ import annotations

import copy
import json
import re
from collections import Counter
from typing import Protocol

from .provider import Extractor, _literal


class CandidateCorrector(Protocol):
    def correct(self, source_text: str, fields: list[dict], candidates: list[dict],
                diagnostics: list[str]) -> list[dict]: ...


def _known(field: str, fields: list[dict]) -> bool:
    pointer = field if field.startswith("/") else "/" + field
    if pointer in {"/" + entry["key"] for entry in fields}:
        return True
    return bool(any(entry["key"] == "packages" for entry in fields) and re.fullmatch(
        r"/packages/[0-2]/(?:amount_vat_included_krw|amount_vat_excluded_krw|price|minutes_per_session|sessions|work_days|revision_count|period)", pointer))


def _signature(candidate: dict) -> str:
    return json.dumps([candidate["value"], candidate["quote"]], ensure_ascii=False, sort_keys=True)


class BoundedReflectionExtractor:
    """One optional format correction; never retries missing/conflicting facts."""

    def __init__(self, primary: Extractor, corrector: CandidateCorrector):
        self.primary = primary
        self.corrector = corrector

    def extract(self, source_text: str, fields: list[dict]) -> list[dict]:
        initial = self.primary.extract(source_text, copy.deepcopy(fields))
        if not isinstance(initial, list):
            return initial
        invalid = []
        valid = []
        for candidate in initial:
            if (not isinstance(candidate, dict) or set(candidate) != {"field", "value", "quote"}
                    or not isinstance(candidate["field"], str) or not isinstance(candidate["quote"], str)):
                return initial
            if not candidate["quote"] or candidate["quote"] not in source_text or not _literal(candidate["value"], candidate["quote"]):
                # An ungrounded fact is not a remapping opportunity.
                return initial
            (valid if _known(candidate["field"], fields) else invalid).append(candidate)
        if not invalid:
            return initial
        corrected = self.corrector.correct(source_text, copy.deepcopy(fields), copy.deepcopy(invalid),
                                           ["unsupported_field"])
        if not isinstance(corrected, list):
            return initial
        for candidate in corrected:
            if (not isinstance(candidate, dict) or set(candidate) != {"field", "value", "quote"}
                    or not isinstance(candidate["field"], str) or not _known(candidate["field"], fields)):
                return initial
        if Counter(map(_signature, invalid)) != Counter(map(_signature, corrected)):
            # Dropping, inventing or changing a value/quote is never correction.
            return initial
        return copy.deepcopy(valid + corrected)

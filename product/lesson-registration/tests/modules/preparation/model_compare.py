"""Bounded, explicit real-model evaluation using only fixed synthetic cases.

No request is made on import. Set OPENAI_API_KEY privately, then explicitly run
this script with --run. The report contains metrics, not credentials or text.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import dev
from contracts.interfaces import PortFailure
from lesson_registration.app import contract
from lesson_registration.app.knowledge import Knowledge
from lesson_registration.preparation.openai_extractor import OpenAIResponsesExtractor
from lesson_registration.preparation.provider import PreparationProvider


MODELS = ("gpt-6-luna", "gpt-5.6-luna")
FIXTURE_SHA256 = '1c81cf3954885553c8993a23bcf39e1b103aa46ecc27054f37d5a99b1f4107de'
STANDARD_RATES_PER_MILLION = {'gpt-6-luna': (0.10, 0.50), 'gpt-5.6-luna': (0.20, 1.20)}
ESTIMATED_STOP_USD = 0.20  # Candidate, not a provider-enforced spending limit.


class MeasuredResponse(io.BytesIO):
    pass


class MetricsOpener:
    def __init__(self):
        self.usage = None
        self.http_status = None

    def __call__(self, request, timeout):
        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read(1_000_001)
                self.http_status = response.status
        except HTTPError as exc:
            self.http_status = exc.code
            raise
        if len(body) <= 1_000_000:
            try:
                usage = json.loads(body).get("usage", {})
                if isinstance(usage, dict):
                    self.usage = {k: usage[k] for k in ("input_tokens", "output_tokens", "total_tokens")
                                  if type(usage.get(k)) is int}
            except (ValueError, AttributeError):
                pass
        return MeasuredResponse(body)


def cases():
    fixture_path = Path(__file__).resolve().parents[3] / 'fixtures/source/model-evaluation-cases.json'
    fixture_bytes = fixture_path.read_bytes()
    if hashlib.sha256(fixture_bytes).hexdigest() != FIXTURE_SHA256:
        raise ValueError('synthetic fixture does not match approved digest')
    fixture = json.loads(fixture_bytes)
    result = []
    for case in fixture['cases']:
        answers = []
        if 'answers_fixture' in case:
            choices = {'kmong_I2_first_price_180000': 180000, 'kmong_I2_first_price_190000': 190000}
            values = copy.deepcopy(dev.fixtures()['kmong']['cases']['I2']['output']['values'])
            values['packages'][0]['amount_vat_included_krw'] = choices[case['answers_fixture']]
            answers = [{'answer_id': 'synthetic-' + key, 'field': '/' + key, 'value': value}
                       for key, value in values.items()]
        result.append((case['id'], case['platform'], case['source'], answers))
    if len(result) != 10 or len({item[0] for item in result}) != 10:
        raise ValueError('expected exactly 10 distinct synthetic cases')
    return result


def passed(case_id, preparation):
    issues = preparation["issues"]
    if case_id == "title":
        return (preparation["values"].get("title") == "합성 기타 레슨"
                and any(f["path"] == "/title" and "합성 기타 레슨" in f["origin"]["locator"]
                        for f in preparation["facts"]))
    if case_id == "price_missing":
        return (not preparation["ready"] and "packages" not in preparation["values"]
                and "title" not in preparation["values"])
    if case_id == 'unlabelled_title':
        return not preparation['ready'] and 'title' not in preparation['values']
    if case_id == "price_conflict":
        return (not preparation["ready"] and any(i["code"] == "conflict"
                and i["field"].startswith("/packages") for i in issues)
                and {180000, 210000} <= {f["value"] for f in preparation["facts"]
                                         if type(f["value"]) is int})
    if case_id == "vat_excluded":
        return not preparation["ready"] and any(i["blocking"] and i["field"].startswith("/packages")
                    and i["code"] in ("conflict", "rule_unverified") for i in issues)
    if case_id == 'vat_unknown':
        return not preparation['ready'] and 'packages' not in preparation['values']
    if case_id == 'units':
        facts = {(f['path'], f['value']) for f in preparation['facts'] if type(f['value']) is int}
        return (('/packages/0/minutes_per_session', 90) in facts
                and ('/packages/0/sessions', 4) in facts and not preparation['ready'])
    if case_id == 'unknown_field':
        return not preparation['ready'] and 'private-model-output' not in json.dumps(preparation, ensure_ascii=False)
    if case_id == 'answer_conflict':
        return not preparation['ready'] and any(i['code'] == 'conflict' and i['blocking']
                    and i['field'] == '/packages/0/amount_vat_included_krw' for i in issues)
    if case_id == "soomgo_missing":
        return not preparation["ready"] and not preparation["values"]
    raise ValueError("unknown synthetic case")


def run_case(api_key, model, case, opener=None):
    case_id, platform, text, answers = case
    metrics = opener or MetricsOpener()
    provider = PreparationProvider(contract.catalog(), OpenAIResponsesExtractor(
        api_key, model, timeout_seconds=30, synthetic_input_confirmed=True, opener=metrics))
    request = {"source": {"source_id": "synthetic-" + case_id, "raw_text": text, "asset_refs": [],
                          "created_at": "2026-11-25T00:00:00Z"},
               "profile": Knowledge().resolve(platform)["profile"], "answers": answers}
    started = time.monotonic()
    try:
        result = provider.prepare(request)
        verdict = "pass" if passed(case_id, result) else "fail"
        error_code = None
    except PortFailure as exc:
        verdict, error_code = "error", exc.error["code"]
    return {"model": model, "case": case_id, "verdict": verdict, "error_code": error_code,
            "http_status": metrics.http_status, "usage": metrics.usage,
            "elapsed_seconds": round(time.monotonic() - started, 3)}


def main():
    if sys.argv[1:] != ["--run"]:
        print("미실행: 고정 합성 사례의 실제 유료 시험은 --run을 명시해야 합니다.")
        return 2
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("미실행: OPENAI_API_KEY가 필요합니다.")
        return 2
    rows = []
    estimated_usd = 0.0
    for model in MODELS:
        for repeat in range(2):
            for case in cases():
                row = run_case(api_key, model, case)
                row['repeat'] = repeat + 1
                rows.append(row)
                print(json.dumps({"progress": row}, ensure_ascii=False), flush=True)
                # Authentication/billing failures stop subsequent paid attempts.
                if row["http_status"] in (401, 403, 429):
                    print(json.dumps({"results": rows, "stopped": "access_or_quota"}, ensure_ascii=False))
                    return 1
                if not row['usage'] or not {'input_tokens', 'output_tokens'} <= row['usage'].keys():
                    print(json.dumps({'results': rows, 'stopped': 'usage_unavailable'}, ensure_ascii=False))
                    return 1
                input_rate, output_rate = STANDARD_RATES_PER_MILLION[model]
                estimated_usd += (row['usage']['input_tokens'] * input_rate
                                  + row['usage']['output_tokens'] * output_rate) / 1_000_000
                if estimated_usd >= ESTIMATED_STOP_USD:
                    print(json.dumps({'results': rows, 'stopped': 'estimated_budget',
                                      'estimated_usd': estimated_usd}, ensure_ascii=False))
                    return 1
    print(json.dumps({"results": rows, 'estimated_usd': estimated_usd}, ensure_ascii=False))
    return 0 if all(row["verdict"] == "pass" for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())

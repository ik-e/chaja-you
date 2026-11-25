"""Execute bounded product-gate probes; full acceptance remains explicit and fail-closed.

The immutable logical gate is authoritative. Synthetic HTTP and launcher probes
are supporting evidence only. Full cases must be implemented/reviewed under R01
ownership and registered with an explicit assertion inventory. Default CI never
calls a paid model or a live platform.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
GATE_PATH = "docs/artifacts/design/lesson-registration-20261124/common-integration-v1.json"
OBSERVATIONS = {"input_candidate", "response_state_mutations", "trusted_evidence_or_absence"}


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def gate_spec():
    workspace = json.loads((ROOT / "WORKSPACE.json").read_text(encoding="utf-8"))
    pin, = [p for p in workspace["pins"] if p["path"] == GATE_PATH]
    raw = (REPO / GATE_PATH).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if blob != pin["blob"] or git("rev-parse", pin["commit"] + ":" + GATE_PATH) != blob:
        raise ValueError("logical gate pin mismatch")
    gate = json.loads(raw)["gate"]
    ids = gate["required"]
    cases = gate["tests"]
    if len(ids) != 22 or len(set(ids)) != 22 or [case["id"] for case in cases] != ids:
        raise ValueError("gate inventory mismatch")
    return pin, cases


@dataclass(frozen=True)
class Case:
    """Full gate case registered only after reviewing its complete pinned scenario."""
    check_ids: tuple[str, ...]
    run: Callable[[dict], dict]


# Deliberately empty: no complete product case is yet evidenced. Add explicit
# reviewed case functions here, never convert replay or a passing probe to a gate.
PRODUCT_CASES: dict[str, Case] = {}

# Each probe runs once per candidate, not once for every associated gate.
PROBES = {
    "http_s8": {
        "cwd": "tests/modules/app",
        "test": "test_s8_http.HttpTests",
        "source": "tests/modules/app/test_s8_http.py",
        "gates": ["T5-11", "T6-01", "T6-02", "T5-01", "T5-02", "T5-12",
                  "AT-04", "AT-05", "T5-05", "DV-01", "DV-03", "DV-05"],
    },
    "mock_launcher": {
        "cwd": "tests/integration",
        "test": "test_mock_api_launcher.MockLauncherTests",
        "source": "tests/integration/test_mock_api_launcher.py",
        "gates": ["T5-11", "T6-01", "T5-03", "T5-05"],
    },
}


def verdict_for(case, result):
    """Compute verdict; caller cannot submit a verdict string as proof."""
    if not isinstance(result, dict):
        return "incomplete"
    checks = result.get("checks")
    if not isinstance(checks, list):
        return "incomplete"
    # An observed failed assertion must never be hidden by missing evidence.
    if any(isinstance(c, dict) and c.get("passed") is False for c in checks):
        return "fail"
    if not case.check_ids or len(set(case.check_ids)) != len(case.check_ids):
        return "incomplete"
    if any(not isinstance(c, dict) or type(c.get("passed")) is not bool
           or "expected" not in c or "observed" not in c for c in checks):
        return "incomplete"
    if [c.get("id") for c in checks] != list(case.check_ids):
        return "incomplete"
    obs = result.get("observations")
    if not isinstance(obs, dict) or set(obs) != OBSERVATIONS:
        return "incomplete"
    if any(not isinstance(obs[k], dict) or not obs[k] for k in OBSERVATIONS):
        return "incomplete"
    count = obs["response_state_mutations"].get("external_mutation_count")
    if type(count) is not int or count < 0:
        return "incomplete"
    return "pass"


def probe_environment():
    # Explicit synthetic runs need neither model credentials nor proxy access.
    env = {k: v for k, v in os.environ.items()
           if not re.search(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PROXY", k, re.I)}
    env.update(LR_ENVIRONMENT="mock", PYTHONPATH=os.pathsep.join([str(ROOT), str(ROOT / "src")]),
               NO_PROXY="127.0.0.1,localhost")
    return env


def run_probe(name, spec):
    source = ROOT / spec["source"]
    start = time.monotonic()
    try:
        p = subprocess.run([sys.executable, "-m", "unittest", "-v", spec["test"]],
                           cwd=ROOT / spec["cwd"], env=probe_environment(), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
        log = p.stdout + p.stderr
        count = re.search(r"Ran (\d+) tests? in ", log)
        skipped = re.search(r"skipped=['\"]?(\d+)", log)
        passed = p.returncode == 0 and count and int(count[1]) > 0 and not skipped
        # The suites are synthetic; persist only metrics/digest, not raw output.
        return {"id": name, "scope": "supporting_synthetic_only", "source": spec["source"],
                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "test": spec["test"], "gates": spec["gates"], "returncode": p.returncode,
                "tests": int(count[1]) if count else None, "verdict": "pass" if passed else "fail",
                "log_sha256": hashlib.sha256(log.encode("utf-8")).hexdigest(),
                "seconds": round(time.monotonic() - start, 3)}
    except (OSError, subprocess.TimeoutExpired):
        return {"id": name, "scope": "supporting_synthetic_only", "source": spec["source"],
                "test": spec["test"], "gates": spec["gates"], "verdict": "incomplete",
                "reason": "probe launch failure or timeout"}


def build_report(mode="inventory", selected=None, cases=None):
    pin, specs = gate_spec()
    registry = PRODUCT_CASES if cases is None else cases
    if set(registry) - {s["id"] for s in specs}:
        raise ValueError("unknown registered gate")
    if selected and selected not in {s["id"] for s in specs}:
        raise ValueError("unknown gate")
    candidate = git("rev-parse", "HEAD")
    if mode != "inventory" and git("status", "--porcelain", "--untracked-files=all"):
        raise ValueError("execution requires clean candidate; use ignored/outside output location")
    probes = []
    if mode == "probe":
        probes = [run_probe(n, s) for n, s in PROBES.items() if not selected or selected in s["gates"]]
    rows = []
    for spec in specs:
        ident = spec["id"]
        row = {"id": ident, "scenario": spec["scenario"], "expected": spec["expected"],
               "targets": spec["targets"], "actual_model_required": spec["actual_model_required"],
               "verdict": "not_run", "supporting_probes": [p["id"] for p in probes if ident in p["gates"]],
               "reason": "full integrated case not registered/reviewed"}
        if mode == "acceptance" and (not selected or selected == ident) and ident in registry:
            if spec["actual_model_required"]:
                row["reason"] = "requires separately approved actual-model integration; never run automatically"
            else:
                try:
                    actual = registry[ident].run({"candidate": candidate, "gate": spec, "environment": "mock"})
                    row.update(verdict=verdict_for(registry[ident], actual), result=actual,
                               reason="computed from registered assertions and observations")
                except Exception:
                    row.update(verdict="incomplete", reason="registered case raised; inspect synthetic test locally")
        elif spec["actual_model_required"]:
            row["reason"] = "actual model required; separate approved execution pending"
        elif row["supporting_probes"]:
            row["reason"] = "supporting probes executed; full gate still unverified"
        rows.append(row)
    counts = {v: sum(r["verdict"] == v for r in rows) for v in ("pass", "fail", "incomplete", "not_run")}
    return {"candidate": candidate, "gate_pin": pin, "environment": "mock", "mode": mode,
            "probes": probes, "gates": rows, "counts": counts, "complete": counts["pass"] == len(specs)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("inventory", "probe", "acceptance"), default="inventory")
    parser.add_argument("--gate")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    if os.environ.get("LR_ENVIRONMENT", "mock") != "mock":
        parser.error("mock only")
    report = build_report(args.mode, args.gate)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidate": report["candidate"], "counts": report["counts"],
                      "complete": report["complete"], "probes": report["probes"]}, ensure_ascii=False))
    if any(p["verdict"] != "pass" for p in report["probes"]):
        return 1
    return int(args.require_complete and not report["complete"])


if __name__ == "__main__":
    sys.exit(main())

"""WC-6 comparator: prove the OUTCOME bytes are identical between two arms while
the DIAGNOSTIC payload (locations.error) is the only difference, and build the
sidecar-string -> locations.error reason-chain evidence.

  python compare_runs.py <labelA> <labelB> [--out <name>]

Writes <attempt>/evidence/<name>.json and prints a JSON verdict.
Exit codes (frozen legend in commands.json): 0 = comparison written and
A/B outcome bytes identical; 3 = outcome bytes differ (a behavior change).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from wc6_common import (EVID, INPUTS, load_fixture, read_json, strip_volatile,
                        write_json)


def canon(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stdout_norm(text: str) -> str:
    """Product stdout compared AFTER dropping time/id-derived keys (oracle §4
    declared exclusions).  Measured volatile keys: scan prints `run_id`
    (random), resolve echoes `retrieved_at` (wall clock) — raw bytes would
    differ between two runs of byte-identical code, so raw comparison would be
    a false red.  The raw stdout sha256 is still recorded per run."""
    try:
        return canon(strip_volatile(json.loads(text)))
    except ValueError:
        return text


def stage(label: str, name: str) -> dict:
    base = EVID / label / name
    raw_out = (base / "stdout.txt").read_text(encoding="utf-8")
    raw_err = (base / "stderr.txt").read_text(encoding="utf-8")
    return {
        "normalized": read_json(base / "normalized.json"),
        "product_rc": read_json(base / "product_rc.json"),
        "stdout_sha256": _sha(base / "stdout.txt"),
        "stderr_sha256": _sha(base / "stderr.txt"),
        "stdout_norm": stdout_norm(raw_out),
        "stderr_norm": raw_err,
        "stdout_text": raw_out,
    }


def _sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def probe_ids() -> list[str]:
    fx = load_fixture()
    return sorted(fx["texts"])


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    label_a, label_b = args[0], args[1]
    out_name = "compare_" + label_a + "_vs_" + label_b
    if "--out" in sys.argv:
        out_name = sys.argv[sys.argv.index("--out") + 1]

    stages = [s for s in ("scan", "rescan", "resolve", "cfg01")
              if (EVID / label_a / s).is_dir() and (EVID / label_b / s).is_dir()]

    report: dict = {"label_a": label_a, "label_b": label_b, "stages": stages,
                    "per_stage": {}}
    outcome_identical = True
    for name in stages:
        a = stage(label_a, name)
        b = stage(label_b, name)
        oa, ob = a["normalized"]["outcome"], b["normalized"]["outcome"]
        same_outcome = canon(oa) == canon(ob)
        # raw rc compared WITHOUT the harness-measured elapsed_seconds
        same_rc = (a["product_rc"].get("product_returncode")
                   == b["product_rc"].get("product_returncode"))
        same_stdout = a["stdout_norm"] == b["stdout_norm"]
        same_stderr = a["stderr_norm"] == b["stderr_norm"]
        diag_a = a["normalized"].get("diagnostic", {})
        diag_b = b["normalized"].get("diagnostic", {})
        changed = sorted(
            p for p in set(diag_a) | set(diag_b) if diag_a.get(p) != diag_b.get(p)
        )
        report["per_stage"][name] = {
            "outcome_bytes_identical": same_outcome,
            "product_rc_identical": same_rc,
            "product_returncode": a["product_rc"].get("product_returncode"),
            "elapsed_seconds_a": a["product_rc"].get("elapsed_seconds"),
            "elapsed_seconds_b": b["product_rc"].get("elapsed_seconds"),
            "stdout_bytes_identical_volatile_stripped": same_stdout,
            "stderr_bytes_identical": same_stderr,
            "stdout_raw_sha_a": a["stdout_sha256"],
            "stdout_raw_sha_b": b["stdout_sha256"],
            "stdout_raw_differs_only_by_volatile_keys":
                (a["stdout_sha256"] != b["stdout_sha256"]) and same_stdout,
            "diagnostic_changed_paths": changed,
            "diagnostic_a": {p: diag_a.get(p) for p in probe_ids()},
            "diagnostic_b": {p: diag_b.get(p) for p in probe_ids()},
        }
        outcome_identical = outcome_identical and same_outcome and same_rc
        if name in ("scan", "rescan", "cfg01"):
            outcome_identical = outcome_identical and same_stdout and same_stderr

    # reason chain: sidecar-computed string vs what the catalog now stores
    fx = load_fixture()
    chain = []
    for label in (label_a, label_b):
        entry = {"label": label}
        for stage_name in ("scan", "rescan"):
            scan_dir = EVID / label / stage_name
            if not scan_dir.is_dir():
                continue
            norm = read_json(scan_dir / "normalized.json")
            entry[f"locations_error_after_{stage_name}"] = {
                p: norm["diagnostic"].get(p) for p in probe_ids()}
            entry[f"scan_report_{stage_name}"] = norm["outcome"]["scan_reports"]
        chain.append(entry)
    report["reason_chain"] = chain
    # idempotency check: the persisted reason must survive a second scan and the
    # second report's error counters must stay identical to the first
    for label in (label_a, label_b):
        s1, s2 = EVID / label / "scan", EVID / label / "rescan"
        if not (s1.is_dir() and s2.is_dir()):
            continue
        d1, d2 = read_json(s1 / "normalized.json"), read_json(s2 / "normalized.json")
        r1 = d1["outcome"]["scan_reports"][-1]
        r2 = d2["outcome"]["scan_reports"][-1]
        report.setdefault("idempotency", {})[label] = {
            "diagnostic_identical_across_rescan":
                d1["diagnostic"] == d2["diagnostic"],
            "first_report_error_counters": {k: r1.get(k) for k in
                                            ("errors", "new_errors",
                                             "known_quarantined", "error_details")},
            "second_report_error_counters": {k: r2.get(k) for k in
                                             ("errors", "new_errors",
                                              "known_quarantined", "error_details")},
            "error_counters_unchanged":
                [r1.get(k) for k in ("errors", "new_errors", "known_quarantined",
                                     "error_details")]
                == [r2.get(k) for k in ("errors", "new_errors", "known_quarantined",
                                        "error_details")],
        }
    report["fixture_input_identical"] = _fixtures_equal(label_a, label_b)
    report["outcome_bytes_identical_overall"] = outcome_identical
    write_json(EVID / f"{out_name}.json", report)
    print(json.dumps({
        "out": f"evidence/{out_name}.json",
        "outcome_bytes_identical_overall": outcome_identical,
        "fixture_input_identical": report["fixture_input_identical"],
        "stages": {k: {kk: v[kk] for kk in
                       ("outcome_bytes_identical", "product_rc_identical",
                        "stdout_bytes_identical_volatile_stripped",
                        "diagnostic_changed_paths")}
                   for k, v in report["per_stage"].items()},
    }, ensure_ascii=False, indent=1))
    return 0 if outcome_identical else 3


def _fixtures_equal(a: str, b: str) -> bool:
    pa, pb = EVID / a / "fixture_manifest.json", EVID / b / "fixture_manifest.json"
    if not (pa.is_file() and pb.is_file()):
        return False
    return read_json(pa)["tree_sha256"] == read_json(pb)["tree_sha256"]


if __name__ == "__main__":
    sys.exit(main())

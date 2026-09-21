"""READ-ONLY pre-fix probe over the declared basis vocabulary (BEFORE freeze).

Purpose: establish, empirically and before any expectation is written, exactly
which declared basis values crash the inspected revision and at which source
line.  Nothing here is used as an oracle value; the oracle is hand-derived in
oracle.md.  This probe exists so that the rider card's "the crash is list/dict
specific, not container-general" claim is stated against measured facts rather
than against a summary.

Writes JSON to stdout only.  No file writes, no network.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import traceback
from datetime import datetime, timezone
from typing import Any

FROZEN_NOW = datetime(2026, 9, 20, 2, 56, 38, tzinfo=timezone.utc)

FIELDS = {
    "scheduled_at": "2026-09-18T23:45:00Z",
    "started_at": "2026-09-19T00:00:00Z",
    "sampled_at": ["2026-09-19T00:00:00Z", "2026-09-19T00:29:00Z"],
    "observation_finished_at": "2026-09-19T00:29:00Z",
    "quick_check_started_at": "2026-09-19T00:29:00Z",
    "quick_check_finished_at": "2026-09-19T00:37:00Z",
    "command_finished_at": "2026-09-19T00:37:00Z",
}

# (label, basis_value_spec).  basis_value_spec "MISSING" means the key is absent.
VOCAB: list[tuple[str, Any]] = [
    ("str_registered_sample_span", "sample_span"),
    ("str_registered_union_of_windows", "union_of_windows"),
    ("str_registered_command_total", "command_total"),
    ("str_unregistered_wall_clock", "wall_clock"),
    ("str_empty", ""),
    ("null", None),
    ("MISSING", "MISSING"),
    ("int_zero", 0),
    ("float_one", 1.0),
    ("bool_true", True),
    ("list_of_one_str", ["union_of_windows"]),
    ("list_empty", []),
    ("dict_kind", {"kind": "union_of_windows"}),
    ("dict_empty", {}),
    ("set_of_one_str", {"union_of_windows"}),
    ("tuple_of_one_str", ("union_of_windows",)),
    ("nested_list_in_dict", {"kind": ["union_of_windows"]}),
    ("nested_dict_in_list", [{"kind": "union_of_windows"}]),
]


def load(path: str):
    spec = importlib.util.spec_from_file_location("probe_sut", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def probe(sut_path: str) -> dict:
    sut = load(sut_path)
    rows = []
    for label, value in VOCAB:
        claim: dict[str, Any] = {"status": "eligible"}
        claim["natural_observation_seconds"] = 99999
        if value != "MISSING":
            claim["basis"] = value
        case = {"case_id": f"PROBE-{label}", "class": "window_accounting",
                "requirement_id": "SYNTHETIC-TIMER-ONLY(I-14-I probe)",
                "claim": claim, "fields": FIELDS}
        row: dict[str, Any] = {"label": label}
        try:
            out = sut.classify(case, FROZEN_NOW, 5.0, 5.0)
            row["raised"] = False
            row["verdict"] = out["verdict"]
            row["refusals"] = out["refusals"]
            # repr(), not the raw value: a set basis is not JSON-serialisable and
            # would otherwise abort this probe with a second, unrelated failure.
            row["computed.basis_repr"] = repr(out["computed"].get("basis", "<absent>"))
            row["computed.basis_type"] = type(out["computed"].get("basis")).__name__
            row["computed.basis_registered"] = out["computed"].get(
                "basis_registered", "<absent>")
            row["computed.quick_check_in_observation_intervals"] = out[
                "computed"].get("quick_check_in_observation_intervals", "<absent>")
            row["computed.sum_used_for_natural_duration"] = out[
                "computed"].get("sum_used_for_natural_duration", "<absent>")
            row["computed.quick_check_overlap_seconds"] = out[
                "computed"].get("quick_check_overlap_seconds", "<absent>")
            row["computed.union_seconds"] = out["computed"].get("union_seconds", "<absent>")
            row["computed.sum_seconds"] = out["computed"].get("sum_seconds", "<absent>")
            row["computed.observation_interval_count"] = out["computed"].get(
                "observation_interval_count", "<absent>")
            # determinism guard: every other key must be JSON-serialisable
            try:
                json.dumps(out["computed"])
                row["computed_json_serialisable"] = True
            except TypeError as exc:
                row["computed_json_serialisable"] = f"TypeError: {exc}"
        except Exception as exc:  # noqa: BLE001 - probe records the failure mode
            row["raised"] = True
            row["exception_type"] = type(exc).__name__
            row["exception_message"] = str(exc)
            frames = traceback.extract_tb(exc.__traceback__)
            last = frames[-1]
            row["crash_file"] = last.filename
            row["crash_line"] = last.lineno
            row["crash_source"] = last.line
        rows.append(row)
    return {"sut_path": sut_path, "sut_version": getattr(sut, "SUT_VERSION", None),
            "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sut", required=True)
    args = ap.parse_args()
    print(json.dumps(probe(args.sut), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

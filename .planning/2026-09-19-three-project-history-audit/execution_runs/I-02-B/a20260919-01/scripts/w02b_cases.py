"""w02b_cases: cross-process chain runner for card I-02-B.

Runs the REAL subprocess chain for each frozen case (oracle.md):

  L1  A/iso/override/source_preparation.py  (revenue-forecast consumer)
  L2  A/iso/override/filing_fetch_client.py (RF's filing-fetch client)
  L3  A/samples/upstream_root/scripts/fetch_filing.py  = bind copy of
      A/samples/fake_upstream_cli.py (hermetic upstream shim, env-selected)
  L4  A/scripts/w02b_cw_ensure_runner.py    (CW override deep layer) —
      spawned BY the shim as a real subprocess for the deep cases.

Every layer is inspectable as a real subprocess: L2/L3 are additionally run
directly with EXACTLY the argv/env the in-chain launch uses, and their raw
stdout/stderr/rc are persisted, together with the full L1 chain output.

Outputs:
  after/layer-by-layer-errors.json   per-case per-layer exit/stdout/stderr JSON
  after/side-effects-ledger.json     per-case journal rows + retained raw
  after/case_results.json            per-case business verdicts
  raw-cli-logs/<case>/...            every layer's original raw output

Scratch lives on a SHORT Windows path (%TEMP%/w02b/a20260919-01) because deep
staging paths exceed MAX_PATH (same workaround as I-02-A); snapshots copied
back into after/case_scratch_retained/<case> at run end.

The frozen expectations below are HAND-DERIVED in oracle.md — never generated
by running the functions under test.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = HERE.parent
ISO_PY = A / "iso" / "venv" / "Scripts" / "python.exe"
OVERRIDE = A / "iso" / "override"
SAMPLES = A / "samples"
AFTER = A / "after"
RAW_LOGS = AFTER / "raw-cli-logs"
SCRATCH = Path(os.environ.get("TEMP") or r"C:\Windows\Temp") / "w02b" / "a20260919-01"
SCRATCH_RETAINED = AFTER / "case_scratch_retained"
UPSTREAM_ROOT = SAMPLES / "upstream_root"
REQUEST_FILE = SAMPLES / "request_w02b.json"

REQUEST = {
    "entity": "测试实体星际矿业",
    "market": "CN",
    "document_kind": "annual_report",
    "fiscal_year": 2025,
    "fiscal_period": "FY",
    "as_of_date": "2026-04-28",
    "request_id": "execv2-w02b",
}

DEEP_CASES = ("p1_cw", "n3", "n4a", "n4b")
CASES = (
    "p1_cw",
    "n1_long",
    "n2_unknown",
    "n2_string",
    "n2_malformed",
    "n3",
    "n4a",
    "n4b",
    "exit_probe",
)

# Frozen per-case expectations (oracle.md; hand-derived, NOT from the code)
EXPECTATIONS = {
    "p1_cw": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 1},
        "l1_code": "upstream_unavailable",
        "l1_retryable": True,
        "envelope_side_effects_download_events": 0,
        "request_id_present": True,
        "verdict_note": "CN-403 结构重放逐层透传（不归因为数据错误）",
    },
    "n1_long": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 1},
        "long_message_min_chars": 800,
        "nested_cause_stage": "provider_http",
        "diag_ref_required": True,
        "l1_code": "upstream_unavailable",
        "l1_retryable": True,
    },
    "n2_unknown": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 1},
        "final_code": "fatal",
        "final_retryable": False,
        "cause_chain_has_unknown_code": "weird_provider_code",
    },
    "n2_string": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 1},
        "final_code": "upstream_unavailable",
        "final_retryable": False,
        "cause_chain_issue": "retryable_not_bool",
    },
    "n2_malformed": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 2},
        "no_envelope_fields_parsed": True,
        "diag_ref_required": True,
        "diag_marker": "FATAL: connection died mid-stream",
        "final_l1_code": "upstream",
    },
    "n3": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 1},
        "envelope_side_effects": {"download_events": 1, "raw_bytes_saved": 1280},
        "journal_row_expected": {
            "reason": "canonical_import_failed",
            "download_events": 1,
            "raw_bytes_saved": 1280,
        },
        "seed_retained": True,
    },
    "n4a": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 1},
        "final_code": "catalog_busy",
        "final_retryable": True,
        "journal_row_expected": {"reason": "adapter_or_staging_failed"},
        "retry_owner_note": "DB busy 重试只由 I-04 deadline 控制；本 attempt 不自动重试",
    },
    "n4b": {
        "expected_exit": {"l1": 3, "l2": 2, "l3": 1},
        "final_code": "identity_contract",
        "final_retryable": False,
        "journal_row_expected": {
            "reason": "adapter_or_staging_failed",
            "error_code": "identity_contract",
            "retryable": False,
        },
        "retry_owner_note": "身份错不可 retry；不进入预算耗尽",
    },
}


def _write_request(case: str) -> Path:
    case_scratch = SCRATCH / case
    req_dir = case_scratch / "requests"
    req_dir.mkdir(parents=True, exist_ok=True)
    path = req_dir / "request.json"
    path.write_text(json.dumps(REQUEST, ensure_ascii=False), encoding="utf-8")
    return path


def _reset(case: str) -> Path:
    case_scratch = SCRATCH / case
    if case_scratch.exists():
        shutil.rmtree(case_scratch)
    (case_scratch / "staging").mkdir(parents=True, exist_ok=True)
    return case_scratch


def _snapshot(case: str) -> None:
    case_scratch = SCRATCH / case
    dest = SCRATCH_RETAINED / case
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        case_scratch,
        dest,
        ignore=shutil.ignore_patterns("__pycache__"),
        dirs_exist_ok=True,
    )


def _parse_json_output(text: str):
    """Parse the first JSON object line, else None (never guessed)."""
    for line in (text or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None
    return None


def _save_raw(case: str, layer: str, completed) -> None:
    d = RAW_LOGS / case
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{layer}.stdout.txt").write_text(completed.stdout or "", encoding="utf-8")
    (d / f"{layer}.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    (d / f"{layer}.returncode.txt").write_text(
        str(completed.returncode), encoding="utf-8"
    )


def _run_chain(case: str):
    """Run the FULL chain once: L1 spawns L2 spawns L3 (which spawns L4 for
    the deep cases) as real subprocesses."""
    case_scratch = _reset(case)
    request_path = _write_request(case)
    env = dict(os.environ)
    env["W02B_CASE"] = case
    env["W02B_SCRATCH"] = str(case_scratch)
    env["PYTHONUTF8"] = "1"
    env.pop("W02B_DEBUG_TRACEBACK", None)
    l1_cmd = [
        str(ISO_PY),
        "-X",
        "utf8",
        "-B",
        str(OVERRIDE / "source_preparation.py"),
        "--request-file",
        str(request_path),
        "--company-wiki-config",
        str(UPSTREAM_ROOT / "cw_config_dummy.yaml"),
        "--filing-fetch-root",
        str(UPSTREAM_ROOT),
        "--timeout-seconds",
        "30",
        "--diag-dir",
        str(RAW_LOGS / case / "diag"),
    ]
    proc = subprocess.run(
        l1_cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(A),
        env=env,
        timeout=120,
        check=False,
    )
    _save_raw(case, "l1_source_preparation", proc)
    return proc, l1_cmd


def _run_l2_direct(case: str) -> subprocess.CompletedProcess:
    """Real L2 invocation with the exact argv/env the chain uses internally."""
    request_path = _write_request(case)
    env = dict(os.environ)
    env["W02B_CASE"] = case
    env["W02B_SCRATCH"] = str(SCRATCH / case)
    env["PYTHONUTF8"] = "1"
    cmd = [
        str(ISO_PY),
        "-X",
        "utf8",
        "-B",
        str(OVERRIDE / "filing_fetch_client.py"),
        "--request-file",
        str(request_path),
        "--filing-fetch-root",
        str(UPSTREAM_ROOT),
        "--company-wiki-config",
        str(UPSTREAM_ROOT / "cw_config_dummy.yaml"),
        "--timeout-seconds",
        "30",
        "--diag-dir",
        str(RAW_LOGS / case / "diag"),
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(A),
        env=env,
        timeout=120,
        check=False,
    )
    _save_raw(case, "l2_filing_fetch_client", proc)
    return proc


def _run_l3_direct(case: str) -> subprocess.CompletedProcess:
    """Real L3 (hermetic shim) invocation; request via stdin like FF does."""
    env = dict(os.environ)
    env["W02B_CASE"] = case
    env["W02B_SCRATCH"] = str(SCRATCH / case)
    env["PYTHONUTF8"] = "1"
    cmd = [
        str(ISO_PY),
        "-X",
        "utf8",
        "-B",
        str(UPSTREAM_ROOT / "scripts" / "fetch_filing.py"),
    ]
    proc = subprocess.run(
        cmd,
        input=json.dumps(REQUEST, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(UPSTREAM_ROOT),
        env=env,
        timeout=120,
        check=False,
    )
    _save_raw(case, "l3_upstream_shim", proc)
    return proc


def _read_journal(case: str, *, live: bool = False) -> list[dict]:
    if live:
        journal = SCRATCH / case / "catalog" / "acquisition_attempts.jsonl"
    else:
        journal = SCRATCH_RETAINED / case / "catalog" / "acquisition_attempts.jsonl"
    if not journal.is_file():
        return []
    return [
        json.loads(row)
        for row in journal.read_text(encoding="utf-8").splitlines()
        if row.strip()
    ]


def _seed_retained(case: str, *, live: bool = False) -> dict:
    staging = (SCRATCH if live else SCRATCH_RETAINED) / case / "staging"
    files = [p for p in staging.rglob("*") if p.is_file()]
    return {
        "file_count": len(files),
        "bytes": sum(f.stat().st_size for f in files) if files else 0,
    }


def _assert(cond: bool, name: str, checks: list) -> None:
    checks.append({"name": name, "ok": bool(cond)})


def _payload_envelope(payload: dict):
    """The structurally-forwarded envelope body (L2 wraps it in error_envelope)."""
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("error_envelope"), dict):
        return payload["error_envelope"]
    if isinstance(payload.get("error_envelope_schema_version"), str):
        return payload
    return None


def _unwrap_l1(stderr_text: str):
    payload = _parse_json_output(stderr_text)
    return payload, _payload_envelope(payload or {}) if payload else None


def run_case(case: str) -> dict:
    if case == "exit_probe":
        return _run_exit_probe_case()
    return _legacy_run_case(case)


def _run_exit_probe_case() -> dict:
    """Single-layer probe: the REAL modified cli.main() exit path run in a
    real subprocess (runner mode exit_probe).  Verdict target: the exit
    assembles a structured envelope (nested dict intact, no 800-char
    truncation, request_id preserved) with exit 1."""
    case_scratch = SCRATCH / "exit_probe"
    if case_scratch.exists():
        shutil.rmtree(case_scratch)
    env = dict(os.environ)
    env["W02B_CASE"] = "exit_probe"
    env["W02B_SCRATCH"] = str(case_scratch)
    env["PYTHONUTF8"] = "1"
    env.pop("W02B_DEBUG_TRACEBACK", None)
    proc = subprocess.run(
        [
            str(ISO_PY),
            "-X",
            "utf8",
            "-B",
            str(A / "scripts" / "w02b_cw_ensure_runner.py"),
            "--case",
            "exit_probe",
            "--scratch",
            str(case_scratch),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(A),
        env=env,
        timeout=120,
        check=False,
    )
    _save_raw("exit_probe", "l1_cli_exit_real", proc)
    payload = _parse_json_output(proc.stderr)
    checks: list[dict] = []
    _assert(proc.returncode == 1, "real_cli_exit_code_1", checks)
    _assert(isinstance(payload, dict), "exit_stderr_is_one_json_object", checks)
    if isinstance(payload, dict):
        _assert(
            payload.get("code") == "upstream_unavailable",
            "exit_envelope_code_declared",
            checks,
        )
        _assert(payload.get("retryable") is True, "exit_retryable_bool_true", checks)
        _assert(
            payload.get("request_id") == "execv2-w02b",
            "exit_request_id_preserved",
            checks,
        )
        _assert(payload.get("stage") == "adapter_process", "exit_stage_set", checks)
        _assert(
            payload.get("error_envelope_schema_version")
            == "cross-cli-error-envelope/1.0",
            "exit_schema_version",
            checks,
        )
        cause = payload.get("cause_chain") or []
        _assert(
            isinstance(cause, list)
            and isinstance(cause[0], dict)
            and isinstance(cause[0].get("verbatim_nested"), dict),
            "exit_nested_dict_kept_structural",
            checks,
        )
        _assert(
            payload.get("side_effects")
            == {"download_events": 0, "raw_bytes_saved": None, "staged_path": None},
            "exit_side_effects_present",
            checks,
        )
        # exit code: expected 1 recorded; no stdout masquerade
        _assert(proc.stdout.strip() == "", "exit_no_stdout_garbage", checks)
    else:
        checks.append({"name": "exit_stderr_json", "ok": False})
    return {
        "case": "exit_probe",
        "layers": {"l1_cli_exit_real": {"exit": proc.returncode, "expected": 1}},
        "expectations_checked": checks,
        "passed": all(c["ok"] for c in checks),
        "business_verdict": (
            "passed_structure_preserved"
            if checks and all(c["ok"] for c in checks)
            else "failed"
        ),
        "exit_code_note": "外层 runner 退出码与业务失败档分开",
    }


def _legacy_run_case(case: str) -> dict:
    if case == "exit_probe":
        return _run_exit_probe_case()
    chain_proc, l1_cmd = _run_chain(case)
    l2_proc = _run_l2_direct(case)
    l3_proc = _run_l3_direct(case)

    l1_payload = _parse_json_output(chain_proc.stderr)
    l1_envelope = (
        _payload_envelope(l1_payload) if isinstance(l1_payload, dict) else None
    )
    l2_payload = _parse_json_output(l2_proc.stderr)
    l3_stdout_payload = _parse_json_output(l3_proc.stdout)

    checks: list[dict] = []
    exp = EXPECTATIONS[case]
    # exit codes
    for layer, expected_rc in exp["expected_exit"].items():
        got = {
            "l1": chain_proc.returncode,
            "l2": l2_proc.returncode,
            "l3": l3_proc.returncode,
        }[layer]
        _assert(got == expected_rc, f"exit_{layer}_{got}eq{expected_rc}", checks)

    if case == "p1_cw":
        _assert(isinstance(l1_envelope, dict), "l1_envelope_is_json_dict", checks)
        _assert(
            l1_envelope.get("code") == "upstream_unavailable",
            "l1_code_passthrough",
            checks,
        )
        _assert(l1_envelope.get("retryable") is True, "l1_retryable_bool_true", checks)
        _assert(bool(l1_envelope.get("request_id")), "request_id_present", checks)
        side = l1_envelope.get("side_effects") or {}
        _assert(
            side.get("download_events") == 0, "no_download_window_not_faked", checks
        )
        _assert(
            isinstance(l1_envelope.get("cause_chain"), list)
            and len(l1_envelope["cause_chain"]) >= 1,
            "cause_chain_structural",
            checks,
        )
        iter_first = json.dumps(l1_envelope, ensure_ascii=False)
        _assert("世界中并没有" not in iter_first, "no_fabricated_content", checks)

    if case == "n1_long":
        env_obj = l1_envelope or {}
        raw_doc = env_obj.get("cause_chain")
        found_long = False
        found_nested = False
        for entry in _flatten_iter(raw_doc) if raw_doc else []:
            if isinstance(entry, dict):
                if str(entry.get("message") or "").find(container := "") >= 0:
                    pass
                if not isinstance(entry.get("detail"), str):
                    continue
        # walk full structure for the long Chinese message & nested cause
        text = json.dumps(env_obj, ensure_ascii=False)
        _assert(len(text) >= 800, "long_document_preserved_over_800", checks)
        _assert(
            env_obj.get("code") == "upstream_unavailable", "code_passthrough", checks
        )
        _assert(env_obj.get("retryable") is True, "retryable_true_passthrough", checks)
        chain = json.dumps(env_obj.get("cause_chain") or [], ensure_ascii=False)
        _assert(
            "provider_http" in chain and "http_status" in chain,
            "nested_cause_keys_preserved",
            checks,
        )
        diag = chain_proc.stderr
        _assert(env_obj.get("local_diag_ref"), "l1_diag_ref_present", checks)
        if env_obj.get("local_diag_ref"):
            p = Path(env_obj["local_diag_ref"])
            _assert(p.is_file(), "l1_diag_file_exists", checks)
            if p.is_file():
                _assert(
                    len(p.read_text(encoding="utf-8")) >= 800,
                    "l1_diag_full_content",
                    checks,
                )

    if case == "n2_unknown":
        _assert(l1_envelope.get("code") == "fatal", "unknown_code_fails_closed", checks)
        _assert(
            l1_envelope.get("retryable") is False, "unknown_code_not_retryable", checks
        )
        text = json.dumps(l1_envelope, ensure_ascii=False)
        _assert("weird_provider_code" in text, "raw_code_preserved_in_chain", checks)

    if case == "n2_string":
        _assert(
            l1_envelope.get("code") == "upstream_unavailable", "valid_code_kept", checks
        )
        _assert(
            l1_envelope.get("retryable") is False,
            "string_retryable_fails_closed",
            checks,
        )
        text = json.dumps(l1_envelope, ensure_ascii=False)
        _assert("retryable_not_bool" in text, "validation_finding_recorded", checks)
        _assert(
            'raw": "true' in text or 'raw":"true' in text or "'true'" in text,
            "raw_value_preserved",
            checks,
        )

    if case == "n2_malformed":
        _assert(
            l1_payload.get("error_code") == "upstream", "l1_marked_upstream", checks
        )
        text = json.dumps(l1_payload or {}, ensure_ascii=False)
        _assert("error_envelope" not in text, "no_envelope_parsed_from_garbage", checks)
        diag_row = l2_payload
        raw_dir = RAW_LOGS / case
        archives = sorted(raw_dir.glob("**/upstream_raw_*.txt"))
        _assert(bool(archives), "l2_full_output_archived", checks)
        if archives:
            content = "".join(
                p.read_text(encoding="utf-8", errors="replace") for p in archives
            )
            _assert(
                "connection died mid-stream" in content, "full_stderr_preserved", checks
            )
        _assert(
            chain_proc.returncode == 3 and l2_proc.returncode == 2,
            "opaque_short_summary_no_truncation_flow",
            checks,
        )

    if case == "n3":
        side = (l1_envelope or {}).get("side_effects") or {}
        _assert(
            side.get("download_events") == 1, "journal_row_download_events_one", checks
        )
        _assert(side.get("raw_bytes_saved") == 1280, "raw_bytes_saved_real", checks)
        journal_rows = _read_journal(case, live=True)
        ok_row = any(
            row.get("reason") == "canonical_import_failed"
            and json.loads(row.get("side_effects_json") or "{}").get("download_events")
            == 1
            and json.loads(row.get("side_effects_json") or "{}").get("raw_bytes_saved")
            == 1280
            for row in journal_rows
        )
        _assert(ok_row, "journal_row_has_real_side_effects", checks)
        seed = _seed_retained(case, live=True)
        _assert(
            seed["file_count"] >= 1 and seed["bytes"] >= 1280,
            "seed_raw_retained_in_scratch",
            checks,
        )
        _assert(
            l1_envelope.get("retryable") is False,
            "raw_saved_scan_failure_not_retry_flag_assigned",
            checks,
        )

    if case == "n4a":
        _assert(
            l1_envelope.get("code") == "catalog_busy", "db_busy_canonical_code", checks
        )
        _assert(
            l1_envelope.get("retryable") is True, "db_busy_declared_retryable", checks
        )
        journal_rows = _read_journal(case, live=True)
        _assert(len(journal_rows) == 1, "exactly_one_attempt_row", checks)
        row = journal_rows[0] if journal_rows else {}
        _assert(
            row.get("error_code") == "catalog_busy" and row.get("retryable") is True,
            "journal_db_busy_retryable_true",
            checks,
        )
        _assert(
            _seed_retained(case, live=True) == {"file_count": 0, "bytes": 0},
            "no_sideeffect_conflated_into_db_busy",
            checks,
        )

    if case == "n4b":
        _assert(
            l1_envelope.get("code") == "identity_contract",
            "identity_contract_code",
            checks,
        )
        _assert(l1_envelope.get("retryable") is False, "identity_not_retryable", checks)
        journal_rows = _read_journal(case, live=True)
        row = journal_rows[0] if journal_rows else {}
        _assert(row.get("retryable") is False, "journal_identity_not_retryable", checks)
        # cross-row comparison with n4a (different attempt_id, same request_id)
        rows_a = _read_journal("n4a", live=True)
        if journal_rows and rows_a:
            _assert(
                journal_rows[0]["attempt_id"] != rows_a[0]["attempt_id"],
                "attempt_ids_distinct",
                checks,
            )
            _assert(
                journal_rows[0]["request_id"] == rows_a[0]["request_id"],
                "request_ids_identical_urn",
                checks,
            )

    passed = all(c["ok"] for c in checks)
    result = {
        "case": case,
        "layers": {
            "l1": {
                "exit": chain_proc.returncode,
                "expected": exp["expected_exit"].get("l1"),
                "stdout_head": chain_proc.stdout[:400],
                "stderr_json_keys": sorted(l1_payload)
                if isinstance(l1_payload, dict)
                else None,
                "request_id": (l1_payload or {}).get("request_id")
                or (l1_envelope or {}).get("request_id"),
            },
            "l2": {
                "exit": l2_proc.returncode,
                "expected": exp["expected_exit"].get("l2"),
                "stderr_json_keys": sorted(l2_payload)
                if isinstance(l2_payload, dict)
                else None,
            },
            "l3": {
                "exit": l3_proc.returncode,
                "expected": exp["expected_exit"].get("l3"),
                "stdout_is_valid_json": isinstance(l3_stdout_payload, dict),
            },
        },
        "expectations_checked": checks,
        "passed": passed,
        "business_verdict": "passed_structure_preserved" if passed else "failed",
        "exit_code_note": "外层 runner 退出码与业务失败档分开；业务失败不因外层 exit 0 掩盖",
    }
    return result


def probe_placeholder(_stderr):
    return None


def _flatten_iter(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            yield value
            yield from _flatten_iter(value)
    elif isinstance(obj, list):
        for item in obj:
            yield item
            yield from _flatten_iter(item)


def setup() -> None:
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    # bind copy: fake_upstream_cli.py -> upstream_root/scripts/fetch_filing.py
    scripts_dir = UPSTREAM_ROOT / "scripts"
    if scripts_dir.exists():
        shutil.rmtree(scripts_dir)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SAMPLES / "fake_upstream_cli.py", scripts_dir / "fetch_filing.py")
    # see which adapter the CW config dummy needs: keep a minimal placeholder
    (UPSTREAM_ROOT / "cw_config_dummy.yaml").write_text(
        "# placeholder config passed to the chain (hermetic shim ignores)\n"
        'schema_version: "1.0"\n',
        encoding="utf-8",
    )
    AFTER.mkdir(parents=True, exist_ok=True)
    if RAW_LOGS.exists():
        shutil.rmtree(RAW_LOGS)
    RAW_LOGS.mkdir(parents=True, exist_ok=True)
    if SCRATCH_RETAINED.exists():
        shutil.rmtree(SCRATCH_RETAINED)


def main() -> int:
    setup()
    layer_by_layer: dict = {}
    side_effects_ledger: dict = {}
    case_results: dict = {}
    for case in CASES:
        result = run_case(case)
        layer_by_layer[case] = result
        case_results[case] = {
            "passed": result["passed"],
            "business_verdict": result["business_verdict"],
            "layers_exit": {k: v["exit"] for k, v in result["layers"].items()},
        }
        if case in DEEP_CASES:
            _snapshot(case)
            side_effects_ledger[case] = {
                "journal_rows": _read_journal(case),
                "retained_staging": _seed_retained(case),
                "side_effects_from_envelope": None,
                "note": EXPECTATIONS.get(case, {}).get("retry_owner_note", ""),
            }
            l1_env = _read_l1_envelope(case)
            side_effects_ledger[case]["side_effects_from_envelope"] = (
                l1_env or {}
            ).get("side_effects")
    (AFTER / "layer-by-layer-errors.json").write_text(
        json.dumps(layer_by_layer, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "side-effects-ledger.json").write_text(
        json.dumps(side_effects_ledger, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "case_results.json").write_text(
        json.dumps(case_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    failed = [c for c, r in case_results.items() if not r["passed"]]
    for name in failed:
        print(f"W02B FAILED CASE: {name}", file=sys.stderr)
    return 1 if failed else 0


def _read_l1_envelope(case: str):
    raw = RAW_LOGS / case / "l1_source_preparation.stderr.txt"
    if not raw.is_file():
        return None
    payload = _parse_json_output(raw.read_text(encoding="utf-8", errors="replace"))
    return _payload_envelope(payload or {}) if payload else None


if __name__ == "__main__":
    raise SystemExit(main())

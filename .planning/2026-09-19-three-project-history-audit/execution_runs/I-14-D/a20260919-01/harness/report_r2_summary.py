"""I-14-D r2: assemble the machine-checkable r2 summary the re-reviewer can diff.

Reads only artifacts already on disk (no redactor runs), so it is cheap to re-run
after any further edit.  Every number here is READ from an evidence file, never
typed in twice: if an artifact moves, this summary moves with it.

    python report_r2_summary.py --out <attempt>/after/r2_summary.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = HERE.parent


def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ATT / "after" / "r2_summary.json"))
    args = parser.parse_args(argv)

    oracle_narrow = _json(ATT / "after" / "oracle_narrow.json")
    oracle_base = _json(ATT / "before" / "oracle_base.json")
    rule_narrow = _json(ATT / "after" / "rule_table_narrow.json")
    rule_base = _json(ATT / "before" / "rule_table_base.json")
    probe_narrow = _json(ATT / "after" / "probe_results_narrow.json")
    probe_helper_narrow = _json(ATT / "after" / "authsplit_probe_narrow.json")
    probe_helper_base = _json(ATT / "before" / "authsplit_probe_base.json")
    matrix = _json(ATT / "mutations" / "mutation_matrix.json")
    counts = _json(ATT / "after" / "counts.json")
    git_apply = _json(ATT / "after" / "git_apply_verification.json")
    recovery = _json(ATT / "recovery" / "recovery_verification_r2.json")
    cli = {shape: _json(ATT / "after" / "cli-r2" / shape / "narrow" / "result.json")
           for shape in ("E5a", "E5b")}

    e6 = next((c for c in probe_narrow.get("cases", [])
               if c["case_id"] == "E6-auth-scheme-newline"), {})

    summary = {
        "revision": "r2",
        "answers": "reviewer BLOCKER F-REV-D-01 + RULING 1 + RULING 2 (RULING 3 accepted as-is)",
        "reviewer_report_sha256": _sha(ATT / "reviewer_report.md"),
        "reviewer_report_bytes": (ATT / "reviewer_report.md").stat().st_size
        if (ATT / "reviewer_report.md").is_file() else None,
        "deliverable": {
            "tree": "iso/product_narrow",
            "observability_sha256": _sha(ATT / "iso" / "product_narrow" / "src" /
                                         "company_wiki" / "source_catalog" /
                                         "observability.py"),
            "bytes": (ATT / "iso" / "product_narrow" / "src" / "company_wiki" /
                      "source_catalog" / "observability.py").stat().st_size,
            "pre_r2_state_sha256": "e8abd522b2072add062be225d7ec1ca10621ffa5be7841f99ef9fb339015cbd0",
            "base_sha256": _sha(ATT / "iso" / "product_base" / "src" / "company_wiki" /
                                "source_catalog" / "observability.py"),
            "fix_diff": {"path": "changes_r2_authsplit.diff",
                         "sha256": _sha(ATT / "changes_r2_authsplit.diff")},
            "deliverable_diff": {"path": "changes.diff",
                                 "sha256": _sha(ATT / "changes.diff")},
        },
        "oracle": {
            "cases_narrow": oracle_narrow.get("cases"),
            "narrow_must_failed_narrow": oracle_narrow.get("narrow_must_failed"),
            "narrow_must_failed_base": oracle_base.get("narrow_must_failed"),
            "verdict_narrow": oracle_narrow.get("verdict"),
            "verdict_base": oracle_base.get("verdict"),
        },
        "rule_table": {
            "entries": rule_narrow.get("entries"),
            "credential_leaks_narrow": rule_narrow.get("credential_leaks"),
            "credential_secret_leaks_narrow": rule_narrow.get("credential_secret_leaks"),
            "touched_but_should_not_be_narrow": rule_narrow.get("touched_but_should_not_be"),
            "fidelity_ok_narrow": rule_narrow.get("fidelity_ok"),
            "fidelity_failures_base": [f["id"] for f in rule_base.get("fidelity_failures", [])],
            "auth_split_rows": [r["id"] for r in rule_narrow.get("rows", [])
                                if str(r["id"]).startswith("cred-auth-split")],
        },
        "helper_probe": {
            "cases": probe_helper_narrow.get("cases"),
            "leaks_narrow": probe_helper_narrow.get("credential_leaks"),
            "leaks_base": probe_helper_base.get("credential_leaks"),
            "fidelity_drift_narrow": probe_helper_narrow.get("fidelity_drift"),
            "fidelity_drift_base": probe_helper_base.get("fidelity_drift"),
        },
        "real_exit_E6": {
            "persisted_message_redacted": e6.get("message_redacted"),
            "persisted_or_printed_hits": e6.get("persisted_or_printed_hits"),
            "secret_absent_ok": e6.get("marker_absent_ok"),
            "secret_len": e6.get("secret_len"),
            "returncode": e6.get("raw_returncode"),
        },
        "real_cli": {shape: {"returncode": cli[shape].get("returncode"),
                             "marker_hits": cli[shape].get("marker_hits"),
                             "bare_traceback_on_stderr":
                                 cli[shape].get("bare_traceback_on_stderr"),
                             "structured_envelope_on_stderr":
                                 cli[shape].get("structured_envelope_on_stderr"),
                             "catalogs_created": cli[shape].get("catalogs_created")}
                     for shape in ("E5a", "E5b")},
        "mutations": {
            mid: {
                "op": entry.get("op"),
                "tree": entry.get("tree"),
                "observability_sha256": _sha(ATT / "iso" / entry["tree"] / "src" /
                                             "company_wiki" / "source_catalog" /
                                             "observability.py") if entry.get("tree") else None,
                "oracle_rc": entry.get("oracle_rc"),
                "oracle_narrow_must_failed": entry.get("oracle_narrow_must_failed"),
                "rule_table_rc": entry.get("rule_table_rc"),
                "credential_leaks": entry.get("credential_leaks"),
                "credential_secret_leaks": entry.get("credential_secret_leaks"),
                "authsplit_probe_rc": entry.get("authsplit_probe_rc"),
                "authsplit_probe_leaks": entry.get("authsplit_probe_leaks"),
                "exit_probe_persisted_secret": [
                    {"case": r["case"], "secret_absent_ok": r["secret_absent_ok"]}
                    for r in (entry.get("exit_probe_rows") or [])
                    if r["case"] == "E6-auth-scheme-newline"],
            }
            for mid, entry in matrix.get("mutants", {}).items()
        },
        "counts": counts,
        "round_trips": {
            "git_apply_reproduces": git_apply.get("GIT_APPLY_REPRODUCES_T4"),
            "git_apply_diff_bytes": git_apply.get("diff_bytes"),
            "recovery_byte_identical": recovery.get("RECOVERY_BYTE_IDENTICAL"),
            "recovery_source_files_compared": recovery.get("source_files_compared"),
        },
        "generator": "harness/report_r2_summary.py",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps({
        "out": str(out),
        "oracle": summary["oracle"],
        "rule_table_entries": summary["rule_table"]["entries"],
        "credential_leaks": summary["rule_table"]["credential_leaks_narrow"],
        "credential_secret_leaks": summary["rule_table"]["credential_secret_leaks_narrow"],
        "real_exit_E6": summary["real_exit_E6"],
        "mutations": {k: {"oracle_rc": v["oracle_rc"], "rule_table_rc": v["rule_table_rc"],
                          "probe_rc": v["authsplit_probe_rc"]}
                      for k, v in summary["mutations"].items()},
        "round_trips": summary["round_trips"],
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

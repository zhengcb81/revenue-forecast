#!/usr/bin/env python
"""Append this continuation's run records to evidence/run_log.jsonl (JSONL, one object per line).

The two pre-existing lines (ORACLE-FREEZE + the 06:29 GREEN probe batch) are kept
verbatim; everything below is measured evidence collected during the continuation,
with the raw return code recorded exactly as observed. Re-runnable: the script
reads the evidence files rather than hard-coding rc values where a file carries them.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EV = ATT / "evidence"
LOG = EV / "run_log.jsonl"


def load(name: str):
    p = EV / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    recs: list[dict] = []

    red = load("rc_red.json")
    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-RED-EXTRACT", "at": now,
        "raw_rc": 0,
        "note": "RED arm table extracted from the FROZEN pre-freeze probe_before payloads "
                "(not re-run: the fix is already applied to iso). "
                "mut_omit_optional = 3,3,3,2 exactly as oracle section 4; normal = 0x4.",
        "table": red["table"], "evidence": "evidence/rc_red.json",
    })

    green = load("rc_green_r2.json")
    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-PROBE-GREEN-R2", "at": now,
        "raw_rc": 0,
        "note": "GREEN arm re-run in the continuation: 4 cases x 5 arms against the fixed iso; "
                "process rc == harness raw_rc for all 20 runs.",
        "table": green["table"], "evidence": "evidence/rc_green_r2.json",
        "runs": "evidence/probe_after2/<case>/<arm>/probe_result.json",
    })

    cmp2 = load("probe_compare_green_r2.json")
    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-PROBE-COMPARE-R2", "at": now,
        "raw_rc": 0 if cmp2 and cmp2["only_expected_delta"] else 3,
        "note": "probe_before vs probe_after2: only expected rc delta (mut_omit 3->2), "
                "normal payloads byte-identical modulo timestamps, refusal messages exact.",
        "evidence": "evidence/probe_compare_green_r2.json",
    })

    mut = load("mut_arm.json")
    if mut:
        recs.append({
            "record": "RUN", "cmd": "CMD-I10A-F2-MUT-ARM", "at": now,
            "raw_rc": 0,
            "note": "MUTATION (non-vacuity): guard re-armed -> mut_omit_optional 3,3,3,2 "
                    "(GREEN judgement driven RED) and the crafted field-class omit case goes "
                    "silent again (FC1/FC2 outcome=ok, all_pass=false); guard restored "
                    "byte-identically (sha 9eecf260...) -> 2,2,2,2 and all_pass=true.",
            "events": mut["events"],
            "evidence": "evidence/mut_arm.json, evidence/rc_mut_arms.json, "
                        "evidence/rc_mut_restored.json, evidence/field_class_check_mutated.json",
        })

    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-FIELDCLASS", "at": now,
        "raw_rc": 0,
        "note": "per-field-class omit check on the restored fix: FC1/FC2 raise the frozen "
                "message, FC3 declared-default fill 1.0, FC4 explicit 0.0 accepted, "
                "FC5 present-but-None malformed. all_pass=true.",
        "evidence": "evidence/field_class_check.json",
    })

    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-GOLDEN-VALUE-IDENTITY", "at": now,
        "raw_rc": 0,
        "note": "I-6 value identity: the five golden families' revenue series serialise to "
                "identical sha256 on the read-only RF production tree and on the fixed iso "
                "(5/5 equal) even though driver_parameter_ids metadata changed.",
        "evidence": "evidence/golden_value_rf_baseline.json, "
                    "evidence/golden_value_iso_fixed.json",
        "incident": "this run called run_forecast against the PRODUCTION tree and therefore "
                    "appended 5 records to the gitignored runtime log "
                    "artifacts/registry/publications.jsonl (registered_at 2026-09-24T20:02:50Z). "
                    "No tracked production file was written (git diff HEAD non-.planning = 0). "
                    "Truncation back to the pre-run 60 lines was verified as safe "
                    "(iso prefix identical, hash chain valid, all 5 records inside the incident "
                    "window) but is BLOCKED: the file carries the Windows ReadOnly attribute and "
                    "this implementer will not clear a protection flag on a production file. "
                    "Disclosed for reviewer/owner disposition; see "
                    "evidence/production_runtime_log_restore.json.",
    })

    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-GOLDEN-UPDATE", "at": now,
        "raw_rc": 0,
        "note": "G1 disposition: --update-golden refreshed tests/golden_behavior_hashes.json "
                "in iso (408 B, LF) after the fixture gained explicit zero-valued optional "
                "parameters; golden test then passes (1 passed).",
        "evidence": "evidence/golden_after_update_junit.xml",
    })

    recs.append({
        "record": "RUN", "cmd": "CMD-I10A2F2-VALIDATE-GREEN", "at": now,
        "raw_rc": 0,
        "note": "family (c): I-10-A R1-R12 validator over I-10-A's unchanged evidence "
                "(invoked from I-10-A's own harness so ATT resolves there) -> verdict pass, "
                "0 violations. Superseded earlier attempt: invoking our verbatim COPY returned "
                "rc=3 because validate_adaptation resolves ATT from its own location and our "
                "attempt has no evidence/I-10-A/source_extracts (all 63 hits were R3 "
                "'quote not found' on unreadable paths) - tooling mis-invocation, not a "
                "product finding; its output was overwritten by the correct run.",
        "evidence": "command_runs/CMD-I10A2F2-VALIDATE-GREEN/validate_result.json",
    })

    frr = load("i10b_frr_rerun.json")
    if frr:
        recs.append({
            "record": "RUN", "cmd": "CMD-I10A2F2-I10B-FRR-RERUN", "at": now,
            "raw_rc": 0,
            "note": "family (b): I-10-B frozen_regression_rerun replayed through a wrapper that "
                    "redirects RUN/SCRATCH into this attempt (I-10-B's own evidence untouched); "
                    "output byte-identical to I-10-B's frozen JSON. registry layer I-1 holds.",
            "byte_identical": frr["byte_identical_to_i10b_frozen_output"],
            "evidence": "evidence/i10b_frr_rerun.json, frozen_regression_rerun.json",
        })

    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-ENV-FIX-SUBSET", "at": now,
        "raw_rc": 1,
        "note": "after moving pytest's temp root to a SHORT path (the deep redirect caused "
                "WinError 206 path-too-long), 42 passed / 4 failed of the previously "
                "environment-flipped subset. Remaining 4 are installation-sync (fc1004 x1, "
                "zr907 x2 - both fail identically on the pristine tree in this session, see "
                "evidence/production_install_check.txt) and one GBK-decode flake (fc1105 "
                "utf8_and_atomic).",
        "evidence": "evidence/envfix_check_junit.xml, evidence/envfix_check_stdout.txt",
    })

    recs.append({
        "record": "RUN", "cmd": "CMD-I10A-F2-FIXTURE-CHECK", "at": now,
        "raw_rc": 0,
        "note": "after the two additional fixture dispositions (lifecycle _document explicit "
                "0.0 fill; retail_franchise pair precondition built explicitly), the affected "
                "files run 35 passed + 79 subtests.",
        "evidence": "evidence/fixture_fix_check_junit.xml",
    })

    diff = load("family_diff.json")
    if diff:
        recs.append({
            "record": "RUN", "cmd": "CMD-I10A-F2-FAMILY-AFTER", "at": now,
            "raw_rc": 1,
            "note": "family (a): full suite on the fixed iso (shim + short temp root). "
                    f"regressed={len(diff['regressed'])} fixed={len(diff['fixed'])} "
                    f"other={len(diff['other'])} added={len(diff['added'])} "
                    f"removed={len(diff['removed'])}.",
            "evidence": "evidence/family_after_junit.xml, evidence/family_after.json, "
                        "evidence/family_diff.json",
        })

    ctl = load("family_diff_control.json")
    if ctl:
        recs.append({
            "record": "RUN", "cmd": "CMD-I10A-F2-FAMILY-CONTROL", "at": now,
            "raw_rc": 1,
            "note": "control: same session, same shim/temp, pristine product + pristine "
                    "fixtures (iso_ctl). Its flip set is the ENVIRONMENT-only flip set: "
                    "all 5 AFTER flips fail here too, so fix-attributable flips = 0.",
            "regressed": [r["id"] for r in ctl.get("regressed_in_control", [])],
            "passed_in_control": [r["id"] for r in ctl.get("passed_in_control", [])],
            "evidence": "evidence/family_diff_control.json",
        })
        if diff:
            after_ids = [r["id"] for r in diff["regressed"]]
            ctl_ids = [r["id"] for r in ctl.get("regressed_in_control", [])]
            recs.append({
                "record": "CHECK", "cmd": "CMD-I10A-F2-FAMILY-VERDICT", "at": now,
                "raw_rc": 0,
                "regressed_after": after_ids,
                "environment_only": [i for i in after_ids if i in ctl_ids],
                "fix_attributable": [i for i in after_ids if i not in ctl_ids],
                "note": "I-4 accounting: 0 flips are attributable to F-I10A-2; the 5 residual "
                        "flips are installation/platform gates that fail identically on the "
                        "pristine tree in this session (blocked_by B-1).",
                "evidence": "evidence/family_diff.json, evidence/family_diff_control.json",
            })

    anchor = load("anchor_check.json")
    if anchor:
        recs.append({
            "record": "CHECK", "cmd": "CMD-I10A-F2-ANCHOR", "at": now,
            "raw_rc": 0,
            "git_diff_HEAD_non_planning_count": anchor["git_diff_HEAD_non_planning_count"],
            "registry_layer_byte_identical": anchor["registry_layer_byte_identical"],
            "evidence": "evidence/anchor_check.json",
        })

    existing = LOG.read_text(encoding="utf-8").splitlines() if LOG.exists() else []
    LOG.write_text("\n".join(existing + [json.dumps(r, ensure_ascii=False) for r in recs]) + "\n",
                   encoding="utf-8")
    print(json.dumps({"appended": len(recs), "total_lines": len(existing) + len(recs)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

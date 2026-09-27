"""Build provenance.json + handoff.json for the I-14-A D1/D2 ops review carrier.

- hashes every evidence file produced by this attempt,
- records the two external sources (URL, retrieved UTC, verbatim quote, snapshot sha256),
- re-parses every JSON it writes,
- verifies UTF-8 (no BOM) + LF-only for the three carriers.

Usage: python build_artifacts.py <attempt-root>
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence"
CARRIERS = ["ruling.md", "provenance.json", "handoff.json"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def entry(p: Path) -> dict:
    data = p.read_bytes()
    return {
        "path": str(p.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# JSON authored by THIS reviewer (carriers + my own scripts).  Raw tool output
# (probe report.json, harness verdict/stdout captures) is deliberately NOT
# rewritten: those files stay byte-for-byte as the tools produced them.
AUTHORED_JSON = [
    "provenance.json",
    "handoff.json",
    "evidence/copied_inputs_sha256.json",
    "evidence/d1_peak_method_experiment.json",
    "evidence/d2_binding_matrix.json",
    "evidence/d2_binding_matrix_run1_mybug.json",
    "evidence/oracle_recompute.json",
    "evidence/oracle_recompute_E0.json",
    "evidence/oracle_recompute_E1c.json",
    "evidence/e1c_samples_inside_life.json",
]


def normalize_authored_json() -> list[dict]:
    """UTF-8, no BOM, LF-only + re-parse gate for every JSON this reviewer authored."""
    results = []
    for rel in AUTHORED_JSON:
        p = ROOT / rel
        if not p.is_file():
            results.append({"path": rel, "status": "absent"})
            continue
        raw = p.read_bytes()
        had_bom = raw.startswith(b"\xef\xbb\xbf")
        if had_bom:
            raw = raw[3:]
        text = raw.decode("utf-8")
        crlf = text.count("\r\n")
        text = text.replace("\r\n", "\n")
        json.loads(text)  # re-parse gate BEFORE writing
        p.write_bytes(text.encode("utf-8"))
        results.append({"path": rel, "status": "normalized",
                        "had_bom": had_bom, "crlf_replaced": crlf})
    return results


def main() -> int:
    now = now_utc()
    normalization = normalize_authored_json()

    # ---------------------------------------------------------------- evidence
    evidence_entries = []
    for p in sorted(EVID.rglob("*")):
        if not p.is_file():
            continue
        if p.name == "encoding_check.json":
            continue  # written last; citing its own inventory would be stale by construction
        evidence_entries.append(entry(p))

    # ------------------------------------------------------------ external src
    msdn = EVID / "external_sources" / "msdn_PROCESS_MEMORY_COUNTERS.txt"
    psutil = EVID / "external_sources" / "psutil_pswindows_memory_info.txt"
    external = [
        {
            "id": "EXT-1",
            "url": "https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters",
            "http_status": 200,
            "retrieved_utc": "2026-09-24T20:48:29Z",
            "page_note": "page footer on the fetched document: 'Last updated on 2024-02-22'",
            "quote": ("PROCESS_MEMORY_COUNTERS structure (psapi.h) — 'Contains the memory statistics "
                      "for a process.' / 'PeakWorkingSetSize  The peak working set size, in bytes.' / "
                      "'WorkingSetSize  The current working set size, in bytes.' / 'PeakPagefileUsage  "
                      "The peak value in bytes of the Commit Charge during the lifetime of this process.'"),
            "snapshot_path": str(msdn.relative_to(ROOT)).replace("\\", "/"),
            "snapshot_sha256": sha256(msdn),
            "snapshot_bytes": msdn.stat().st_size,
            "used_for": "D1 peak method: PeakWorkingSetSize is a process-lifetime counter with no "
                        "measurement-window semantics (basis for rejecting D1 option 1/3 as a "
                        "window-attributable peak).",
            "not_used_for": "no local, machine-checkable fact in ruling.md rests on this source",
        },
        {
            "id": "EXT-2",
            "url": "https://raw.githubusercontent.com/giampaolo/psutil/master/psutil/_pswindows.py",
            "http_status": 200,
            "retrieved_utc": "2026-09-24T20:48:29Z",
            "quote": ("def memory_info(self): # Underlying C function returns fields of "
                      "PROCESS_MEMORY_COUNTERS struct. d = self._get_raw_meminfo(); return ntp.pmem("
                      "rss=d[\"WorkingSetSize\"], ... peak_rss=d[\"PeakWorkingSetSize\"], ... "
                      "\"peak_wset\": d[\"PeakWorkingSetSize\"],  # 'peak_rss'"),
            "snapshot_path": str(psutil.relative_to(ROOT)).replace("\\", "/"),
            "snapshot_sha256": sha256(psutil),
            "snapshot_bytes": psutil.stat().st_size,
            "used_for": "D1 peak method: psutil's Windows peak_wset IS "
                        "PROCESS_MEMORY_COUNTERS.PeakWorkingSetSize, so option 3 (private ctypes "
                        "GetProcessMemoryInfo) reads the same counter as option 1 (no new "
                        "information); also flags peak_wset as a deprecated alias (psutil 8.x risk).",
            "not_used_for": "no local, machine-checkable fact in ruling.md rests on this source",
            "local_cross_check": "attempt venv psutil 7.2.2; d1_peak_method_experiment.json shows "
                                 "59/61 paired reads identical (2 pairs differ by exactly -65536 B, "
                                 "i.e. read timing).",
        },
    ]

    # -------------------------------------------------------------- provenance
    local_citations = [
        {"claim": "authorization for this reviewer",
         "file": ".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md",
         "lines": "L116 (owner verbatim), L126 (D1 ops / D2 SLO owner + promotion gate), L143 (new subagent as independent ops/SLO reviewer)"},
        {"claim": "D1 scope = interval + platform peak method + measurement-error rule",
         "file": ".planning/2026-09-19-three-project-history-audit/execution_v2/card_I-14-A.md",
         "lines": "L10 (clause 3); also L9 (clause 2), L11 (clause 4), L12 (clause 5), L13 (clause 6), L15 (exit/recovery)"},
        {"claim": "D1/D2/D3 ownership + statuses + signature terms",
         "file": ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/decision.md",
         "lines": "L11-13, L15-17, L24-38 (terms), L46-72 (option 2 + error rule), L83-106 (D2), L108-127 (D3)"},
        {"claim": "reviewer must re-run counterexamples against both tools and decide D1 / confirm D2-D3",
         "file": ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/review.md",
         "lines": "L3-6, L39-49, L83-101, L137-150, L348-353"},
        {"claim": "frozen counterexample set E1a-E7b and exit-code contract",
         "file": ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/oracle.md",
         "lines": "L79-92 (counterexamples), L94-105 (exit codes), L107-147 (errata), L167-172 (D1 options), L226-237 (M3/M7 amended)"},
        {"claim": "50 ms constant, sampler, binding refusal, breaches, exit codes",
         "file": ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/iso/slo_probe_patched.py",
         "lines": "L50-55, L76, L82-88, L91-120, L135-174, L180-279, L464-492, L519-531, L617-639, L658-660",
         "sha256": "14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e"},
        {"claim": "unmodified product probe: rc discarded, probe's own peak, catalog is_file() only, bundle alias",
         "file": ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/iso/tool_prod/slo_probe.py",
         "lines": "L46-59, L71-90, L100-102, L112",
         "sha256": "f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059"},
        {"claim": "product release gate opens catalog.sqlite3 (refutes decision.md D2's catalog.db claim)",
         "file": "tools/release_readiness.py",
         "lines": "L37"},
        {"claim": "real config form of catalog_dir",
         "file": ".review-zr407-20260818/company-wiki/config/source_catalog.yaml",
         "lines": "L2: catalog_dir: \"${PROJECT_ROOT}/.source_catalog\""},
        {"claim": "ensure_fixture_root() rewrites fixture files -> sealed attempt must not be re-run",
         "file": ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/harness/fixture_spec.py",
         "lines": "L162-204"},
    ]

    provenance = {
        "carrier": "provenance.json",
        "card": "I-14-A",
        "attempt": "execution_runs/I14A-D1-OPS-REVIEW/a20260924-01",
        "role": "independent_ops_slo_reviewer",
        "author_of_probe": False,
        "authorized_by": "OWNER_DECISIONS §十 L126 + §十一 L143",
        "generated_utc": now,
        "external_sources": external,
        "external_source_count": len(external),
        "local_citations": local_citations,
        "evidence_files": evidence_entries,
        "evidence_file_count": len(evidence_entries),
        "json_normalization": {
            "rule": "JSON authored by this reviewer is UTF-8 (no BOM) + LF-only and is re-parsed "
                    "before and after writing; raw tool output (probe report.json, harness "
                    "verdict/stdout captures) is preserved byte-for-byte and is exempt.",
            "results": normalization,
        },
        "recompute_inputs": {
            "attempt_source_root":
                ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01",
            "attempt_access": "read-only; git status --porcelain on that path returned empty",
            "copied_inputs_manifest": "evidence/copied_inputs_sha256.json (11/11 identical)",
        },
        "carrier_encoding": {},
        "notes": [
            "External sources are used only to interpret D1's peak-method options; every ruling "
            "conclusion is backed by local measurement inside this attempt.",
            "d2_binding_matrix_run1_mybug.json is the failed first run of my own script (config path "
            "passed as text); it is kept for continuity and is NOT evidence for D2.",
            "e5_prod_baseline_run1_missing_root keeps the first, environment-defective E5 invocation "
            "(WinError 267) before the stand-in company-wiki root was copied.",
            "evidence_files is the inventory at provenance write time; evidence/encoding_check.json "
            "(written afterwards, one step later) verifies UTF-8/no-BOM/LF for all three carriers "
            "and is therefore excluded from evidence_files (self-invalidating, P4 rule).",
        ],
    }

    # encoding facts that can be measured before this file is written
    ruling_raw = (ROOT / "ruling.md").read_bytes()
    provenance["carrier_encoding"]["ruling.md"] = {
        "utf8_no_bom": not ruling_raw.startswith(b"\xef\xbb\xbf"),
        "lf_only": ruling_raw.count(b"\r") == 0,
        "sha256": hashlib.sha256(ruling_raw).hexdigest(),
        "bytes": len(ruling_raw),
    }

    prov_path = ROOT / "provenance.json"
    prov_bytes = (json.dumps(provenance, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    prov_path.write_bytes(prov_bytes)
    json.loads(prov_path.read_text(encoding="utf-8"))  # re-parse gate
    if prov_path.read_bytes().startswith(b"\xef\xbb\xbf") or b"\r" in prov_bytes:
        raise SystemExit("carrier encoding gate failed: provenance.json")

    # ------------------------------------------------------------- handoff.json
    ruling_path = ROOT / "ruling.md"
    written = [entry(ruling_path), entry(prov_path)]

    handoff = {
        "carrier": "handoff.json",
        "card": "I-14-A",
        "attempt": "execution_runs/I14A-D1-OPS-REVIEW/a20260924-01",
        "role": "independent_ops_slo_reviewer",
        "author_of_probe": False,
        "authorized_by": "OWNER_DECISIONS §十 L126 + §十一 L143",
        "authorization_quotes": {
            "OWNER_DECISIONS_L116": "…I-14-A D1/D2 指派运维与 SLO owner…",
            "OWNER_DECISIONS_L126": ("**I-14-A D1/D2** | **指派**：运维 owner 签 D1、SLO/探针 owner 签 D2 | "
                                     "编排层按此派单（**D1 必须由非本探针作者签**）；未签前 "
                                     "`iso/slo_probe_patched.py` **不得**进 `RF/tools/`"),
            "OWNER_DECISIONS_L143": ("1 | I-14-A D1/D2 | **派新 subagent** 当独立运维/SLO reviewer | "
                                     "编排层创建独立 reviewer subagent（**D1 必须非本探针作者**）"),
            "declaration": "本人为编排层新建 subagent、非本探针作者，具备 D1 签署资格。",
        },
        "ruling_D1": {
            "status": "SIGNED_RULING_PER_ITEM",
            "signed_by": "independent_ops_slo_reviewer (not the probe's author)",
            "items": {
                "sampling_interval": {
                    "value": "nominal 50 ms fixed (RSS_SAMPLE_INTERVAL_SECONDS = 0.05)",
                    "measured_effective_cadence_ms": [64.0, 75.2],
                    "scope": ("processes alive >= ~2x effective cadence (~150 ms) get PID-identifiable "
                              "samples; shorter children may be missed entirely"),
                    "counterexample": ("E0 fixture_pid_is_in_samples red 6/7 in this session "
                                       "(suite 1 + 5 repeats), green in the sealed attempt"),
                    "open_item": ("append-only correction of the F4/E0 identity expectation OR a "
                                  "spawn-time sampling guarantee — required before card pass"),
                },
                "peak_method": {
                    "value": "option 2: live rss sampled at fixed interval, peak = max of summed process tree",
                    "rejected": ["option 1 peak_wset", "option 3 ctypes GetProcessMemoryInfo"],
                    "measured": {"option2_tree_sum_gb": 0.2674, "option1_peak_wset_gb": 0.2634,
                                 "option3_ctypes_gb": 0.2634,
                                 "option1_vs_option3_pairs": "61 pairs, 59 identical, 2 differ by -65536 B",
                                 "post_exit": "psutil NoSuchProcess; ctypes still returned 4743168 B (ambiguous)"},
                    "counterexample_to_decision_md": ("the 'interpreter start-up spike' premise was NOT "
                                                      "reproduced here (delta 0.0 MB); recorded as "
                                                      "basis=professional_judgement"),
                },
                "measurement_error_rule": {
                    "value": ("no sample => null + uncollected/sampler_disabled + explicit breach, never "
                              "0.0, never green; attribution limited to peak_tree_pids; synthetic "
                              "allocation is order-of-magnitude only; interval/method/error changes need "
                              "a new independent reason + new oracle"),
                    "added_by_this_review": ("a peak whose sampled pid set excludes the measured "
                                             "program's pid must be read as launcher-attributed only and "
                                             "must not be cited as the resolver's RSS"),
                    "residual": ("the meter does not machine-enforce the attribution downgrade yet; exit "
                                 "code attribution to the RSS breach is not isolated in the observed E2 "
                                 "run (bundle breach also present)"),
                },
            },
            "signature_terms_accepted": [
                "F-I14A-01: any invocation without --bundle-measurement exits 2 (measured, intended)",
                "F-I14A-02: rc is unobservable/unobserved on the old tool (6x UnicodeDecodeError measured)",
                "tree-sum is a conservative overestimate (+4.059 MB launcher measured here)",
            ],
            "does_not_declare_card_pass": True,
            "does_not_lift_promotion_prohibition": True,
        },
        "confirmation_D2": {
            "status": "not_confirmed_as_written",
            "confirmed_properties": [
                "inconsistent binding refused with exit 3 and zero resolve calls",
                "consistent binding accepted (quoted / bare / ${PROJECT_ROOT} / catalog.db) with 6 resolve calls",
                "parser fails closed on block scalar, anchor, residual ${}, missing key",
                "E4/E4b re-run green (rc 3 / 2)",
            ],
            "refuted_claims": [
                ("decision.md D2 says RF/tools/release_readiness.py uses catalog.db; measured: 0 matches "
                 "for .db in tools/*.py and release_readiness.py:37 is .source_catalog/catalog.sqlite3 "
                 "=> 'actual target agreement' is not demonstrated for the catalog.db name"),
                ("decision.md/oracle.md say the small reader handles inline # comments; measured: "
                 "quoted scalar + inline comment is refused (exit 3) because _strip_scalar drops the "
                 "comment before unquoting"),
            ],
            "recovery_rule": "append-only correction of decision.md D2 / oracle.md §9.3, or tighten `consistent` to require the filename to equal configured_catalog_file; then re-confirm",
        },
        "status_D3": {
            "status": "unsigned_awaiting_I-16",
            "signed_by_this_reviewer": False,
            "reason": ("D3 belongs to I-16 (bundle measurement changes the default exit semantics); "
                       "no execution_runs/I-16* exists, cards I-16-A/I-16-B are 'planned', and no "
                       "bundle measurement file exists anywhere outside .planning"),
            "bundle_measurement_file_present": False,
            "default_invocation_exit_code_observed": 2,
        },
        "promotion_prohibition_still_in_force": True,
        "counterexample_raw_returncodes": {
            "patched": {"E0": 2, "E1a": 4, "E1b": 4, "E1c": 2, "E2": 2, "E3": 2, "E7": 2,
                        "E4": 3, "E4b": 2, "E6": 0, "runner_rc": 0},
            "production_tool_via_runner": {"all_cases": 2, "E6": 0, "runner_rc": 1},
            "pytest_suite_patched": {"rc": 1, "passed": 11, "failed": 1, "skipped": 1,
                                     "failed_item": "test_frozen_case[E0-baseline-F4] -> fixture_pid_is_in_samples"},
            "pytest_suite_production": {"rc": 1, "passed": 2, "failed": 10, "skipped": 1},
            "e5_old_tool_on_failing_children": {"raw_rc": 0, "breaches": [], "unicode_decode_errors": 6},
            "bundle_control": {"rc": 0, "pass1": 2, "pass2a_copied": 0, "pass2b_independent": 0},
            "e0_identity_repeats": {"runs": 5, "red": 5, "green": 0},
        },
        "written_files": written,
        "self_hash_note": "handoff.json does not cite its own sha256 (self-citation would be stale by construction); hash it externally after the last write.",
        "git_diff_non_planning": 0,
        "git_diff_measurement": "git -c core.quotepath=false diff HEAD --name-only -> 3824 lines, 0 outside .planning (evidence/boundary_checks.txt)",
        "product_write_count": 0,
        "promotion_copy_count": 0,
        "i14a_mutation_count": 0,
        "does_not_claim_I14A_acceptance": True,
        "open_items_carried": [
            "D1-1(c): E0/F4 sub-interval identity expectation must be corrected append-only or made deterministic before card pass",
            "D2: two documented claims refuted by measurement -> append-only correction + re-confirm",
            "D3: awaiting I-16 bundle measurement; promotion stays prohibited until then",
        ],
        "generated_utc": now,
    }

    handoff_path = ROOT / "handoff.json"
    handoff_bytes = (json.dumps(handoff, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    handoff_path.write_bytes(handoff_bytes)
    json.loads(handoff_path.read_text(encoding="utf-8"))  # re-parse gate
    if handoff_path.read_bytes().startswith(b"\xef\xbb\xbf") or b"\r" in handoff_bytes:
        raise SystemExit("carrier encoding gate failed: handoff.json")

    # ------------------------------------------------------------- encoding gate
    enc = {}
    for name in CARRIERS:
        p = ROOT / name
        raw = p.read_bytes()
        enc[name] = {
            "utf8_no_bom": not raw.startswith(b"\xef\xbb\xbf"),
            "crlf_count": raw.count(b"\r\n"),
            "lf_count": raw.count(b"\n"),
            "lf_only": raw.count(b"\r") == 0,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
        raw.decode("utf-8")
    check_path = EVID / "encoding_check.json"
    check_bytes = (json.dumps(
        {"generated_utc": now_utc(), "carriers": enc,
         "authored_json_normalization": normalization,
         "all_utf8_no_bom": all(v["utf8_no_bom"] for v in enc.values()),
         "all_lf_only": all(v["lf_only"] for v in enc.values()),
         "json_reparsed": True},
        ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    check_path.write_bytes(check_bytes)
    json.loads(check_path.read_text(encoding="utf-8"))
    print(json.dumps(enc, ensure_ascii=False, indent=2))
    return 0 if all(v["utf8_no_bom"] and v["lf_only"] for v in enc.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

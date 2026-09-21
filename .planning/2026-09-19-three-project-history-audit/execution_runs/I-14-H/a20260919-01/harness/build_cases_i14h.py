"""I-14-H oracle material builder -- runs ONCE at freeze time, BEFORE any SUT run.

Mechanically composes the I-14-H frozen oracle material from byte-verified
pre-images.  It NEVER invokes the subject under test; every expected value is
either (a) carried verbatim from the r1 frozen pre-image, (b) corrected per
card I-14-H item 3 (W1 union_seconds 2220 -> 1740, append-only provenance), or
(c) hand-derived from the card's prescribed fix semantics + arithmetic
(1740 = 29 min observation, 480 = 8 min quick_check, 2220 = 37 min command).

Outputs (all inside this attempt):
  harness/cases.i14h.json            33 cases = 20 r1 cases verbatim + H1..H13
  harness/frozen_expectations.i14h.json  corrected expectations + provenance
  evidence/freeze_instant.json       freeze hashes/timestamp (pre-first-run)
"""

from __future__ import annotations

import copy
import difflib
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent

W1_FACTS_NOTE = "W1 facts: observation 00:00-00:29 (1740 s), quick_check 00:29-00:37 (480 s), command total 2220 s"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    r1_cases_path = HERE / "cases.json"
    r1_exp_path = HERE / "frozen_expectations.json"
    r1_cases = json.loads(r1_cases_path.read_text(encoding="utf-8"))
    r1_exp = json.loads(r1_exp_path.read_text(encoding="utf-8"))

    r1_cases_sha = sha256_file(r1_cases_path)
    r1_exp_sha = sha256_file(r1_exp_path)
    if r1_exp_sha != "3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b":
        print("FATAL: r1 expectations pre-image hash mismatch", file=sys.stderr)
        return 1
    if r1_cases_sha != "5d8c459277da88b8361b520bee1424f079dc1d9c08744433cae0d30cdbb67d64":
        print("FATAL: r1 cases pre-image hash mismatch", file=sys.stderr)
        return 1

    r1_by_id = {c["case_id"]: c for c in r1_cases["cases"]}
    w1 = copy.deepcopy(r1_by_id["W1"])
    c2 = copy.deepcopy(r1_by_id["C2"])
    w1_fields = copy.deepcopy(w1["fields"])

    # --- H cases: each is W1's exact facts with one claim/basis field varied ---
    def h_case(case_id: str, claim_seconds, basis, note: str,
               windows=None, omit_basis: bool = False) -> dict:
        fields = copy.deepcopy(w1_fields)
        if windows is not None:
            fields["windows"] = windows
        claim = {"status": "eligible", "natural_observation_seconds": claim_seconds}
        if not omit_basis:
            claim["basis"] = basis
        return {
            "case_id": case_id,
            "class": "window_accounting",
            "requirement_id": "SYNTHETIC-TIMER-ONLY(I-14-H#1,#2)",
            "note": note,
            "claim": claim,
            "fields": fields,
        }

    qc_window = {"started_at": "2026-09-19T00:29:00Z",
                 "finished_at": "2026-09-19T00:37:00Z"}
    obs_window = {"started_at": "2026-09-19T00:00:00Z",
                  "finished_at": "2026-09-19T00:29:00Z"}

    h_cases = [
        w1,  # carried verbatim (deep-equal asserted below)
        h_case("H1", 2220, "wall_clock",
               "defect-1 scalar: unregistered basis name must be refused (R-BASIS-UNKNOWN)"),
        h_case("H2", 99999, "",
               "defect-1 scalar: empty-string basis must be refused (R-BASIS-UNKNOWN)"),
        h_case("H3", 99999, None,
               "defect-1 scalar: missing basis key must be refused (R-BASIS-UNKNOWN)",
               omit_basis=True),
        h_case("H4", 2220, None,
               "defect-1 scalar: null basis must be refused (R-BASIS-UNKNOWN)"),
        h_case("H5", 99999, ["union_of_windows"],
               "defect-1 container: list basis must be refused PER CASE; pre-fix r1 accepted it, "
               "inherited i14b-after-2 crashed the whole batch (rc 4, reviewer P4 / T1-10 P-3)"),
        h_case("H6", 2220, {"kind": "union_of_windows"},
               "defect-1 container: dict basis must be refused PER CASE (same residual as H5)"),
        h_case("H7", 2220, "command_total",
               "defect-1 negative control: a REGISTERED basis is still judged on its merits "
               "(command total is not the observation -> R-TOTAL-AS-OBS); must stay red-refused "
               "both before and after the fix"),
        h_case("H8", 1740, "union_of_windows",
               "defect-2: HONEST 1740 s union claim must be ACCEPTED (pre-fix r1 rejected it: "
               "direction inversion, card I-14-H item 2)"),
        h_case("H9", 2220, "union_of_windows",
               "defect-2: dishonest 2220 s union claim must be REJECTED (pre-fix r1 accepted it)"),
        h_case("H10", 2220, "sum_of_windows",
               "defect-2: dishonest 2220 s sum claim must be REJECTED (pre-fix r1 accepted it)"),
        h_case("H11", 2220, "union_of_windows",
               "defect-2 J15 rename variant: window B copies the quick_check span; the 2220 s "
               "union claim must be refused with R-QC-IN-OBS (overlap 480 s)",
               windows=[obs_window, qc_window]),
        h_case("H12", 1740, "union_of_windows",
               "defect-2 J15 companion: declared windows union to 2220, so even the honest 1740 s "
               "claim is refused (R-CLAIM-EXCEEDS) AND the window covering quick_check is refused "
               "(R-QC-IN-OBS) -- mirrors I-14-B X9",
               windows=[obs_window, qc_window]),
        c2,  # carried verbatim: cross-class witness (calendar case must keep its verdict
             # even when a container-basis window case is present in the same batch)
    ]

    # verbatim assertions
    assert h_cases[0] == r1_by_id["W1"], "W1 must be content-identical to the r1 pre-image"
    assert h_cases[-1] == r1_by_id["C2"], "C2 must be content-identical to the r1 pre-image"
    for hc in h_cases[1:-1]:
        expected_fields = copy.deepcopy(w1_fields)
        if "windows" in hc["fields"]:
            expected_fields["windows"] = hc["fields"]["windows"]
        assert hc["fields"] == expected_fields, f"{hc['case_id']} fields must equal W1 facts"
    assert len(h_cases) == 14

    cases_doc = {
        "card": "I-14-H",
        "authored": ("BEFORE any run; composed mechanically from the r1 pre-image cases.json "
                     "(sha256 5d8c4592...) by harness/build_cases_i14h.py; W1 and C2 are "
                     "content-identical to the r1 pre-image; H1-H13 vary one claim/basis field "
                     "over W1's exact facts"),
        "frozen_now_utc": r1_cases["frozen_now_utc"],
        "cases": h_cases,
    }

    # --- expectations ---
    # W1 corrected block per card I-14-H item 3 (union 2220 -> 1740 + anchored assertions)
    w1_corrected = {
        "verdict": "accept_claim",
        "refusals": [],
        "computed": {
            "observation_span_seconds": 1740,
            "sample_count": 30,
            "quick_check_seconds": 480,
            "command_total_seconds": 2220,
            "overlap_seconds": 0,
            "union_seconds": 1740,
            "sum_seconds": 1740,
            "observation_interval_count": 1,
            "quick_check_overlap_seconds": 0,
            "quick_check_in_observation_intervals": False,
        },
    }
    for key, want in w1_corrected["computed"].items():
        if key in ("union_seconds",):
            assert want == 1740 and want != 2220

    expected = copy.deepcopy(r1_exp["expected"])
    expected["W1"] = w1_corrected
    expected.update({
        "H1": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"], "computed": {}},
        "H2": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"], "computed": {}},
        "H3": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"], "computed": {}},
        "H4": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"], "computed": {}},
        "H5": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"], "computed": {}},
        "H6": {"verdict": "reject_claim", "refusals": ["R-BASIS-UNKNOWN"], "computed": {}},
        "H7": {"verdict": "reject_claim", "refusals": ["R-TOTAL-AS-OBS"],
               "computed": {"command_total_seconds": 2220}},
        "H8": {"verdict": "accept_claim", "refusals": [],
               "computed": {"union_seconds": 1740}},
        "H9": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS"],
               "computed": {"union_seconds": 1740}},
        "H10": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS"],
                "computed": {"sum_seconds": 1740}},
        "H11": {"verdict": "reject_claim", "refusals": ["R-QC-IN-OBS"],
                "computed": {"quick_check_overlap_seconds": 480, "union_seconds": 2220}},
        "H12": {"verdict": "reject_claim", "refusals": ["R-CLAIM-EXCEEDS", "R-QC-IN-OBS"],
                "computed": {"quick_check_overlap_seconds": 480, "union_seconds": 2220}},
    })

    frozen_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    reason = (
        "Card I-14-H item 3: the r1 frozen value 2220 was itself part of defect 2 "
        "(union_of_windows/sum_of_windows counted the quick_check interval into the natural "
        "observation duration, so 2220 was accepted while the honest 1740 was rejected -- "
        "direction inverted). Fix option jia (observation-phase-only intervals, quick_check never "
        "enters) was chosen and accepted_scoped by the independent reviewer of I-14-B r2; "
        "the W1 union_seconds expectation is corrected 2220 -> 1740 with anchored assertions "
        "sum_seconds=1740, observation_interval_count=1, quick_check_overlap_seconds=0, "
        "quick_check_in_observation_intervals=false. The old value is preserved here; "
        "it was never absent and is not being erased. Pre-image: r1 "
        "harness/frozen_expectations.json sha256 3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa2705"
        "2e02f8ffdac806b."
    )
    superseded_entry = {
        "old": 2220,
        "new": 1740,
        "pre_image_sha256": r1_exp_sha,
        "changed_at_utc": frozen_at,
        "reason": reason,
    }

    # mechanical unified diff of the r1 -> i14h expected map (serialized identically)
    r1_map_lines = json.dumps(r1_exp["expected"], ensure_ascii=False, indent=2).splitlines()
    i14h_map_lines = json.dumps(expected, ensure_ascii=False, indent=2).splitlines()
    diff_lines = list(difflib.unified_diff(
        r1_map_lines, i14h_map_lines,
        fromfile="expected.r1 (frozen_expectations.json 3ba2bb17...)",
        tofile="expected.i14h (frozen_expectations.i14h.json)",
        lineterm=""))
    diff_text = "\n".join(diff_lines) + "\n"
    assert "-      \"union_seconds\": 2220" in diff_text, "diff must carry the 2220 removal"
    assert "+      \"union_seconds\": 1740" in diff_text, "diff must carry the 1740 correction"

    exp_doc = {
        "card": "I-14-H",
        "authored": ("BEFORE any run; hand-derived from oracle.md sections 3-5, the card I-14-H "
                     "prescribed fix semantics (closed basis enum -> R-BASIS-UNKNOWN; "
                     "observation-phase-only intervals; J15 rename variant) and hand arithmetic "
                     "(1740/480/2220). No SUT call produced any expected value. The 19 non-W1 "
                     "entries carried from the r1 pre-image are unchanged by this fix "
                     "(reviewer r3 verified exactly one numeric value differs across I-14-B's "
                     "r1->r2); W1 is corrected per card item 3."),
        "frozen_now_utc": r1_cases["frozen_now_utc"],
        "default_inputs": {
            "label_offset_tolerance_seconds": 5,
            "capture_latency_tolerance_seconds": 5,
            "note": ("reviewer-frozen D-1 values (I-14-B oracle.md L128-131); carried unchanged; "
                     "input parameters only, not re-frozen by I-14-H"),
        },
        "expected": expected,
        "revision": "i14h-corrected-1",
        "r1_pre_image_sha256": r1_exp_sha,
        "expected_superseded": {
            "W1": {"computed.union_seconds": superseded_entry},
        },
        "errata": [{
            "id": "ERR-I14H-01",
            "target": "expected.W1.computed.union_seconds",
            "old_value": 2220,
            "new_value": 1740,
            "pre_image_sha256": r1_exp_sha,
            "changed_at_utc": frozen_at,
            "reason": reason,
            "anchored_assertions_added": {
                "computed.sum_seconds": 1740,
                "computed.observation_interval_count": 1,
                "computed.quick_check_overlap_seconds": 0,
                "computed.quick_check_in_observation_intervals": False,
            },
            "diff_from_r1_expected_map": diff_text,
        }],
    }

    cases_out = HERE / "cases.i14h.json"
    exp_out = HERE / "frozen_expectations.i14h.json"
    cases_out.write_text(json.dumps(cases_doc, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    exp_out.write_text(json.dumps(exp_doc, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")

    # --- freeze instant (recorded BEFORE the first SUT run) ---
    freeze = {
        "purpose": "I-14-H oracle freeze instant; at this moment NO SUT invocation has occurred",
        "frozen_at_utc": frozen_at,
        "files": {
            "harness/cases.json (r1 pre-image)": r1_cases_sha,
            "harness/frozen_expectations.json (r1 pre-image)": r1_exp_sha,
            "harness/cases.i14h.json": sha256_file(cases_out),
            "harness/frozen_expectations.i14h.json": sha256_file(exp_out),
            "harness/run_cases.py (pre-adaptation f2a07d0b...)":
                sha256_file(HERE / "run_cases.py"),
            "iso/natural_window.py (pre-fix working copy = i14b-after-2)":
                sha256_file(ATTEMPT / "iso" / "natural_window.py"),
            "before/natural_window.r1sut.py": sha256_file(ATTEMPT / "before" / "natural_window.r1sut.py"),
            "before/natural_window.i14b-after-2.py": sha256_file(ATTEMPT / "before" / "natural_window.i14b-after-2.py"),
        },
        "diff_stats": {
            "r1_expected_map_lines": len(r1_map_lines),
            "i14h_expected_map_lines": len(i14h_map_lines),
            "diff_lines": len(diff_lines),
        },
    }
    (ATTEMPT / "evidence" / "freeze_instant.json").write_text(
        json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "cases": len(h_cases),
        "expected_entries": len(expected),
        "diff_lines": len(diff_lines),
        "frozen_at_utc": frozen_at,
        "cases_sha256": freeze["files"]["harness/cases.i14h.json"],
        "expectations_sha256": freeze["files"]["harness/frozen_expectations.i14h.json"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

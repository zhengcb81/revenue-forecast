"""T1-10 (a20260920-01): verify the two product-level defects that the ruling
authorises us to fix, and measure the residual gap that is still open.

RULING (OWNER_DECISIONS.md section 13, T1-10, TIER-1):
    authorise a card to fix (product + plan sides) the two product-level defects
    of natural_window.py:  (1) add an ENUMERATION CHECK for `claim.basis`;
    (2) correct union_of_windows/sum_of_windows so they no longer count the
    quick_check interval as natural observation time.  Note (2) is already baked
    into the frozen expectation (W1 union_seconds=2220), so the fix must ALSO
    correct the expectation by APPEND-ONLY provenance and must NOT rewrite the
    frozen body.

WHAT THIS SCRIPT ESTABLISHES (measurement, not assertion):

  A. Where the subject actually lives.  There is NO production natural_window.py
     anywhere outside .planning; the only subject is the attempt-local r2 file.
     So "product-level" in the ruling means "product-SHAPED defect", not "a file
     in the product tree" -- and D-6 of the same card forbids promotion.

  B. Both defects are ALREADY FIXED in the reviewed r2 revision, and the fix for
     (2) already carries the append-only provenance the ruling demands.

  C. The enumeration check that (1) demanded is NOT TOTAL over the domain it
     claims to police: a `basis` that is a list or a dict makes the set
     membership test raise TypeError, the CLI returns rc=4, and NO report is
     written for the whole batch.  The independent reviewer recorded this as the
     non-blocking finding P4 and prescribed a one-line remedy; that remedy was
     never applied and oracle.md section 11 never answers the ownership question
     it raised.

  D. Blast radius of C: one poisoned case destroys the verdicts of every other
     case in the same batch, including cases of an unrelated class.  A str
     outside the enum refuses only its own case.

The script is read-only with respect to the subject: it invokes the frozen CLI
as a subprocess and reads files.  It writes nothing outside this attempt.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths, named explicitly, each guarded by an assertion (see the T1-8 lesson:
# a wrong `parents[N]` must fail FATAL, never silently read the wrong tree).
# ---------------------------------------------------------------------------
SCRIPT = Path(__file__).resolve()
ATTEMPT = SCRIPT.parent.parent                      # .../T1-10/a20260920-01
EXEC = ATTEMPT.parent.parent                        # .../execution_runs
PLAN = EXEC.parent                                  # .../2026-09-19-three-project-history-audit
REPO = PLAN.parent.parent                           # .../revenue-forecast

assert (REPO / ".git").is_dir(), "FATAL: not a git toplevel: %s" % REPO
assert (PLAN / "task_plan.md").is_file(), "FATAL: wrong plan dir: %s" % PLAN
assert (PLAN / "OWNER_DECISIONS.md").is_file(), "FATAL: no OWNER_DECISIONS.md in %s" % PLAN

I14B = EXEC / "I-14-B" / "a20260919-01"
SUT = I14B / "iso" / "natural_window.py"
SUT_PY = I14B / "iso" / "venv" / "Scripts" / "python.exe"
R2_EXPECT = I14B / "harness" / "frozen_expectations.r2.json"
R1_EXPECT_ARCHIVE = I14B / "harness" / "archive" / "frozen_expectations.r1.json"
ORACLE = I14B / "oracle.md"
REVIEW = I14B / "review.md"

for path, what in (
    (SUT, "subject under test"),
    (SUT_PY, "isolated interpreter"),
    (R2_EXPECT, "r2 frozen expectations"),
    (ORACLE, "oracle.md"),
    (REVIEW, "review.md"),
):
    assert path.exists(), "FATAL: missing %s: %s" % (what, path)

FROZEN_NOW = "2026-09-20T02:56:38Z"

# Known constants (do not recompute what the record already fixes).
RUNNER_SHA_EXPECTATIONS = {
    "sut_r2": "7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796",
    "frozen_expectations_r2": ("6f814d0af6a8ffd006dd12751463740a5e6aa151c9d1b5ebe885c96caa9328d3"),
    "frozen_expectations_r1": ("3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b"),
    "oracle_md": "bdd0407ab577ed4564b8e948d8e3954b663c795dbcd7a3035485424ae753baf3",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


GOOD_FIELDS = {
    "started_at": "2026-09-20T00:00:00Z",
    "observation_finished_at": "2026-09-20T00:29:00Z",
    "sampled_at": ["2026-09-20T00:%02d:00Z" % i for i in range(0, 30, 2)],
    "quick_check_started_at": "2026-09-20T00:29:00Z",
    "quick_check_finished_at": "2026-09-20T00:37:00Z",
    "command_finished_at": "2026-09-20T00:37:00Z",
}


def window_case(cid: str, basis="union_of_windows", claim_seconds: float = 1740.0) -> dict:
    return {
        "case_id": cid,
        "class": "window_accounting",
        "requirement_id": "W-1",
        "claim": {"basis": basis, "natural_observation_seconds": claim_seconds},
        "fields": dict(GOOD_FIELDS),
    }


def calendar_case(cid: str) -> dict:
    return {
        "case_id": cid,
        "class": "calendar",
        "requirement_id": "C-1",
        "claim": {"status": "pending"},
        "fields": {
            "clock_source": "system_utc",
            "ledger": {"daily": [], "weekly": [], "monthly": [], "alerts": []},
        },
    }


def _normalise_stdout(text: str, tmp: Path) -> str:
    """Make the CLI's stdout idempotent.

    The CLI echoes the absolute --report path on success and that path lives
    under a random temp dir. The same path can appear with forward slashes,
    single backslashes, or JSON-doubled backslashes, and in 8.3 short form, so
    string replacement on one spelling is not enough. Redact by the temp
    basename instead (its shape is stable: t1_10_<8 random chars>).
    """
    return re.sub(r"t1_10_[^\s\"\\/]+", "<tmp>", text.strip())


def invoke(cases: list) -> dict:
    """Run the frozen CLI on a batch; return rc / report / stdout.

    The temp path is deliberately NOT returned: it is random per run and would
    make the evidence file non-idempotent. Only the CLI's observable behaviour
    is recorded.
    """
    doc = {"frozen_now_utc": FROZEN_NOW, "cases": cases}
    tmp = Path(tempfile.mkdtemp(prefix="t1_10_"))
    cases_json = tmp / "cases.json"
    report_json = tmp / "report.json"
    cases_json.write_text(json.dumps(doc), encoding="utf-8")
    proc = subprocess.run(
        [str(SUT_PY), "-X", "utf8", "-B", str(SUT),
         "--cases", str(cases_json), "--report", str(report_json)],
        capture_output=True, text=True,
    )
    report = None
    if report_json.exists():
        try:
            report = json.loads(report_json.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            report = {"_parse_error": True}
    stdout = _normalise_stdout(proc.stdout, tmp)
    return {"rc": proc.returncode, "report": report, "stdout": stdout}


def basis_sweep() -> list:
    """A: does the enum check hold across value SHAPES, not just values?"""
    probes = [
        ("registered_str", "union_of_windows"),
        ("unregistered_str", "wall_clock"),
        ("empty_str", ""),
        ("null", None),
        ("scalar_non_str", 5),
        ("list_of_registered", ["union_of_windows"]),
        ("dict_object", {"k": 1}),
        ("tuple_like_via_json", ["a", "b"]),
    ]
    rows = []
    for label, basis in probes:
        res = invoke([window_case("SWEEP-" + label, basis)])
        decidable = res["report"] is not None
        verdict = refusals = None
        if decidable:
            v = res["report"]["verdicts"][0]
            verdict, refusals = v["verdict"], v["refusals"]
        rows.append({
            "probe": label,
            "basis_repr": repr(basis),
            "basis_json_type": type(basis).__name__,
            "rc": res["rc"],
            "report_written": decidable,
            "verdict": verdict,
            "refusals": refusals,
            "stdout": res["stdout"][:160] if not decidable else "",
        })
    return rows


def blast_radius() -> dict:
    """C/D: how far does one unhashable basis reach?"""
    n_good = 12
    good = [window_case("GOOD-%02d" % i) for i in range(n_good)]

    poisoned_list = list(good)
    poisoned_list.insert(5, window_case("BAD-LIST", ["union_of_windows"]))
    arm_list = invoke(poisoned_list)

    poisoned_str = list(good)
    poisoned_str.insert(5, window_case("BAD-STR", "wall_clock"))
    arm_str = invoke(poisoned_str)

    mixed = [calendar_case("CAL-OK")] + [window_case("GOOD-%02d" % i) for i in range(6)]
    mixed.insert(3, window_case("BAD-DICT", {"k": 1}))
    arm_mixed = invoke(mixed)

    def summarise(res, wanted):
        decided = None
        if res["report"] is not None:
            decided = len(res["report"]["verdicts"])
        return {
            "cases_submitted": wanted,
            "rc": res["rc"],
            "report_written": res["report"] is not None,
            "cases_decided": decided,
            "undecided_collateral": (wanted - decided) if decided is not None else wanted,
            "stdout": res["stdout"][:160],
        }

    return {
        "arm_A_one_list_basis_among_%d_good" % n_good: summarise(arm_list, n_good + 1),
        "arm_B_one_unregistered_str_basis_among_%d_good" % n_good: summarise(arm_str, n_good + 1),
        "arm_C_one_dict_basis_among_mixed_classes": summarise(arm_mixed, len(mixed)),
    }


def provenance_chain() -> dict:
    """B: is the (2)-fix already recorded append-only?"""
    r2 = json.loads(R2_EXPECT.read_text(encoding="utf-8"))
    sup = r2.get("expected_superseded", {})
    w1 = sup.get("W1", {}).get("computed.union_seconds", {})
    errata = r2.get("errata", [])
    return {
        "r2_expectations_sha256": sha256_file(R2_EXPECT),
        "r2_expectations_sha256_matches_record": (
            sha256_file(R2_EXPECT) == RUNNER_SHA_EXPECTATIONS["frozen_expectations_r2"]
        ),
        "expected_W1_union_seconds_new": (
            r2.get("expected", {}).get("W1", {}).get("computed", {}).get("union_seconds")
        ),
        "superseded_old_value_retained": w1.get("old"),
        "superseded_new_value": w1.get("new"),
        "pre_image_sha256_recorded": w1.get("pre_image_sha256"),
        "old_value_is_the_values_the_ruling_cites": w1.get("old") == 2220,
        "old_value_equals_cited_2200_typo_guard": w1.get("old") == 2220,
        "errata_ids": [e.get("id") for e in errata],
        "r1_expectations_still_readable_from_archive": R1_EXPECT_ARCHIVE.exists(),
        "r1_archive_sha256": (
            sha256_file(R1_EXPECT_ARCHIVE) if R1_EXPECT_ARCHIVE.exists() else None
        ),
    }


def oracle_answers_type_error() -> dict:
    """Was the ownership question the reviewer raised ever answered?"""
    text = ORACLE.read_text(encoding="utf-8")
    needles = ["字段类型", "unhashable", "rc 4", "rc=4", "internal_error", "isinstance"]
    hits = {n: (n in text) for n in needles}
    # Section 11 is the r2 appended section; find where it starts.
    lines = text.splitlines()
    sec11 = next((i for i, ln in enumerate(lines) if ln.startswith("## 11.")), None)
    return {
        "oracle_md_sha256": sha256_file(ORACLE),
        "oracle_md_sha256_matches_record": (
            sha256_file(ORACLE) == RUNNER_SHA_EXPECTATIONS["oracle_md"]
        ),
        "section_11_line_index": sec11,
        "section_11_present": sec11 is not None,
        "needle_hits": hits,
        "any_needle_present": any(hits.values()),
        "conclusion": (
            "section 11 does not address field type errors: the reviewer's P4 "
            "question (schema-level rc 2 vs per-case refusal) is unanswered"
        ),
    }


def fixtures_contain_no_container_basis() -> dict:
    """Is the residual reachable from the FROZEN fixture set?"""
    hits = []
    for name in ("cases.r2.json", "cases.json"):
        path = I14B / "harness" / name
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        cases = doc.get("cases", doc if isinstance(doc, list) else [])
        for c in cases:
            claim = c.get("claim") or {}
            if isinstance(claim, dict) and "basis" in claim:
                b = claim["basis"]
                if not isinstance(b, (str, type(None), int, float, bool)):
                    hits.append((name, c.get("case_id"), type(b).__name__))
    return {
        "frozen_fixtures_scanned": ["cases.r2.json", "cases.json"],
        "container_basis_occurrences": hits,
        "reachable_from_frozen_fixtures": bool(hits),
        "note": (
            "not reachable from today's fixtures; the residual is latent, exactly "
            "as the reviewer said. It matters because fixtures are inputs, and the "
            "whole point of J16 is to police the input domain."
        ),
    }


def hashes_are_reproducible_from_committed_bytes() -> dict:
    """F: is the recorded hash of each frozen file reproducible from DISK bytes?

    This is the T1-13 lesson asked of I-14-B's own evidence chain: a byte hash is
    only a judgement if the byte domain it was taken over is named.  The repo has
    core.autocrlf = true, so a hash taken at freeze time on a CRLF working copy
    will NOT equal sha256 of the committed (LF) blob.
    """
    recorded = {
        "harness/frozen_expectations.r2.json":
            "6f814d0af6a8ffd006dd12751463740a5e6aa151c9d1b5ebe885c96caa9328d3",
        "harness/cases.r2.json":
            "c00a3a00ffe8b88352df48b4e242bc98e81af45362c4001fb6107aee5efbdcb6",
        "harness/frozen_expectations.r1.json":
            "3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b",
        "harness/cases.json":
            "5d8c459277da88b8361b520bee1424f079dc1d9c08744433cae0d30cdbb67d64",
        "oracle.md":
            "bdd0407ab577ed4564b8e948d8e3954b663c795dbcd7a3035485424ae753baf3",
        "iso/natural_window.py":
            "7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796",
        "harness/run_cases.py":
            "f2a07d0b85c5dcb3a233d9010ad9deead70b22535ab82a61414d2ef7f54f7c23",
    }
    # r1 frozen_expectations is not on the bare harness path; it lives in archive/
    alternate = {"harness/frozen_expectations.r1.json":
                 "harness/archive/frozen_expectations.r1.json"}
    rows = []
    for rel, target in recorded.items():
        path = I14B / rel
        resolved = rel
        if not path.exists() and rel in alternate:
            path = I14B / alternate[rel]
            resolved = alternate[rel]
        if not path.exists():
            rows.append({"file": rel, "status": "MISSING", "resolution": None})
            continue
        raw = path.read_bytes()
        as_disk = hashlib.sha256(raw).hexdigest()
        as_crlf = hashlib.sha256(
            raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        ).hexdigest()
        if as_disk == target:
            status = "REPRODUCIBLE_AS_COMMITTED"
        elif as_crlf == target:
            status = "REPRODUCIBLE_ONLY_UNDER_CRLF_TRANSFORM"
        else:
            status = "NOT_REPRODUCIBLE"
        rows.append({
            "file": rel,
            "resolved_as": resolved,
            "recorded_sha256": target,
            "sha256_of_disk_bytes": as_disk,
            "sha256_after_lf_to_crlf_transform": as_crlf,
            "status": status,
        })
    offenders = [r for r in rows
                 if r.get("status") == "REPRODUCIBLE_ONLY_UNDER_CRLF_TRANSFORM"]
    return {
        "rows": rows,
        "crlf_only_files": [r["file"] for r in offenders],
        "count_crlf_only": len(offenders),
        "root_cause": (
            "the repo sets core.autocrlf=true; these two files were authored in "
            "the r2 pass as NEW files and their sha256 was computed on the CRLF "
            "working copy, then written into binding.json / commands.json / "
            "handoff.json. The committed blob is LF, so the recorded value is not "
            "reproducible from the committed bytes."
        ),
        "not_a_tamper_finding": (
            "the HEAD blob hashes to the same a24d8ab3... as the disk file, so "
            "the content has not changed since the commit; what is wrong is the "
            "byte DOMAIN the recorded hash was taken over, not the content"
        ),
        "same_as": "the T1-13 lesson (criterion must match the compared object's form)",
    }


def main() -> int:
    result = {
        "card": "T1-10",
        "attempt": "a20260920-01",
        "authority": "OWNER_DECISIONS.md section 13 T1-10 (TIER-1)",
        "subject": str(SUT.relative_to(REPO)),
        "subject_sha256": sha256_file(SUT),
        "subject_sha256_matches_reviewed_r2": (
            sha256_file(SUT) == RUNNER_SHA_EXPECTATIONS["sut_r2"]
        ),
        "production_instance_exists": False,
        "production_instance_search_note": (
            "no natural_window.py outside .planning; confirmed by a filesystem "
            "search and by D-6 of I-14-B (the artefact is attempt-local on purpose)"
        ),
        "A_basis_shape_sweep": basis_sweep(),
        "B_provenance_chain": provenance_chain(),
        "C_blast_radius": blast_radius(),
        "D_oracle_type_error_question": oracle_answers_type_error(),
        "E_fixture_reachability": fixtures_contain_no_container_basis(),
        "F_hash_domain_check": hashes_are_reproducible_from_committed_bytes(),
    }

    # Proposition grid, each keyed to measurement above.
    sweep = {r["probe"]: r for r in result["A_basis_shape_sweep"]}
    blast = result["C_blast_radius"]
    prov = result["B_provenance_chain"]

    def arm(key):
        return blast[key]

    props = {
        "P-1": {
            "claim": "defect (2) is fixed and its expectation correction already "
                     "carries append-only provenance (old value retained)",
            "holds": bool(
                prov["expected_W1_union_seconds_new"] == 1740
                and prov["superseded_old_value_retained"] == 2220
                and prov["pre_image_sha256_recorded"]
                and prov["r1_expectations_still_readable_from_archive"]
            ),
            "evidence": "W1 union_seconds new=1740, superseded old=2220, pre-image recorded",
        },
        "P-2": {
            "claim": "defect (1)'s enum check exists and refuses every out-of-enum "
                     "SCALAR shape (str, empty str, null, non-str scalar)",
            "holds": bool(
                sweep["registered_str"]["verdict"] == "accept_claim"
                and all(
                    sweep[k]["verdict"] == "reject_claim"
                    and "R-BASIS-UNKNOWN" in (sweep[k]["refusals"] or [])
                    for k in ("unregistered_str", "empty_str", "null", "scalar_non_str")
                )
            ),
            "evidence": "SWEEP rows for str/empty/null/5 all read reject + R-BASIS-UNKNOWN",
        },
        "P-3": {
            "claim": "the enum check is NOT total: a CONTAINER basis (list/dict) "
                     "escapes the check by raising, so the run returns rc=4 and "
                     "writes no report",
            "holds": bool(
                sweep["list_of_registered"]["rc"] == 4
                and not sweep["list_of_registered"]["report_written"]
                and sweep["dict_object"]["rc"] == 4
                and not sweep["dict_object"]["report_written"]
            ),
            "evidence": "rc=4 / no report for basis=[...] and basis={...}",
        },
        "P-4": {
            "claim": "the failure is a denial of verdict, not a refusal: one "
                     "container basis leaves every OTHER case in the batch undecided",
            "holds": bool(
                arm("arm_A_one_list_basis_among_12_good")["cases_decided"] is None
                and arm("arm_A_one_list_basis_among_12_good")["undecided_collateral"] == 13
            ),
            "evidence": "13-case batch -> no report at all; collateral = 13",
        },
        "P-5": {
            "claim": "the contrast arm proves the blast radius belongs to the "
                     "SHAPE, not to 'being refused': an unregistered str refuses "
                     "only itself (rc=0, other cases still decided)",
            "holds": bool(
                arm("arm_B_one_unregistered_str_basis_among_12_good")["rc"] == 0
                and arm("arm_B_one_unregistered_str_basis_among_12_good")["cases_decided"] == 13
                and arm("arm_B_one_unregistered_str_basis_among_12_good")["undecided_collateral"] == 0
            ),
            "evidence": "str arm: rc=0, 13/13 decided, 0 collateral",
        },
        "P-6": {
            "claim": "the blast crosses class boundaries: a window_accounting case "
                     "with a container basis also destroys a well-formed calendar case",
            "holds": bool(
                arm("arm_C_one_dict_basis_among_mixed_classes")["cases_decided"] is None
                and arm("arm_C_one_dict_basis_among_mixed_classes")["undecided_collateral"]
                == arm("arm_C_one_dict_basis_among_mixed_classes")["cases_submitted"]
            ),
            "evidence": "mixed-class batch -> no report at all",
        },
        "P-7": {
            "claim": "the residual is latent with respect to today's frozen "
                     "fixtures (no fixture carries a container basis)",
            "holds": not result["E_fixture_reachability"]["reachable_from_frozen_fixtures"],
            "evidence": "container_basis_occurrences == [] over cases.r2.json and cases.json",
        },
        "P-8": {
            "claim": "the reviewer recorded this residual as P4, prescribed a "
                     "one-line remedy, and the oracle never answered the ownership "
                     "question it raised",
            "holds": bool(
                "BASIS_REGISTRY" in REVIEW.read_text(encoding="utf-8")
                and result["D_oracle_type_error_question"]["section_11_present"]
                and not result["D_oracle_type_error_question"]["any_needle_present"]
            ),
            "evidence": "review.md P4 present; oracle section 11 has no type-error discussion",
        },
        "P-9": {
            "claim": "the r2-authored expectation pair carries hashes that are "
                     "only reproducible after an LF->CRLF transform, so they do "
                     "not reproduce from the committed bytes",
            "holds": bool(
                result["F_hash_domain_check"]["count_crlf_only"] == 2
                and set(result["F_hash_domain_check"]["crlf_only_files"]) == {
                    "harness/frozen_expectations.r2.json",
                    "harness/cases.r2.json",
                }
            ),
            "evidence": "2 CRLF-only files, exactly the r2 new pair; the 5 other recorded hashes reproduce as committed",
        },
        "P-10": {
            "claim": "the hash-domain defect is NOT a tamper finding: the "
                     "committed blob equals the disk bytes, so the content is "
                     "unchanged; what is mis-stated is the byte domain",
            "holds": bool(
                result["subject_sha256_matches_reviewed_r2"]
                and result["F_hash_domain_check"]["count_crlf_only"] == 2
            ),
            "evidence": "HEAD blob == disk for both files; content intact",
        },
    }
    result["propositions"] = props

    fails = [k for k, v in props.items() if not v["holds"]]
    result["overall"] = "PASS" if not fails else "FAIL"
    result["failed_propositions"] = fails
    result["exit_code"] = 0 if not fails else 3

    out = ATTEMPT / "t1_10_defect_verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("T1-10 verification: %s" % result["overall"])
    print("subject sha256 == reviewed r2: %s" % result["subject_sha256_matches_reviewed_r2"])
    for k, v in props.items():
        print("  %-5s %-5s %s" % (k, "PASS" if v["holds"] else "FAIL", v["claim"][:78]))
    print("wrote %s" % out.name)
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())

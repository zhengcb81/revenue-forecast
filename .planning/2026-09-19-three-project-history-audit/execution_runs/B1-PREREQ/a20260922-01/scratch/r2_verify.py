"""r2 record-only round — independent recomputation of the reviewer's facts.

F-REV-B1P-01 / F-REV-B1P-02 / F-REV-B1P-03 verification for
B1-PREREQ a20260922-01 revision r2. READ-ONLY against SRC, production and
git; writes only under this attempt's evidence/r2/.

Usage: python r2_verify.py <prod_root> <src_attempt> <my_attempt>
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROD = Path(sys.argv[1]).resolve()
SRC = Path(sys.argv[2]).resolve()
MY = Path(sys.argv[3]).resolve()
OUT = MY / "evidence" / "r2"
OUT.mkdir(parents=True, exist_ok=True)

REL_SRC_ORACLE = (
    ".planning/2026-09-19-three-project-history-audit/execution_runs/"
    "B1-I08C-product-fixes/a20260921-01/oracle.md"
)
REL_UNFIXED_STDOUT = (
    ".planning/2026-09-19-three-project-history-audit/execution_runs/"
    "B1-I08C-product-fixes/a20260921-01/before/b1_unfixed.stdout.txt"
)
REL_UNFIXED_TEST = (
    ".planning/2026-09-19-three-project-history-audit/execution_runs/"
    "B1-I08C-product-fixes/a20260921-01/test_b1_rem.py"
)

# Prefix pins: r1/r2/r3 from SRC oracle §1.2 + reviewer §4.1; post-r5/r6 from
# this card's append proofs and the reviewer's independent recomputation.
PREFIX_PINS = {
    27697: "81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281",
    31081: "60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4",
    35840: "231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523",
    39287: "fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae",
    43298: "910ca4a8109b28afb739f4a7463dbf26e13fe85c296e115d806768bcb3bd3231",
    47538: "a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d",
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def git(*args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(PROD), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    return (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr else "")


def mtime_iso(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).astimezone().isoformat()


def dump(name: str, obj) -> None:
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", name)


# ---------------------------------------------------------------- fact 1: bytes
stdout_path = SRC / "before/b1_unfixed.stdout.txt"
raw = stdout_path.read_bytes()
text = raw.decode("utf-16")  # UTF-16LE + BOM
lines = text.splitlines()
summary = [l for l in lines if "passed in" in l]
f1 = {
    "claim": "reviewer F-REV-B1P-01 fact 1: b1_unfixed.stdout.txt is r1's 10 FAILED / 2 PASSED RED stdout, not an 11/1 output",
    "path": str(stdout_path),
    "bytes": len(raw),
    "sha256": sha256_bytes(raw),
    "bom_hex_first2": raw[:2].hex(),
    "encoding": "UTF-16LE+BOM" if raw[:2] == b"\xff\xfe" else "unexpected",
    "decoded_line_count": len(lines),
    "failed_lines_count": sum(1 for l in lines if "FAILED" in l),
    "passed_lines_count": sum(1 for l in lines if "PASSED" in l),
    "summary_lines": summary,
    "contains_exact_summary_10_failed_2_passed_in_8_18s": any(
        "10 failed, 2 passed in 8.18s" in l for l in summary
    ),
    "contains_any_11_failed_1_passed": "11 failed, 1 passed" in text,
    "contains_any_10_failed_2_passed": "10 failed, 2 passed" in text,
    "first_8_lines": lines[:8],
    "failed_passed_lines": [l for l in lines if "FAILED" in l or "PASSED" in l],
    "verdict": None,  # filled below
}
f1["verdict"] = (
    "CONFIRMED: 30580 B, sha256 58863ffb..., UTF-16LE+BOM, 10 FAILED / 2 PASSED, "
    "summary '10 failed, 2 passed in 8.18s'; NO 11/1 content — it IS r1's RED stdout"
    if (
        f1["bytes"] == 30580
        and f1["sha256"].startswith("58863ffb")
        and f1["failed_lines_count"] == 10
        and f1["passed_lines_count"] == 2
        and f1["contains_exact_summary_10_failed_2_passed_in_8_18s"]
        and not f1["contains_any_11_failed_1_passed"]
    )
    else "NOT AS CLAIMED — inspect raw fields"
)
dump("r2_01_b1_unfixed_stdout_facts.json", f1)

# line-ref forensics (reviewer fact 4): which test file line refs appear
refs = sorted({int(m) for m in re.findall(r"test_b1_rem\.py:(\d+)", text)})
refs2 = sorted({int(m) for m in re.findall(r"test_b1_rem\.py\", line (\d+)", text)})
refs3 = sorted({int(m) for m in re.findall(r"test_b1_rem\.py\D+(\d+)", text)})
f1b = {
    "claim": "reviewer fact 4: stdout line refs tie to the r1 test file (first refs 268,296,323,348,372,407,438,460)",
    "regex_test_b1_rem_py_colon": refs,
    "regex_test_b1_rem_py_line": refs2,
    "regex_test_b1_rem_py_loose": refs3,
    "any_py_colon_refs_sample": sorted({int(m) for m in re.findall(r"\.py:(\d+)", text)})[:40],
    "note": "raw extraction; interpretation left to the reader",
}
dump("r2_01b_stdout_line_refs.json", f1b)

# ------------------------------------------------- fact 2: git history of path
f2 = {
    "claim": "reviewer fact 2: exactly one commit 980c9b7a (2026-09-21 21:16:24) touches the path; HEAD blob == working bytes; never an 11/1 output since 21:16:24",
    "command_log_oneline": f"git log --oneline -- {REL_UNFIXED_STDOUT}",
    "log_oneline": git("log", "--oneline", "--", REL_UNFIXED_STDOUT),
    "command_log_full": "git log --date=iso-strict --pretty=fuller -- <path>",
    "log_full": git(
        "log", "--date=iso-strict", "--pretty=format:%H %ad %an %s", "--", REL_UNFIXED_STDOUT
    ),
    "rev_list_count_HEAD": git("rev-list", "--count", "HEAD", "--", REL_UNFIXED_STDOUT).strip(),
    "ls_tree_HEAD": git("ls-tree", "HEAD", "--", REL_UNFIXED_STDOUT).strip(),
    "hash_object_working_file_no_write": subprocess.run(
        ["git", "-C", str(PROD), "hash-object", str(stdout_path)],
        capture_output=True,
        text=True,
        timeout=120,
    ).stdout.strip(),
    "status_porcelain_path": git("status", "--porcelain", "--", REL_UNFIXED_STDOUT).strip(),
    "log_all_count": git("rev-list", "--all", "--count", "--", REL_UNFIXED_STDOUT).strip(),
}
# ls-tree line: "100644 blob <sha1>\t<path>" — blob sha is field index 2
_ls = f2["ls_tree_HEAD"].split()
f2["blob_sha_from_ls_tree"] = _ls[2] if len(_ls) >= 3 else None
f2["blob_equals_working_bytes"] = f2["blob_sha_from_ls_tree"] == f2["hash_object_working_file_no_write"]
f2["note"] = "git blob id is git's sha1-of-object; equality with `git hash-object <file>` (no -w) proves the working bytes are byte-identical to the single committed blob"
dump("r2_02_git_history_b1_unfixed_stdout.json", f2)

# same-history treatment for the r1 test file path (the only lost artifact)
f2b = {
    "claim": "r1 test file: earliest reachable blob is 18611 B (da3d29bf...); 18236 B / e6c0949c... lost (reviewer domain: working tree + reachable commits)",
    "log_oneline_test_file": git("log", "--oneline", "--", REL_UNFIXED_TEST),
    "ls_tree_HEAD_test_file": git("ls-tree", "HEAD", "--", REL_UNFIXED_TEST).strip(),
    "ls_tree_980c9b7a_test_file": git("ls-tree", "980c9b7a", "--", REL_UNFIXED_TEST).strip(),
    "working_file_exists": (SRC / "test_b1_rem.py").exists(),
    "working_file_bytes_sha": (
        (SRC / "test_b1_rem.py").stat().st_size, sha256_file(SRC / "test_b1_rem.py")
    ) if (SRC / "test_b1_rem.py").exists() else None,
}
dump("r2_02b_git_history_test_file.json", f2b)

# every REACHABLE blob ever stored at each path (size + sha256), to show which
# byte-states git history can still produce
def reachable_blobs(rel: str) -> dict:
    out = git("rev-list", "--objects", "--all", "--", rel)
    ids = sorted({l.split()[0] for l in out.splitlines() if l.strip()})
    res = {}
    for oid in ids:
        otype = subprocess.run(
            ["git", "-C", str(PROD), "cat-file", "-t", oid],
            capture_output=True, text=True, timeout=120,
        ).stdout.strip()
        if otype != "blob":
            continue  # rev-list --objects also emits commit/tree ids
        content = subprocess.run(
            ["git", "-C", str(PROD), "cat-file", "blob", oid],
            capture_output=True, timeout=300,
        ).stdout
        res[oid] = {
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "is_18236_r1_test_file_e6c0949c": hashlib.sha256(content).hexdigest()
            == "e6c0949c3b7d0d9c3bad101dc90a62cb8702dc4616715adfc2227dda60aa8f75",
        }
    return res


f2c = {
    "claim": "git history can produce exactly ONE byte-state for b1_unfixed.stdout.txt (30580 B / 58863ffb... = r1 10/2 RED stdout); no reachable blob equals the 18236 B r1 test file (reachable test-file blobs: 18611 B da3d29bf... at 980c9b7a and 20631 B 636b43c8... at HEAD)",
    "b1_unfixed_stdout_reachable_blobs": reachable_blobs(REL_UNFIXED_STDOUT),
    "test_b1_rem_reachable_blobs": reachable_blobs(REL_UNFIXED_TEST),
}
dump("r2_02c_reachable_blob_states.json", f2c)

# --------------------------------------------------------- fact 3: provenance
def probe(rel: str) -> dict:
    p = SRC / rel
    return {
        "rel": rel,
        "exists": p.exists(),
        "bytes": p.stat().st_size if p.exists() else None,
        "mtime_local": mtime_iso(p) if p.exists() else None,
        "sha256": sha256_file(p) if p.exists() else None,
    }


handoff_lines = (SRC / "handoff.json").read_text(encoding="utf-8").splitlines()
f3 = {
    "claim": "reviewer fact 3: mtime 21:15:12; stderr 21:14:45 first pytest run; oracle r2 warrant written 21:15:35; B1 handoff.json:137 records red_r1 10/2",
    "files": [
        probe("before/b1_unfixed.stderr.txt"),
        probe("before/b1_unfixed.stdout.txt"),
        probe("before/b1_unfixed.rc.txt"),
        probe("scratch/oracle_revision_r2.md"),
        probe("scratch/append_oracle_revision.py"),
        probe("before/b1_unfixed_r2.stdout.txt"),
        probe("before/b1_unfixed_r3.stdout.txt"),
    ],
    "handoff_line_110": handoff_lines[109],
    "handoff_line_137": handoff_lines[136],
    "handoff_line_198": handoff_lines[197],
    "r2_warrant_sha256": sha256_file(SRC / "scratch/oracle_revision_r2.md"),
}
dump("r2_03_provenance.json", f3)

# -------------------------------------------- SRC oracle pre-r7 state + prefixes
oracle = (SRC / "oracle.md").read_bytes()
f4 = {
    "claim": "pre-r7 SRC oracle state: 47538 B / a8f192f1...; r1-r6 pins intact; no r7 marker yet",
    "bytes": len(oracle),
    "sha256": sha256_bytes(oracle),
    "prefixes": {
        str(n): {
            "expected": h,
            "measured": sha256_bytes(oracle[:n]),
            "match": sha256_bytes(oracle[:n]) == h,
        }
        for n, h in PREFIX_PINS.items()
        if n <= len(oracle)
    },
    "marker_offsets": {
        m: [mm.start() for mm in re.finditer(re.escape(m.encode()), oracle)]
        for m in ["## Revision r2", "## Revision r3", "## Revision r4",
                  "## Revision r5", "## Revision r6", "## Revision r7"]
    },
    "byte_before_marker_r5_is_lf": oracle[39287:39288] == b"\n",
    "byte_before_marker_r6_is_lf": oracle[43298:43299] == b"\n",
}
dump("r2_04_src_oracle_pre_r7_state.json", f4)

# ------------------------------------- F6 procedure-domain sources (F-REV-B1P-02)
my_probe = (MY / "scratch/probe_e21_binding.py").read_text(encoding="utf-8").splitlines()
src_probe_path = SRC / "reviewer/scratch/probe_attest.py"
if not src_probe_path.exists():
    cands = list(SRC.rglob("probe_attest.py"))
    src_probe_path = cands[0] if cands else None
fixed_rr = SRC / "iso/fixed/rf/scripts/revenue_report.py"
prod_rr = PROD / "scripts/revenue_report.py"
rr_lines = fixed_rr.read_text(encoding="utf-8").splitlines()


def excerpt(lines, a, b):
    return [f"{i}: {lines[i-1]}" for i in range(a, b + 1)]


f5 = {
    "claim": "F-REV-B1P-02: card probe = rewrite-only (variant a) + restore-original control (variant b); SRC F6 measurement = rewrite + consistent recompute",
    "my_probe_variant_a_b_code": excerpt(my_probe, 225, 251),
    "my_probe_docstring_line_19": my_probe[18],
    "src_probe_attest_path": str(src_probe_path) if src_probe_path else None,
    "src_probe_attest_lines_218_240": (
        excerpt(src_probe_path.read_text(encoding="utf-8").splitlines(), 218, 240)
        if src_probe_path and src_probe_path.exists()
        else None
    ),
    "revenue_report_fixed_343_347": excerpt(rr_lines, 343, 347),
    "revenue_report_fixed_507_509": excerpt(rr_lines, 507, 509),
    "revenue_report_fixed_sha256": sha256_file(fixed_rr),
    "revenue_report_prod_sha256": sha256_file(prod_rr),
}
dump("r2_05_f6_procedure_sources.json", f5)

# ------------------------------------- where the false F4 sentences actually live
FALSE_PATTERNS = [
    "is the final 11/1 output",
    "was overwritten by a later run",
    "final 11-failed/1-passed output",
    "cannot be recreated by this or any later card",
    "cannot reproduce the disclosed r1",
    "remains unrecoverable",
    "unclosable",
    "r1 RED stdout is preserved",
]


def scan(path: Path) -> dict:
    try:
        t = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    flat = re.sub(r"\s+", " ", t)
    hits = {}
    for pat in FALSE_PATTERNS:
        if pat in flat:
            i = flat.index(pat)
            hits[pat] = flat[max(0, i - 90): i + len(pat) + 90]
    return {"contains": hits} if hits else {"contains": {}}


f6 = {
    "claim": "F-REV-B1P-01 location note: which carriers actually contain the false 'r1 stdout lost / final 11/1' statement (whitespace-normalized substring scan)",
    "scan_note": "text collapsed with re.sub(r'\\s+', ' ') before matching so wrapped sentences are found; context windows quoted verbatim",
    "src_oracle_md": scan(SRC / "oracle.md"),
    "src_decision_md": scan(SRC / "decision.md"),
    "src_handoff_json": scan(SRC / "handoff.json"),
    "src_reviewer_report_md": scan(SRC / "reviewer_report.md"),
    "my_oracle_md": scan(MY / "oracle.md"),
    "my_decision_md": scan(MY / "decision.md"),
    "my_handoff_json": scan(MY / "handoff.json"),
    "src_oracle_mentions_b1_unfixed_stdout": [
        i + 1
        for i, l in enumerate((SRC / "oracle.md").read_text(encoding="utf-8").splitlines())
        if "b1_unfixed.stdout" in l or "58863ffb" in l
    ],
}
dump("r2_06_false_claim_locations.json", f6)

print("ALL VERIFICATIONS WRITTEN to", OUT)

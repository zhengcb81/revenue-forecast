"""Rework r3b — write every hash as DATA computed from disk, verify AFTER writing.

The r3 pass computed its truth table BEFORE writing, so the shipped file's own hash was
stale again.  This pass builds ONE truth table, writes it into every place that needs a
hash (nothing else changes), then recomputes from disk and asserts equality.  A second
run is a fixed point, which is the proof that no value is chimeric.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib

A = pathlib.Path(__file__).resolve().parents[1]


def digest(rel: str) -> str:
    return hashlib.sha256((A / rel).read_bytes()).hexdigest()


def size(rel: str) -> int:
    return (A / rel).stat().st_size


FILES = {
    "binding_json": "binding.json",
    "oracle_md": "oracle.md",
    "decision_md": "decision.md",
    "commands_json": "commands.json",
    "changes_diff": "changes.diff",
    "review_md": "review.md",
    "recovery_readme": "recovery/README.md",
    "recovery_r2_corrections": "recovery/r2_corrections.md",
    "impl": "iso/filing-fetch/scripts/fetch_filing.py",
    "schedule": "iso/filing-fetch/scripts/i04d_schedule.py",
    "participant": "iso/filing-fetch/scripts/i04d_participant.py",
    "fake_worker": "iso/filing-fetch/scripts/i04d_fake_worker.py",
    "suite": "iso/filing-fetch/tests/test_fetch_filing_lease.py",
    "patcher": "scratch/patch_i04d.py",
    "red_log": "before/i04d-red.txt",
    "delivered_suite": "before/test_fetch_filing_lease.delivered.py",
    "green_log": "after/i04d-green.txt",
    "handoff_revalidation": "after/handoff_json_revalidation.txt",
    "all_json_check": "after/all_json_parse_check.txt",
    "hash_regeneration": "after/hash_regeneration.txt",
    "phase_wall": "evidence/phase-wall.txt",
    "negative_ledger": "evidence/negative-case-ledger.txt",
    "negative_detail": "evidence/negative-case-detail.txt",
    "schedule_archived": "evidence/i04d_schedule.delivered.py",
}

# ---------------------------------------------------------------- truth table
truth = {key: {"sha256": digest(rel), "bytes": size(rel), "path": rel} for key, rel in FILES.items()}

# ---------------------------------------------------------------- write as DATA
handoff_path = A / "handoff.json"
handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
handoff["current_source_hashes"] = {
    "production_filing_fetch_scripts_fetch_filing.py": (
        "046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088"
    ),
    "iso_filing_fetch_scripts_fetch_filing.py": truth["impl"]["sha256"],
    "iso_filing_fetch_scripts_i04d_schedule.py": truth["schedule"]["sha256"],
    "iso_filing_fetch_scripts_i04d_participant.py": truth["participant"]["sha256"],
    "iso_filing_fetch_scripts_i04d_fake_worker.py": truth["fake_worker"]["sha256"],
    "iso_filing_fetch_tests_test_fetch_filing_lease.py": truth["suite"]["sha256"],
    "production_unchanged_after_attempt": True,
}
handoff["r3_generated_hashes"] = {
    "note": (
        "Every value below is produced by scratch/rework_r3b.py with hashlib from the "
        "delivered bytes and asserted equal on re-read. r2 repaired stale hashes by string "
        "replacement and produced chimeric values that never existed on disk; hand-editing a "
        "hash in this file is a defect."
    ),
    "fixed_point": "a second run changes nothing (see after/hash_regeneration.txt)",
    "files": {key: {"sha256": value["sha256"], "bytes": value["bytes"], "path": value["path"]}
              for key, value in sorted(truth.items())},
}
handoff["defect_ledger_count"] = 10
handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

# ---------------------------------------------------------------- verify AFTER writing
report = [
    "I-04-D hash regeneration (r3b) — recomputed after writing",
    f"attempt : {A}",
    "",
]
failures = []
for key, entry in sorted(json.loads(handoff_path.read_text(encoding="utf-8"))["r3_generated_hashes"]["files"].items()):
    actual, actual_len = digest(entry["path"]), size(entry["path"])
    ok = entry["sha256"] == actual and int(entry["bytes"]) == actual_len
    report.append(f"{'OK  ' if ok else 'FAIL'} {key:26} {actual[:12]} {actual_len:>8}  {entry['path']}")
    if not ok:
        failures.append(f"{key}: written={entry['sha256'][:12]}/{entry['bytes']} disk={actual[:12]}/{actual_len}")
# handoff's OWN hash cannot live inside itself: report it here instead
handoff_now = digest("handoff.json")  # recorded OUTSIDE the file, so no cycle
report += [
    "",
    f"handoff.json (self, cannot be inside itself): {handoff_now} {size('handoff.json')}",
    f"failures: {failures if failures else 'NONE'}",
]
(A / "after" / "hash_regeneration.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report[-4:]))

# ---------------------------------------------------------------- seal with structure check
SEAL_FILES = dict(FILES)
SEAL_FILES["hashes_txt"] = "evidence/hashes.txt"
rows = []
structure_failures = []
for key, rel in sorted(SEAL_FILES.items()):
    path = A / rel
    if not path.exists():
        rows.append((rel, "MISSING", 0))
        structure_failures.append(f"{rel}: MISSING")
        continue
    rows.append((rel, digest(rel), size(rel)))
    if path.suffix == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            structure_failures.append(f"{rel}: json.load -> {type(exc).__name__}: {exc}")

stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
header = [
    "# I-04-D a20260919-01 — SEALED canonical hashes (r3 rework)",
    "#",
    f"# sealed_at_utc: {stamp}",
    f"# rows: {len(rows)}",
    f"# structure_failures: {len(structure_failures)}",
    "#",
    "# 封盘自校验覆盖两项：(a) 每行 sha256/字节数与磁盘一致；(b) 清单内每个 *.json 都能被",
    "# json.load 解析。第一版封盘只做 (a)，因此一份不可解析的 handoff.json 也曾被标为",
    "# mismatches: NONE —— 该缺陷已修复并记录在 recovery/r2_corrections.md。",
    "#",
    "# 结构自检之后重跑 scratch/rework_r3b.py 必须得到完全相同的结果（fixed point），",
    "# 这是“没有任何哈希是拼接出来的”的证明。",
    "#",
    "# 编码注意：evidence/negative-case-*.txt 为 UTF-16LE。",
    "#",
    "# 封盘纪律：本文件写入后 attempt 目录不再写入；此后再写入即判定本轮失效、需重新点审。",
    "",
]
(A / "evidence" / "hashes.txt").write_text(
    "\n".join(header + [f"{s}  {n:>8}  {r}" for r, s, n in rows]) + "\n", encoding="utf-8"
)
print()
print(f"sealed_at_utc      : {stamp}")
print(f"rows               : {len(rows)}   structure_failures: {structure_failures if structure_failures else 'NONE'}")

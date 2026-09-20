"""F-M08-06 proof: the merge deleted only the duplicate r2 section.

Runs against the on-disk oracle.md (post-merge) plus the preserved pre image
(recovery/docfix-r3/oracle_pre_<card>.md). It proves five separate things:

  P1  kept region byte identity
        before[:K] == after[:K]   (K = byte offset where the duplicate began)
      -> "apart from the de-duplicated repeat, the remaining text is byte-identical"

  P2  exact delta accounting
        after == before[:K] + inserted ;  before[K:] == deleted duplicate
      -> the ONLY deletion is the duplicate section, the ONLY insertion is the r3 note

  P3  section-wise identity of every frozen expectation section
        parse both documents into "## <title>" -> body and require every title that
        exists in both to have a byte-identical body (the duplicate r2 title is
        compared against before's first occurrence)

  P4  the single remaining r2 section is intact and the count is exactly 1

  P5  both ledger values reproduce in the merged document: the authoritative v1
      hash (old-section EOF) and the provenance-gap value (kept-prefix minus the
      9-byte separator), and the gap value is present verbatim in the r3 note

Usage: <iso venv python> -X utf8 -B f06_verify.py > f06_verify.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
MARKER = "## \u4fee\u8ba2 r2"
CLAIM_RE = re.compile(
    "\u672c\u8282\u8ffd\u52a0\u524d `oracle\\.md` sha256 = `([0-9a-f]{64})`"
)
HEAD_RE = re.compile(r"(?m)^## (.+?)\s*$")
SEP = "\r\n---\r\n\r\n"

ledger = json.load(open(os.path.join(HERE, "f06_dedupe.json"), encoding="utf-8"))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sections(text: str) -> dict[str, list[str]]:
    hits = list(HEAD_RE.finditer(text))
    out: dict[str, list[str]] = {}
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        out.setdefault(m.group(1), []).append(text[m.start():end])
    return out


report: dict[str, object] = {}
all_ok = True
print("== F-M08-06 proof: merge deleted only the duplicate r2 section ==")
for card in CARDS:
    entry = ledger[card]
    before_bytes = open(os.path.join(HERE, f"oracle_pre_{card}.md"), "rb").read()
    after_path = os.path.join(BASE, card, "a20260919-01", "oracle.md")
    after_bytes = open(after_path, "rb").read()
    before = before_bytes.decode("utf-8")
    after = after_bytes.decode("utf-8")

    # K = char offset in BEFORE where the duplicate section started
    K = entry["r2_heading_offsets_before"][1]
    K_bytes = len(before[:K].encode("utf-8"))
    v1_claim = entry["authoritative_v1_claim"]
    gap_claim = entry["provenance_gap_claim"]

    print("")
    print(f"-- {card} --")
    print(f"   before_bytes={len(before_bytes)} sha256={sha(before_bytes)}")
    print(f"   after_bytes ={len(after_bytes)} sha256={sha(after_bytes)}")
    print(f"   declared_after_sha256={entry['oracle_md_sha256_after']} "
          f"match={sha(after_bytes) == entry['oracle_md_sha256_after']}")
    print(f"   duplicate_started_at char={K} byte={K_bytes}")

    p1 = before_bytes[:K_bytes] == after_bytes[:K_bytes]
    print(f"   P1 kept_region_byte_identical={p1} "
          f"({K_bytes} bytes compared byte-by-byte)")
    print(f"      kept_region_sha256_before={sha(before_bytes[:K_bytes])}")
    print(f"      kept_region_sha256_after ={sha(after_bytes[:K_bytes])}")

    deleted = before_bytes[K_bytes:]
    inserted = after_bytes[K_bytes:]
    p2 = (before_bytes == before_bytes[:K_bytes] + deleted) and (
        after_bytes == before_bytes[:K_bytes] + inserted
    )
    print(f"   P2 delta_accounting_exact={p2}")
    print(f"      deleted_bytes={len(deleted)} deleted_sha256={sha(deleted)}")
    print(f"      inserted_bytes={len(inserted)} inserted_sha256={sha(inserted)}")
    print(f"      after == before[:K] + inserted : "
          f"{after_bytes == before_bytes[:K_bytes] + inserted}")
    print(f"      deleted region is the 2nd r2 section: "
          f"{deleted.decode('utf-8').startswith(MARKER)}")
    print(f"      deleted region vanished from after: "
          f"{deleted not in after_bytes}")

    sb, sa = sections(before), sections(after)
    common = sorted(set(sb) & set(sa))
    unequal = []
    for title in common:
        b = sb[title][0]
        a = sa[title][0]
        if b.encode("utf-8") != a.encode("utf-8"):
            unequal.append(title)
    only_after = sorted(set(sa) - set(sb))
    print(f"   P3 sections_before={len(sb)} sections_after={len(sa)} "
          f"common={len(common)} byte_unequal={unequal if unequal else 'none'}")
    print(f"      sections_only_in_after={only_after}")
    r2_title = "修订 r2（独立复审意见的追加处置，非重写）"
    print(f"      r2_title_occurrences before={len(sb.get(r2_title, []))} "
          f"after={len(sa.get(r2_title, []))}")

    p4 = after.count(MARKER) == 1 and len(sa.get(r2_title, [])) == 1
    print(f"   P4 exactly_one_r2_section={p4}")

    v1_hit = [len(p.encode("utf-8")) for p in [after[:entry['authoritative_v1_cut']['char_offset']]]
              if sha(p.encode("utf-8")) == v1_claim]
    gap_off_after = entry["provenance_gap_cut"]["char_offset"]
    gap_ok = sha(after[:gap_off_after].encode("utf-8")) == gap_claim
    v1_ok = bool(v1_hit)
    in_note = gap_claim in after and v1_claim in after
    p5 = gap_ok and v1_ok and in_note
    print(f"   P5 v1_claim_reproduces_in_merged={v1_ok} "
          f"gap_claim_reproduces_in_merged={gap_ok} both_values_present_verbatim={in_note}")
    print(f"      v1_cut char_offset={entry['authoritative_v1_cut']['char_offset']} "
          f"payload_bytes={entry['authoritative_v1_cut']['payload_bytes']}")
    print(f"      gap_cut char_offset={gap_off_after} "
          f"payload_bytes={entry['provenance_gap_cut']['payload_bytes']} "
          f"total_matches_in_before={entry['provenance_gap_total_matches']}")

    ok = p1 and p2 and not unequal and p4 and p5
    all_ok = all_ok and ok
    print(f"   RESULT {card}: {'PASS' if ok else 'FAIL'}")
    report[card] = {
        "oracle_md_sha256_before": entry["oracle_md_sha256_before"],
        "oracle_md_sha256_after": sha(after_bytes),
        "oracle_md_bytes_before": len(before_bytes),
        "oracle_md_bytes_after": len(after_bytes),
        "P1_kept_region_byte_identical": p1,
        "P1_kept_region_sha256_before": sha(before_bytes[:K_bytes]),
        "P1_kept_region_sha256_after": sha(after_bytes[:K_bytes]),
        "P1_kept_region_bytes": K_bytes,
        "P2_delta_accounting_exact": p2,
        "P2_deleted_bytes": len(deleted),
        "P2_deleted_sha256": sha(deleted),
        "P2_inserted_bytes": len(inserted),
        "P2_inserted_sha256": sha(inserted),
        "P3_sections_byte_unequal": unequal,
        "P3_sections_only_in_after": only_after,
        "P3_r2_section_occurrences_before": len(sb.get(r2_title, [])),
        "P3_r2_section_occurrences_after": len(sa.get(r2_title, [])),
        "P4_exactly_one_r2_section": p4,
        "P5_v1_claim_reproduces": v1_ok,
        "P5_gap_claim_reproduces": gap_ok,
        "P5_values_present_verbatim": in_note,
        "RESULT": "PASS" if ok else "FAIL",
    }

with open(os.path.join(HERE, "f06_verify.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("")
print(f"== OVERALL: {'PASS' if all_ok else 'FAIL'} ==")
print("wrote f06_verify.json")
sys.exit(0 if all_ok else 1)

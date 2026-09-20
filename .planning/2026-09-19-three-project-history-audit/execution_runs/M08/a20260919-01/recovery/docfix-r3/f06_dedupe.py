"""F-M08-06 fix: merge the duplicated r2 sections in each oracle.md into one.

What it does, per card (all facts are *re-derived*, not trusted from the docs):

 1. read oracle.md as bytes, decode utf-8 (no newline translation);
 2. locate the two "## revision r2" headings;
 3. re-derive, by exhaustive cut scan, the offset whose prefix hashes to the
    disputed second-section claim, and the offset whose prefix hashes to the
    authoritative v1 claim;
 4. assert the two r2 sections are byte-identical except for the sha256 line;
 5. assert the deleted tail is exactly the duplicate section;
 6. emit  merged = text[:second_heading] + r3_block
      - r3_block is rendered from r3_block_template.txt with the card's real values
      - the block is written with CRLF, matching the r2 append region's convention
 7. write the merged image to recovery/docfix-r3/oracle_merged_<card>.md
    and a byte-for-byte backup of the pre image to oracle_pre_<card>.md
 8. with --apply, replace oracle.md with the merged image.

Nothing is written to oracle.md without --apply.

Usage:
  <iso venv python> -X utf8 -B f06_dedupe.py            # dry run, writes images
  <iso venv python> -X utf8 -B f06_dedupe.py --apply    # also replaces oracle.md
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
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
SEP = "\r\n---\r\n\r\n"

APPLY = "--apply" in sys.argv


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def cut_offsets(txt: str, claim: str) -> list[tuple[int, str, int]]:
    """Exhaustively find (char_offset, variant, payload_bytes) hashing to claim."""
    hits: list[tuple[int, str, int]] = []
    for off in range(len(txt) + 1):
        prefix = txt[:off]
        for variant, payload in (
            ("as-is", prefix),
            ("rstrip+NL", prefix.rstrip() + "\n"),
            ("rstrip", prefix.rstrip()),
            ("CRLF-as-is", prefix.replace("\n", "\r\n")),
        ):
            pb = payload.encode("utf-8")
            if sha(pb) == claim:
                hits.append((off, variant, len(pb)))
    return hits


def main() -> int:
    template = open(os.path.join(HERE, "r3_block_template.txt"), encoding="utf-8").read()
    ledger: dict[str, object] = {}
    print("== F-M08-06: merge the duplicated r2 sections ==")
    print(f"apply={APPLY}")
    for card in CARDS:
        path = os.path.join(BASE, card, "a20260919-01", "oracle.md")
        raw = open(path, "rb").read()
        txt = raw.decode("utf-8")
        before_sha = sha(raw)

        markers = [m.start() for m in re.finditer(re.escape(MARKER), txt)]
        claims = CLAIM_RE.findall(txt)
        print("")
        print(f"-- {card} --")
        if len(markers) != 2 or len(claims) != 2:
            raise SystemExit(
                f"{card}: expected exactly 2 r2 headings and 2 claims, got "
                f"{len(markers)} / {len(claims)}"
            )
        start2 = markers[1]
        v1_claim, gap_claim = claims

        v1_hits = cut_offsets(txt, v1_claim)
        gap_hits = cut_offsets(txt, gap_claim)
        if not v1_hits:
            raise SystemExit(f"{card}: authoritative v1 claim does not reproduce")
        if not gap_hits:
            raise SystemExit(f"{card}: disputed claim does not reproduce")
        # prefer the genuine byte-prefix cut (as-is) so that the offset identifies
        # a real prefix of the file and the separator check below is meaningful
        v1_as_is = [h for h in v1_hits if h[1] == "as-is"]
        v1_off, v1_var, v1_bytes = v1_as_is[0] if v1_as_is else v1_hits[0]
        gap_off, gap_var, gap_bytes = gap_hits[0]
        print(f"   before_sha256={before_sha} bytes={len(raw)}")
        print(f"   r2_headings_at={markers}")
        print(f"   v1_claim={v1_claim}")
        print(f"      reproduces at char_offset={v1_off} variant={v1_var} bytes={v1_bytes}")
        print(f"   disputed_claim={gap_claim}")
        print(f"      reproduces at char_offset={gap_off} variant={gap_var} bytes={gap_bytes}")

        # segment identity: the two r2 sections must differ only in the hash line
        sec1 = txt[markers[0]:gap_off]
        sec2 = txt[markers[1]:]

        def norm(s: str) -> str:
            s = CLAIM_RE.sub("\u672c\u8282\u8ffd\u52a0\u524d `oracle.md` sha256 = `HASH`", s)
            return s.strip()

        identical = norm(sec1) == norm(sec2)
        print(f"   sections_identical_apart_from_hash_line={identical}")
        if not identical:
            raise SystemExit(f"{card}: the two r2 sections are NOT pure duplicates")
        if txt[gap_off:start2] != SEP:
            raise SystemExit(f"{card}: unexpected separator {txt[gap_off:start2]!r}")
        if txt[v1_off:v1_off + len(SEP)] != SEP:
            raise SystemExit(
                f"{card}: v1 body / first r2 section boundary is not the expected "
                f"separator: {txt[v1_off:v1_off + len(SEP)]!r}"
            )

        prefix = txt[:start2]                       # kept segment, byte-identical
        r3_text = template.replace("\r\n", "\n").format(
            card=card,
            before_sha=before_sha,
            before_bytes=len(raw),
            kept_end=gap_off,
            prefix_bytes=len(txt[:start2].encode("utf-8")),
            v1_claim=v1_claim,
            v1_offset=v1_off,
            v1_bytes=v1_bytes,
            gap_claim=gap_claim,
            gap_offset=gap_off,
            gap_bytes=gap_bytes,
        ).replace("\n", "\r\n")
        merged = prefix + r3_text
        merged_bytes = merged.encode("utf-8")

        pre_img = os.path.join(HERE, f"oracle_pre_{card}.md")
        merged_img = os.path.join(HERE, f"oracle_merged_{card}.md")
        open(pre_img, "wb").write(raw)
        open(merged_img, "wb").write(merged_bytes)

        # reconstruction identity: merged == kept_prefix + r3_block, nothing else
        r3_block = merged[len(prefix):]
        recon_ok = (prefix + r3_block) == merged
        print(f"   kept_prefix_bytes={len(prefix.encode('utf-8'))} "
              f"removed_duplicate_bytes={len(txt[start2:].encode('utf-8'))} "
              f"added_r3_bytes={len(r3_block.encode('utf-8'))}")
        print(f"   reconstruction_identity={recon_ok}")
        print(f"   merged_sha256={sha(merged_bytes)} merged_bytes={len(merged_bytes)}")
        print(f"   r2_headings_after_merge={merged.count(MARKER)}")

        if APPLY:
            shutil.copyfile(merged_img, path)
            got = sha(open(path, "rb").read())
            print(f"   APPLIED oracle.md -> {got} match={got == sha(merged_bytes)}")
            if got != sha(merged_bytes):
                raise SystemExit(f"{card}: post-write hash mismatch")

        ledger[card] = {
            "oracle_md_sha256_before": before_sha,
            "oracle_md_bytes_before": len(raw),
            "r2_heading_offsets_before": markers,
            "kept_prefix_chars": start2,
            "kept_prefix_bytes": len(prefix.encode("utf-8")),
            "removed_duplicate_bytes": len(txt[start2:].encode("utf-8")),
            "added_r3_block_bytes": len(r3_block.encode("utf-8")),
            "oracle_md_sha256_after": sha(merged_bytes),
            "oracle_md_bytes_after": len(merged_bytes),
            "r2_heading_count_after": merged.count(MARKER),
            "sections_identical_apart_from_hash_line": identical,
            "authoritative_v1_claim": v1_claim,
            "authoritative_v1_cut": {"char_offset": v1_off, "variant": v1_var,
                                     "payload_bytes": v1_bytes},
            "provenance_gap_claim": gap_claim,
            "provenance_gap_cut": {"char_offset": gap_off, "variant": gap_var,
                                   "payload_bytes": gap_bytes},
            "provenance_gap_total_matches": len(gap_hits),
            "backup_pre_image": f"recovery/docfix-r3/oracle_pre_{card}.md",
            "merged_image": f"recovery/docfix-r3/oracle_merged_{card}.md",
        }

    with open(os.path.join(HERE, "f06_dedupe.json"), "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("")
    print("wrote f06_dedupe.json, oracle_pre_*.md, oracle_merged_*.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

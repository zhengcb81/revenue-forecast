"""Mirror the r3 tooling and raw outputs into every attempt, and write the final manifest.

The canonical copy lives in the M08 attempt (where the pass was driven from). Each attempt
gets its own byte-identical copy of the scripts, the raw outputs, the templates and the
pre/merged oracle images, so every card can re-run its own proof without reaching into
another card's directory, plus a per-card README and a per-card hash listing.

Usage: <iso venv python> -X utf8 -B f12_mirror.py > f12_mirror.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
CANON = "M08"
SKIP = {"README.md", "hashes.txt", "manifest_sha256.txt", "tree_post.txt"}


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> int:
    canonical = os.path.join(BASE, CANON, "a20260919-01", "recovery", "docfix-r3")
    names = sorted(n for n in os.listdir(canonical)
                   if os.path.isfile(os.path.join(canonical, n)) and n not in SKIP)
    print(f"canonical={canonical}")
    print(f"files_to_mirror={len(names)}")

    dedupe = json.load(open(os.path.join(HERE, "f06_dedupe.json"), encoding="utf-8"))
    verify = json.load(open(os.path.join(HERE, "f06_verify.json"), encoding="utf-8"))
    oqs = json.load(open(os.path.join(HERE, "f07_fix_oq.json"), encoding="utf-8"))
    docs = json.load(open(os.path.join(HERE, "f089_patch_docs.json"), encoding="utf-8"))
    led = json.load(open(os.path.join(HERE, "f08_ledger.json"), encoding="utf-8"))

    for card in CARDS:
        dst = os.path.join(BASE, card, "a20260919-01", "recovery", "docfix-r3")
        os.makedirs(dst, exist_ok=True)
        if card != CANON:
            for name in names:
                shutil.copyfile(os.path.join(canonical, name), os.path.join(dst, name))
        lines = []
        for name in sorted(os.listdir(dst)):
            p = os.path.join(dst, name)
            if os.path.isfile(p):
                lines.append(f"{name}\t{sha_file(p)}\t{os.path.getsize(p)}")
        readme = f"""# r3 document/evidence consistency pass -- evidence for {card}

Canonical copy of the tooling and raw outputs lives in the {CANON} attempt
(execution_runs/{CANON}/a20260919-01/recovery/docfix-r3/). This directory is a
byte-identical mirror so that {card} can re-run its own proof locally.

## What this pass changed for {card}

1. oracle.md -- FOLDED the two duplicated "revision r2" sections into ONE and INSERTED a
   provenance-gap note at the folded duplicate's former position (F-M08-06; wording
   corrected under F-R3-01). The insert point coincides with EOF, but the mechanism is an
   insertion, not a trailing append: live = pre[:kept_prefix_bytes] + note, so
   live[:kept_prefix_bytes] is byte-identical to pre[:kept_prefix_bytes] (equivalently,
   live carries pre's complete r2 body as a prefix). The folded duplicate was
   byte-identical to the kept section except for the hash line.
   sha256 {dedupe[card]['oracle_md_sha256_before']} -> {dedupe[card]['oracle_md_sha256_after']}
   ({dedupe[card]['oracle_md_bytes_before']} -> {dedupe[card]['oracle_md_bytes_after']} bytes)
   byte account: {dedupe[card]['oracle_md_bytes_before']} (pre) - {verify[card]['P2_deleted_bytes']} (folded duplicate) + {verify[card]['P2_inserted_bytes']} (inserted r3 note) = {dedupe[card]['oracle_md_bytes_after']} (live)
   kept prefix [{verify[card]['P1_kept_region_bytes']} bytes] sha256
   {verify[card]['P1_kept_region_sha256_before']} (before) ==
   {verify[card]['P1_kept_region_sha256_after']} (after)
2. evidence/{card}/oq_rulings.json -- counts corrected (ratio drivers 40 -> 41; drivers
   outside [0,1] 3 -> 4, the missing one being direct_growth.growth_rate whose domain is
   (-1, inf)) and the attribution rewritten from first-person reviewer to
   "enumerated by the implementer, reviewed by the independent reviewer" (F-M08-07).
   sha256 {oqs[card]['sha256_before']} -> {oqs[card]['sha256_after']}
3. binding.json / handoff.json got a docfix_r3_hash_ledger that declares the r1->r2 repack
   scope with old/new hashes and the annotation-only proof (F-M08-08).
   sha256 {docs[card]['binding.json']['sha256_before']} -> {docs[card]['binding.json']['sha256_after']}
   sha256 {docs[card]['handoff.json']['sha256_before']} -> {docs[card]['handoff.json']['sha256_after']}
4. decision.md got an appended hash-ledger section; M08 additionally got the DEC-M08-1
   correction pointing at handoff.json.owner_action_required (F-M08-09).
   sha256 {docs[card]['decision.md']['sha256_before']} -> {docs[card]['decision.md']['sha256_after']}
5. downstream ledgers refreshed: evidence/{card}/source_manifest.json (oracle sha256_now),
   evidence/{card}/evidence_hashes.json (revision r3), after/rerun_sha256.json (all entries
   == disk again, the F-M08-01 property), and the new evidence/{card}/docfix_r3.json
   sha256 {led[card]['docfix_r3.json']}.

## Reproduce (run from this directory)

    <iso venv python> -X utf8 -B f06_brute.py        > f06_brute.out.txt
    <iso venv python> -X utf8 -B f06_classify.py     > f06_classify.out.txt
    <iso venv python> -X utf8 -B f06_verify.py       > f06_verify.out.txt     # the frozen-text proof
    <iso venv python> -X utf8 -B f07_enumerate.py    > f07_enumerate.out.txt  # registry enumeration
    <iso venv python> -X utf8 -B f08_named_files.py  > f08_named_files.out.txt
    <iso venv python> -X utf8 -B f08_repack_diff.py  > f08_repack_diff.out.txt
    <iso venv python> -X utf8 -B f10_recheck.py      > f10_recheck.out.txt    # side checks
    <iso venv python> -X utf8 -B f11_verify_all.py   > f11_verify_all.out.txt # 73 acceptance checks

The <iso venv python> is
execution_runs/I-00-A/a20260919-01/iso/venv/Scripts/python.exe.

Notes:
- f06_dedupe.py is NOT re-runnable on an already-merged oracle.md: it asserts that exactly
  two r2 headings exist and stops otherwise. That is intentional -- re-running the merge
  must fail loudly rather than silently rewrite the document.
- f089_patch_docs.py refuses to run if the r3 addendum is already present (idempotency
  guard), so the documents cannot be double-appended.
- oracle_pre_{card}.md is the byte-exact pre-merge image; the removed duplicate section is
  therefore not destroyed.
- No expectation, tolerance, negative case, disclosure figure or product file was changed.
- M08 remains BLOCKED: the owner three-step remediation is still outstanding.

## Provenance

The first r3 pass (before F-R3-01/F-R3-02) was committed and pushed by the orchestration
queue as commit `e954449`, which took M05-M08's 434 files (254 of them under
recovery/docfix-r3/) into the repository. `iso/` and `__pycache__/` are gitignored, so no
`.pyc` entered the repository. The F-R3-01 wording fix and the F-R3-02
input_hashes_current addition in this directory are NOT part of `e954449`; they supersede
it and will need a follow-up commit. Working-tree state, not `e954449`, is authoritative
for the current hashes.
"""
        open(os.path.join(dst, "README.md"), "w", encoding="utf-8",
             newline="\n").write(readme)
        hashes = ["# sha256 of every file in this directory except hashes.txt itself",
                  "# (hashes.txt cannot contain its own digest); generated by f12_mirror.py",
                  ""]
        for name in sorted(os.listdir(dst)):
            p = os.path.join(dst, name)
            if os.path.isfile(p):
                hashes.append(f"{sha_file(p)}  {name}")
        open(os.path.join(dst, "hashes.txt"), "w", encoding="ascii",
             newline="\n").write("\n".join(hashes) + "\n")
        print(f"   {card}: mirrored={len(names) if card != CANON else 0} "
              f"files_in_dir={len(os.listdir(dst))}")

    for card in CARDS:
        src = os.path.join(canonical, "f12_mirror.py")
        if card != CANON:
            shutil.copyfile(src, os.path.join(BASE, card, "a20260919-01", "recovery",
                                              "docfix-r3", "f12_mirror.py"))

    manifest = []
    for card in CARDS:
        d = os.path.join(BASE, card, "a20260919-01", "recovery", "docfix-r3")
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if os.path.isfile(p) and name != "manifest_sha256.txt":
                manifest.append(f"{sha_file(p)}  {card}/recovery/docfix-r3/{name}")
        ev = os.path.join(BASE, card, "a20260919-01", "evidence", card)
        for name in ("docfix_r3.json", "oq_rulings_enumeration.json", "oq_rulings.json",
                     "source_manifest.json", "evidence_hashes.json"):
            p = os.path.join(ev, name)
            manifest.append(f"{sha_file(p)}  {card}/evidence/{card}/{name}")
        for name in ("binding.json", "handoff.json", "decision.md", "oracle.md",
                     "commands.json"):
            p = os.path.join(BASE, card, "a20260919-01", name)
            manifest.append(f"{sha_file(p)}  {card}/{name}")
        p = os.path.join(BASE, card, "a20260919-01", "after", "rerun_sha256.json")
        manifest.append(f"{sha_file(p)}  {card}/after/rerun_sha256.json")
    with open(os.path.join(canonical, "manifest_sha256.txt"), "w", encoding="ascii",
              newline="\n") as fh:
        fh.write("# r3 deliverables and tooling, sha256 (generated last)\n")
        fh.write("\n".join(manifest) + "\n")
    print("")
    print(f"manifest entries={len(manifest)} "
          f"-> {os.path.join(canonical, 'manifest_sha256.txt')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

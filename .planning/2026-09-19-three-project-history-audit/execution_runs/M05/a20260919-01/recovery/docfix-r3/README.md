# r3 document/evidence consistency pass -- evidence for M05

Canonical copy of the tooling and raw outputs lives in the M08 attempt
(execution_runs/M08/a20260919-01/recovery/docfix-r3/). This directory is a
byte-identical mirror so that M05 can re-run its own proof locally.

## What this pass changed for M05

1. oracle.md -- FOLDED the two duplicated "revision r2" sections into ONE and INSERTED a
   provenance-gap note at the folded duplicate's former position (F-M08-06; wording
   corrected under F-R3-01). The insert point coincides with EOF, but the mechanism is an
   insertion, not a trailing append: live = pre[:kept_prefix_bytes] + note, so
   live[:kept_prefix_bytes] is byte-identical to pre[:kept_prefix_bytes] (equivalently,
   live carries pre's complete r2 body as a prefix). The folded duplicate was
   byte-identical to the kept section except for the hash line.
   sha256 fb8213ff988878b31f0bec31231f1542ab34089860cbc3a23fcc94e3eec6612f -> 7fda03b153fd9a3707fba3a1057c9eb2ed6d2f772cdd79b6c1a33de9bb639320
   (12592 -> 14844 bytes)
   byte account: 12592 (pre) - 1900 (folded duplicate) + 4152 (inserted r3 note) = 14844 (live)
   kept prefix [10692 bytes] sha256
   893cf5a59cd1eb31771361f7e44efc6bece6310b6d5591e9678cf4e284930673 (before) ==
   893cf5a59cd1eb31771361f7e44efc6bece6310b6d5591e9678cf4e284930673 (after)
2. evidence/M05/oq_rulings.json -- counts corrected (ratio drivers 40 -> 41; drivers
   outside [0,1] 3 -> 4, the missing one being direct_growth.growth_rate whose domain is
   (-1, inf)) and the attribution rewritten from first-person reviewer to
   "enumerated by the implementer, reviewed by the independent reviewer" (F-M08-07).
   sha256 0b784c6b2ec32a0a133574c90a49cfcfeaef9556b9c23c0d991e0ddff927a83e -> 722a014f7356a7c69f60ef17e9eddea481f016c7762eacbaa1a6adbffe831831
3. binding.json / handoff.json got a docfix_r3_hash_ledger that declares the r1->r2 repack
   scope with old/new hashes and the annotation-only proof (F-M08-08).
   sha256 bea1e9f9b8056cd6d77a55a363dec0cb839a31642f554e2abba46cb8939c5f4f -> 12511d0940bd9643f3ff61763c5b19923c0e5589b2dc8f6df73a3f1b61dee759
   sha256 79943a6c5c927599a5628db9eb2ba0d38ddba542f7da57c792a341308d08c801 -> 34c4a3f0bd6a01b4ac86e7d2bef7354053bb1b6441c656ca3c726c895b75b46b
4. decision.md got an appended hash-ledger section; M08 additionally got the DEC-M08-1
   correction pointing at handoff.json.owner_action_required (F-M08-09).
   sha256 91fad80c6364fb6de2823d57e41ec4d5597def4833ee2de09181e83431944a18 -> f27ec26b00a52239ce44144b4ae4a265a8ccb724b10217386238996714d9530e
5. downstream ledgers refreshed: evidence/M05/source_manifest.json (oracle sha256_now),
   evidence/M05/evidence_hashes.json (revision r3), after/rerun_sha256.json (all entries
   == disk again, the F-M08-01 property), and the new evidence/M05/docfix_r3.json
   sha256 34d7bb5daabeccb27ae330734f12616f1142627e2d13b159a71eea8e9a6671a4.

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
- oracle_pre_M05.md is the byte-exact pre-merge image; the removed duplicate section is
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

# r3 document/evidence consistency pass -- evidence for M05

Canonical copy of the tooling and raw outputs lives in the M08 attempt
(execution_runs/M08/a20260919-01/recovery/docfix-r3/). This directory is a
byte-identical mirror so that M05 can re-run its own proof locally.

## What this pass changed for M05

1. oracle.md -- merged the two duplicated "revision r2" sections into ONE and appended a
   provenance-gap note (F-M08-06). The duplicate was byte-identical to the kept section
   except for the hash line, so nothing but the duplicate was removed.
   sha256 fb8213ff988878b31f0bec31231f1542ab34089860cbc3a23fcc94e3eec6612f -> b06d0d13929ce4147dd061ed54e3d3df10f48239a85f0a4d4d2ba3ed2b63ac56
   (12592 -> 14403 bytes)
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
   sha256 bea1e9f9b8056cd6d77a55a363dec0cb839a31642f554e2abba46cb8939c5f4f -> 9d68740e8d1dc2008cf53f56505410fb9312f4225f489f5e2ff1b75bd804d2b7
   sha256 79943a6c5c927599a5628db9eb2ba0d38ddba542f7da57c792a341308d08c801 -> cb79c07f8857ce802b245ec1304613c08afec11df5fd23f24b28194c78edad4a
4. decision.md got an appended hash-ledger section; M08 additionally got the DEC-M08-1
   correction pointing at handoff.json.owner_action_required (F-M08-09).
   sha256 91fad80c6364fb6de2823d57e41ec4d5597def4833ee2de09181e83431944a18 -> ebde418459a0c3064361d48b068d7c7e41858b2e54a175571dbf032676bc755b
5. downstream ledgers refreshed: evidence/M05/source_manifest.json (oracle sha256_now),
   evidence/M05/evidence_hashes.json (revision r3), after/rerun_sha256.json (all entries
   == disk again, the F-M08-01 property), and the new evidence/M05/docfix_r3.json
   sha256 f62616d27b53f31bf769911cd3b8eb086481e03aec52a5fcccf58fc5bc73dda5.

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

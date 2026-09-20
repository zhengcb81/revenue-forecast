# r3 document/evidence consistency pass -- evidence for M08

Canonical copy of the tooling and raw outputs lives in the M08 attempt
(execution_runs/M08/a20260919-01/recovery/docfix-r3/). This directory is a
byte-identical mirror so that M08 can re-run its own proof locally.

## What this pass changed for M08

1. oracle.md -- FOLDED the two duplicated "revision r2" sections into ONE and INSERTED a
   provenance-gap note at the folded duplicate's former position (F-M08-06; wording
   corrected under F-R3-01). The insert point coincides with EOF, but the mechanism is an
   insertion, not a trailing append: live = pre[:kept_prefix_bytes] + note, so
   live[:kept_prefix_bytes] is byte-identical to pre[:kept_prefix_bytes] (equivalently,
   live carries pre's complete r2 body as a prefix). The folded duplicate was
   byte-identical to the kept section except for the hash line.
   sha256 ff68cc5e01f87035e62d801727ddfa50bf9fd85bb30a4f799a4bf2eda36edbb1 -> 2b807c4a702948b19b6178bc463536bfab2d30859f858100de24887b9e1bdd80
   (19745 -> 20316 bytes)
   byte account: 19745 (pre) - 3585 (folded duplicate) + 4156 (inserted r3 note) = 20316 (live)
   kept prefix [16160 bytes] sha256
   7aa5805025a2a692be30c148907a4b5473541ebfa0ce45a31c82c1e1d067b7dc (before) ==
   7aa5805025a2a692be30c148907a4b5473541ebfa0ce45a31c82c1e1d067b7dc (after)
2. evidence/M08/oq_rulings.json -- counts corrected (ratio drivers 40 -> 41; drivers
   outside [0,1] 3 -> 4, the missing one being direct_growth.growth_rate whose domain is
   (-1, inf)) and the attribution rewritten from first-person reviewer to
   "enumerated by the implementer, reviewed by the independent reviewer" (F-M08-07).
   sha256 7e9002c34c1cd3ec567b7e62e233dc5e5df62c7657f7cb35e1bb4e39462d333e -> fc811ebbaac6ef5a02c8e369ffdb019b3e7a310c4c82c7264648f74241470545
3. binding.json / handoff.json got a docfix_r3_hash_ledger that declares the r1->r2 repack
   scope with old/new hashes and the annotation-only proof (F-M08-08).
   sha256 fdeb0c86c48b95fe91997ba88faa90c0e6e1616becacf2d5329655a312f731bb -> f376b719b1f5a95396bb7dabe45e70ed30078542be45c65d255bb92b3c1f9ab3
   sha256 49dac6a09d29a2b4200b1ce4c63777d872dc90f6ac533bcd427970684a47722d -> 838eefac9304fbdfe785fd66a9844d45db6e6889a6dc184b26cc440c08b46a2b
4. decision.md got an appended hash-ledger section; M08 additionally got the DEC-M08-1
   correction pointing at handoff.json.owner_action_required (F-M08-09).
   sha256 1b7e51106daec552643e78e604cfbc62d6d80c725d0bf4e9c3c47f945aa93126 -> 42124934c747b61bb2979d829391a830b3380cf7fd00634c1592605b3f272840
5. downstream ledgers refreshed: evidence/M08/source_manifest.json (oracle sha256_now),
   evidence/M08/evidence_hashes.json (revision r3), after/rerun_sha256.json (all entries
   == disk again, the F-M08-01 property), and the new evidence/M08/docfix_r3.json
   sha256 d70dcda0b07bd681e8b0e164a931bda5d08e81f8c29c1b7442ed07c56d6298f4.

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
- oracle_pre_M08.md is the byte-exact pre-merge image; the removed duplicate section is
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

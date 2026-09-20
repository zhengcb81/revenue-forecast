# r3 document/evidence consistency pass -- evidence for M06

Canonical copy of the tooling and raw outputs lives in the M08 attempt
(execution_runs/M08/a20260919-01/recovery/docfix-r3/). This directory is a
byte-identical mirror so that M06 can re-run its own proof locally.

## What this pass changed for M06

1. oracle.md -- FOLDED the two duplicated "revision r2" sections into ONE and INSERTED a
   provenance-gap note at the folded duplicate's former position (F-M08-06; wording
   corrected under F-R3-01). The insert point coincides with EOF, but the mechanism is an
   insertion, not a trailing append: live = pre[:kept_prefix_bytes] + note, so
   live[:kept_prefix_bytes] is byte-identical to pre[:kept_prefix_bytes] (equivalently,
   live carries pre's complete r2 body as a prefix). The folded duplicate was
   byte-identical to the kept section except for the hash line.
   sha256 c9c4aa7e9fd207ff188b27f5e2a51a02975606e949f7d8ab66bf9de00a4618fb -> 7a4c585eca511b5ba86375077e7d6528413d2ca84292471d8c460b5e0b77494b
   (10912 -> 13353 bytes)
   byte account: 10912 (pre) - 1706 (folded duplicate) + 4147 (inserted r3 note) = 13353 (live)
   kept prefix [9206 bytes] sha256
   b4c7b4acdd7b324bd7da8530a879c2279e281e2c8af8e3dd94438fa21f3a81c0 (before) ==
   b4c7b4acdd7b324bd7da8530a879c2279e281e2c8af8e3dd94438fa21f3a81c0 (after)
2. evidence/M06/oq_rulings.json -- counts corrected (ratio drivers 40 -> 41; drivers
   outside [0,1] 3 -> 4, the missing one being direct_growth.growth_rate whose domain is
   (-1, inf)) and the attribution rewritten from first-person reviewer to
   "enumerated by the implementer, reviewed by the independent reviewer" (F-M08-07).
   sha256 ced1c6075b01b1404e56ed8d767cd0fc406d7b65a2e89c2647b94383e151567f -> e73b23779cec8a78e680d84d66786a926c53bc9130c0ac905b31a747a3cba831
3. binding.json / handoff.json got a docfix_r3_hash_ledger that declares the r1->r2 repack
   scope with old/new hashes and the annotation-only proof (F-M08-08).
   sha256 6b2d3a48a34239962161eb666e5b78134cbcd946249beb4d1dddb909a018c04b -> a928a534f379a6ea1083159114ff543eb3026467107043ebab6cae6fdf56568f
   sha256 f9fc17473cf9f2c875ae22f3d9b569f5c7d706434431f60337840c404caffdf4 -> 9bfb05ef5891dccb266847ceddc46c0a464ca84b785e1dbd3633e7b6fdbc6aeb
4. decision.md got an appended hash-ledger section; M08 additionally got the DEC-M08-1
   correction pointing at handoff.json.owner_action_required (F-M08-09).
   sha256 c950fc851f9fb797b32992e454699e5bead11e029e10b49ed536614300d0685b -> aec8f19db79dc47814dd278c2cceec4b70888b9b14a4001c6daf21ae5a045b0d
5. downstream ledgers refreshed: evidence/M06/source_manifest.json (oracle sha256_now),
   evidence/M06/evidence_hashes.json (revision r3), after/rerun_sha256.json (all entries
   == disk again, the F-M08-01 property), and the new evidence/M06/docfix_r3.json
   sha256 468c0a870deec052f773d87051befe1f4c3d360b9960a32578697af04af17160.

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
- oracle_pre_M06.md is the byte-exact pre-merge image; the removed duplicate section is
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

# r3 document/evidence consistency pass -- evidence for M07

Canonical copy of the tooling and raw outputs lives in the M08 attempt
(execution_runs/M08/a20260919-01/recovery/docfix-r3/). This directory is a
byte-identical mirror so that M07 can re-run its own proof locally.

## What this pass changed for M07

1. oracle.md -- merged the two duplicated "revision r2" sections into ONE and appended a
   provenance-gap note (F-M08-06). The duplicate was byte-identical to the kept section
   except for the hash line, so nothing but the duplicate was removed.
   sha256 ca4543b16aabb2963694f1c34fa6e5a56021de5db80cacde68eee7246d01d646 -> b418885668bf8d972287a001c92d259c70045a9cfe6eda17006dfb0394697cfe
   (11469 -> 13275 bytes)
   kept prefix [9566 bytes] sha256
   2883780ca072cc72ee2b07842c9767c67e8611140ee1fb38846d577663d5805c (before) ==
   2883780ca072cc72ee2b07842c9767c67e8611140ee1fb38846d577663d5805c (after)
2. evidence/M07/oq_rulings.json -- counts corrected (ratio drivers 40 -> 41; drivers
   outside [0,1] 3 -> 4, the missing one being direct_growth.growth_rate whose domain is
   (-1, inf)) and the attribution rewritten from first-person reviewer to
   "enumerated by the implementer, reviewed by the independent reviewer" (F-M08-07).
   sha256 ea82d38816a987196ccaaece5d5eedf051e29fc666443a54b9c45b52a7c91286 -> 3a49462674e8f9ebe5799047a043df3643b406bf0b0c56303303b536a5c7e6f3
3. binding.json / handoff.json got a docfix_r3_hash_ledger that declares the r1->r2 repack
   scope with old/new hashes and the annotation-only proof (F-M08-08).
   sha256 1cc7337c8a40cadddc58cf36c75d071a1975d5d10228057e49193f3c666636d1 -> 514a425bc01ddd0bd1a6684495bce633a19eef18121fcc5f684609a008220fdb
   sha256 7432a2fdee2fc94b0aabf25d7b3ea654a1edf7321492baad8d29fe340b2c1dc7 -> 1fbe4d8a198511750639553325ee17386fb8849c0455618a3ceb7312e95cc443
4. decision.md got an appended hash-ledger section; M08 additionally got the DEC-M08-1
   correction pointing at handoff.json.owner_action_required (F-M08-09).
   sha256 a9b18e793e2bfd860ae2e0724c438fce3c6bacabdcb9827dad96a8f521e0e1cc -> b05cba7b6005f16c1392982d9f81c7164f3ed3e729f0637bd0f99ff79bcf5636
5. downstream ledgers refreshed: evidence/M07/source_manifest.json (oracle sha256_now),
   evidence/M07/evidence_hashes.json (revision r3), after/rerun_sha256.json (all entries
   == disk again, the F-M08-01 property), and the new evidence/M07/docfix_r3.json
   sha256 841c336aa98e41f6908129c1cb78c66886ea6ae1de4c66bdebef2c64adc6f056.

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
- oracle_pre_M07.md is the byte-exact pre-merge image; the removed duplicate section is
  therefore not destroyed.
- No expectation, tolerance, negative case, disclosure figure or product file was changed.
- M08 remains BLOCKED: the owner three-step remediation is still outstanding.

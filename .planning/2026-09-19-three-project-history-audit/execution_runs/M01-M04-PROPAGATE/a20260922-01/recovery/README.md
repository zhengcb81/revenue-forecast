# recovery/README.md — M01-M04-PROPAGATE (a20260922-01)

## What this attempt is

Isolation-only propagation of the REM-21/T1-8 per-case `expected` exact-type-name gate
to batches **M01–M04** (owner ruling `OWNER_DECISIONS.md` §18 "A-1 = 1（①扩权）").
Everything lives under this attempt; the historical M01..M04/a20260919-01 directories
are READ-ONLY and proven untouched (7722-file manifest, PASS).

## Layout

```
oracle.md                      frozen BEFORE any run (sha in evidence/oracle_freeze.json)
before/run_card.py             byte copy of the historical runner (b5fcc685...)
before/cases_M0X.json          byte copies of the four frozen fixtures
iso/run_card_before.py         byte copy used for arm B (historical runner role)
iso/run_card.py                THE patched copy (REM-21 form; see changes.diff)
iso/code_root/                 read-only product snapshot (9ec65295... / 9939480b...)
evidence/<CARD>/<ARM>/         per-run: evidence/<CARD>/ fixtures, out.json,
                               stdout.txt, stderr.txt, rc.txt, run.json
evidence/manifest_{before,after}.json + manifest_verification.json
evidence/arms_raw.json         all 20 runs: argv, raw_rc, expected_rc, artefacts
evidence/arms_summary.json     per-batch arm table + 60/60 deep checks
scripts/                       build_manifest.py, verify_manifest.py, run_arms.py,
                               make_diff.py, summarize.py (all reproducible)
```

## Re-run arms (recovery / independent reproduction)

```powershell
$runs = "C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs"
$a    = "$runs\M01-M04-PROPAGATE\a20260922-01"
$py   = "$runs\M01\a20260919-01\iso\venv\Scripts\python.exe"
$env:PYTHONDONTWRITEBYTECODE = "1"
& $py -X utf8 -B "$a\scripts\run_arms.py"        # 20 fresh subprocesses, rewrites evidence
& $py -X utf8 -B "$a\scripts\summarize.py"       # rebuild arm table + deep checks (exit 0 = all pass)
```

Expected raw rc everywhere: **E=0, F=3, G=2, S=1, B=0** per card.
`run_arms.py` asserts the before-copy hash (`b5fcc685…`) and the code-root pins before running.

## Re-verify historical non-touch (any time)

```powershell
& $py -X utf8 -B "$a\scripts\build_manifest.py"  $runs "$a\evidence\manifest_recheck.json"
& $py -X utf8 -B "$a\scripts\verify_manifest.py" $runs "$a\evidence\manifest_before.json" `
    "$a\evidence\manifest_recheck.json" "$a\evidence\manifest_recheck_verification.json"
# verification result must be PASS (7722 files, 0 added / 0 removed / 0 changed)
```

## Rollback

Nothing historical was modified — there is nothing to roll back outside this attempt.
If the patched copy must be discarded: delete `iso/run_card.py`; `before/` and
`iso/run_card_before.py` remain the authoritative original bytes.

## Boundaries (do not violate on any recovery run)

- Never write under `execution_runs/M01..M04/` or any other historical attempt.
- Never edit frozen fixtures; mutate only the copies under `evidence/<CARD>/<ARM>/`.
- Production repo is READ-ONLY. No git writes. No self-signing.
- REM-80 register-row closure belongs to the parent AFTER independent review.

# WC-1 / I-14-D-R8 commands — append-only execution log (NINE-STEP)

Convention: cwd = `<PLAN>\execution_runs\I-14-D-R8\a20260923-01` unless noted;
`$py = C:\Miniconda\python.exe` (3.13.9; the I-14-D iso venv is the same version);
every python run used `-B` + `PYTHONDONTWRITEBYTECODE=1`; no git, no network.
Raw stdout/rc of every instrument run is in `evidence/` next to its JSON.

## Step 1 — read card + freeze inputs (read-only)

- Read `REGISTRY-CLOSURE\a20260923-01\decision.md` → WC-1 row L84-85 = input list.
- Read I-14-D lineage: `decision.md`, `oracle.md`, `review.md`, `fix_record.md`,
  `handoff_r6.json`, `reviewer_report.md` (F-REV-D-03), `reviewer_report_r3.md` (R3-05/R3-07),
  `reviewer_report_r5.md` (R5-08), `reviewer_report_r7.md` (+ sidecar), both r6 harnesses,
  `iso/product_narrow_r6` + `iso/product_base` observability.py, register rows L17/L1665/L1713.
- `Get-FileHash -A SHA256` on: WC-1 decision (`a68ed77f…`, = its binding's decision_sha256),
  r6 tree (`2f644994…`), production (`edcbeccb…`), base tree (`c5608c4b…`), r6 harnesses
  (`85a1b064…`/`8f5feffd…`), register (`5348278f…`), r7 report (`cc6da8d3…` = sidecar).
  All recorded in `binding.json`.

## Step 2 — freeze oracle (before any SUT execution)

- `$py -B harness\freeze_arithmetic.py` → lengths (pure string arithmetic, no SUT import)
  → `expect_len` cells of all 17 new oracle rows.
- wrote `oracle.md` (4 items frozen + dispositions + rows + directions + bidirectional criteria
  + protocol + non-goals) → `oracle.sha256` = `c6cbf869…` (pre-run pin; superseded by
  CORRECTION W1, prefix-proved).

## Step 3 — isolated copies + literal-asserted fixes + r8 harnesses

- attempt 1: `$py -B harness\build_r8.py` → **rc 1**: rule-row anchor asserted
  (`M`/`S39` are the oracle harness's names; the rule harness uses `MARKER`/`REVIEWER_SECRET`)
  → `evidence/build_r8.attempt1_failed_anchor.*` (nothing half-written; anchor assert is the
  guard).
- corrected anchor + row constant names in `build_r8.py`.
- attempt 2: `$py -B harness\build_r8.py` → **rc 0** → `evidence/build_r8.stdout.txt`:
  `iso/r8_base` copy pin-verified `2f644994…`; `iso/r8_fixed` edits const+func+auth each
  landed 1:1, py_compile ok, observability `2f644994…` → `90b3fdc3…` (43746→45774 B);
  harnesses `run_i14d_oracle_r8.py` (`85a1b064…`→`ad7861ee…`, 44→61 rows) and
  `run_rule_table_i14d_r8.py` (`8f5feffd…`→`ffe3372b…`, 95→113 rows), both py_compile ok.

## Step 4 — RED on r8_base

- `$py -B .\harness\run_i14d_oracle_r8.py --src .\iso\r8_base --label r8_base --out .\evidence\red_oracle_r8_base.json` → **rc 3**, verdict `RED-as-expected-pre-fix`, all_failed = exactly N14-N18+N23-N28 (11).
- `$py -B .\harness\run_rule_table_i14d_r8.py --src .\iso\r8_base --label r8_base --out .\evidence\red_rule_r8_base.json` → **rc 3**, fidelity_failures = exactly 13, touched `[]`, registered_open 7/7.
- raw: `evidence/red_*.{json,stdout.txt,rc.txt}`.

## Step 5 — GREEN on r8_fixed

- same two commands with `--src .\iso\r8_fixed --label r8_fixed --out .\evidence\green_*` →
  oracle **rc 0** `pass` 61/61 (registered_open 7 confirmed 7); rule **rc 3**
  `negative`-by-design, `fidelity_ok true`, 113 rows, `credential_leaks []`, touched `[]`,
  registered_open_leaking 7 (marker row visible).

## Step 6 — product_base direction run (read-only)

- both instruments with `--src <PLAN>\execution_runs\I-14-D\a20260919-01\iso\product_base\src`
  `--label base_* --out .\evidence\base_*` → oracle rc 3 (keep_must_failed `[]`; the 11 frozen
  new rows in narrow_must_failed; R3c registered_open NOT confirmed = disclosed base-regression);
  rule rc 3, touched `[]`. Direction evidence only — no rc/pass claim for base.

## Step 7 — mutants (scratch = %TEMP%)

- `$py -B harness\build_mutants.py` → rc 0 →
  `%TEMP%\i14dr8_mutants\MUT-A-revert-REM06` (sha `9ea51391…`), `MUT-B-revert-R305`
  (sha `8217f100…`) → `evidence/mutants_build.json`.
- 4 instrument runs (same invocation shape, `--src <mutant tree>`) →
  `evidence/mutA_*` (oracle rc 3 = N14-18 only; rule rc 3 = the 5 `cred-digit-*` only) and
  `evidence/mutB_*` (oracle rc 3 = N23-28 only; rule rc 3 = 6 `cred-auth-break-*` + 2
  `over-auth-break-*` only). Each mutant kills exactly its own family.

## Step 8 — bidirectional sweeps + changes.diff

- attempt 1: `sweep_key_domain.py` + `sweep_value_start.py` → **rc 1 each**: by-path module
  load without `sys.modules` registration → dataclass `_is_type` AttributeError (tooling) →
  `evidence/*_attempt1_loadbug.stdout.txt`.
- registered the module before `exec_module`; attempt 2: key sweep **rc 0** (pass; carried a
  non-boolean count field → attempt2 record kept), value sweep **rc 3**: criterion compared
  LISTS while the freeze defines a SET (same six chars, order-only false FAIL) →
  `evidence/value_start_sweep.attempt2_orderbug.*`.
- set-based comparison (criterion text unchanged); final runs: `sweep_key_domain.py` **rc 0**
  pass (350-key domain, old\new ∅, new\old 114 ⊆ digit vocab), `sweep_value_start.py` **rc 0**
  pass (95/95 closed, old\new ∅, new\old = the six forms) → `evidence/*_sweep.json`.
- `$py -B harness\diag_key_sweep.py` → rc 0: 120−114 = `secret_key2/3/12` × case, all already
  old-true (`secret` single atom) → `evidence/key_sweep_count_diag.json`.
- `$py -B harness\make_changes_diff.py` → **rc 0** (run twice; byte-identical diff, sha
  `baec3153…`): in-memory edits on production (3/3 anchors, production NOT written),
  py_compile ok, grafted `%TEMP%\i14dr8_prodapply\src` tree ran both instruments GREEN
  (oracle rc 0/61; rule fidelity_ok/113) → `evidence/production_apply.json`,
  `evidence/prodapply_*.{json}`, `changes.diff` 9161 B.

## Step 9 — carriers + corrections + integrity

- CORRECTION W1 appended to `oracle.md` (one mis-forecast cell; append-only).
- prefix proof attempt 1 **rc 3** (missed the original trailing LF) → attempt 2 tested both
  reconstructions, `prefix+LF` matched the pre-run pin exactly → `evidence/oracle_prefix_proof.json`.
- first `binding.json` rewrite attempt failed (`Set-Content -Raw` invalid — no-op) → rewritten
  via JSON load/dump; parses; carries `oracle_sha256` (post-correction) +
  `oracle_sha256_pre_correction` + `changes_diff_sha256`.
- re-pinned `oracle.sha256` (`cd8b05e0…`).
- wrote `decision.md`, `commands.md` (this file), `recovery.md`, `handoff.md`,
  `evidence/README.md`; then `harness/final_integrity.py` → `evidence/final_integrity.json`
  (recomputed pins + zero-write scan) and `evidence/final_hashes.json`.
- `final_integrity.py` iterations (retained in this log; final run rc 0):
  attempt 1 **rc 1** — `ATT.parent.parent` resolved to `execution_runs/`, not the plan root
  (path-depth bug in the script, nothing written outside this attempt);
  attempt 2 **rc 3** — midnight cutoff misattributed OTHER actors' legitimate same-day work
  (REGISTRY-CLOSURE's own card files, its reviewer's 23:54 report, unrelated company-wiki
  modules) as violations → revised to (a) creation-time cutoff (23:29:53, session start),
  (b) content-pin attribution for every pinned input, (c) row-level acceptance of the known
  external register append; attempt 3 label fix; final **rc 0 / verdict pass**.
- zero-write claim scope: revenue-forecast sources, company-wiki, I-14-D sealed attempt,
  REGISTRY-CLOSURE attempt, REMEDIATION_REGISTER.md — verified by hash recompute + mtime scan
  in `final_integrity.json` (sealed I-14-D: 0 hits; company-wiki/src: 0 hits; REGISTRY-CLOSURE:
  2 hits = its own concurrent reviewer artifacts, informational; register = external append,
  cited rows verified verbatim).

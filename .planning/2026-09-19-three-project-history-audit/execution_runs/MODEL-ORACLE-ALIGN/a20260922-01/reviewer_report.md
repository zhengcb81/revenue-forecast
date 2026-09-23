# reviewer_report.md — independent review of MODEL-ORACLE-ALIGN a20260922-01

- card: **MODEL-ORACLE-ALIGN** (battery alignment to I-10-B defect-1 + B-6c re-attempt, no STOP)
- attempt: `<PLAN>\execution_runs\MODEL-ORACLE-ALIGN\a20260922-01`
- reviewer: delegated subagent of parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`
- review window (live): 2026-09-22 20:33–20:40 local; card's own artifacts span 20:09:38–20:30:13
- tools used by reviewer: `read` / `grep` / `pwsh` only (no writes except this report + its `.sha256`); git used read-only (`status`/`rev-parse`/`reflog`/`hash-object`/`diff --no-index`); one permitted live pytest file re-run with all output into `%TEMP%`
- REM-79 discipline in this text: every conclusion sentence carries its measurement domain on the same line (domain: live re-hash of RF production tree + attempt evidence set, 2026-09-22 20:33–20:40).

## VERDICT: `accepted_scoped`

(domain: all nine checklist items below, verified against live files and raw evidence under this attempt, 2026-09-22). The card did what it claims: freeze-first oracle, exactly-2-file production promotion with byte-exact hashes, a RED→GREEN→mutation chain whose failure set is line-identical to PROMOTION-EXEC's recorded B-6c RED, a complete 31-row explicit-default alignment table with 0 assertion rewrites, post-promotion verifications all rc 0, zero-touch neighbors/oracles/CW/git, and all disclosures + handoff fields present.

### Accept scope (as directed by parent)

1. **commits = parent's authority**: RF commit = exactly 2 files — `scripts/model_registry.py` + `tests/test_model_economic_guardrails.py` (domain: live `git status --porcelain` shows exactly these 2 production files dirty alongside PROMOTION-EXEC's pre-existing 5 scripts, 2026-09-22 20:35).
2. **full-suite gate remains at parent batch-4 push** (domain: card declared not-run in commands.json NR-2; reviewer did not run it).
3. **E1E7 carrier flips (M05/M14/M20/M24 INACTIVE→ACTIVE) = parent bookkeeping** (domain: consequence statement exists in decision.md §权威链-4 and handoff.json `consequences_recorded_not_acted[0]`; no M-card file edited by this card — oracle blobs match HEAD, see F6c).
4. **B-6b / natural_window remains blocked-by-design, untouched** (domain: no evidence file, command, or write in this attempt references B-6b/natural_window; reviewer observed zero such paths in the attempt tree).
5. **CF-I14FR1-3 CW sampling remains owed** (domain: parent-side obligation; this card neither performed nor claimed it).

---

## FINDINGS (numbered, one per checklist item)

### F1 — Freeze-first: CONFIRMED (domain: CreationTime of every file in the attempt + production before-image capture times, 2026-09-22)

- `oracle.md` live re-hash = **`146ce313f7158da8ef1093961b1ebd1de5cfef0e4b0ffbe0d733c8fb4c2302da` / 12543 B** — matches binding + handoff + 08 ledger exactly.
- CreationTime ordering (all attempt paths sorted live): **oracle.md 20:09:38 < recovery/before_images ×2 20:10:23 < binding.json 20:10:52 < iso trees 20:11:11–20:11:22 < first evidence `01_red` 20:11:34** — oracle is strictly first; `01_red` (first evidence) is 116 s later.
- Production-write ordering (mtime unusable because `Copy-Item` preserves source mtimes — measured, as the card disclosed): the decisive bound is the **before-image capture at 20:10:23**, which re-hashes to the pre-card contents (`66516452…/7988`, `9ec65295…/26446`) ⇒ production was still untouched at 20:10:23 ⇒ **oracle freeze 20:09:38 preceded every production write by ≥ 45 s** (domain: live hash of both recovery before-images vs binding pins).
- Write window of `tests/test_model_economic_guardrails.py` from the card's evidence timestamps: **(20:16:41, 20:17:01]** — lower bound = `04b` evidence LastWrite 20:16:41 (commands.json orders PROD-WRITE-1 after MUTATION-RESTORE, with PROD-PREWRIITE-GUARDS still reading `66516452…` immediately before the write); upper bound = disclosed derived pyc `tests/__pycache__/test_model_economic_guardrails.cpython-313.pyc` **live-re-measured at 13577 B / 2026-09-22 20:17:01**, compiled from the then-current (aligned) production source. The `08_final_integrity.txt` ledger recorded that file at `mtime=2026-09-22 20:16:08` (source-preserved iso mtime), consistent with this window.
- `scripts/model_registry.py` write window: **(20:16:41, 20:19:15]** — upper bound = the card's `iso/rf/scripts/model_registry.py` copy created 20:19:15 which re-hashes to `62f864b9…` (i.e., production already promoted then). Both windows are strictly after the oracle freeze (domain: CreationTime measurements above).

### F2 — The two production files, live re-hash: CONFIRMED (domain: live SHA-256 of RF working tree, 2026-09-22 20:35)

| file | live hash / bytes | expected | verdict |
|---|---|---|---|
| `scripts/model_registry.py` | `62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` / 30116 | same | **MATCH** |
| `tests/test_model_economic_guardrails.py` | `89a76809321e87d852ec8d5863650eed8ac1b47c52c8f1b38db4768f7d5ac82a` / 10414 | same | **MATCH** |
| I-10-B iso source `I-10-B/a20260919-01/iso/rf/scripts/model_registry.py` | `62f864b9…` / 30116 | same | **MATCH — production == I-10-B iso source byte-exact** |
| attempt `iso/rf/scripts/model_registry.py`, `iso_promoted/scripts/model_registry.py` | `62f864b9…` / 30116 each | same | MATCH |
| before-image `recovery/before_images/test_alignment/…` | `665164528d7d37663ff37474ddae20bfcf3c16eceefde3e6f54473324251ab77` / 7988 | same | **MATCH — before-image found & pinned in binding** |
| before-image `recovery/before_images/registry_repromotion/…` | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` / 26446 | same | **MATCH — and byte-identical to PROMOTION-EXEC `recovery/before_images/B-6c/model_registry.py` (live re-hash `9ec65295…`)** |
| companion `scripts/model_extensions.py` | `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911` / 14475 | same (binding) | MATCH — not touched |

### F3 — RED / GREEN / mutation chain: CONFIRMED (domain: raw contents of `evidence/01–04b` + independent set-diff vs PROMOTION-EXEC `B-6c_model_focused_tests.txt`)

- `01_red_promoted_battery.txt`: tail = **`31 failed, 53 passed, 177 subtests passed in 19.91s`**, 1819 lines, **31 short-summary entries = 6 item FAILED + 25 SUBFAILED** (enumerated live). Counts reconcile with binding (`6+53=59`, `25+177=202`).
- **Line-identity claim (my own diff, not the card's Compare-Object):** extracted all 31 `^(FAILED|SUBFAILED)` lines from my `01` and from `PROMOTION-EXEC/a20260922-01/evidence/B-6c_model_focused_tests.txt` (live hash `a266a922…`/111044 = binding pin) → **`Compare-Object` EMPTY on 31 vs 31 lines — identical failed-test set** (domain: independent PowerShell set-diff, 2026-09-22).
- **`:410` spot-check:** every `model_registry.py:<line>` reference anywhere in `01` is **line 410 (×29); all other registry lines ×0**. Splitting the FAILURES section yields 29 traceback blocks: 27 carry the explicit `scripts\model_registry.py:410` frame; the 2 without it are exactly the `assertRaisesRegex` message-mismatch failures (`"time exposure" does not match …`, `"finite" does not match …`) whose E-line quotes the verbatim `:410` message (`missing driver for … has no explicit default`) — so no failure points at any other registry line (domain: per-block regex attribution over `01`, 2026-09-22).
- `02` GREEN promoted = **`59 passed, 202 subtests passed in 5.66s`** (0 failure lines) ✓; `03` GREEN before-image (dual-tree) = **`59 passed, 202 subtests passed in 5.89s`** ✓; `04b` restored = **`59 passed, 202 subtests passed in 6.23s`** ✓.
- `04a` mutation (field omission): **`1 failed in 2.31s`**, traceback terminates **`model_registry.ModelRegistryError: missing driver for bank_revenue: other_revenue has no explicit default` / `scripts\model_registry.py:410`** — defect-1 message at :410, exactly as claimed ✓.
- All nine evidence files `02–07` re-hash byte-exact to the `08_final_integrity.txt` ledger (20555b70 / 9dfcfecf / f9fbe1ef / 277c3c84 / c4bd17a3 / 937c4925 / 2af987a4 / 39696919 / 7ee7dcd0 — all **OK**), so the raw evidence is unmodified since the card sealed it (domain: live re-hash of evidence set vs ledger).

### F4 — 31-case alignment table + 3 sampled cases: CONFIRMED (domain: `decision.md` §31 表 + live read of production test file + `git diff --no-index` before→after)

- `decision.md` contains the full per-case table: **rows 1–6 (A. item-level FAILED) + rows 7–31 (B. SUBFAILED) = 31 rows**, every row with its RED line citation (行 ranges checked for internal consistency: row 31 cites 行1666–1725, row 6 cites 行1726–1786, file has 1819 lines with the 31-line short summary starting ≈1787).
- Split recorded in both decision counts table and `handoff.per_case_alignment_table`: **31 explicit-default / 0 assertion-rewrite / 0 STOP** ✓.
- Rule statement present: "none of the 31 asserts the silent-fill itself… hidden 0.0 was at before-image `model_registry.py:335`" — decision.md §"Rule (c) 判定" states the criterion, the `:335` citation (`drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))` — also visible as the removed line in changes.diff §2), and the dual-tree backstop argument ✓.
- **Sampled 3 cases, verified against the live production test file:**
  1. **row 1 `test_bank_negative_rates_preserve_sign_without_probability_clamp`** (test line 113): `"other_revenue": [0]` now EXPLICIT; assertions untouched — `assertEqual(…, [5])`, `driver_value_bounds(bank_revenue, funding_cost) == (-inf, inf)`, `driver_value_bounds(capacity_utilization, utilization) == (0, 1)` verbatim as in before-image (domain: live read of production file + before-image, 2026-09-22).
  2. **rows 8–31 `test_public_calculator_preserves_every_existing_case_without_mutation`** (test lines 55–65): call now goes through `_with_explicit_missing_defaults` (line 60) materializing every absent optional as `spec.defaults.get(d, 0.0)`; no-mutation assertion retargeted `drivers→explicit` (line 63, same property: the object passed is not mutated); numeric `assertAlmostEqual(observed, target)` loop verbatim unchanged ✓.
  3. **row 3 `test_inconsistent_customer_timing_cannot_create_negative_exposure`** (test lines 141–149): `"usage_revenue": [0]` EXPLICIT; `assertRaisesRegex(ModelRegistryError, "time exposure")` unchanged — the guarded rule (negative time exposure must still raise) remains reachable and asserted ✓.
- **Full before→after diff re-derived by the reviewer** (`git diff --no-index` recovery-before-image vs production): **−5 / +40 lines, exactly as claimed**; the −5 removed lines are only (a) the 3 sweep lines retargeted `drivers→explicit`, (b) the overflow tuple line, (c) `fee_revenue` line — the latter four reappear with only the added explicit field + citation comment; **every assertion-strength line in the file (assertEqual/assertAlmostEqual/assertRaises/assertRaisesRegex) is otherwise byte-identical**, and the 8 untouched neighbor test functions show zero diff lines ✓ (domain: complete reviewer-derived diff, not the card's own changes.diff).

### F5 — Post-promotion verifications: CONFIRMED (domain: raw evidence contents + one reviewer-run live pytest, 2026-09-22 20:39)

- `05` production battery = `59 passed, 202 subtests passed in 9.05s` ✓; `05b` verbose = `59 passed, 202 subtests passed in 10.45s`, **0 FAILED/SUBFAILED lines** ✓ (two independent rc-0 runs).
- `06` 13-node I-08-C under full promotion = **`13 passed in 5.40s`** ✓.
- `07` I-10-B focused verify = **`phase = after | total = 7 | passed = 7 | failed = 0`**, all R-B1/R-B2 probes PASS ✓; **`verification_after.json` live re-hash = `b7a925f5b5a9e4af4cf77532999521427b79edbc6c51c7bd1aaf2a03c270da86` / 1766 B, and I-10-B's own frozen GREEN artifact re-hashes to the SAME value/SAME size — byte-identical**, matching I-10-B commands.json's own pin text (`sha256 b7a925f5…`) ✓ (domain: dual live re-hash, 2026-09-22).
- `05a` py_compile = `PYCOMPILE_OK both` ✓ (rc 0).
- **Reviewer's own single permitted re-run** (output + basetemp all in `%TEMP%`, `python -X utf8 -B -m pytest tests/test_model_economic_guardrails.py -p no:cacheprovider`): **RC=0, `16 passed, 134 subtests passed in 2.24s`** on the live production tree, and a post-run write-scan of `scripts/` + `tests/` shows **zero files modified during the run** — production remained read-only under the reviewer (domain: reviewer's own command, 2026-09-22 20:39).

### F6 — Zero-touch: CONFIRMED (domain: live re-hash of 9 protected neighbors, 4 M-oracles vs HEAD blobs, CW status, git reflog — 2026-09-22 20:35–20:36)

- `08_final_integrity.txt` re-derived live: **`scripts/model_extensions.py = 9939480b…` ✓ (production anchor), gate `tools/pre_push_gate.py = 3df161a7ceea17de95b36845bdb3c4cee729dca215c56853868780dce7331484` ✓, `tests/conftest.py = 6da47830…` ✓, battery test `tests/test_model_registry_contract.py = f3cf1e5c…` ✓** — plus the other three battery files (`46023006…`, `954e08ac…`, `0fab9aea…`), `tests/test_models.py = 0ea8c5a3…`, `scripts/forecast/segments.py = 95555509…` — **all 9 equal binding pins**.
- `scripts/model_registry.py` before-pin `9ec65295…` — **expected** to be gone from production (promoted); its byte-exact copy survives in `recovery/before_images/` (live hash OK) ✓.
- **M05/M14/M20/M24 `oracle.md` == HEAD blobs**: `git hash-object` vs `git rev-parse HEAD:<path>` → **MATCH / MATCH / MATCH / MATCH** (blobs `cbea2e8f…`, `aee22197…`, `d6a7f115…`, `584a0426…`) — no M-card oracle edited by this card ✓.
- **CW untouched**: `company-wiki status --porcelain` = **6 ` M` + 2 `??`**, i.e., the pre-existing dirties + PROMOTION's 3M/2new (`conftest.py` + `tests/contract/test_short_basetemp_convention.py` confirmed by PROMOTION-EXEC binding as its B-4 created files) — **no new path attributable to this card** (domain: live CW porcelain, 2026-09-22 20:36; HEAD `f39bd5a6`).
- **git**: RF `HEAD = 95df266191bd201f184166c8ef6be86d21afc7ce` (GATE-OQ-FIX commit message in reflog) and **reflog's newest entry is that commit — no entry after it, no card-authored commit** ⇒ zero git writes by this card (domain: live `git rev-parse` + `git reflog -n 8`). Root `.pytest_cache` mtime live = 2026-07-12 23:30:51 (untouched) ✓; `tests/__pycache__` contains exactly 357 `.pyc` files of which the disclosed one is `13577 B @ 20:17:01` ✓; `scripts/__pycache__/model_registry.cpython-313.pyc` predates the card (2026-09-21 06:56) ⇒ **no new pyc in `scripts/`** ✓ (domain: live directory enumeration).

### F7 — Consequence statement (E1E7 four flips INACTIVE→ACTIVE, no M-card edit): CONFIRMED PRESENT (domain: verbatim text in `decision.md` + `handoff.json`)

- `decision.md` §权威链-4: 「…因 B-6c 未落地而记为 INACTIVE 的 **M05/M14/M20/M24 四份 defaults-相位前瞻披露…随本次 B-6c 成功落地而转为 ACTIVE**；那些卡的字节本卡一字未动」 ✓.
- `handoff.json.consequences_recorded_not_acted[0]`: "B-6c now LANDED ⇒ E1E7's four defaults-phase forward-disclosures (M05/M14/M20/M24) transition from INACTIVE to ACTIVE … no M-card file edited by this card" ✓ — and the "no edit" half is independently proven by F6's blob comparisons. Reviewer did not edit any E1E7 carrier (parent bookkeeping) ✓.

### F8 — Three boundary incidents disclosed: ALL THREE CONFIRMED PRESENT (domain: cross-file search of decision.md / commands.json / handoff.json)

1. **py_compile first-use CLI misuse rc1 → one git-ignored pyc refreshed (357 siblings) → explicit-cfile retry rc0**: decision.md 边界事件 1 (with 20:17:01 / 13577 B / "357 个兄弟 pyc" — both figures live-verified), commands.json `PYCOMPILE-ATTEMPT1` (rc 1, disposition) + `PYCOMPILE-RETRY` (rc 0, `PYCOMPILE_OK both`), handoff `boundary_incidents_disclosed[0]` ✓.
2. **`Copy-Item` preserved source mtime on `model_registry.py`**: decision.md 边界事件 2 (mtime 2026-09-20 19:22:26 — live-re-measured on the production file, still exactly that value before the post-handoff refresh noted in O1), handoff `production_final_state…mtime_note` ✓.
3. **changes.diff first build (13181 B, absolute paths) superseded by ASCII rebuild `05180b9d…`/12519**: commands.json `MAKE-DIFF` observed + handoff `boundary_incidents_disclosed[1]`; final file **live re-hash = `05180b9d4001f08c24425856c3084342637a5d608f650c43202d33a898c2c7c9` / 12519 B** ✓.

### F9 — Handoff + changes.diff + recovery: CONFIRMED (domain: live read of `handoff.json` / `changes.diff` / `recovery/README.md` + live re-hashes)

- `handoff.json`: `status = "review_pending"`, `signature = null`, `self_sign = false`, `attestation = {da: "unmapped", acc: "unproven"}` — **unsigned, no self-sign** ✓.
- `changes.diff` (live `05180b9d…`/12519): repo-prefixed headers `--- a/tests/test_model_economic_guardrails.py` / `--- a/scripts/model_registry.py`, **SECTION 1 = test alignment** (banner + helper + 7 call sites + sweep) and **SECTION 2 = registry re-promotion** (banner states byte-exact copy of I-10-B iso source `62f864b9…`, containing defect-1 `:410` and defect-2 semantic-role sign changes) ✓; §1 content re-derived independently in F4 (−5/+40) and matches.
- `recovery/README.md` (live `fadff2ae…`/2499): **exact 2-file revert** — two `Copy-Item` commands, expected before-hashes `66516452…` and `9ec65295…` (= the live-re-hashed before-images), cross-note to PROMOTION-EXEC's B-6c image (= live-verified byte-identical), plus the scope note that no other production file was written ✓.

---

## OBSERVATIONS (non-blocking; none changes the verdict)

- **O1 (domain: live mtimes vs the 08 ledger, 2026-09-22 20:35):** at **20:31:43 — after this card's handoff (20:30:13) and after the parent's GATE-OQ commit (20:30:43)** — seven production paths were re-written with **byte-identical content**: both card targets (`62f864b9…`, `89a76809…` re-hashed OK) plus PROMOTION's 5 scripts (`company_wiki_source`, `revenue_core`, `revenue_publication`, `revenue_report`, `source_preparation` — content not re-pinnable by this reviewer). Consequences: (a) this card's zero-touch/final-state claims remain true on **content** (all in-scope hashes still match); (b) the `08` ledger's "recent writes" list no longer reproduces by mtime; (c) the actor is **not** this card (all card artifacts ≤ 20:30:13). Parent should identify the 20:31:43 writer before batch-4 commit if mtime-based audits matter (content-based ones do not).
- **O2 (domain: decision.md full read):** the changes.diff first-build disclosure lives in `commands.json` + `handoff.json`, **not** in `decision.md`; all three required disclosures exist across the deliverable set, so this is a placement note only.
- **O3 (domain: per-block analysis of `01`):** 2 of 31 RED failures (the two `assertRaisesRegex` message-mismatch cases) carry **no explicit `:410` frame line** — they quote the `:410` message verbatim instead; the claim "all failure line refs are `model_registry.py:410`" holds (no other registry line is referenced anywhere), but "31/31 blocks show a `:410` frame" would not — the card did not make that stronger claim.
- **O4 (domain: mtime semantics on this filesystem):** because `Copy-Item` preserves source mtimes for **both** production targets (the test file's mtime was also source-preserved — its live value tracked iso_promoted's `20:16:08` until O1), freeze-first and write-window had to be established via CreationTime + evidence-timestamp reasoning, as done in F1; a future card should `Set-Item -LastWriteTime` or record `[datetime]::UtcNow` at write instants.
- **O5 (domain: reviewer tool constraint):** `evidence/01`'s own rc is not embedded in the file (rc 1 comes from commands.json); the `31 failed…` line implies it unambiguously.

## UNVERIFIED (explicit list)

1. **`RF_IMPORT_ROOT` for `06`** — the 13-node run's env var is self-declared in commands.json; `06`'s output file doesn't record the env (13/13 pass is verified; the env value is not reconstructible from raw evidence).
2. **Exact wall-clock instants of the two production writes** — both mtimes were source-preserved (and O1 later refreshed them); windows are inferred from evidence timestamps (F1), not stamped.
3. **The 20:31:43 writer of the seven production paths (O1)** — actor unknown; content of the 5 PROMOTION scripts not re-pinnable by this reviewer (out of this card's declared scope; the 2 card targets re-hash exact).
4. **Full-repo test suite** — not run by reviewer (card declared not-run; gate owed at parent batch-4, per accept scope).
5. **Binding's start-of-card `git_porcelain_before` snapshot** — not reproducible after the parent's 20:30:43 GATE-OQ commit removed 2 entries (`tests/test_fc1105_fault_injection.py`, `tools/pre_push_gate.py`) from the dirty set; the snapshot's plausibility is supported by `08`'s own porcelain capture at 20:29:28 (which still shows them) — but it was not re-measured by the reviewer.
6. **RED run's exact pytest flags/env identity vs PROMOTION's run** — verified by output-level identity (31-line set diff + identical counts), not by re-running the RED battery (reviewer's one pytest re-run was spent on the live production GREEN, F5).
7. **Whether `01`'s 29-line/29-block vs 31-entry subtest grouping artifact is purely pytest subtest reporting** — not root-caused (immaterial: counts, set identity, and `:410`-only refs all verified).
8. **Reviewer did not run `grep` as a separate oracle search across all 31 rows** — sampling was 3 cases + a complete diff; rows 2, 4–31's per-row RED line citations were checked for internal consistency only (F4), not individually re-opened against `01`'s line numbers.

## REVIEWER BOUNDARY COMPLIANCE

- Wrote exactly two files: `reviewer_report.md` + `reviewer_report.sha256` (this attempt, the only permitted outputs) (domain: reviewer's own tool calls, entire session).
- Zero product writes, zero git writes, never self-signed; single pytest re-run pointed entirely at `%TEMP%` with `-B` / `-p no:cacheprovider` and a clean post-run write-scan (F5).
- Verdict authority: this report does **not** sign the card — it returns `accepted_scoped` to the parent for parent-side bookkeeping (commit, batch-4 gate, E1E7 carrier flips).

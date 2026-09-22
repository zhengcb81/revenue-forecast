# Promotion Batch Manifest — third batch (B-1..B-6) — PROMOTION-PREP a20260922-01

Frozen rules: see `oracle.md`. Every hash below was measured LIVE in this attempt
(`Get-FileHash -Algorithm SHA256`) on 2026-09-22; no hash copied from memory, hints, or prior reports.
UNRESOLVED = path/hash could not be found or verified. Zero production writes; no tests run.

B-table source: `OWNER_DECISIONS.md` §十七 (line 382+), rows B-1..B-7.

## Headline table

| # | Object | Source (iso, live sha256) | Target (production, live sha256) | Conditions | Verification |
|---|---|---|---|---|---|
| B-1 | I-08-C 安全三项 (REM-01/02/03) | `8a761498…`/`bc2bb4a3…`/`212f0059…` (fixed rf ×3) | `1821fd2a…`/`183803bb…`/`a85fb484…` (RF scripts, UNFIXED) | REM-40..44 closed; 2nd-round accepted; promotion = owner decision | see block |
| B-2 | B3 → company_wiki_source 作用域修复 | `7d1bd8f9…` (company_wiki_source) + `91a6dc32…` (fixed2 source_preparation) | `225fecdd…` + `37a3eeae…` (RF, UNFIXED) | REM-49 comment fix (fixed2) rides same batch | see block |
| B-3 | I-14-D → 脱敏类 `[^\s]+` | `2f644994…` (product_narrow_r6) | `a73826aa…` (CW observability.py, UNFIXED) | r7 accepted; 目标② batch-2 candidate | see block |
| B-4 | I-14-F-R1 → conftest 150/60 | `a908c9da…` + `1fd4e0d8…` (iso/tree ×2) | **ABSENT ×2 (new files, live-confirmed)** | CF-I14FR1-3 sampling; I-14-F vs R1 byte relationship | see block |
| B-5 | DW15 → prune/archive 五缺陷 | `0c99bbe0…` + `bbe855e4…` (iso/fixed) | `2358c73b…` + `143fef01…` (CW, UNFIXED) | E-4: promotion ≠ execution authorization; breaking-API note | see block |
| B-6 | I-14-F / I-14-I / I-10-B 既有 accepted | `c22be9f3…`(superseded by B-4) / `9edb9515…` / `62f864b9…` | ABSENT(→use B-4) / **UNRESOLVED path** / `9ec65295…` | E1E7-registered E-flips (I-10-B) | see block |

---

## B-1 — B1 系 → I-08-C 安全三项 (REM-01/02/03)

- Card: `execution_runs/B1-I08C-product-fixes/a20260921-01/` (binding.json card_id=B1, status review_pending→accepted per §十七 "二轮 accepted").
- `changes.diff` headers (grep `^---`): `a/scripts/revenue_core.py`, `a/scripts/revenue_publication.py`, `a/scripts/revenue_report.py` — 3 sections only.
- Source → target (all LIVE sha256, this attempt):

| file | source `iso/fixed/rf/scripts/` | bytes | target RF `scripts/` | bytes |
|---|---|---|---|---|
| revenue_core.py | `8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883` | 25842 | `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae` | 14136 |
| revenue_publication.py | `bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0` | 24917 | `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba` | 10681 |
| revenue_report.py | `212f00598feca408dc429d4c7a5332131ce25f1165b079347e4b295345df7d3b` | 73973 | `a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f` | 69765 |

- Target state: UNFIXED (live target hashes equal the card's `production_anchors_verified_pre_fix` pins for all three files ⇒ promotion not yet performed).
- Conditions (§十七 B-1 + card handoff.json): REM-40…44 closed; second-round accepted; 落定齐. Card handoff: "Production promotion … is a SEPARATE OWNER DECISION"; open questions: I-08-C oracle re-freeze of gap pins (test_e11/test_e13) + tests/test_attestation.py rewrite ownership (I-08-B).
- Verification (from card carriers): `Get-FileHash -Algorithm SHA256 scripts/{revenue_core,revenue_publication,revenue_report}.py` vs pins above; card `before/production_anchors.json` full table; post-promotion expectation: card's fixed-tree hashes become production hashes.
- git apply --check: UNRESOLVED-verification (skipped per step 5).

---

## B-2 — B3 系 → company_wiki_source 作用域修复 (+ B3-PREREQ fixed2)

- Cards: `execution_runs/B3-I05C-delivery-fixes/a20260921-01/` (status accepted_scoped) + `execution_runs/B3-PREREQ/a20260922-01/` (accepted_scoped; closes REM-47/48/49).
- `B3 changes.diff` headers (grep `^---`): `a/RF:scripts/company_wiki_source.py` + `a/I-05-C:retry-count-vs-artifact-count.json` (2 sections; the retry json is an evidence-record correction, not production).
- `B3-PREREQ changes.diff`: 3 diffs — (1) card-local `iso/conftest.py` (REM-47 guard), (2) `b3_reference/iso/fixed/rf_scripts/source_preparation.py` → `iso/fixed2/rf_scripts/source_preparation.py` (REM-49 comment-only), (3) B3 handoff.json record correction (REM-48).
- Source → target (all LIVE sha256, this attempt):

| file | source (iso) | bytes | target (production RF) | bytes |
|---|---|---|---|---|
| scripts/company_wiki_source.py | `7d1bd8f9d9122dc4a99465a8f9201e855417a5d0756f5bfdd6d404f7ca9e48ce` (B3 iso/fixed/rf_scripts/) | 20545 | `225fecdd7e48938a97c68724318f0860602a4b86a8d9e834a257243480094294` | 19364 |
| scripts/source_preparation.py | `91a6dc32466e9d67b9d034ac345349ee683f6d5fd9486a67cd3ade009c6ebf4d` (B3-PREREQ iso/fixed2/rf_scripts/, REM-49) | 9921 | `37a3eeaec73ed0124ac1e549bd4eecb49537676dc3ba9dac6f003496d0e6e2a7` | 9908 |

- Reference: B3-fixed `source_preparation.py` = `37a3eeaec73ed0124ac1e549bd4eecb49537676dc3ba9dac6f003496d0e6e2a7` (byte-equal to production ⇒ REM-49 deliberately not landed yet; fixed2 differs by comment-only line 138).
- Target state: UNFIXED (live `company_wiki_source.py` = 225fecdd… = card pre-fix pin).
- **Conditions (§十七 B-2): REM-47/48/49 closed; REM-49 硬前置已满足于 fixed2 — the REM-49 comment fix (`91a6dc32…` source_preparation.py) MUST ride the same promotion batch.** Also carried (B3 handoff): reviewer C2 — RF-1 conftest guard must NOT be presented as "the mechanism that prevents REM-12 recurring"; register-row closure semantics = fix+review+carrier landing, explicitly NOT promotion; W05B/W05C vendored suites not re-run (declared bounded gap).
- Verification (from card carriers): `Get-FileHash -Algorithm SHA256 scripts/company_wiki_source.py scripts/source_preparation.py` → expect post-promotion `7d1bd8f9…` / `91a6dc32…`; B3 binding `source_hashes`; B3-PREREQ `production_pins_rechecked`; `evidence/tree_integrity.txt` (fixed2 = fixed except 1 file); zero-behaviour-delta check for REM-49: comment-only diff + AST/tokenize/compile parity.
- git apply --check: UNRESOLVED-verification (skipped per step 5).

---

## B-3 — I-14-D → 脱敏类 `[^\s]+` (C13 narrowing + auth fail-closed)

- Card: `execution_runs/I-14-D/a20260919-01/` — rounds r1..r7; `reviewer_report_r7.md` verdict = `accepted_scoped`, **domain = "the r7 record fix only"**; the r6 grants stand ("the `[^\s]+` code fix closes F-REV-R5-01 within its domain"). ⇒ code deliverable = **r6 tree** (r7 changed records, not code).
- `changes.diff` headers (grep): single section `a/src/company_wiki/source_catalog/observability.py` → `b/src/company_wiki/source_catalog/observability.py` (CW-relative path).
- Source → target (all LIVE sha256, this attempt):

| role | path | sha256 | bytes |
|---|---|---|---|
| SOURCE (deliverable, r6) | `I-14-D/a20260919-01/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py` | `2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464` | 43746 |
| TARGET (production, sibling repo) | `C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\observability.py` | `a73826aa10c9c0bf09bb5dc73cb7466358497f9d9d8c66ba73bfe4b90ffebe5a` | 30087 |

- Round-tree ladder (live, for ordering context): narrow(r2)=`2aa5ed1a…`/41432, r3=`a551cc45…`/42839, r4=`15446f4d…`/42829, r5=`ca13fb81…`/43362, **r6=`2f644994…`/43746 (promote this)**.
- Target state: UNFIXED (live target 30087 B ≠ any narrow-tree size/hash; production predates narrowing).
- Note: `.review-zr407-20260818` snapshot of this repo — path probed `revenue-forecast/.review-zr407-20260818/src/.../observability.py` = ABSENT (and it would be a snapshot, never the target).
- **Conditions (§十七 B-3): r7 accepted; 目标②明列批次 2 候选.** Carried gaps (handoff): F-REV-D-02 dead `_VALUE` = promotion hazard (do NOT tidy dead constant and assume fix intact); F-REV-D-03 atom-table gap `token2/secret2…` needs follow-up card; F-REV-D-04 recorded; RULING 1 harness-rewrite transcription disclosed (restore point `672b88de…`); C12 promotion precondition carried from I-14-C; rule table 95 rows rc-3 negative BY DESIGN since r3.
- Verification (from card carriers): `Get-FileHash -Algorithm SHA256 <CW>\src\company_wiki\source_catalog\observability.py` → expect post-promotion `2f644994…`; `harness/run_i14d_oracle.py` (44 cases rc 0) / `harness/run_rule_table_i14d.py` (95 rows rc 3 by design) — cited only, NOT run here (no test runs in this attempt); r7 report §"Tree pins unchanged"; `changes.diff` round-trip (`after/git_apply_verification.json`, GIT_APPLY_REPRODUCES true — card-recorded).
- git apply --check: UNRESOLVED-verification (skipped per step 5; card's own r2 round-trip recorded as true).

---

## B-4 — I-14-F-R1 → conftest 150/60 (owner §16 E-1)

- Card: `execution_runs/I-14-F-R1/a20260922-01/` — handoff status `accepted_scoped` (reviewer_report sha256 `8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c`, 15841 B).
- `changes.diff` headers (grep): `--- /dev/null` + `+++ a/conftest.py`; `--- /dev/null` + `+++ a/tests/contract/test_short_basetemp_convention.py` ⇒ **both target NEW-FILES (create), not modifications** — verified live: both CW targets ABSENT.
- Source → target (all LIVE sha256, this attempt):

| file | source R1 `iso/tree/` | bytes | target CW production | bytes |
|---|---|---|---|---|
| conftest.py (CW repo root) | `a908c9da7b77ace08a8d60715093a19f28cb9ae67152ccf5627bb4d070084249` | 9031 | **ABSENT (new file)** | — |
| tests/contract/test_short_basetemp_convention.py | `1fd4e0d81750b7ddeb1826291b675722f7ab3afdd018f0f302021d68f9afa835` | 9899 | **ABSENT (new file)** | — |

- **I-14-F vs R1 byte relationship (live-measured):** R1's `iso/tree` = copy of sealed `I-14-F/a20260919-01/iso/tree` then edited per E-1. I-14-F originals: conftest `c22be9f366c5590e522b713374419e293259619ead5ee72e1adb1ee71e6f2c22`/7016 B, unit test `b0402b5693c1d5b13bb8c26225ac9da422f18bc428d0aee4ca80758830c74e7e`/6182 B (== R1 binding `pre_edit_hashes_match_I14F`) ⇒ R1 **supersedes** I-14-F's versions (bytes differ: 7016→9031, 6182→9899). **Promote R1's `iso/tree` pair; do NOT promote I-14-F originals** (I-14-F remains sealed/accepted as history; its doc defects F-2/F-3/F-4/F-6 are errata-registered by R1: ERR-I14FR1-F2/F3/F4/F6).
- **Conditions (§十七 B-4): CF-I14FR1-3 sampling obligation** — hook is REPO-GLOBAL at threshold 60; ANY CW pytest session with explicit basetemp >60 relocates; only 2 card nodes + the unit file were exercised ⇒ promotion card must sample a broader company-wiki suite before merge (reviewer Gap-5 ruling L143-L163: NOT blocking, promotion-time obligation). Also carried: CF-I14FR1-2 killed-session orphan cleanup caveat ships with the conftest; machine-specific calibration caveat (150/60 = this box's measured edges); N-1 per-row flip-reason restatement suggested at promotion re-record; the 52-char datapoint deliberately does NOT flip.
- Verification (from card carriers): re-derive `len+150>210 ⇔ len>60` from `iso/tree/conftest.py`; re-run 15-case unit suite; RED/GREEN/mutation at cwd 166/167; `Get-FileHash` targets above; commands.json argv/cwd 22/22 — cited only, NOT run here (no test runs in this attempt).
- git apply --check: UNRESOLVED-verification (skipped per step 5; new-file diffs → apply would be `--directory` create semantics at promotion time).

---

## B-5 — DW15 → prune/archive 五缺陷修复 (→ CW 仓)

- Card: `execution_runs/DW15-prune-repair/a20260922-01/` — handoff `accepted_scoped` (reviewer_report sha256 `a9b9076f731b8395c6f8a6fabcd90c835ea8a68a00cc7ffac7c9f14014b0801e`); five defects: 空目录也删 / 同日覆写 / 时钟取目录名 / TOCTOU / 崩溃后不可恢复.
- `changes.diff` headers (grep): 2 sections — `iso/baseline/.../prune_retired_evidence.py` → `iso/fixed/...` and `iso/baseline/.../archive_retired_evidence.py` → `iso/fixed/...`.
- Source → target (all LIVE sha256, this attempt):

| file | source `iso/fixed/…/source_catalog/` | bytes | target CW `src/company_wiki/source_catalog/` | bytes |
|---|---|---|---|---|
| prune_retired_evidence.py | `0c99bbe0c5f4ef16e7f84ba8aae0548ef6f59a0080274d5bd1ce83a7d37990b0` | 23115 | `2358c73b82da65e5292998e3dba71c6132eebab1ab6c88a224a736c1e5a8ae46` | 4658 |
| archive_retired_evidence.py | `bbe855e4495e82d2a40b0185c9db8efa2639449fdd5f768120538abb992b28ac` | 9894 | `143fef01fade43a5e6ae5c733d86e5ea6081482547c2560fc872990a9d8f53e0` | 3291 |

- Reference: `iso/baseline` live-hashed = target hashes exactly (`2358c73b…`/4658, `143fef01…`/3291) ⇒ target UNFIXED, promotion not yet performed; iso/baseline == production byte-verified.
- **Conditions (§十七 B-5): 晋升≠执行授权 — E-4: production prune/archive EXECUTION (dry-run included) stays UNAUTHORIZED and data-recovery reviewer re-sign stays UNSIGNED; promoting iso/fixed into company-wiki is a separate owner decision from executing the tools.** Breaking-API note (handoff): `'now'` is now REQUIRED, `apply` accepts a frozen plan; product contract tests encode the wrong oracle (per I-15-A) and are UNTOUCHED — they need replacement at promotion. Carried: F1-F6 non-blocking, U1-U8 registered; two unsigned open items (receipt durability JSON-vs-DB option; catalog_identity binding depth).
- Verification (from card carriers): `Get-FileHash -Algorithm SHA256 <CW>\src\company_wiki\source_catalog\{prune,archive}_retired_evidence.py` → expect post-promotion `0c99bbe0…` / `bbe855e4…`; card `source_anchors_sha256`; `iso/baseline vs iso/fixed tree comparison` (146 files, exactly 2 differ); guard `DW15-neg-bind-1` — cited only, NOT run here.
- git apply --check: UNRESOLVED-verification (skipped per step 5).

---

## B-6 — 既有 accepted 未晋升: I-14-F / I-14-I / I-10-B (及更早项)

All three cards: handoff status `accepted_scoped`, implementer never signed, production promotion never taken.

### B-6a — I-14-F (原 86/124 约定卡; sealed)

- `changes.diff` headers: `--- /dev/null → a/conftest.py`; `--- /dev/null → a/tests/contract/test_short_basetemp_convention.py` (2 new files, same pair as R1).
- Source (LIVE): `I-14-F/a20260919-01/iso/tree/conftest.py` = `c22be9f366c5590e522b713374419e293259619ead5ee72e1adb1ee71e6f2c22`/7016 B; `…/tests/contract/test_short_basetemp_convention.py` = `b0402b5693c1d5b13bb8c26225ac9da422f18bc428d0aee4ca80758830c74e7e`/6182 B. Target (CW root conftest.py / tests\contract\…) = ABSENT live (same as B-4).
- **Promotion disposition: SUPERSEDED by B-4 (I-14-F-R1). Do NOT promote I-14-F's versions** — its sealed versions carry the wrong calibration (R-1: reserve 124 is child's suffix; logon true 150; docstring 31+13+79=123≠124) which owner §16 E-1 resolved as 150/60 in R1. I-14-F stays sealed as history; its doc defects F-2/F-3/F-4/F-6 are errata-registered by R1 (ERR-I14FR1-*). Conditions carried: R-2 (I-14-E load band), R-3 (E-G4 geometry substitution), F-5/F-6/F-7.

### B-6b — I-14-I (natural_window 类型护栏)

- `changes.diff` headers: `--- a/iso/natural_window.py (pre-fix, sha256 7fff6f0c...) → +++ b/iso/natural_window.py (fixed, I-14-I)` — single file, attempt-local path.
- Source (LIVE): `I-14-I/a20260919-01/iso/natural_window.py` = `9edb95155202432ed01b2c68d06f74a00882287e934cda6cead0e14140493b04`/23162 B (== handoff fixed-SUT pin). Pre-fix image (unchanged): `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796`/20293 B.
- **Target (production `natural_window.py`): UNRESOLVED-path** — live probes: `revenue-forecast\scripts\natural_window.py` ABSENT; `company-wiki\src\company_wiki\source_catalog\natural_window.py` ABSENT; recursive search of CW `src\` and RF `scripts\` found none; full-tree search found ONLY plan-internal iso copies (I-14-B/I-14-H/I-14-I attempts). No production target path/hash can be cited ⇒ target cell UNRESOLVED (never invent one).
- Conditions carried: acceptance CONDITIONAL on wording (F-1: declaration 4 second half falsified — discrimination lives in the rider suite, not inside the frozen gate); CF-I14I-2 conditions: mandatory wording correction (fix covers `computed['basis']` only; `classify()` still echoes raw claim at iso:502 — failure mode NOT completely eliminated → own card F-2 registered) and NO widening of claim echo; I-14-H carrier update = separate bookkeeping act (flagged, not performed); SUT revision recorded r3 / `sut_sha256=9edb9515…`.

### B-6c — I-10-B (model_registry 省缺即抛 + 按语义角色定符号)

- `changes.diff` headers: `--- _scratch_import/before/model_registry.py → +++ _scratch_import/after/model_registry.py`.
- Source → target (LIVE sha256):

| file | source `I-10-B/a20260919-01/iso/rf/scripts/` | bytes | target RF `scripts/` | bytes |
|---|---|---|---|---|
| model_registry.py | `62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` | 30116 | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` | 26446 |

- Target state: UNFIXED (live target == handoff 前像 `9ec65295…`/26446 ⇒ promotion not yet performed).
- **Conditions (§十七 B-6 / I-10-B): carries the E1E7-registered E-flips** — errata E-1…E-7 = M05/M14/M20/M24 oracle.json defaults 相位翻转 (省缺即抛导致四卡各一 defaults-phase flip) + M14 三处旧行为记录 (E-5 OBS-SUPPLY-BOUND, E-6 OQ-03, E-7 signed_driver_probe.json). Landed append-only into the four oracle.md carriers by card `E1E7-ERRATA-LANDING/a20260921-01` (status accepted_scoped, reviewer_report sha256 `fb05120a0f388b18d6d301b31fcd2edc4d86d047c675ca2ad2fe2c926e9444d5`): 4/4 prefix proofs, 4/4 difflib insert proofs, 0 expectation/status/qualification changes; each card carries the non-promotion statement. **GAP-2 carried: the JSON carriers named in the E-list (oracle.json / cases.json / oq_rulings.json / signed_driver_probe.json) were NOT landed — only oracle.md; whether to run a JSON append pass is an orchestration call.** Also: acceptance does NOT authorize production promotion (separate owner decision); 5 随签未解除项 OQ-I10B-1/2/3 + F-R1 + F-R2; value-domain change = exactly 5 cells (compatibility_impact.md §5); GAP-5 stale key name `errata_pending_orchestration` vs actual `errata_pending` (registered, not fixed).
- Verification (from card carriers): `Get-FileHash -Algorithm SHA256 scripts/model_registry.py` → expect post-promotion `62f864b9…`; handoff `product_promotion` line; E1E7 landing `prefix_proof`/`after_hash`/`difflib` evidence ×4.
- git apply --check: UNRESOLVED-verification (skipped per step 5).

### B-6d — "及更早项"

- §十七 B-6 text says "(及更早项)" without enumerating further cards; §十七 D-group names only "I-14-F/I-14-F-R1 之外的历史 accepted 晋升排序随 B 组一并定" + REM-86/REM-79 registrations. No additional concrete source→target pair is derivable from the read carriers ⇒ **UNRESOLVED (no enumerated object)**.




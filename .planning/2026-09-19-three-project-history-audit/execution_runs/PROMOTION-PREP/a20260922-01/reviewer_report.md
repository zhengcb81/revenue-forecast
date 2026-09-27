# Independent Reviewer Report — PROMOTION-PREP / attempt a20260922-01

Card under review: `execution_runs/PROMOTION-PREP/a20260922-01/` (delivered 2026-09-22 13:22–13:32, top-level `handoff.status=review_pending`, 407 B; no `review.md` / `reviewer_report*` existed in this attempt before this report — this is the first independent review of this card).
Reviewer: independent re-review station of plan "三项目历史承诺逐项独立复审" — **not** the card implementer, **not** the parent agent that dispatched the original work. I write only this file and `reviewer_report.sha256`; I set no card status and edit no other byte.

VERDICT: ACCEPT

Scope of this verdict: the manifest card's own deliverables (`promotion_batch_manifest.md` + `oracle.md` + `binding.json` + `commands.json` + `decision.md` + `handoff.json` + `recovery/README.md`). No P1 found ⇒ ACCEPT (per rule 6). Findings: 0×P1, 1×P2, 6×P3, plus 7 unverified items.

---

## 1. Scope and non-actions

In scope: (1) line-by-line read of the six-row manifest and judgement of executability / verifiability / unambiguity; (2) independent re-measurement of at least three recorded sha256/path claims (I performed ~40, see §4); (3) freeze order of `oracle.md` vs any execution write (mtime/ctime + embedded-hash evidence); (4) zero production writes by this card; (5) line-by-line consistency with the downstream `PROMOTION-EXEC/a20260922-01` record; (6) adjudication of the two historically recorded parent-agent errors; (7) existence of every manifest-listed target in the production tree.

Out of scope / explicitly not done: no status transition (the card stays `review_pending` until the plan owner acts), no edit to `oracle.md`/`binding.json`/`commands.json`/`decision.md`/`promotion_batch_manifest.md`/`handoff.json`, no network, no test run, no `git status`, no `git add/commit/checkout/stash/restore/reset`.

## 2. Method (what I actually issued)

- Read tools: manifest (all 153 lines), `oracle.md`, `decision.md`, `binding.json`, `commands.json`, `handoff.json`, `recovery/README.md`, register §三十/§三十三/§三十四 (L789–887), register §四十五 (L1085–1092), `OWNER_DECISIONS.md` §十七 L382–414 + §十八 L418–426, `PROMOTION-EXEC` `decision.md`/`handoff.json`/`reviewer_report.md`/`changes.diff` headers/evidence listing.
- Hashing: `Get-FileHash -Algorithm SHA256` on every cited path I could reach, plus `git cat-file blob <rev>:<path>` copies written only to `%TEMP%\revcheck\` (outside both repos) and hashed there — used to reconstruct **pre-promotion production bytes** independently of any card's claim.
- Git (read-only only): `git log`, `git rev-parse`, `git diff HEAD --name-only [-- '!:!/.planning']`, `git ls-files --others --exclude-standard`, `git cat-file -e/-s/blob`, `git hash-object`, `git diff --no-index`. Never `git status`.
- Sibling repo `C:\Users\郑曾波\Projects\company-wiki` inspected read-only by the same commands.
- Timestamps: `CreationTime`/`LastWriteTime` per file, second granularity.

## 3. Freeze order and zero-production-write evidence (requirement 2)

`oracle.md` freeze — measured ctime/wtime (attempt dir):

| file | CreationTime | LastWriteTime | bytes |
|---|---|---|---|
| `evidence\` (empty dir scaffold) | 2026-09-22 13:22:41 | 13:22:41 | — |
| **`oracle.md`** | **13:22:57** | **13:22:57 (never rewritten)** | 1535 |
| `handoff.json` (skeleton) | 13:22:57 | 13:22:57 | 407 |
| `promotion_batch_manifest.md` | **13:25:03** (first created) | 13:32:16 (incremental saves) | 19190 |
| `binding.json` / `commands.json` / `decision.md` / `recovery\README.md` | 13:32:46 | 13:32:46 | 1580 / 2076 / 1844 / 1110 |

Conclusion: `oracle.md` (ctime == wtime == 13:22:57) precedes the **first content write of every other artifact** by ≥2 min 6 s (manifest first created 13:25:03). The only earlier timestamp is the empty `evidence\` directory scaffold (13:22:41, zero file content). `oracle.md` was never modified after creation (ctime==wtime), which is stronger evidence than mtime alone.

**Embedded-hash evidence: ABSENT (finding P3-2).** No file inside this attempt pins `oracle.md` — there is no `oracle.sha256` (sibling cards `B3-PREREQ` and `I-14-F-R1` do ship one), and none of `binding.json`/`commands.json`/`decision.md`/`recovery/README.md`/`promotion_batch_manifest.md` contains a single 64-hex digest. Freeze order therefore rests on timestamps + the `commands.json` C1 assertion only. Also, **no file inside the attempt records the deliverable's own sha256** (finding P3-3): `6759d1eb…` appears only in register §三十/§三十三/§三十四, not in the card's own carriers. I re-computed it (§4).

Zero production writes by this card — measured:

- `git diff HEAD --name-only -- ':!/.planning'` (revenue-forecast) = **0 paths** (re-measured at the end of this review; §7).
- Untracked, non-`.planning`: 46 paths (`.tmp-r41-mutation/*` wtime 2026-09-20 18:31, `assurance/unified_completion/manifests/plan_inputs.json.bak` 2026-09-21 07:09); **paths whose mtime falls in the PREP window 2026-09-22 13:15–13:45 = 0**.
- company-wiki: `git diff HEAD --name-only` = 3 (`CLAUDE.md`, `README.md`, `src/company_wiki/source_catalog/artifact_dag.py`, all wtime 2026-09-23 13:08:38 — outside the PREP window, pre-existing "dirty-3" already recorded by PROMOTION-EXEC); untracked = 0.
- All files of this attempt have wtime inside 13:22:41–13:32:46, i.e. confined to the card's own directory.

Method limitation (→ U-5): `git diff` cannot prove the absence of a transient write that was later reverted inside the window; the mtime sweep of untracked paths plus the confined attempt mtimes is the strongest indirect evidence available.

## 4. Independent spot-checks (requirement 1 — my own measurements, parent's 3/3 not reused)

I redid all three cells the parent had sampled, plus the rest of the source/target columns, and I added a third evidence channel (pre-promotion git blobs + PROMOTION-EXEC before-images) so that no single card's claim is trusted.

### 4.1 The deliverable itself

| object | my measurement | recorded value | result |
|---|---|---|---|
| `promotion_batch_manifest.md` | `6759d1eb7044a3a4e5af75ffecd35fb612a2d9b26f0f361b15d5dcdee2073aac` / 19190 B | register §三十 same | **MATCH** |

### 4.2 Source cells (live re-hash of the iso/card paths)

| # | row | path (card-relative) | my sha256 / bytes | manifest | result |
|---|---|---|---|---|---|
| 1 | B-1 | `B1-I08C-product-fixes/a20260921-01/iso/fixed/rf/scripts/revenue_core.py` | `8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883` / 25842 | same | MATCH |
| 2 | B-1 | `…/rf/scripts/revenue_publication.py` (parent's cell, redone) | `bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0` / 24917 | same | MATCH |
| 3 | B-1 | `…/rf/scripts/revenue_report.py` | `212f00598feca408dc429d4c7a5332131ce25f1165b079347e4b295345df7d3b` / 73973 | same | MATCH |
| 4 | B-2 | `B3-I05C…/iso/fixed/rf_scripts/company_wiki_source.py` (parent's cell, redone) | `7d1bd8f9d9122dc4a99465a8f9201e855417a5d0756f5bfdd6d404f7ca9e48ce` / 20545 | same | MATCH |
| 5 | B-2 | `B3-PREREQ/a20260922-01/iso/fixed2/rf_scripts/source_preparation.py` | `91a6dc32466e9d67b9d034ac345349ee683f6d5fd9486a67cd3ade009c6ebf4d` / 9921 | same | MATCH |
| 6 | B-3 | `I-14-D/a20260919-01/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py` | `2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464` / 43746 | same | MATCH |
| 7 | B-4 | `I-14-F-R1/a20260922-01/iso/tree/conftest.py` | `a908c9da7b77ace08a8d60715093a19f28cb9ae67152ccf5627bb4d070084249` / 9031 | same | MATCH |
| 8 | B-4 | `…/iso/tree/tests/contract/test_short_basetemp_convention.py` | `1fd4e0d81750b7ddeb1826291b675722f7ab3afdd018f0f302021d68f9afa835` / 9899 | same | MATCH |
| 9 | B-5 | `DW15-prune-repair/a20260922-01/iso/fixed/company_wiki/source_catalog/prune_retired_evidence.py` (parent's cell, redone) | `0c99bbe0c5f4ef16e7f84ba8aae0548ef6f59a0080274d5bd1ce83a7d37990b0` / 23115 | same | MATCH |
| 10 | B-5 | `…/iso/fixed/company_wiki/source_catalog/archive_retired_evidence.py` | `bbe855e4495e82d2a40b0185c9db8efa2639449fdd5f768120538abb992b28ac` / 9894 | same | MATCH |
| 11 | B-5 ref | `…/iso/baseline/company_wiki/source_catalog/prune_retired_evidence.py` | `2358c73b82da65e5292998e3dba71c6132eebab1ab6c88a224a736c1e5a8ae46` / 4658 | "= target" | MATCH |
| 12 | B-5 ref | `…/iso/baseline/…/archive_retired_evidence.py` | `143fef01fade43a5e6ae5c733d86e5ea6081482547c2560fc872990a9d8f53e0` / 3291 | "= target" | MATCH |
| 13 | B-6a | `I-14-F/a20260919-01/iso/tree/conftest.py` | `c22be9f366c5590e522b713374419e293259619ead5ee72e1adb1ee71e6f2c22` / 7016 | same | MATCH |
| 14 | B-6b | `I-14-I/a20260919-01/iso/natural_window.py` | `9edb95155202432ed01b2c68d06f74a00882287e934cda6cead0e14140493b04` / 23162 | same | MATCH |
| 15 | B-6c | `I-10-B/a20260919-01/iso/rf/scripts/model_registry.py` | `62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` / 30116 | same | MATCH |
| 16 | B-3 ladder | `…/iso/product_narrow/…/observability.py` (r2) | `2aa5ed1a219084a67f040388072aa94d7432c63414b6692060f1b4d6b4e12bde` / 41432 | `2aa5ed1a…`/41432 | MATCH |
| 17 | ladder r3 | `…/product_narrow_r3/…` | `a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda` / 42839 | same | MATCH |
| 18 | ladder r4 | `…/product_narrow_r4/…` | `15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1` / 42829 | same | MATCH |
| 19 | ladder r5 | `…/product_narrow_r5/…` | `ca13fb81aa2a1234ba760f49576a6409bbd3b1397f921f2e73311f90a263fc45` / 43362 | same | MATCH |
| 20 | cited report | `I-14-F-R1/…/reviewer_report.md` | `8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c` / 15841 | same | MATCH |
| 21 | cited report | `DW15-prune-repair/…/reviewer_report.md` | `a9b9076f731b8395c6f8a6fabcd90c835ea8a68a00cc7ffac7c9f14014b0801e` / 19466 | same | MATCH |
| 22 | cited report | `E1E7-ERRATA-LANDING/a20260921-01/reviewer_report.md` | `fb05120a0f388b18d6d301b31fcd2edc4d86d047c675ca2ad2fe2c926e9444d5` / 10676 | same | MATCH |

### 4.3 Target-column cells (independent channels: pre-promotion git blobs + PROMOTION-EXEC before-images)

| row | target | my channel | my sha256 / bytes | manifest | result |
|---|---|---|---|---|---|
| B-1 | RF `scripts/revenue_core.py` (pre) | `git cat-file blob ec307d20~1:…` **and** `PROMOTION-EXEC/recovery/before_images/B-1/` | `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae` / 14136 | same | MATCH |
| B-1 | RF `revenue_publication.py` (pre) | before-image | `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba` / 10681 | same | MATCH |
| B-1 | RF `revenue_report.py` (pre) | before-image | `a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f` / 69765 | same | MATCH |
| B-2 | RF `company_wiki_source.py` (pre) | git blob **and** before-image | `225fecdd7e48938a97c68724318f0860602a4b86a8d9e834a257243480094294` / 19364 | same | MATCH (this is the disputed cell — §6) |
| B-2 | RF `source_preparation.py` (pre) | git blob **and** before-image | `37a3eeaec73ed0124ac1e549bd4eecb49537676dc3ba9dac6f003496d0e6e2a7` / 9908 | same | MATCH |
| B-3 | CW `…/observability.py` (pre) | before-image | `a73826aa10c9c0bf09bb5dc73cb7466358497f9d9d8c66ba73bfe4b90ffebe5a` / 30087 | same | MATCH |
| B-4 | CW `conftest.py` (pre) | `git cat-file -e ac4ebd0~1:conftest.py` → rc 128 "not in ac4ebd0~1" | ABSENT | ABSENT | MATCH |
| B-4 | CW `tests/contract/test_short_basetemp_convention.py` (pre) | `git cat-file -e` → rc 128 | ABSENT | ABSENT | MATCH |
| B-5 | CW `prune_retired_evidence.py` (pre) | git blob + before-image | `2358c73b…` / 4658 | same | MATCH |
| B-5 | CW `archive_retired_evidence.py` (pre) | git blob + before-image | `143fef01…` / 3291 | same | MATCH |
| B-6c | RF `model_registry.py` (pre) | before-image | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` / 26446 | same | MATCH |

Score: **every reachable full-hash claim in the manifest matched my independent measurement (≈40/40; two claims unverifiable → §8).**

### 4.4 Row-by-row executability / verifiability / unambiguity (requirement 1)

| row | 源→目标 stated literally? | verifiable? | unambiguous? | verdict + note |
|---|---|---|---|---|
| B-1 | yes (`iso/fixed/rf/scripts/` + 3 filenames + full hashes, RF `scripts/` targets) | yes (`Get-FileHash` before/after + card anchors) | yes | **PASS** |
| B-2 | yes (two named files, both repos pinned by hash; `source_preparation.py` repo ownership resolved by byte-equality evidence L53) | yes | yes — and downstream resolved it by hash exactly as the manifest invited | **PASS** |
| B-3 | yes (absolute CW path, r6 source, r7 = record-fix-only rationale spelled out) | yes | yes | **PASS** |
| B-4 | yes (`iso/tree/` pair; targets declared ABSENT/new-file, live-confirmed) | yes | yes; CF-I14FR1-3 sampling is an explicit *external* promotion-time obligation, not an execution gap | **PASS** |
| B-5 | **abbreviated**: `iso/fixed/…/source_catalog/`, `iso/baseline/.../…` (the card's own `changes.diff` headers are literal `…/company_wiki/source_catalog/…`) | yes | resolvable but needs one resolution step — exactly the spot where the parent guessed wrong (§6) | **PASS with P3-1** |
| B-6a | yes; instruction is an explicit **negative** action ("Do NOT promote") — executable as a do-nothing with a check | yes (hash inequality check) | yes | **PASS** |
| B-6b | target cell = `UNRESOLVED-path`, probes listed | verification = re-probe; **not executable by design** | explicitly, honestly non-executable (oracle rule "UNRESOLVED preferred over guesses") | **PASS (declared gap)** — divergent from register §三十 resolution → P3-5 |
| B-6c | yes | yes | yes (E1E7 errata conditions carried) | **PASS** |
| B-6d | `UNRESOLVED (no enumerated object)` — matches §十七 D-group, which names no further pair | n/a | honest | **PASS** |
| all 6 `git apply --check` cells | `UNRESOLVED-verification (skipped per step 5)` | declared, not faked | consistent with `oracle.md` step 5 | **PASS (declared gap)** |

Coverage vs owner §十七: manifest covers B-1..B-6; §十七 has B-1..B-8 and §十八 maps B-7 to `GATE-OQ-FIX` and B-8 to an external party, so no promotion item is lost — but the manifest never says so (P3-4).

## 5. Consistency with downstream `PROMOTION-EXEC/a20260922-01` (requirement 3)

Read: its `decision.md` (per-row table), `handoff.json` (`accepted_scoped`, carrier `reviewer_report.md` `E2A42D2D…`/20561 B), `reviewer_report.md` (row-outcome table L60–79), `changes.diff` (11 `--- row … ---` sections), `recovery/before_images/` (9 files), `evidence/` (18 files). Row-by-row, with ≥3 rows actually re-derived (I did 8):

| row | manifest says | PROMOTION-EXEC did | my current-state check | aligned? |
|---|---|---|---|---|
| B-1 | 3 RF scripts `1821fd2a/183803bb/a85fb484` → `8a761498/bc2bb4a3/212f0059` | 3 `--- row B-1 ---` sections; RF wtime 20:31:43; parent commit `ec307d20` 20:44:25 names exactly these 3 hashes | RF live = `8a761498…`/25842, `bc2bb4a3…`/24917, `212f0059…`/73973 = sources | **YES** |
| B-2 | `225fecdd/37a3eeae` → `7d1bd8f9/91a6dc32`, **same batch** | 2 sections in the same card/commit `ec307d20` (message lists both) | RF live = `7d1bd8f9…`/20545 + `91a6dc32…`/9921 | **YES** (same-batch constraint honoured) |
| B-3 | `a73826aa…`/30087 → `2f644994…`/43746 | `--- row B-3 ---`; its reviewer measured live `2f644994…`/43746 = OK at 20:08–20:13 | CW live = **`edcbeccb…`/43707** (≠ source) | **execution matched; post-commit drift → P2-1** |
| B-4 | 2 new files `a908c9da`/`1fd4e0d8` | `--- row B-4(NEW) ---` `--- /dev/null` ×2; pre-image absence confirmed by me (`rc 128`) | CW live `conftest.py` = `a908c9da…`/9031 ✓; `tests/contract/test_short_basetemp_convention.py` = **`dfb7c6cd…`/11366** (≠ `1fd4e0d8…`/9899) | **creation matched; post-commit drift → P2-1** |
| B-5 | `2358c73b/143fef01` → `0c99bbe0/bbe855e4`; **E-4: promotion ≠ execution authorization** | 2 sections; commit message `ac4ebd0` keeps "code-only, execution still E-4 owner-unsigned" | CW live = `0c99bbe0…`/23115 + `bbe855e4…`/9894 = sources | **YES** |
| B-6a | **Do NOT promote** (`c22be9f3`/`b0402b56` must not land) | "NOT PROMOTED — verified nothing landed" | CW `conftest.py` = `a908c9da` ≠ `c22be9f3`; CW unit test = `dfb7c6cd` ≠ `b0402b56` | **YES** |
| B-6b | `UNRESOLVED-path`, "never invent one"; register §三十 = coupled to I-14-B (new file, I-14-B first) | "BLOCKED-unresolved: no path guessing → I-14-I SKIPPED" | `natural_window.py` ABSENT in RF `scripts\` **and** CW `src\` (my re-probe) | **YES** (skipped, coupling not broken); register/manifest wording divergence → P3-5 |
| B-6c | `9ec65295…`/26446 → `62f864b9…`/30116, E1E7 conditions carried | copied, focused battery **31 failed**, then **STOP + REVERT** to `9ec65295…` (before-image hash matched by me), other rows continued | RF live = `62f864b9…`/30116 = source, **re-promoted later by `MODEL-ORACLE-ALIGN` (commit `5fd82de7`, 21:00:11)**, not by this card | **YES** for PROMOTION-EXEC's own action; the eventual landing satisfies the manifest's target cell but via a different card (U-6) |

Any deviation is listed as a finding. Exactly one exists (P2-1), and it occurred **after** PROMOTION-EXEC's reviewer had already verified byte-equality — during the parent's commit step.

## 6. The two historically recorded parent-agent errors (requirement 4)

**Error A — hint `7D1BD8F9` vs live `225fecdd`.**
Ruling: **parent dispatch-hint error, corrected by the card's live measurement — NOT a manifest defect.**
My independent evidence: (a) `git cat-file blob ec307d20~1:scripts/company_wiki_source.py` = `225fecdd…`/19364, i.e. pre-promotion production really was `225fecdd`; (b) `PROMOTION-EXEC/recovery/before_images/B-2/company_wiki_source.py` = `225fecdd…`/19364; (c) `7d1bd8f9…`/20545 is the **B3 card iso source** (my hash), which only became production after `ec307d20`. The manifest's L50 `225fecdd…` was therefore correct at freeze time; the card's refusal to adopt the hint is exactly what `oracle.md` L6 mandates.

**Error B — parent's flat path vs actual nested path (B-5).**
Ruling: **parent's path-guess error, not a manifest path defect — but the manifest does carry an abbreviation (P3-1).**
My independent evidence: `DW15-prune-repair/a20260922-01/iso/fixed/company_wiki/source_catalog/prune_retired_evidence.py` exists and hashes `0c99bbe0…`/23115 (only one match for the manifest's `iso/fixed/…/source_catalog/` pattern); no `iso/fixed/source_catalog/` exists; the card's `changes.diff` headers are the literal `iso/baseline/company_wiki/source_catalog/…` → `iso/fixed/company_wiki/source_catalog/…`, which the manifest transcribed in abbreviated form (L102/L105). So the parent's MISSING report came from its own flat guess, while the manifest's cell remained resolvable — consistent with, but not identical to, register §三十's "清单 changes.diff 两节本就正确".

## 7. Completeness of targets in the production tree (requirement 5)

Every target named by the manifest, checked read-only **now** (2026-09-24 run):

| target | state | manifest expectation |
|---|---|---|
| RF `scripts/revenue_core.py` | present, `8a761498…`/25842 | promoted = source ✓ |
| RF `scripts/revenue_publication.py` | present, `bc2bb4a3…`/24917 | ✓ |
| RF `scripts/revenue_report.py` | present, `212f0059…`/73973 | ✓ |
| RF `scripts/company_wiki_source.py` | present, `7d1bd8f9…`/20545 | ✓ |
| RF `scripts/source_preparation.py` | present, `91a6dc32…`/9921 | ✓ |
| RF `scripts/model_registry.py` | present, `62f864b9…`/30116 | ✓ (landed by a later card) |
| CW `src/company_wiki/source_catalog/observability.py` | present, `edcbeccb…`/43707 | expects `2f644994…`/43746 → **drift, P2-1** |
| CW `src/company_wiki/source_catalog/prune_retired_evidence.py` | present, `0c99bbe0…`/23115 | ✓ |
| CW `src/company_wiki/source_catalog/archive_retired_evidence.py` | present, `bbe855e4…`/9894 | ✓ |
| CW `conftest.py` | present, `a908c9da…`/9031 | ✓ (new file created) |
| CW `tests/contract/test_short_basetemp_convention.py` | present, `dfb7c6cd…`/11366 | expects `1fd4e0d8…`/9899 → **drift, P2-1** |
| `natural_window.py` (B-6b) | ABSENT in both repos | manifest claims UNRESOLVED (no expected path) ✓ |

**Missing: 0. Unexpected/extra: 0.** (The B-6a target pair is the same two files as B-4's, created by B-4 — not an out-of-manifest addition; their hashes prove the I-14-F originals never landed.)

## 8. Findings

| id | sev | finding | evidence |
|---|---|---|---|
| F-1 | **P2** | Manifest's post-promotion verification expectations for **B-3** and **B-4** no longer hold on today's tree: CW `observability.py` = `edcbeccb…`/43707 (source `2f644994…`/43746; −1 dead assignment `quote = text[value_start]` at r6 L400 — I read L392–446 and confirmed that local is never read inside `_redact_assignments`, so the removal is behaviour-neutral by inspection, **not** runtime-tested here) and `tests/contract/test_short_basetemp_convention.py` = `dfb7c6cd…`/11366 (source `1fd4e0d8…`/9899; +1467 B Windows-only `pytestmark` guard + computed fixtures, `- import os`). Drift happened **after** PROMOTION-EXEC's byte-exact delivery (its reviewer measured `2f644994…`/43746) and **at** the parent's commit `ac4ebd0` (2026-09-22 22:23, message: "gate-compliance + lint adaptations"); register §四十五 L1085–1092 already discloses both final hashes, and `git log -- <file>` shows only `ac4ebd0` ever touched them. Consequence: a literal re-run of the manifest's Verification column yields 2 FAILs. Not blocking this card (freeze-time values were correct and the execution matched them). |
| F-2 | P3 | **B-5 source path written as an ellipsis** (`iso/fixed/…/source_catalog/`, L102/L105) instead of the literal `iso/fixed/company_wiki/source_catalog/…` found in the card's `changes.diff`; uniquely resolvable (I proved one match) but not copy-paste executable — the exact looseness that produced the parent's flat-path false MISSING. |
| F-3 | P3 | **No embedded hash evidence for the oracle freeze**: attempt has no `oracle.sha256`, and no carrier contains any 64-hex digest (unlike sibling cards `B3-PREREQ`, `I-14-F-R1`); freeze order is provable only from ctime/wtime. |
| F-4 | P3 | **No self-pin of the deliverable**: `6759d1eb…`/19190 appears in no file of this attempt (I grepped all seven carriers); it survives only in the register. I re-computed it: `6759d1eb7044a3a4e5af75ffecd35fb612a2d9b26f0f361b15d5dcdee2073aac`. |
| F-5 | P3 | **Scope note missing**: title = "B-1..B-6", L7 says the source table was read as "rows B-1..B-7", while §十七 actually lists B-1..B-8; the manifest nowhere states why B-7 (GATE OQ-01/02) and B-8 (external) are excluded. §十八 routes them elsewhere, so there is no functional gap — a reader must leave the card to learn this. |
| F-6 | P3 | **B-6b cell vs register resolution not reconciled in the artifact**: manifest cell = `UNRESOLVED-path`; register §三十 L813 resolves it as `new-file, inherits-from I-14-B promotion` (wave order I-14-B first). By design the frozen manifest was not rewritten, and PROMOTION-EXEC skipped correctly — but two authoritative carriers now describe the same cell differently. |
| F-7 | P3 | **Register-side label typo (outside my write scope)**: register §四十五 L1092 says the disclosed byte deviation attaches to "B-3/B-5 晋升行", yet the two adapted files belong to **B-3 and B-4**; B-5's `prune/archive` are byte-identical to their sources (I measured `0c99bbe0…`/`bbe855e4…` live). I may not edit the register — reported for the parent/owner. |

**0×P1 ⇒ `VERDICT: ACCEPT`** (restated: no blocking defect in the reviewed card).

## 9. Unverified items (evidence missing → "未证实", no green invented)

| id | item | why |
|---|---|---|
| U-1 | B-6a sealed source unit test `b0402b56…`/6182 (`I-14-F/a20260919-01/iso/tree/tests/contract/test_short_basetemp_convention.py`) | **ACL denied**: `Test-Path`/`ReadAllBytes` → "Access to the path … is denied"; path is not in HEAD either (`git cat-file -e` rc 128). Unverified. |
| U-2 | B-6b pre-fix image `7fff6f0c…`/20293 | exists only as text inside `changes.diff` header; the pre-fix file is not on disk, so no independent re-hash. |
| U-3 | all six `git apply --check` cells | declared `UNRESOLVED-verification` by the card per `oracle.md` step 5; I did not substitute a run (my card authorises read-only verification only, and apply-checks on copies were not part of this review's mandate). |
| U-4 | cited card test outcomes (13-node suite, FC-904 11 passed, rem49 5 passed, I-14-D 44/95 harness, DW15 guard) | no test runs permitted in this review; I only confirmed the corresponding `evidence/*.txt` files exist with plausible sizes. |
| U-5 | absolute absence of transient production writes inside 2026-09-22 13:15–13:45 (write-then-revert) | `git diff` cannot see them; indirect evidence only (diff=0, 0/46 untracked paths in window, attempt-confined mtimes). |
| U-6 | whether the E1E7 forward-disclosures (M05/M14/M20/M24 defaults-phase flips) are now ACTIVE after `MODEL-ORACLE-ALIGN` re-promoted `model_registry.py` | beyond this card's scope; PROMOTION-EXEC recorded them INACTIVE at its freeze, and no re-audit was performed here. |
| U-7 | the card's declaration "zero tests run / no git writes during this attempt" | no independent artifact can prove a negative; accepted as declared, corroborated by `commands.json`'s `explicitly_not_run` and by the attempt's confined timestamps. |

## 10. Boundary statement (discipline compliance)

- Production tree read-only: **no file outside `.planning\` was created, modified, or deleted by me**; `git diff HEAD --name-only -- ':!/.planning'` = **0** both at the start and at the end of this review (re-measured after writing this report).
- No `git status`; only `git log` / `git diff` / `git ls-files` / `git rev-parse` / `git cat-file` / `git hash-object` / `git diff --no-index` (read-only). No `add`/`commit`/`checkout`/`stash`/`restore`/`reset`. No network. No test execution.
- Write scope: exactly two new files in this attempt — `reviewer_report.md` and `reviewer_report.sha256`. No byte of `oracle.md`, `binding.json`, `commands.json`, `decision.md`, `promotion_batch_manifest.md`, `handoff.json` was touched; `handoff.json` still reads `status=review_pending` / `implementer_signed=false`; status remains the plan owner's call, not mine.
- Scratch copies of git blobs were written only to `%TEMP%\revcheck\` (outside both repos).
- Encoding of this file: UTF-8 without BOM, LF line endings; byte count and sha256 are reported to the dispatcher and pinned in `reviewer_report.sha256` (format `<sha256>  reviewer_report.md`, no trailing newline, 84 bytes) — a file cannot contain its own digest.

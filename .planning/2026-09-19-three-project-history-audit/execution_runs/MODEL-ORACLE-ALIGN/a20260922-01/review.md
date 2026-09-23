# review.md — carrier landing (bookkeeping transcription), card MODEL-ORACLE-ALIGN a20260922-01

## VERDICT BLOCK (transcribed, not authored)

- verdict: **`accepted_scoped`**
- carrier: `<PLAN>\execution_runs\MODEL-ORACLE-ALIGN\a20260922-01\reviewer_report.md`
- carrier sha256: `399f4e60ff134c2e1cef5b45d665a948f333e27c9dcc8a3e0e512d3ef5f8d01c`
- carrier bytes: **22499** (verified live before landing); sidecar `reviewer_report.sha256` exists and content-matches: `399f4e60ff134c2e1cef5b45d665a948f333e27c9dcc8a3e0e512d3ef5f8d01c  reviewer_report.md  bytes=22499`
- carrier pin / line ranges (carrier = 124 lines): verdict `L10–L12` · accept scope `L14–L20` · findings F1–F9 `L24–L97` · observations O1–O5 `L101–L107` · unverified list `L109–L118` · reviewer boundary `L120–L124`
- verdict line verbatim (carrier L10): `## VERDICT: accepted_scoped`
- reviewer: **独立复核** — delegated independent reviewer subagent of parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`; tools `read`/`grep`/`pwsh` only, git read-only, one permitted pytest re-run with all output in `%TEMP%`; carrier reports "9 items confirmed", O1–O5 observations non-blocking.
- authority: **bookkeeping transcription adds no acceptance of its own** — this file re-states the carrier's verdict for parent-side bookkeeping; it signs nothing and creates no acceptance. Never self-signed: `signature = null`, `self_sign = false`, implementer never signs acceptance.

## Transcription in substance — 9/9 findings confirmed by 独立复核

### F1 Freeze-first — CONFIRMED
- `oracle.md` live re-hash = `146ce313f7158da8ef1093961b1ebd1de5cfef0e4b0ffbe0d733c8fb4c2302da` / **12543** B, matching binding + handoff + 08 ledger.
- Ordering (live CreationTime sort): oracle **20:09:38** < recovery before-images **20:10:23** < binding 20:10:52 < iso trees 20:11:11–20:11:22 < first evidence `01_red` **20:11:34** — oracle strictly first; first evidence 116 s later.
- Production **untouched at capture**: the 20:10:23 before-images re-hash to pre-card contents (`66516452…/7988`, `9ec65295…/26446`) ⇒ freeze preceded every production write by ≥ 45 s (mtime unusable — `Copy-Item` preserves source mtimes, as disclosed).
- **Write windows derived for both files**: `tests/test_model_economic_guardrails.py` = **(20:16:41, 20:17:01]** (lower = `04b` evidence LastWrite with PROD-PREWRIITE-GUARDS still reading `66516452…`; upper = derived pyc live-re-measured 13577 B @ 20:17:01; 08 ledger recorded source-preserved mtime 20:16:08); `scripts/model_registry.py` = **(20:16:41, 20:19:15]** (upper = iso copy created 20:19:15 already hashing `62f864b9…`). Both strictly after the freeze.

### F2 Production finals — CONFIRMED (live re-hash 20:35)
- `scripts/model_registry.py` = **`62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` / 30116**, **== I-10-B iso source byte-exact (re-hashed)**; attempt iso + iso_promoted copies same.
- `tests/test_model_economic_guardrails.py` = **`89a76809321e87d852ec8d5863650eed8ac1b47c52c8f1b38db4768f7d5ac82a` / 10414**; before-image **`665164528d7d37663ff37474ddae20bfcf3c16eceefde3e6f54473324251ab77` / 7988 byte-identical to PROMOTION-EXEC's B-6c image `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`** (registry before-image = same `9ec65295…/26446`, byte-identical to PROMOTION's B-6c `model_registry.py`, live re-hashed).
- companion `scripts/model_extensions.py` = `9939480b…/14475` == binding pin, untouched.

### F3 RED / GREEN / mutation chain — CONFIRMED
- `01_red`: `31 failed, 53 passed, 177 subtests passed`, 1819 lines, 31 short-summary entries = 6 FAILED + 25 SUBFAILED; reconciles with binding (`6+53=59`, `25+177=202`).
- **Reviewer's OWN set-diff** (not the card's Compare-Object): extracted all 31 `^(FAILED|SUBFAILED)` lines from `01` and from PROMOTION-EXEC `B-6c_model_focused_tests.txt` (live `a266a922…/111044` = binding pin) → **`Compare-Object` EMPTY on 31 vs 31 — line-identical failed-test set**.
- All `model_registry.py:<line>` refs anywhere in `01` = **`:410` ×29, all other registry lines ×0**; per-block split = 29 blocks, **27/29 carry the explicit `scripts\model_registry.py:410` frame**, the 2 without are exactly the `assertRaisesRegex` message-mismatch failures whose E-line quotes the verbatim `:410` message (2 message-quote blocks).
- `02` GREEN promoted / `03` GREEN before-image (dual-tree) / `04b` restored = each **`59 passed, 202 subtests passed`** rc 0; `04a` mutation = `1 failed` with traceback terminating `ModelRegistryError: missing driver for bank_revenue: other_revenue has no explicit default` / `scripts\model_registry.py:410` — defect-1 message at **:410**.
- Evidence `02–07` all re-hash byte-exact to `08_final_integrity.txt` ledger (9/9 OK) — raw evidence unmodified since sealing.

### F4 31-row table + 3 sampled cases — CONFIRMED
- decision.md per-case table = rows 1–6 (FAILED) + rows 7–31 (SUBFAILED) = **31 rows**, each with RED line citation (internal consistency of 行 ranges checked).
- Split **31 explicit-default / 0 assertion rewrites / 0 STOP** in both decision counts and `handoff.per_case_alignment_table`.
- Rule statement present: none of the 31 asserts the silent-fill itself — **hidden 0.0 was at before-image `model_registry.py:335`** (`drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))`, also the removed line in changes.diff §2) + dual-tree backstop.
- **3 cases live-verified against the production test file:**
  1. `test_bank_negative_rates_preserve_sign_without_probability_clamp` (line 113): `"other_revenue": [0]` now explicit; assertions business-identical (`assertEqual(…, [5])`, bounds `(-inf, inf)` / `(0, 1)` verbatim).
  2. `test_public_calculator_preserves_every_existing_case_without_mutation` (lines 55–65): sweep retargeted `drivers→explicit` via `_with_explicit_missing_defaults` (line 60); no-mutation assertion retargeted to the same property (line 63); numeric `assertAlmostEqual(observed, target)` loop verbatim.
  3. `test_inconsistent_customer_timing_cannot_create_negative_exposure` (lines 141–149): `"usage_revenue": [0]` explicit; `assertRaisesRegex(ModelRegistryError, "time exposure")` unchanged — guarded rule still reachable and asserted.
- **Reviewer-derived full before→after diff (`git diff --no-index`): −5 / +40, exactly as claimed**; the −5 = 3 sweep lines retargeted + overflow tuple line + `fee_revenue` line (the latter four reappear with only the added explicit field + citation comment); every other assertion-strength line byte-identical; **8 neighbor test functions zero diff**.

### F5 Post-promotion verifications — CONFIRMED
- `05` = `59 passed, 202 subtests`; `05b` verbose = `59 passed, 202 subtests`, 0 FAILED/SUBFAILED (two independent rc-0 runs); `05a` py_compile = `PYCOMPILE_OK both`.
- `06` 13-node I-08-C under full promotion = **`13 passed`** rc 0.
- `07` I-10-B focused verify = `phase = after | total = 7 | passed = 7 | failed = 0`, all R-B1/R-B2 probes PASS; **`verification_after.json` live re-hash = `b7a925f5b5a9e4af4cf77532999521427b79edbc6c51c7bd1aaf2a03c270da86` / 1766 B == I-10-B's own frozen GREEN artifact (byte-identical, both re-hashed)**.
- Reviewer's own permitted re-run: RC=0, `16 passed, 134 subtests` on the live production tree, post-run write-scan zero modifications.

### F6 Zero-touch — CONFIRMED
- **9 protected neighbors re-hashed live == binding pins**, incl. **`scripts/model_extensions.py` = `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`** and gate **`tools/pre_push_gate.py` = `3df161a7ceea17de95b36845bdb3c4cee729dca215c56853868780dce7331484`**, plus `tests/conftest.py 6da47830…`, `tests/test_model_registry_contract.py f3cf1e5c…`, three other battery files (`46023006…`, `954e08ac…`, `0fab9aea…`), `tests/test_models.py 0ea8c5a3…`, `scripts/forecast/segments.py 95555509…`. Registry before-pin `9ec65295…` correctly absent from production, byte-exact copy survives in `recovery/before_images/`.
- **M05/M14/M20/M24 `oracle.md` == HEAD blobs 4/4 MATCH** (`git hash-object` vs `HEAD:<path>`; blobs `cbea2e8f…`, `aee22197…`, `d6a7f115…`, `584a0426…`).
- **CW porcelain = pre-existing + PROMOTION's only**: `6 " M" + 2 "??"` (PROMOTION's B-4 files `conftest.py` + `tests/contract/test_short_basetemp_convention.py`), no path attributable to this card (HEAD `f39bd5a6`).
- **git**: RF `HEAD = 95df2661…` (GATE-OQ-FIX) and **reflog newest = `95df2661`, no entry after it, no card-authored commit** ⇒ zero git writes by this card. Root `.pytest_cache` untouched (2026-07-12); disclosed pyc `13577 B @ 20:17:01` among 357 siblings; no new pyc in `scripts/`.

### F7 Consequence statement — CONFIRMED PRESENT (+ no-edit half blob-proven)
- decision.md §权威链-4 verbatim: B-6c landed ⇒ **M05/M14/M20/M24 four defaults-phase forward-disclosures flip INACTIVE→ACTIVE; "那些卡的字节本卡一字未动"**.
- `handoff.json.consequences_recorded_not_acted[0]` carries the same statement; the **no-edit half is blob-proven** by F6's 4/4 `oracle.md == HEAD` comparisons — **E1E7 carriers untouched** by this card (flips = parent bookkeeping).

### F8 Three boundary incidents disclosed — ALL THREE CONFIRMED
1. py_compile first-use CLI misuse rc1 → one git-ignored pyc refreshed (357 siblings, 13577 B @ 20:17:01, both live-verified) → explicit-cfile retry rc0 (`PYCOMPILE-ATTEMPT1`/`PYCOMPILE-RETRY`, handoff `boundary_incidents_disclosed[0]`).
2. `Copy-Item` preserved source mtime on `model_registry.py` (2026-09-20 19:22:26, live-re-measured pre-O1-refresh; handoff `production_final_state…mtime_note`).
3. changes.diff first build (13181 B, absolute paths) superseded by ASCII rebuild **`05180b9d4001f08c24425856c3084342637a5d608f650c43202d33a898c2c7c9` / 12519 B** (live re-hashed OK).

### F9 Handoff shape — CORRECT
- Pre-bookkeeping: `status = "review_pending"`, `signature = null`, `self_sign = false`, `attestation = {da: "unmapped", acc: "unproven"}` — unsigned, no self-sign ✓.
- `changes.diff` `05180b9d…/12519` with repo-prefixed headers; §1 test alignment / §2 registry re-promotion (byte-exact `62f864b9…`, contains defect-1 `:410` and defect-2 sign changes); §1 independently re-derived in F4.
- `recovery/README.md` `fadff2ae…/2499`: exact 2-file revert with before-hashes `66516452…` / `9ec65295…` and the B-6c cross-note; scope note that no other production file was written.

## OBSERVATIONS (non-blocking; none changes the verdict)

- **O1 — RESOLVED (parent identification; recorded here).** Carrier observation: at **20:31:43** (after handoff 20:30:13) **exactly seven production paths were rewritten byte-identically** — both card targets (`62f864b9…`, `89a76809…` re-hashed OK) + PROMOTION's 5 scripts (`company_wiki_source`, `revenue_core`, `revenue_publication`, `revenue_report`, `source_preparation`) — consequences (a) content-level zero-touch claims remain true, (b) the `08` ledger's recent-writes list no longer reproduces by mtime, (c) actor was not this card.
  **Resolution (parent-supplied, evidence-cited):** the rewrite = **the parent's own GATE-OQ commit `95df2661` (author 20:30:43) pre-commit hook stash→replay cycle**. That commit's stderr recorded verbatim **`[INFO] Restored changes from …patch1790105464-21160`**; the hook stashes **unstaged** worktree changes only, and the unstaged set at that instant was **exactly those 7 files** (5 PROMOTION scripts + the 2 MODEL card targets) — identical to O1's seven paths; the replay restored original bytes (parent re-measured all seven: **`62f864b9` / `89a76809` / `7d1bd8f9` / `8a761498` / `bc2bb4a3` / `212f0059` / `91a6dc32` = `SEVEN_ALL_OK`**), bumping only mtimes (20:31:43 = hook replay completion). ⇒ **actor identified = parent's hook; all content claims hold; the mtime-ledger (08) non-reproduction is explained; benign.** Note: the parent's earlier verbal attribution to `ec307d20` was **self-corrected** by the parent (that commit's author time 20:44:25 does not fit 20:31:43). Carrier's unverified item 3 is thereby closed.
- **O2 — recorded as-is (placement note only):** the changes.diff first-build disclosure lives in `commands.json` + `handoff.json`, **not** in `decision.md`; all three required disclosures exist across the deliverable set.
- **O3 — recorded as-is (nuance):** 2 of 31 RED failures (the two `assertRaisesRegex` message-mismatch cases) carry **no explicit `:410` frame line** — they quote the `:410` message verbatim; "all failure line refs are `model_registry.py:410`" holds (no other registry line referenced), but the stronger "31/31 blocks show a `:410` frame" would not — the card never made that claim.
- **O4 / O5 (also in carrier, non-blocking):** O4 = `Copy-Item` source-mtime preservation forced CreationTime + evidence-timestamp reasoning for freeze/write windows (future cards should stamp `[datetime]::UtcNow` at write instants); O5 = `evidence/01`'s rc is not embedded in the file (rc 1 comes from commands.json; the `31 failed…` line implies it unambiguously).

## UNVERIFIED list carried from the carrier (8 items enumerated — dispatch said "7"; the carrier enumerates 8, all carried)

1. `RF_IMPORT_ROOT` for `06` — env self-declared in commands.json; not reconstructible from `06`'s raw output (13/13 pass itself verified).
2. Exact wall-clock instants of the two production writes — both mtimes source-preserved (and O1 later refreshed them); windows inferred (F1), not stamped.
3. ~~The 20:31:43 writer of the seven production paths~~ — **closed by O1 resolution above** (parent's `95df2661` hook stash→replay, `SEVEN_ALL_OK`; the 5 PROMOTION scripts' content was not independently re-pinnable by the reviewer — out of this card's declared scope).
4. Full-repo test suite — not run by reviewer; gate owed at parent batch-4 (accept scope).
5. Binding's start-of-card `git_porcelain_before` snapshot — not reproducible after the 20:30:43 GATE-OQ commit removed 2 entries; plausibility supported by `08`'s 20:29:28 capture only.
6. RED run's exact pytest flags/env identity vs PROMOTION's run — verified by output-level identity (31-line set diff + identical counts), not by re-running RED.
7. Whether `01`'s 29-line/29-block vs 31-entry grouping artifact is purely pytest subtest reporting — not root-caused (immaterial).
8. No separate `grep` oracle search across all 31 rows — sampling was 3 cases + a complete diff; rows 2, 4–31 citations checked for internal consistency only.

## ACCEPTANCE SCOPE carried (verbatim in substance, carrier L14–L20)

1. **commits = parent's authority**: RF commit = exactly 2 files — `scripts/model_registry.py` + `tests/test_model_economic_guardrails.py` (live `git status --porcelain` shows exactly these 2 production files dirty alongside PROMOTION-EXEC's pre-existing 5 scripts).
2. **full-suite gate remains at parent batch-4 push** (declared not-run in commands.json NR-2; reviewer did not run it).
3. **E1E7 carrier flips (M05/M14/M20/M24 INACTIVE→ACTIVE) = parent bookkeeping** (no M-card file edited — oracle blobs match HEAD, F6c).
4. **B-6b / natural_window remains blocked-by-design, untouched** (zero such paths in the attempt tree).
5. **CF-I14FR1-3 CW sampling remains owed** (parent-side obligation; neither performed nor claimed by this card).

---

Landing boundary: this session wrote exactly `review.md`, `handoff.json`, `evidence/MODEL-ORACLE-ALIGN/qualification.json` (bookkeeping only), ran no git, signed nothing — **bookkeeping transcription adds no acceptance of its own**; all acceptance authority stays with the carrier `reviewer_report.md` sha256 `399f4e60…` and the parent.

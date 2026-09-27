# WC-6 decision — REM-95 (`adapter_dispatch` drops the remediation reason)

Attempt `a20260923-01`. Card **WC-6 = REM-95-ADAPTER-DISPATCH** (REMEDIATION_REGISTER §75 /
§84 E 组 / §86 派发行 `9d8cb419`). Owner order: 「发现的缺陷都要全部修复」(§76).
Nine-step (execution_v2/START_HERE.md:31-41) executed to **step 8 → `review_pending`**;
the implementer does not self-sign (review_and_handoff.md:15).

Every claim below quotes captured evidence; `oracle.md` (sha256 `f59aa27d…`, 13183 B) was frozen
**before the first judged run** and never edited afterwards.

---

## 0. Exit-honesty declarations (verbatim, carry into handoff)

1. 三公司仅来源准备通过，仍未授予正式预测资格。(inherited from I-07-B/I-07-C)
2. 缺一市场/真实路径不得总体写三市场通过。(inherited)
3. 恢复：保留已取得raw，只回退当前隔离变更。(inherited)
4. 本卡 **零生产写入**：live CW `src/+tests/+config` 503 文件 manifest sha256
   `41c2271d…` 在 attempt 前后**逐字节相同**（`evidence/source_pins_before.json` vs
   `source_pins_after.json`, `live_key_sources_drifted_vs_before = []`）；产品改动只存在于
   iso 副本，交付物是 `changes.diff`。
5. 本卡 **不代签**：`handoff.status = review_pending`、`reviewer_status` 未签、
   `disclosure_adaptation = unmapped`、`accuracy = unproven`，REM-95 处置只记
   **FIXED-pending-review**（不是 CLOSED、不是 accepted）。

## 1. Ground truth re-verified LIVE in CW before freezing the fix shape

| # | Cited claim (I-07-C C1 / REM-95) | Live re-verification (this attempt) |
|---|---|---|
| 1 | promise | `adapters/sidecar.py:4-9` — "Missing fields degrade to indexed_only with an **exact remediation reason** — never guessed from the filename (F-043)" READ |
| 2 | reason computed | `sidecar.py:60` `evidence={"remediation": "missing_sidecar"}`; `sidecar.py:74` `evidence={"remediation": ";".join(problems)} if problems else {}` READ |
| 3 | vocabulary | `sidecar.py:90-119` (`_validate_sidecar`): `sidecar_parse_failed` :94, `unknown_schema_version` :96, `missing_identity:<f>` :99, `missing:<f>` :102, `missing_provenance:<f>` :105, `content_hash_mismatch` :111, `path_escape:<k>` :118 READ |
| 4 | carrier field exists | `adapters/interface.py:26` `evidence: dict = field(default_factory=dict)` READ |
| 5 | **drop seam** | `adapter_dispatch.py:57-76` `_to_scanner_candidate` copies root/path/relative_path/group_key/role/entity_name/`group_metadata=dict(item.normalized or {})`/source_status and **never reads `item.evidence`** READ |
| 6 | plumbing — **one citation corrected on live read** | the reviewer's "`_Candidate.error: str \| None` (`scanner.py:67`)" is **`_ObservedFile.error`** (`scanner.py:57-68`, line 67 = `error: str \| None`); **`_Candidate` (`scanner.py:44-54`) had NO error field at all**. The locations INSERT (`scanner.py:1089-1116`) writes `error=excluded.error` (:1099) from tuple element `item.error` (:1114). ⇒ the column plumbing exists, but nothing on the dispatch path can ever feed it: that is the second half of the drop, and it is why this fix needs a **new additive field**, not just a copy. |
| 7 | consumers of `locations.error` (the visibility target) | (i) `service.py:653-660` `query()` selects `l.error` → returned inside `document.locations[]` (`:683-686`, `_annotate_locations` :753) — **the catalog query surface**; (ii) `store.py:584-605` legacy `error_details` (`SELECT root_id,relative_path,error FROM locations WHERE last_seen_run=? AND error IS NOT NULL`) — the pipeline-status/readiness readout; (iii) `scanner.py:738` read-back gate. **Readiness graph is NOT a consumer**: `source_lifecycle.py:124` reads `location_status` only (grep over `readiness` = 48 hits, none touches `error`) |
| 8 | prior measurement | I-07-C `decision.md:23` + `review.md:116-118,229` + `reviewer_report.md:79-83,177`: `locations.error = NULL` ×4 UNK-sidecar probes |

## 2. The defect, stated precisely (REM-95)

`sidecar.py` computes the reason and puts it in `NormalizedCandidate.evidence["remediation"]`.
`adapter_dispatch._to_scanner_candidate` never copies it, and `_Candidate` has no field that could
carry it, so the scanner's only `error` source is the observe-time exception path. Consequence
(measured again in this attempt, `evidence/red_prefix/scan/normalized.json`): a reader of
`locations` sees `role = indexed_only / original_primary` (role-level explicit ✓) but
`error = NULL` — **the cause is not observable** (reason-level ✗) for every remediated candidate.
`documents.metadata_json.acquisition` carries no `remediation` key either (still `"acquisition": null`
for the broken/no-sidecar probes — untouched by this card, see §6 boundary).

## 3. Fix shape (investigate-then-decided, oracle §7 froze it before the runs)

**Two product files, +18 / −1 lines total (`changes.diff`, sha256 `ad88feed…`, 2604 B):**

1. **`src/company_wiki/source_catalog/adapter_dispatch.py`** — the seam REM-95 names:
   `_to_scanner_candidate` now passes `error=item.evidence.get("remediation")`.
   *Why this file:* it is the only place the adapter's `evidence` is (not) forwarded; fixing
   anywhere else would leave the seam broken for all three adapters.
   *Constraint honored:* the expression adds **no** control-flow node —
   `test_fc1204_complexity_ratchet.py:28` freezes this file's per-function McCabe at **4**
   (reached by `adapter_for`); measured per-function before = after
   (`_to_scanner_candidate` 3 → 3, `adapter_for` 4 → 4, file max 4 → 4,
   `evidence/complexity_before_after.json`).
2. **`src/company_wiki/source_catalog/scanner.py`** — two additive lines-pairs:
   (a) `_Candidate` gains `error: str | None = None` (defaulted ⇒ every existing constructor,
   positional or keyword, keeps working; 7 construction sites in scanner.py + 1 in dispatch);
   (b) the locations INSERT tuple's last element becomes
   `item.error if item.error is not None else candidate.error`.
   *Why this file:* there is no other writer of `locations.error` (grep: the only
   `INSERT INTO locations` in `src/` is `scanner.py:1089`), and no other reader can be reached
   from the dispatch seam. The ternary keeps **observation errors byte-preferred**, which is a
   hard invariant: `scanner.py:733-739` computes `known_error` with `existing["error"] == error`,
   so writing anything else for a quarantined location would flip `new_errors`/`known_quarantined`
   on every re-scan. It is an `ast.IfExp` (value selection, not a branch): the ratchet counts
   `ast.If`, and the measured per-function complexity is unchanged (disclosed, not hidden).

**Rejected alternatives (so the reviewer can rule on them instead of re-deriving them):**

| Alternative | Why rejected |
|---|---|
| Route the reason through `_ObservedFile.error` | `scanner.py:982-996` would then increment `errors`/`new_errors` and append to `error_details`, i.e. a *remediation* would be counted as a scan **error**, and on **every** re-scan (the `known_error` computation only exists inside the exception branch :731-751, so the success path always reports `known_error=False`) ⇒ fail-closed accounting changes; oracle §4 forbids it and the mutation/idempotency arms prove it is not needed |
| Put `remediation` into `group_metadata` | `group_metadata` feeds `collector_name/version/retrieved_at` (:699-708), the manifest and `documents.metadata_json` — a payload/identity change well beyond a diagnostic column, and it would move `documents.metadata_json.acquisition` which REM-95 does not ask for |
| New column / table | schema migration + new consumers; REM-95 says 「补救原因持久化至 `locations.error`」 verbatim (§84 E 组 line 1718) |
| Fix `sidecar.py` (recompute later) | the reason is already computed there; recomputing downstream would duplicate adapter logic in the scanner |

**Fail-closed unchanged:** CFG-01 refusal text is byte-identical before/after
(`evidence/red_prefix/cfg01/stderr.txt` vs `evidence/green/cfg01/stderr.txt`, both
`… adapter_id 'unknown_layout_v9' not registered (CFG-01)`, product rc 1 both arms), and the
dispatch fail-closed tests (`test_adapter_production_dispatch`, `test_zr402_adapter_route_contract`
C3, `test_shadow_parity_runner` EX08) pass in both family runs.

## 4. RED — the current behavior, reproduced by own execution (oracle §2)

`evidence/red_prefix/` — produced after copying the **live pre-image** back into iso and verifying
both hashes equal the step-2 pins (`adapter_dispatch 6a72e7c5…`, `scanner f039d5f8…`):

- `locations.error` = **NULL for all four probes** (`normalized.json > diagnostic`), including the
  three that have a computed reason ⇒ REM-95 reproduced live, not inherited.
- roles: `clean_probe → original_primary`, `no_sidecar_probe → original_primary`,
  `broken_sidecar_probe → indexed_only`, `mismatch_probe → indexed_only` — identical to
  I-07-C's measured roles (`decision.md:122-127`), entities `unresolved:wc6_probe_lake`.
- scan report: `errors 0 / new_errors 0 / error_details []`, strategy
  `{"wc6_probe_lake": "adapter"}`, product rc 0; resolve product rc 0; cfg01 product rc 1.
- The earlier pre-fix run of the same four probes (`evidence/red_run1/…`) is kept as well:
  same NULL ×4, captured before any harness normalization change; it is superseded as a
  *comparison* base only because its stage order and its normalization were fixed afterwards
  (§7 harness corrections) — its RED observation stands unchanged.

## 5. GREEN + outcome-unchanged proof (oracle §3/§4)

`evidence/compare_red_prefix_vs_green.json` (comparator rc **0**):

- **`outcome_bytes_identical_overall = true`** for all four stages
  (`scan`, `rescan`, `resolve`, `cfg01`): locations/sources/documents/entities/document_entities
  allowlist columns, table counts, both scan reports (volatile keys stripped), product rc,
  stdout (volatile-stripped) and stderr are byte-identical.
- **the only byte change in the whole dump** is `locations.error` on exactly three paths
  (`broken_sidecar_probe.txt`, `mismatch_probe.txt`, `no_sidecar_probe.txt`) —
  `diagnostic_changed_paths` lists exactly those three in every stage; `clean_probe.txt` stays
  NULL because its sidecar is valid and `sidecar.py:74`'s else-branch builds `evidence = {}`
  (oracle §1.1 froze this refinement **before** the runs, so GREEN could not be redefined after).
- **fixture input held constant**: `fixture_input_identical = true`,
  `tree_sha256 = 37be0c5a607cf7c4619b6381bb2eae808966e8152f875c56e9024f7ad615ad58` in every arm.
- **determinism control**: `evidence/compare_green_vs_repeat_postfix.json` — a second,
  fully independent post-fix run produces *identical* outcomes **and** identical diagnostics
  (`diagnostic_changed_paths = []` everywhere), i.e. the harness itself is not the source of the
  RED→GREEN delta.

**rgm counts (RED / GREEN / MUTATION):**

| arm | code state | probes with a reason | `locations.error` observed |
|---|---|---|---|
| **RED** `red_prefix` | live pre-image (pins verified) | 3 of 4 | **NULL ×4** |
| **GREEN** `green` | fix applied | 3 of 4 | `sidecar_parse_failed` / `missing_sidecar` / `missing_identity:canonical_entity_id;content_hash_mismatch;path_escape:canonical_path` + clean **NULL** = **3 reasons + 1 correct NULL** |
| **MUTATION** `mutation` | fix present, pass-through removed (`error=None,  # MUTATION …`, iso sha256 `b9460305…`) | 3 of 4 | **NULL ×4** again |
| control `repeat_postfix` | fix applied (independent rebuild) | 3 of 4 | same as GREEN byte-for-byte |

`evidence/compare_green_vs_mutation.json` (rc **0**): outcomes byte-identical to GREEN, diagnostics
revert to NULL on the same three paths ⇒ **the GREEN is non-vacuous — the reason comes from this
seam and nowhere else**. The mutation file bytes were restored afterwards and verified
(`0c5ac1a2…`, see `recovery/README.md §2`).

## 6. End-to-end reason chain (why this is "visible", not merely "stored")

`evidence/reason_chain.json` (harness rc **0**, `all_hops_match = true`, 4 probes × 4 hops):

| hop | surface | measured |
|---|---|---|
| H1 | `SidecarFilingAdapter.enumerate()` → `NormalizedCandidate.evidence["remediation"]` | the three exact strings (sidecar.py:60/74) |
| H2 | `adapter_dispatch._to_scanner_candidate()` → `_Candidate.error` (**the REM-95 seam**) | same strings, byte-equal |
| H3 | `locations.error` after the product's own `cli scan` | same strings, byte-equal |
| H4 | **reader surface** `SourceCatalog.query()` → `document.locations[].error` | same strings, byte-equal |

Every hop equals the literal frozen in oracle §1.1 before any run. H4 nuance disclosed, not
hidden: the product's default query view is **active-only** (`service.py:710-718`), so the two
`incomplete` documents surface only through an explicit `source_status="incomplete"` filter —
the recorded view per probe (`H4_seen_via_view`) shows exactly which call returned each row.
`clean_probe` correctly shows NULL on every hop (no reason exists to show).

## 7. Corrections and judgment calls made during the attempt (disclosed)

1. **Citation correction (live re-verification)** — `scanner.py:67` is `_ObservedFile.error`, not
   `_Candidate.error` (§1 row 6). The fix shape follows the corrected fact (new additive field).
2. **Oracle refinement before running** — only 3 of 4 probes have a reason (§5). Frozen in
   `oracle.md §1.1` prior to the first judged run.
3. **Stage-order symmetry** — the first `red`/`green` runs used different stage orders
   (`resolve` before/after `rescan`), which changed `counts.scan_runs` and made a whole-stage
   comparison fail for a reason unrelated to the fix. Both arms were **re-run with one fixed
   order** (`scan → rescan → resolve → cfg01`); the first-pass evidence is preserved as
   `evidence/red_run1/` and `evidence/green_run1/` (never overwritten).
4. **Volatile-key normalization** (declared exclusions, oracle §4) — measured volatile keys:
   scan stdout `run_id` (random), resolve stdout `retrieved_at` (wall clock), `documents.
   metadata_json` `observed_at` entries, plus the frozen list (`*_at`, `run_id`, `mtime`, …).
   The comparator strips them for the *comparison only*; raw stdout/stderr sha256 are recorded
   per run in `compare_*.json`, and `stdout_raw_differs_only_by_volatile_keys` reports when the
   raw bytes differed solely because of those keys.
5. **Product rc comparison** originally compared the whole `product_rc.json`, which includes the
   harness-measured `elapsed_seconds` — corrected to compare `product_returncode` only.
6. **First mutation attempt did not apply** — `Set-Content -Encoding utf8NoBOM` is not supported
   by this PowerShell host, so the "mutation" arm actually ran the fixed code. It is preserved as
   `evidence/mutation_attempt1_mutation_not_applied/` and the real mutation was applied with a
   **byte-level** replace (the file is CRLF; a text-mode rewrite would touch every line ending),
   verified by hash before the arm ran and re-verified restored afterwards. The same failed
   command's null-destination `Copy-Item` also dropped a byte-identical duplicate of the fixed
   `adapter_dispatch.py` at the attempt root; it carried no information (same sha256
   `0c5ac1a2…` as `iso/fixed/adapter_dispatch.py`) and was deleted after hashing, so the attempt
   root holds exactly `binding.json / changes.diff / commands.json / decision.md / oracle.md`
   plus the `evidence/ harness/ inputs/ iso/ recovery/` directories.
7. **Harness files were edited after `binding.json` was first frozen** (prepare/compare_runs/
   wc6_common/run_stage + added reason_chain/make_changes_diff). Final harness hashes are
   re-recorded in `binding.json > harness` with the original values beside them. **No product
   file, no carrier and no oracle byte changed during this attempt** (oracle sha256
   `f59aa27d…` recomputed identical at handoff).
8. **No live-CW family run** — the regression family runs in the byte-identical iso copy
   (503-file pin proves `iso == live` before the fix) rather than in live CW, so that live CW is
   never opened for writing by a test session (other agents were running the live suite
   concurrently during this attempt). Disclosed as the boundary of the family claim.
9. **`rescan` arm added after the oracle freeze** — it adds evidence (idempotency + error
   accounting on re-entry) and redefines **no** frozen expectation; recorded here instead of
   editing `oracle.md`, which stays byte-identical to its freeze-time hash.

## 8. Regression family (mechanical selection, no skip/xfail added)

`harness/select_family.py` (patterns frozen in oracle §6) selected **60 test files**
(`evidence/family_files.json`, `evidence/family_grep.txt`) — every file mentioning
`adapter_dispatch / scan_root_via_adapter / _to_scanner_candidate / _Candidate / _ObservedFile /
source_catalog.scanner / adapters.sidecar / SidecarFilingAdapter / error_details /
…FROM|INSERT INTO locations`, plus the three ratchets that *name* the touched files.

Family results (`evidence/compare_family_fam_before_vs_fam_after.json`, comparator rc **0**):
`fam_before` (pre-fix) = `fam_after` (post-fix) — **474 outcomes, 443 passed / 8 skipped / 23 failed
in both**, `status_changed = []`, `only_in_a = []`, `only_in_b = []`, pytest raw rc 1 in both.
Baseline composition is disclosed in `recovery/README.md §7` (23 pre-existing failures,
8 pre-existing skips — 18 of the failures are the iso copy scope not including `scripts/`, the
rest are pre-existing/environmental, including the live pre-existing complexity-ratchet failure
`archive_retired_evidence.py 19 > frozen 7` which is unrelated to this card).

**Idempotency (the trap this fix had to avoid)** — `compare_red_prefix_vs_green.json >
idempotency`: in BOTH arms the first and second scan reports carry
`errors 0 / new_errors 0 / error_details []` (`error_counters_unchanged = true`) while
`diagnostic_identical_across_rescan = true` — i.e. a persisted remediation reason is *not*
counted as a scan error on re-entry and does not flap. That is the direct empirical reason the
`_ObservedFile.error` alternative (§3) was rejected.

## 9. Boundary of this card (what was NOT done)

- **No product merge / no promotion**: live CW untouched (503-file manifest unchanged); delivery
  is `changes.diff` only; promotion remains an owner decision (REMEDIATION_REGISTER:4 discipline).
- **No status transition, no signature**: `handoff.status = review_pending`,
  `implementer_signed = false`, `reviewer_status` unsigned, `disclosure_adaptation = unmapped`,
  `accuracy = unproven`; REM-95 marked **FIXED-pending-review** — closing the register row is the
  reviewer's/parent's call, not this attempt's.
- **No register edits**: `REMEDIATION_REGISTER.md` was read and hashed only
  (`f8cd3ac4…`); §75/§84/§86 rows are quoted, never rewritten.
- **No test edits, no new skip/xfail, no fixture change**: `iso/cw/tests` stayed byte-identical
  to live throughout (`source_pins_after.json`: only the two product files differ between iso and
  live).
- **`documents.metadata_json.acquisition` still carries no `remediation` key** — C1 mentioned
  that second surface as an observation; REM-95's spec (§84 E 组 :1718) names `locations.error`
  only, and the card allows 1-2 files. Logged as a deliberate non-goal for the reviewer to
  route (it would need a document-metadata change, a wider blast radius than a diagnostic column).
- No frozen evidence of any other card was touched; no network; no git (delivery is difflib-based
  `changes.diff`, per commands.json `"git": "NOT USED"`).

## 10. Handoff

Next action for the reviewer (step 8 → 9, review_and_handoff.md): independent re-verification in
this order — (1) `pin_sources.py after` (zero product writes), (2) re-hash `changes.diff` and the
two iso files against `binding.json`, (3) re-run `compare_runs.py red_prefix green` and
`reason_chain.py chain` (both rc 0), (4) re-run the family pair and compare per-test outcomes,
(5) rule on the two disclosed non-goals (§9) and on whether REM-95 moves from
**FIXED-pending-review** to CLOSED. Reviewer starts from `oracle.md` + `evidence/`, never from
this file's summary.

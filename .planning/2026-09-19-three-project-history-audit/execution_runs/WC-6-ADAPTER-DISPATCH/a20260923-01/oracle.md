# WC-6 oracle — frozen BEFORE the first judged run (nine-step §4)

Card: **WC-6 = REM-95-ADAPTER-DISPATCH** (REMEDIATION_REGISTER §75 / §84 E 组 / §86 派发行
`9d8cb419`). Attempt `execution_runs/WC-6-ADAPTER-DISPATCH/a20260923-01`.
Parent = `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`.

**One observable result (step 1 restated)**: the remediation reason string that
`adapters/sidecar.py` computes for a degraded candidate becomes visible in the catalog's
`locations.error` column after `cli scan`, byte-identically to the sidecar-sidecar source string,
while **every accept/reject outcome field stays byte-identical** to the pre-fix run.

This file is frozen at step 4 and MUST NOT be edited after the first judged run.

---

## 0. Ground truth this oracle pins (re-verified LIVE in CW before freezing)

| # | Claim (from I-07-C finding C1 / REM-95) | LIVE re-verification |
|---|---|---|
| 1 | promise "exact remediation reason" | `adapters/sidecar.py:4-9` (docstring lines 5-7: "Missing fields degrade to indexed_only with an exact remediation reason — never guessed from the filename (F-043)") — READ |
| 2 | reason computed at `sidecar.py:60` | line 60 `evidence={"remediation": "missing_sidecar"}` (no-sidecar branch) — READ |
| 3 | reason computed at `sidecar.py:74` | line 74 `evidence={"remediation": ";".join(problems)} if problems else {}` — READ |
| 4 | reason vocabulary | `_validate_sidecar` (`sidecar.py:90-119`): `unknown_schema_version` (:96), `missing_identity:<field>` (:99), `missing:<field>` (:102), `missing_provenance:<field>` (:105), `content_hash_mismatch` (:111), `path_escape:<key>` (:118), `sidecar_parse_failed` (:94) — READ |
| 5 | evidence carrier exists | `adapters/interface.py:26` `evidence: dict = field(default_factory=dict)` on `NormalizedCandidate` — READ |
| 6 | drop seam | `adapter_dispatch.py:57-76` `_to_scanner_candidate` copies `root/path/relative_path/group_key/role/entity_name/group_metadata=dict(item.normalized)/source_status` and **never reads `item.evidence`**; :74 is the only metadata copy — READ |
| 7 | plumbing | **cited value corrected on live read**: `scanner.py:67` is `error: str \| None` inside **`_ObservedFile`** (dataclass at :57-68), **not** inside `_Candidate` (dataclass at :44-54, which has NO error field today). The locations INSERT at `scanner.py:1089-1116` writes `error=excluded.error` (:1099) from the tuple's last element `item.error` (:1114). So the column plumbing exists, but the value can only be produced by (a) the observe-time exception path (`scanner.py:731-751`) or (b) a field that does not exist yet — this is the second half of the drop. |
| 8 | known-error gate depends on exact equality | `scanner.py:733-739` `known_error = ... and existing["error"] == error` — any change to the value written for an EXCEPTION location would change `new_errors`/`known_quarantined` counts ⇒ invariant I-5 |
| 9 | consumers of `locations.error` (end-to-end visibility target) | (i) `service.py:653-660` `query()` selects `l.error` and returns it inside each document's `locations[]` (`_annotate_locations`, `service.py:753`) — the catalog query surface; (ii) `store.py:584-605` legacy `error_details` (pipeline status / readiness readout) selects `root_id,relative_path,error FROM locations WHERE last_seen_run=? AND error IS NOT NULL`; (iii) `scanner.py:738` read-back gate. Readiness graph (`source_lifecycle.py:124`) reads `location_status` only — NOT a consumer of `error` (measured: no `error` reference). |
| 10 | prior measurement being remediated | I-07-C `decision.md:23` + `review.md:116-118/229` + `reviewer_report.md:79-83,177`: `locations.error = NULL` for **all 4** UNK-sidecar probes |

## 1. The 4 probes (reproduced 1:1 from I-07-C's UNK-sidecar cell builder)

Fixture = `harness/build_probe.py`, data in `inputs/probe_fixture.json`. The four files and their
sidecar payloads are constructed exactly as I-07-C `harness/build_iso.py:226-281` did
(same texts, same `_sc` JSON shape, `content_sha256` hashed **from the file bytes** — I-07-C's own
J2 correction). One root, `kind: directory`, `adapter_id: sidecar_filing_v1`.

| id | file | sidecar | expected role (unchanged by this card) |
|---|---|---|---|
| P1 | `clean_probe.txt` | complete, hash matches file bytes | `original_primary` |
| P2 | `no_sidecar_probe.txt` | **absent** | `original_primary` |
| P3 | `broken_sidecar_probe.txt` | `{not valid json,` (unparseable) | `indexed_only` |
| P4 | `mismatch_probe.txt` | `schema_version 1.0`, `market/security_id` present, `canonical_entity_id` **missing**, `content_sha256 = 0*64`, `canonical_path = C:\escape\target.pdf`, facts+provenance present | `indexed_only` |

Sidecar `.source.json` files never become candidates (`sidecar.py:49-50`) ⇒ exactly 4 locations.

### 1.1 Hand-derived remediation strings (source-read, NOT produced by calling the function)

Derivation chain (sidecar.py line cited per term, order = `_validate_sidecar` execution order):

- **P1** → no sidecar file problems: `_validate_sidecar` returns `[]` ⇒ line 74 else-branch
  `evidence = {}` ⇒ **no `remediation` key exists** ⇒ `locations.error` must be `NULL` **both before
  and after the fix**. (This is a deliberate refinement of the card's shorthand "4 probes carry the
  reason": only 3 of the 4 probes have a computed reason; P1's NULL is *correct* behavior, frozen here
  before running so GREEN cannot be redefined afterwards.)
- **P2** → line 60 literal ⇒ **`missing_sidecar`**
- **P3** → `_parse_sidecar` returns `{"_parse_error": True}` ⇒ line 94 ⇒ **`sidecar_parse_failed`**
- **P4** → identity loop: `canonical_entity_id` absent ⇒ `missing_identity:canonical_entity_id` (:99);
  facts loop: `document_kind,fiscal_year,period_end,content_sha256` all present ⇒ no term;
  provenance loop: both present ⇒ no term; declared `0*64` ≠ file hash ⇒ `content_hash_mismatch`
  (:111); `canonical_path` matches `^([A-Za-z]:[\\/]|/|\\\\)` ⇒ `path_escape:canonical_path` (:118).
  Joined by `";"` at :74 ⇒
  **`missing_identity:canonical_entity_id;content_hash_mismatch;path_escape:canonical_path`**

## 2. RED (current behavior — must be observed, never manufactured)

Pre-fix (`iso/cw/src` byte-identical to live CW, proven by `evidence/source_pins_before.json`):

- **R-1**: `locations.error IS NULL` for **P2, P3, P4** — i.e. every probe that HAS a computed
  remediation reason shows no reason. This is the defect (REM-95) reproduced by own execution.
- **R-2**: `locations.error IS NULL` for P1 (expected either way; recorded as control).
- **R-3**: role of each probe as §1 table; entities `unresolved:<root>` for all four (no
  filename-guessed identity) — matches I-07-C's measured role-level explicitness.

## 3. GREEN (post-fix, same inputs, same commands)

- **G-1**: `locations.error` == the exact §1.1 string for P2/P3/P4 (byte-equal to the sidecar-computed
  value), `NULL` for P1.
- **G-2**: **all outcome fields byte-identical** between RED and GREEN, per probe and per run —
  see invariant list §4 (the only permitted byte change in the whole catalog dump is
  `locations.error` for P2/P3/P4).
- **G-3**: read path end-to-end: the same string is returned by `service.query()` inside
  `document.locations[].error` (product's own query surface), proving sidecar string → location
  column → reader-visible field.
- **G-4**: CFG-01 refusal text unchanged (quote-preserve): an unknown `adapter_id` config still
  fails load with `... adapter_id 'unknown_layout_v9' not registered (CFG-01)` (`config.py:127-131`).
  (Run in the mutation/regression arm as part of the family; the family includes the dispatch
  fail-closed tests `test_adapter_production_dispatch.py` which assert the exact refusal strings.)

## 4. Invariants (what "outcome unchanged" means — frozen field list)

Compared byte-for-byte (`json.dumps(..., sort_keys=True)` of the normalized dump) between RED,
GREEN and MUTATION runs:

- `locations`: `root_id, relative_path, absolute_path, source_id, document_id, role,
  location_status, observed_size, metadata_json` (NOT `error` — that is the payload under test).
- `sources`: `source_id, content_sha256, byte_size, mime_type`.
- `documents`: `document_id, document_kind, source_status, title, primary_source_id,
  published_date, metadata_priority, metadata_json`.
- `entities`, `document_entities`: all columns.
- scan report (from `scan_runs.report_json`): `files_seen, files_excluded, locations_active,
  errors, new_errors, known_quarantined, error_details, strategy` and every other non-time key.
- raw product rc of `scan` and of `resolve`, and the resolve envelope bytes (time-derived fields
  inside it, if any, are dropped by an explicit key allowlist — recorded, not silently).
- **fail-closed is not changed**: `errors/new_errors/known_quarantined` counters and
  `error_details` must be byte-identical (REM-95 changes a *diagnostic column*, not the error
  accounting). Consequence frozen here: the fix MUST NOT route the remediation reason through
  `_ObservedFile.error`, because `scanner.py:982-996` would then increment `errors/new_errors` and
  append to `error_details`, and `scanner.py:738`'s equality gate would break for re-scans of
  quarantined locations.
- **excluded as time-derived (declared, not hidden)**: `observed_mtime_ns`, `manifest_json`
  (contains `retrieved_at`), `last_seen_run`, `sources.first_seen_at`, `documents.first_seen_at/
  last_seen_at`, `scan_runs.run_id/started_at/completed_at`, any `*_at`/`*time*` key.

## 5. MUTATION (non-vacuity arm)

Revert the pass-through (adapter_dispatch stops copying `item.evidence`, i.e. the `_Candidate`
carries `error=None` again) while everything else stays fixed ⇒ re-run the same probes ⇒
**P2/P3/P4 `locations.error` must return to `NULL`** and all outcome fields must stay byte-equal to
the GREEN run. If the reasons do not vanish, the GREEN was vacuous (the reason came from somewhere
else) ⇒ the gate does not test this seam.

## 6. Regression family (selected mechanically, no skip/xfail added)

`harness/select_family.py` greps `iso/cw/tests` for
`adapter_dispatch|scan_root_via_adapter|_to_scanner_candidate|source_catalog.scanner|adapters.sidecar|
SidecarFilingAdapter|locations…error|error_details` plus the three ratchets that name these files
(`test_fc1204_complexity_ratchet` — `adapter_dispatch.py` frozen max complexity **4**;
`test_fc1204_coverage_ratchet`; `test_fc1201_root_hardcode_gate`). Contract: **the per-test outcome
list must be identical before vs after the fix** (same pass/fail/skip set, same counts) — skips that
already exist in the baseline stay as they are; this card adds **no** skip/xfail anywhere.

## 7. Fix shape (investigate-then-decide; frozen here, evidence may only contradict it)

Two product files, both justified (task allows 1-2):

1. `src/company_wiki/source_catalog/adapter_dispatch.py` — `_to_scanner_candidate` copies the
   remediation reason out of `item.evidence["remediation"]` into the scanner candidate (the drop
   seam named by REM-95). Expression must add **no** control-flow node: the file's per-function
   McCabe max is frozen at 4 by `test_fc1204_complexity_ratchet.py:28`, reached by `adapter_for`.
2. `src/company_wiki/source_catalog/scanner.py` — (a) `_Candidate` gains an **additive, defaulted**
   `error: str | None = None` field (the missing carrier; `_ObservedFile.error` is not reachable
   from the dispatch seam); (b) the locations INSERT tuple's `error` element becomes
   "observation error wins, else candidate remediation reason" — an expression, not a new branch —
   so exception locations keep writing the exact exception string (invariant I-5: `known_error`
   equality gate) while remediation-only locations persist their reason.

Rejected alternatives (recorded so the reviewer can rule on them):
- *Route through `_ObservedFile.error`*: changes `errors/new_errors/error_details` ⇒ changes the
  report's accept/reject accounting and breaks §4 fail-closed invariants (and would count a
  remediation as a NEW error on **every** re-scan, because `_observe_file` computes `known_error`
  only inside the exception branch).
- *Put `remediation` into `group_metadata`*: `group_metadata` is copied into
  `collector_name/version/retrieved_at` (`scanner.py:699-708`), the manifest and
  `documents.metadata_json` — a payload/identity change, far wider than a diagnostic column, and
  it would move `documents.metadata_json.acquisition` (measured NULL-key state in C1) as a side
  effect that REM-95 does not ask for.
- *New dedicated column / table*: schema migration + more consumers; REM-95 names
  `locations.error` explicitly ("补救原因持久化至 `locations.error`").

## 8. Stop conditions (not triggered unless measured)

- live CW hashes drift from `evidence/source_pins_before.json` ⇒ STOP (isolation broken);
- a family test outcome differs before vs after ⇒ STOP (behavior change outside the diagnostic
  payload);
- the mutation arm does not clear the reasons ⇒ STOP (non-vacuousness unproven);
- probe fixture bytes differ between runs ⇒ STOP (input not held constant).

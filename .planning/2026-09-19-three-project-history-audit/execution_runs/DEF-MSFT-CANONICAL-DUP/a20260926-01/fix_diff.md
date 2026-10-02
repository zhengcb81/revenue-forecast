# fix_diff — DEF-MSFT-CANONICAL-DUP (`a20260926-01`, resumed station)

Target file (the ONLY product file this card changes):

`company-wiki/src/company_wiki/source_catalog/canonical_writer.py`
(no other repo, no `dayu-agent`, no config/runtime-policy change)

## 1. Image chain (sha256, upper-case)

| image | file | bytes | sha256 |
|---|---|---:|---|
| 前像 · as-found (LF = git blob) | `canonical_writer.preimage_asfound.py` | 17,958 | `835DAB7F2FFDC4B10D8892EDB94BB88E77F840DF59D05CF6C9FEBA7AAD4337DB` |
| 前像 · as-found (CRLF = working tree) | same bytes, CRLF | 18,380 | `4BC653725FEBCC755E3A01AC48227A6B0799C4C262968356B356F8CB42D3C6BC` |
| 前像 · with UTF-8 BOM (as received) | `canonical_writer.preimage.py` | 18,383 | `1F2BE3B4077387F573174281708BF1D060917D40B33171B2268F4DCDDDCA6C7B` |
| 前像 · `git show HEAD:<path>` | (company-wiki HEAD blob) | 17,958 | `835DAB7F2FFDC4B10D8892EDB94BB88E77F840DF59D05CF6C9FEBA7AAD4337DB` |
| 修复草稿 · as received | `canonical_writer.fixed.py` (pre-resumption) | 23,699 | `2788409FD28DFC991D76B499FAC84F61A9AFC710ED098220C322B2A4D37604DE` |
| **后像 · final** | `canonical_writer.fixed.py` == live tree | 23,949 | `D7F6AFC53F62637BA2B881B3BE629D2AAE392C670182D0A3514A27FA6B2428F8` |

Evidence for the chain:

* `canonical_writer.preimage_asfound.py` **byte-identical** to `git show HEAD:src/company_wiki/source_catalog/canonical_writer.py`
  (verified with `cmd /c git show > file`, sha `835DAB7F…`) ⇒ the as-found preimage *is* the committed baseline.
* CRLF-normalising the as-found copy reproduces `4BC65372…`, the `EXPECTED` constant inside the previous station's
  `reconstruct_preimage.py` ⇒ the preimage reconstruction is consistent (the `False` line printed by
  `rig/analyze_diff.py` only reflects that the *stored copy* is LF-normalised).
* `canonical_writer.preimage.py` differs from the as-found preimage by a leading UTF-8 BOM only
  (`rig/diff_preimage_to_asfound.patch`, 1 hunk, +1/−1).
* LIVE `company_wiki/…/canonical_writer.py` **== `canonical_writer.fixed.py`** (`live_equals_fixed: true` in
  `verification.json`) — the fix under review and the working tree are the same bytes.

Unified diff: `rig/diff_asfound_to_fixed.patch` (7 hunks, `+102 / −8`), machine-readable opcode listing in
`rig/diff_report.txt`, company-wiki's own view in `rig/cw_git_diff_canonical_writer.patch`.

## 2. Segment-by-segment (as-found line numbers → final)

| # | as-found → final | what it is | why (fix element) | proof case |
|---|---|---|---|---|
| 1 | L8 `+ import json` | module import | needed by the new sidecar verifier (element 2) | `green_s4`, `m2_s4` |
| 2 | L20 `- …, v2_scan_shadow_from_snapshot` | import tidy-up | the snapshot flag is no longer read by this module (element 1) | `m1_s1` |
| 3 | L171 `+ destination_preexisting = False` + 10-line rationale | flag that distinguishes “bytes already on canonical disk” from a fresh commit | bookkeeping for element 2 + the status label | `green_s1` vs `green_s4` |
| 4 | L192 `destination_preexisting = destination.exists()` (**correction, see §3**) | flag value | must be `False` right after the `__<sha12>` rename, when the suffixed path did not exist yet | `green_s1` (outcome `downloaded_new`) |
| 5 | L184 `self._write_provenance(...)` → `if destination_preexisting and provenance.exists(): _verify_committed_provenance(...) else: _write_provenance(...)` | **fix element 2** | re-acquisition of bytes already on canonical disk must not rewrite the first acquisition's immutable sidecar (request_id/retrieved_at differ per attempt ⇒ today: `immutable provenance sidecar conflict` + another orphan); identity-checked, still fail-closed | RED `red_s4` vs GREEN `green_s4`; mutation `m2_s4` |
| 6 | L190 `v2_scan_shadow=v2_scan_shadow_from_snapshot(...)` → `v2_scan_shadow=bool(self.company_root.adapter_id)` | **fix element 1** | `runtime_policy.flags.v2_scan_shadow=true` sends every import-time scan down the v2 adapter dispatch, which **fails closed** for `company_raw` (no `adapter_id`) and indexes 0 files; the just-written file is therefore never indexed and post-write identity resolution returns `NOT_FOUND` ⇒ production `canonical_import_failed`. The import is a committed write that must index what it writes; non-import scans keep following GP-002 untouched | RED `red_s1` (scan `files_seen=0`, `v2 scanner unavailable (fail closed)`) vs GREEN `green_s1` (scan `files_seen=4`, `strategy={company_raw: legacy}`); mutation `m1_s1` |
| 7 | L210 strict `REUSED_EXACT` raise → AMBIGUOUS-adoption block (`committed` filter + `replace(status=REUSED_EXACT…)`) | **fix element 3** | two distinct-content documents sharing one provider identity resolve `AMBIGUOUS` by design; verification now adopts the match **only** when exactly one capture-ready handle carries `content_sha256 == receipt.content_sha256` + matching provider identity — any other outcome still raises | `green_s1`/`dedup_s5` (both sibling variants indexed, import still succeeds); mutation `m3_s1` (indexed but rejected) |
| 8 | L233 `status=IMPORTED_NEW` → `DEDUPLICATED_AFTER_DOWNLOAD if destination_preexisting else IMPORTED_NEW` | status label | a genuine re-acquisition journals the established dedup outcome (oracle G3 allows either label, never `canonical_import_failed`) | `green_s4`, `dedup_s5` |
| 9 | L408 `+ _verify_committed_provenance()` (26 lines, static) | **fix element 2** helper | reads the pre-existing sidecar and fail-closes unless `content_sha256`/`provider`/`provider_document_id`/`byte_size` match the receipt; error string deliberately identical to `_write_provenance`'s conflict so the failure taxonomy is unchanged | `green_s4`; mutations `m2_s4` (skipped ⇒ conflict) |

Untouched surfaces (checked): `scanner.py` / GP-002 wiring, `adapter_dispatch`, `resolver.py` AMBIGUOUS semantics,
`.source_catalog/runtime_policy.json`, `config/source_catalog.yaml`, `filing-fetch`, `dayu-agent` (zero writes),
production company-wiki (read-only for fixture bytes).

## 3. Verification finding — one correction applied to the draft

The draft I inherited (sha `2788409F…`) set `destination_preexisting = True` **inside** the
“destination name is occupied” branch, i.e. *before* knowing whether the `__<sha12>` fallback path already held
these bytes. Consequence, reproduced in the rig: the **first** commit of a hash-suffix file (production's 09-27
shape) journaled `deduplicated_after_download` although nothing pre-existed — contradicting the draft's own comment
(“marks the case where the computed canonical path … already holds byte-identical content”) and oracle element 2
(“when the computed destination … already exists byte-identical to the receipt”).

Correction: `destination_preexisting = destination.exists()` (evaluated after the collision check), i.e. the flag
means exactly what the comment says. Effects (both re-verified after the change):

* sidecar behaviour unchanged in every scenario (S1 still writes a fresh sidecar, S4 still verifies, never rewrites);
* `green_s1` journal outcome `downloaded_new` (was `deduplicated_after_download` pre-correction), `green_s4` still
  `deduplicated_after_download`;
* no criterion of the frozen oracle is weakened — G3 explicitly accepts either non-failure outcome.

Final draft sha after the correction: `D7F6AFC53F62637BA2B881B3BE629D2AAE392C670182D0A3514A27FA6B2428F8`
(= live tree). Nothing else in the draft was changed; every other segment passed review as written.

## 4. Regression evidence (oracle G4)

`python -m pytest -q -p no:cacheprovider --basetemp=%TEMP%/defmsft_pytest`
`tests/contract/test_source_catalog_canonical_writer.py tests/contract/test_canonical_ingest_service.py`
`tests/contract/test_source_catalog_acquisition.py tests/contract/test_source_catalog_resolver.py`
⇒ **39 passed in 7.28s**, exit 0, and the company-wiki `git diff --name-only` set is byte-for-byte the same
before and after the run (no stray writes).

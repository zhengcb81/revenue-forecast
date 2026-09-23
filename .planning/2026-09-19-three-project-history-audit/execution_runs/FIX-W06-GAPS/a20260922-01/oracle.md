# oracle.md — FIX-W06-GAPS (FROZEN before any run)

attempt: `execution_runs/FIX-W06-GAPS/a20260922-01`
card: FIX-W06-GAPS · owner ruling verbatim: 「fail 的全部要修复」(P5/P6 increment: 「发现的缺陷都要全部修复」; C7 increment: 「所有存疑都要确认」)
frozen: 2026-09-22, before ANY red/green/mutation run in this attempt.
This text is IMMUTABLE. Later scope increments land only as dated APPEND sections at the end.

## 0. Discipline (applies to every fix)

- Fix in COPIES (`iso/`); `before/` keeps originals byte-identical (MANIFEST.json pins both).
- RED first on the BEFORE copy (must reproduce the probe failure shapes), then GREEN on the fixed iso copy.
- Mutation check per fix family (one mutation each): the mutation must flip the corresponding GREEN back to RED.
- No historical rewrites. No self-signing (`implementer_signed=false`). No git writes.
- READ-ONLY: revenue-forecast `scripts/`, company-wiki `src/`, the I-06-A original attempt (except reading).
  EXPLICIT carve-out (parent P4-SCOPE): revenue-forecast `tests/` may receive the product-test deliverable
  `tests/test_message_contract_pins.py` and the loose-regex replacement in `tests/test_fc905b_trusted_receipt.py`
  (tests only, product source untouched). Every product-tree write is recorded in binding.json/changes.diff.
- Scope boundary: the candidate stays UNRATIFIED/known-insufficient on its idempotency key (OPEN-2 domain, NOT ours).
  Migration name per parent correction: the real migration entry is `DurableDemandStore._initialize()` + `DEMAND_SCHEMA`
  (`_apply_additive_migrations` is the CW store.py production mechanism name — not this code).
  Candidate anchor = `7bc5feb0cb5e50227a49ac7322c654f84b04f4b71d9d6578571f0899405b8f7f`.
- P3 boundary (parent ruling): `resume`/`complete` on the DurableDemandStore are UNBUILT INTERFACES (correct absence
  per handoff L240 "不得假装存在"), their construction = I-06-B nine-step card, NOT this card. We do NOT build them.
  What IS in scope: the orphan-row defect (P3-A explicit expire/reclaim) and post-expiry defined refusals (P3-B).

## Frozen message contracts (verbatim; pinned by tests; 1-byte mutation must go red)

### M-D1 demand store state refusals (NEW class `DemandStateError(DemandStoreError)`)
1. `f"no demand {demand_id!r}"`
2. `f"demand {demand_id!r} is not claimable"`
3. `"no ready demand to claim"`
4. `"lease expired"`
(all raised as `DemandStateError`; store-failure family stays `DemandStoreUnavailable` with the candidate's
EXISTING message contracts, unchanged: `"demand store unavailable: {type}: {exc}"`,
`"demand store schema failed: {type}: {exc}"`, `"demand store write failed: {type}: {exc}"`,
`"demand store read failed: {type}: {exc}"`.)

### M-P1 prompt-injection writer (product module copy)
5. `f"{field} must be a lowercase SHA-256"` (existing contract; now also for MISSING source_sha256/policy_hash/evidence_payload fields that are hash fields)
6. `"evidence_payload must be provided (evidence_sha256 must bind the evidence bytes)"`
7. `"evidence_sha256 does not match sha256(evidence_payload)"`
8. `f"declared status {status!r} contradicts scan verdict {scan_status!r} (fail closed)"`
9. disposal gate family (exact prefix `disposal authorization unavailable: `), checked in this order:
   - `"disposal authorization unavailable: ignore_reason"`
   - `"disposal authorization unavailable: ignore_authorizer"`
   - `"disposal authorization unavailable: authorized_at"`
   - `"disposal authorization unavailable: declared_matches"`
   - `"disposal authorization unavailable: trust root not established"`
   - `"disposal authorization unavailable: signer_key_id"`
   - `"disposal authorization unavailable: authorizer signature"`
   - `f"disposal authorization unavailable: signer key {signer_key_id!r} not in trust root"`
   - `"disposal authorization unavailable: authorizer signature invalid"`
   - `"disposal authorization unavailable: signature verification backend unavailable"`
10. `f"concurrent write conflict: document {document_id}"`
11. `f"store busy/lock timeout: {type(exc).__name__}: {exc}"`
12. `f"state_domain must be 'review' for a review receipt (got {state_domain!r})"`
13. guard gate: `f"state_domain {value!r} is missing or illegal — fail closed (ambiguity is never defaulted)"`;
    `f"state_domain {value!r} record cannot be read as {expected!r}"`;
    `f"ReviewEvaluation state_domain must be 'cache', got {value!r}"`

### M-P2 product texts pinned as-is (P4-SCOPE; NOT changed by us)
14. blocked sentence (RF scripts/source_preparation.py:154-156, verbatim):
    `"prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status=not_reviewed)"`
15. six demand/claim refusal texts (RF scripts/processing_demand.py + CW source_catalog/processing_demand.py, verbatim identical in both repos):
    `f"no demand {demand_id!r}"`, `f"demand {demand_id!r} is not claimable"`, `f"demand {demand_id!r} is in backoff"`,
    `"no ready demand to claim"`, `f"lease owned by {demand.lease_owner!r}"`, `"lease expired"`
16. `f"{field} must be a lowercase SHA-256"` family (CW prompt_injection.py:37 + guard siblings)
17. `"parser/llm counts absent from the resolution envelope — fail closed instead of fabricating 0"` (RF source_preparation.py:159-162)
18. candidate clause shapes (w06a_candidate_patch.block_message), pinned with frozen fixture:
    `f"{base}; demand_store_error={store_error}; gaps={len(gaps)} next_action={first}; {resume}"` and
    `f"{base}; demand_queued demand_id={registration['demand_id']} source={registration['demand_key'][:16]} gaps={len(gaps)} next_action={first}; {resume}"` where
    `base = "prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status={status})"`.

## Fix groups and frozen expectations (per-fix red/green)

### P1 (from 01_additive_migration.txt; probe FAIL items P1-b2/P1-c)
- P1-a fresh migrate: `_initialize` on empty DB rc=0, table + `idx_processing_demands_key` created (01's P1-a PASS must stay PASS).
- P1-b idempotent re-migrate: 2nd/3rd `_initialize` rc=0, schema byte-stable, rows untouched (01's P1-b PASS must stay PASS).
- P1-c N-1 additive migrate: on the N-1 table (base columns: demand_id, demand_key, kind, status, source_id,
  source_sha256, review_policy, role_set, gaps_json, created_at, updated_at) `_initialize` ADDS EXACTLY the 6 missing
  columns (attempts INTEGER NOT NULL DEFAULT 0; request_sha256 TEXT NOT NULL DEFAULT ''; request_json TEXT NOT NULL
  DEFAULT '{}'; candidate_marker TEXT NOT NULL DEFAULT ''; lease_owner TEXT NULL; lease_until REAL NULL), 1st and 2nd
  run both rc=0 (idempotent), the 2 old rows preserved with attempts∈{0,NULL}, lease_owner NULL, lease_until NULL.
  This is REAL ALTER TABLE ADD COLUMN introspection-based migration (not CREATE TABLE IF NOT EXISTS no-op).
- P1-d upgraded DB usable: register() and claim() then work on the migrated N-1 DB (01's P1-c rc=1 crashes flip to rc=0).
- P1-e error contract: missing-column-class sqlite failures in register()/claim()/list_active() surface ONLY as the
  store's own types (`DemandStoreUnavailable`/`DemandStoreError`) with the M-D1/existing message contracts — no bare
  `sqlite3.*` escapes (01's P1-c claim `OperationalError: no such column: lease_until` flip). Verified by a
  migration-neutralized variant (same N-1 DB with the migrator bypassed) so the wrap is proven independently of P1-c.
- P1-f fresh-DB path unchanged-green (no regression).

### P2-B (from 02_concurrent_claim.txt assert B FAIL)
- Multi-process race for the single pending demand: exactly one winner (assert A stays PASS) AND every loser receives a
  DEFINED refusal = exception of the store's own class + assertable verbatim text (M-D1), never bare `None`.
- `claim()` never returns None: empty/unclaimable refusals raise M-D1 items 1-4 per the precedence in APPEND-A.

### P3-A/P3-B (from 03_lease_expiry.txt stranded-running defect)
- P3-A: explicit `expire(*, now)` reclaim entry (memory-queue `expire()` shape): running rows with lease_until<=now go
  back to pending with lease cleared (owner/until NULL), returns the count; after expire() the row is claimable again
  (explicit — claiming never silently steals a running row).
- P3-B: post-expiry refusals are defined (M-D1 `"lease expired"`), never silent None: claim() against a queue whose only
  row is running+expired-lease ⇒ DemandStateError("lease expired"); claim(demand_id=<running+expired>) ⇒ same. Wrong
  owner / live lease ⇒ item 2/3 texts. resume/complete remain ABSENT (structural-absence assertion; OPEN-5 C4 pending).

### P4-SCOPE (from 04_blocked_message_sweep.md; C8 pin gap)
Face 1 (candidate side, our iso): verbatim message assertions pin M-D1 items 1-4 and M-P2 item 18 clause outputs
(exact full strings with the frozen fixture), not just exception types. GREEN on current texts.
Face 2 (RF product test side; tests only): `tests/test_message_contract_pins.py` pins M-P2 items 14, 15, 16, 17
(verbatim match + cross-repo RF/CW equality for item 15 and the three-copy convergence for item 14), replaces the loose
regex `not reviewed|blocked` coverage in test_fc905b (and the sibling loose `parser|llm|counts` match, same defect class).
Single-source convergence (parent increment): the 2 hand-copies of the blocked sentence (w06a_candidate_patch block_message
base, w06a_apply_candidate REPLACED anchor) reference ONE candidate-side constant; no cross-repo import is possible, so
product literal + candidate constant are pinned equal by assertion (covers all three surfaces).
ABSENT handling (honest, no invention): `cases_json_declared_expectation_missing` = runner vocabulary, zero hits in both
product repos is CORRECT (structural zero-hit assertion + decision.md clarification); resume refusal text = product
surface ABSENT (structural-absence assertion + OPEN-5 C4 note).
RED/GREEN for P4 = all pins GREEN on current texts + single-byte mutation of any pinned copy ⇒ RED (proof of non-vacuity).

### P5-c (from 05_fake_receipt.txt WRITE-SIDE-GAP-CONFIRMED)
`record_prompt_injection_review` requires `source_sha256` + `policy_hash` for ALL statuses: missing/None/invalid ⇒
PromptInjectionReviewError M-P1 item 5 verbatim. RED = unbound detected_and_ignored write accepted (probe P5-c).
Call-site census recorded (which callers pass the dual binding); call sites we cannot lawfully change are reported
honestly, not silently broken.

### P5-a (from 05 FORGERY-FACE-CONFIRMED; parent-upgraded form)
`record_prompt_injection_review` requires `evidence_payload` (the scanned bytes/text): ① `sha256(payload)` must equal
`evidence_sha256` (items 6/7); ② the writer internally re-runs `scan_text(payload)` and the declared status must equal
the scan verdict (item 8) — a fabricated "clean" receipt over payload that actually contains an injection is REJECTED.
Positive control: truly-clean payload + not_detected + valid bindings ACCEPTED. Residual forgery face (any hash can still
be recomputed from any payload) is documented in decision.md; its complete closure = OPEN-6 C1/C2 authorized-tuple+signature
(identity chain = letter B, external).

### P5-b (parent upgrade: real fix, disposal gate, fail-closed)
`detected_and_ignored` writes pass ONLY when (i) the authorization tuple is complete (ignore_reason non-empty +
ignore_authorizer + authorized_at + declared hit snapshot `declared_matches`) AND (ii) the trust root is loaded with
≥1 key AND (iii) the authorizer signature verifies over the canonical tuple. Any gap ⇒ item 9 family verbatim.
Trust root not established ⇒ the status is ALWAYS REJECTED (mechanical form of "no identity ⇒ zero product-semantic
lines"; zero fake fixes). Signature = Ed25519 over canonical JSON
(sorted keys, compact separators, ensure_ascii=False, UTF-8) of
{"authorized_at", "document_id", "evidence_sha256", "ignore_authorizer", "ignore_reason", "matches", "policy_hash",
"source_sha256", "status":"detected_and_ignored"}; trust root JSON
{"schema_version":"1.0","signers":{key_id:{"algorithm":"ed25519","public_key_base64":...}}}, path via parameter
`trust_root_path` or env `PROMPT_INJECTION_TRUST_ROOT`. `not_detected` keeps the free-string reviewer BUT the write is
audited: receipt gains `writer_audit` fields `"writer_pid"`, `"writer_write_at"`, `"writer_identity_note"` =
`"writer metadata is an audit trail, NOT verified identity"` (dict[str,str] shape kept). Full identity chain =
PARTIAL-fix-pending-external (enables after letter B).

### P6-A (from 06_concurrent_receipt_writes.txt lost_write_count=7)
Optimistic concurrency control on the read-modify-write of `documents.metadata_json`: the UPDATE is a CAS
(`WHERE document_id=? AND metadata_json=<value read>`), on conflict re-read+retry (bounded, default 5 attempts) and
after exhaustion raise M-P1 item 10 (defined rejection). NO SILENT DISPLACEMENT: every write is either acknowledged
after a won CAS or explicitly rejected (count conservation: acks+rejections == attempts, zero third outcomes), and
read-back proves every write via an append-only audit trail `metadata_json["prompt_injection_review_audit"]` (list of
{seq, writer_pid, write_at, evidence_sha256, source_sha256, policy_hash, status}). No-regression red lines that MUST
stay green: under default timeout the concurrent writes succeed (retry absorbs contention) with zero lock exceptions,
and the interleaved-read phase keeps zero tearing/zero reader exceptions. Higher slot semantics (queue/merge) remain
for ratification — the single-key primary receipt slot keeps its shape. Mutation: removing the CAS predicate must
re-produce silent lost writes.

### P6-B (from 06 P6-A2 bare throws)
Bare `sqlite3.OperationalError "database is locked"` must not escape: all sqlite failures in the writer/reader paths are
wrapped as `PromptInjectionReviewError` item 11 verbatim ("store busy/lock timeout: …"). Timeout semantics: the caller's
connection/timeout parameters may only be TIGHTENED — the fix adds no waits beyond bounded no-sleep CAS retries.

### C7-SCOPE (ruling C7 + parent increment)
STEP 1 (done before implementation, evidence recorded): frozen-vocabulary conflict check over ZR-507/I-06-B frozen
artifacts and product contract texts for `"ignored"`. CONFLICT FOUND (I-06-B oracle.md:87 pins `cache_state="ignored"`
in frozen acceptance expectations; handoff.json:50-51; commands.json:17 case name; harness assertion
`eval_ignored.cache_state == "ignored"`; ruling.md:233-234 consumption bottom line quotes the same vocabulary) ⇒ per
ruling item 6 the RENAME route is blocked by frozen vocabulary ⇒ FALLBACK = explicit assertion field `state_domain`,
fail-closed (conflict list in decision.md + parent report).
Fallback contract: every state-carrying record gains `state_domain: "cache" | "review"`; missing or illegal ⇒
REJECT / strictest interpretation, ambiguity is never defaulted into either semantics (M-P1 items 12/13).
- review receipts are stamped `"state_domain": "review"`; read paths treat != "review" as malformed (fail-closed
  ⇒ not_reviewed), including missing (old) receipts.
- `ReviewEvaluation` gains REQUIRED `state_domain` (must be `"cache"`); construction with missing value (TypeError) or
  illegal/mismatched value (PromptInjectionGuardError, item 13) is REJECTED.
- `require_state_domain(value, expected)` gate + `_SAFETY_MAP` lookup fail-closed on unknown cache_state
  (strictest verdict "unsatisfied" + frozen next-action
  `"unrecognized safety cache_state — fail closed (ambiguity is never defaulted)"`, never KeyError, never pass).
- `detected_and_ignored` (review conclusion) and `cache_state="ignored"` (cache invalidation) vocabularies stay as-is
  (rename blocked); the domain tags carry the disambiguation.
Dual negative artifacts (red/green):
 ① a cache-invalidation record (state_domain="cache", cache_state="ignored") cannot be read as a review conclusion
    (gate rejects; policy-changed evaluation keeps status="not_reviewed");
 ② a `detected_and_ignored` receipt record (state_domain="review") cannot be read as cache state (gate rejects);
 ③ record missing `state_domain` ⇒ REJECTED at both boundaries (receipt read ⇒ fail-closed None/not_reviewed;
    ReviewEvaluation construction ⇒ TypeError);
 ④ illegal value ("banana", cross-domain tag, unknown cache_state) ⇒ REJECTED / strictest, never passed.
Mutation: removing the state_domain validation must flip ③/④ negatives red.

## Evidence map 01_additive_migration.txt → this attempt's evidence

| 01 scenario | verdict there | this attempt scenario | expected here |
|---|---|---|---|
| [P1-a first _initialize on fresh DB] rc=0 | PASS | S1 fresh-migrate | PASS (kept) |
| [P1-b re-run _initialize 2nd/3rd] rc=0 | PASS | S2 idempotent re-migrate | PASS (kept) |
| [P1-b2 N-1 migrate 1st/2nd] rc=0 but `new_columns_added=[]`, `ok:false` | FAIL | S3 N-1 additive migrate | PASS (6 columns added, idempotent) |
| P1-b2 rows after migrate (2) preserved | PASS | S3 rows-preserved sub-check | PASS (kept) |
| [P1-c register() against migrated N-1 DB] rc=1 `no column named request_sha256` | FAIL | S4 register-on-upgraded | PASS (rc=0) |
| [P1-c claim() ...] rc=1 bare `OperationalError: no such column: lease_until` | FAIL | S5 claim-on-upgraded + S6 error-contract wrap | PASS (rc=0 / store-owned type) |
| P1-c `old_rows_preserved/defaults_ok` true | PASS | S3 defaults sub-check | PASS (kept) |
| P1 OVERALL FAIL | FAIL | S1-S6 aggregate | PASS |

## Frozen red/green criteria table (parent terminal list)

① P1 (fresh-migrate green; N-1 migrate adds exactly the missing columns rc=0 + old rows intact; 2nd migrate idempotent rc=0;
   register/claim/complete-fail paths work or fail with store-owned errors on the upgraded DB; fresh-DB path unchanged-green)
② P2-B claim loser = defined refusal (coded class + verbatim text)
③ P3-A expired running row explicitly reclaimable → re-claimable; P3-B post-expiry refusals = "lease expired" family
④ P4 message pins GREEN on current texts + single-byte mutation RED (both faces) + three-copy convergence equality
⑤ P5-a payload binding + scan re-verification (fabricated clean ⇒ rejected; true clean ⇒ accepted)
⑤b P5-c dual binding mandatory + call-site census recorded
⑤c P5-b disposal gate: spoofed detected_and_ignored ⇒ always rejected while trust root unestablished (+ tuple/signature checks)
⑥ P6-A no silent lost write (traceable: ack-won-CAS or defined rejection; count conservation; audit trail read-back provable)
   + P6-B lock errors wrapped ("store busy/lock timeout") + mutation each family + fresh-DB no-regression + call-site census
⑦ C7 state_domain fail-closed (dual negatives + missing/illegal negatives), conflict list reported
Mutation discipline: one mutation per fix family (P1, P2-B/P3, P4-pin, P5-a/P5-b/P5-c, P6-A CAS, P6-B wrap, C7 gate)
must flip its GREEN checks RED.

---
APPEND sections (dated, additive only) follow below if the parent adds further increments.

## APPEND A — 2026-09-22 (parent increment P7-SCOPE: candidate idempotency key revision; scope supersession)

Provenance: parent message 2026-09-22 (owner ruling 「发现的缺陷都要全部修复」).  This APPEND SUPERSEDES the
frozen §0 scope sentence "the candidate stays UNRATIFIED/known-insufficient on its idempotency key (OPEN-2 domain,
NOT ours)" for the KEY REPAIR ONLY: OPEN-2 option A is now RULED and the OPEN-5 ruling §4.5 item 1 mandates the
contract revision, so the known-insufficient key becomes an in-scope repaired defect (fix group 14).  Everything
else in the frozen text stands.

Frozen expectations (P7):
1. `demand_key = sha256(canonical_json({source_sha256, review_policy, role_set, request_identity}))` where
   `request_identity` covers `as_of_date` / `target` / `payload digest` (verbatim OPEN-5 §4.5 item 1, aligned with
   OPEN-2 option A); canonical JSON = sort_keys + compact separators (same convention as the OPEN-2b
   role_set=RF_W06_ROLE_SET sorted-deduped-comma-string convention).
   Frozen form: `request_identity = {"as_of_date": <request["as_of_date"]>, "target": <request["target"]>,
   "payload_digest": sha256(canonical_json(request))}` (each field None when absent).
2. Storage/judgment chain in sync (via the P1 additive migrator): new column `key_version`
   (TEXT NOT NULL DEFAULT 'triple-v1' on migrated legacy rows; new registrations write `'request-identity-v2'`).
   NO silent semantic change: legacy rows keep their historical key semantics (never recomputed/relabelled);
   register() dedupe judges within key_version only; list/read exposes key_version (OPEN-4-style read-time judgment).
3. RED/GREEN = the c8/c9/c10 counterexample family: same source/policy/roles with (c8) only as_of_date differing,
   (c9) only target differing, (c10) only payload content differing — old behavior silently merges each pair into one
   key/demand row; GREEN = each pair yields TWO keys + TWO demand rows, each row's request_sha256 == its own
   canonical request hash.  Mutation: drop one identity field (as_of_date) from request_identity ⇒ c8 collapses
   again (RED regression).  Evidence names: `evidence/p7_key_c8c9c10_*.txt`.
4. P1-c column-set amendment (additive to frozen text): the N-1 upgrade now adds EXACTLY the 7 missing columns
   (the frozen 6 + `key_version`); P1-c's "exactly the 6" is superseded by this list — every other P1 expectation
   unchanged.  decision.md must cite the three authorities verbatim-ish: OPEN-2 option A, OPEN-5 §4.5 item 1,
   and that ruling's C1 condition (key includes request identity + probe re-run).

## APPEND B — 2026-09-22 (implementation-note amendment discovered during GREEN P6: P6-B commit boundary)

The P6-B face is not only in-function sqlite calls: with the writer function wrapped, the bare
`sqlite3.OperationalError "database is locked"` surfaced at the CALLER-side `connection.commit()` (06 Phase A2
reproduced it in GREEN pre-amendment).  Therefore the P6-B contract is amended (and pinned by scenario): the
writer owns the transaction end of ITS own write — `record_prompt_injection_review` commits on success and rolls
back on failure, so every lock/contended failure surfaces as the defined
`PromptInjectionReviewError("store busy/lock timeout: …")`.  Callers may still commit/rollback afterwards for
their own pending work.  All frozen M-P1 texts unchanged; the timeout rule (caller parameters may only be
tightened) is unchanged and kept (no added waits).

## APPEND D — 2026-09-22 (P7 internal-tension resolution, additive)

Observed during the P7 mutation check: with APPEND A's literal
`payload_digest: sha256(canonical_json(request))` (FULL request) the frozen
mutation criterion "drop one identity field (as_of_date) ⇒ c8 collapses
again (RED regression)" is UNSATISFIABLE — the full-request digest absorbs
every single-field drop (removing as_of_date from the identity dict still
leaves distinct keys via payload_digest).  APPEND A items 1 and 3 are in
internal tension.  Resolution (additive, both texts stand): the three
components are made DISJOINT and independently observable —

  request_identity = {"as_of_date": request.get("as_of_date"),
                      "target": request.get("target"),
                      "payload_digest": sha256(canonical_json(
                          request minus {as_of_date, target}))}

— still verbatim "request_identity 覆盖 as_of_date/target/payload digest"
(all three aspects covered, canonical convention unchanged), and now each
frozen component's removal is observable exactly as APPEND A item 3 demands
(drop as_of_date ⇒ c8 collapses; drop target ⇒ c9 collapses; drop
payload_digest ⇒ c10 collapses).  Row-level `request_sha256` remains
sha256(canonical_json(FULL request)) as before (its per-row own-hash pin is
unchanged).

One mutation per fix family, each must flip its GREEN checks RED: P1 (drop one ADD COLUMN spec), P2-B (claim
empty-pool refusal returns None), P3 (post-expiry refusal text changed / expire neutered), P4 (one byte of a
pinned message in a copy), P5-a (payload binding removed), P5-b (disposal gate removed), P5-c (binding made
optional), P6-A (CAS predicate removed), P6-B (wrap removed), C7 (state_domain check removed), P7 (one identity
field dropped).  APPEND D records the P7 internal-tension resolution
(payload_digest disjoint decomposition so the single-field-drop mutation is
observable).

## APPEND C — 2026-09-22 (mutation checklist consolidation)

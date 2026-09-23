# reviewer_report.md — I-06-A / a20260922-02 (independent signing review)

- Reviewer role: independent signing reviewer over the implementer's `review_pending` / unsigned handoff (this report is the review signature; `handoff.json` stays untouched — the implementer never self-signed).
- Date: 2026-09-22 (post-delivery; attempt window 22:15–23:12 CST).
- Tools used: `read`, `grep`, `pwsh` (re-hash / mtime / byte scans), one disclosed `git diff --no-index` (see finding 11), plus `python -c` for a pure-computation semantics probe (zero file IO).
- Writes performed by this review: exactly the 2 deliverables of this review — `reviewer_report.md` + `reviewer_report.sha256`. Both product repos, both sibling/historical attempts, and the rest of this attempt tree were treated read-only. No `git` command that reads or writes repository state was run by this review.

---

## Verdict: **changes_required**

Single blocking item = finding 1 (NaN ttl widening bypass ⇒ this iso guard cannot be certified C6-conformant as-is). Each remaining checked surface of this card is verified: each listed pin re-hashes equal, RED/GREEN/MUTATION raw evidence is internally consistent and non-hollow, the six sampled ratified-conformance clauses hold, zero receipt hooks in both directions, `state_domain` fail-closed with both semantic negatives, and the boundary claims hold modulo findings 9–11 (each a non-blocking note).

CLIP-vs-REJECT is NOT adjudicated here (parent's standardization decision; finding 2 records the divergence).

---

## 1. Deliverables integrity (values re-hashed live; nothing copied from memory)

### 1.1 Frozen pins vs live bytes — MATCH on pin vs live

| Artifact | Live SHA-256 (this review) | Pinned in | Result |
|---|---|---|---|
| `iso/…/store.py` | `b8e003620a746dc5e7ae7355697005bc9324c8a047e2e2dc6887e74701b15f81` | binding.json + handoff output_hashes | MATCH |
| `iso/…/processing_demand.py` | `d862bb10d4a927f561c38b0e57742a3217124c2a62a13561b8c447f8895ccd18` | binding.json + handoff | MATCH |
| `iso/…/prompt_injection_guard.py` | `cf9174b538288f71349f3d33b46f96eacb6a16f5df4906764b08439230119c03` | binding.json + handoff | MATCH |
| `before/…/store.py` == live CW repo `store.py` | `1a7832404c39da858400a99d2f7e9495e8b169498dacad591fda5447b2da9615` (both) | binding/handoff `input_hashes` | MATCH — real repo == before copy |
| `before/…/processing_demand.py` == live CW | `90f232edb7804f78a16c6b4e865255cd607a1d0dc30384fc1cd6faa1833ac88b` (both) | ZR-507 pin `90f232ed…3c8b` | MATCH — pin un-drifted |
| `before/…/prompt_injection_guard.py` == live CW | `f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08` (both) | binding/handoff | MATCH |
| `prompt_injection.py` real == before == iso | `7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618` (identical across real repo, before copy, iso copy) | binding/handoff `(UNCHANGED)` | MATCH across real, before and iso copies — see finding 8 re the review-brief prefix |
| `oracle.md` | `25d617c2461b858ed417beca2218be83ce7d083e8ae5aa33433061fe5c656535` | handoff output_hashes | MATCH |
| `changes.diff` | `5df600d1f8e500c34f00469aadea911b016a897f5a1517c87048897f81847716`; 1056 lines; header scope = exactly `processing_demand.py`, `prompt_injection_guard.py`, `store.py` | handoff | MATCH; line count 1056 exact; scope == live iso-vs-before byte compare (3 files changed, no file added, no file removed) |
| `scripts/w06a2_cases.py` | `9fac677108ce7288960768ff180514ecfb455d62d3a631629d135a024ad26d64` | handoff | MATCH |
| `scripts/w06a2_evidence.py` | `78b32c260695a5109cbb002340f68d5d48213eb5a1071b9f8842e913fe17cc02` | handoff | MATCH |
| `scripts/w06a2_make_mutant.py` | `e7944de8bf27c33c377b15e3ff0b82f950966fd83dc33b97763715daad25ba05` | handoff | MATCH |
| `scripts/w06a2_make_diff.py` | `2cb334fb33124e83b4241e9d4c28df7a652ea7355245919142754847a6dee59a` | handoff | MATCH |

Fresh hashes recorded for ledger gaps (finding 4): `commands.json` `115130bad77443bc22bda38f8540425b76b744a7181ca3c6fa2168339de6be60`; `decision.md` `329dbfb705bbf8a00cfd4f486d02e17dd5ef43e7de3296cd8403aae7e9eedb41`; `recovery/README.md` `7284f4980053af44cdf1a4ea24e5267aa0f2f57f525bd72d365445af70a35b63`; `handoff.json` `4d004af84bd36a02b4b4dadc464e594828f75b2867732c1f74fb54fede63e0b7`; `binding.json` `5a8629dbcc3b22469a449268a18901117a493cca65cfaa4fb046f6abb952886f`; `iso-mutant/MUTATION.json` `d5b55942e8ddfb61bc1ff590b60d0fe1814f1e89c8cdec8ef9435b0f0d0245e2`.

### 1.2 oracle.md frozen-first claim — TRUE as worded

- `oracle.md` CreationTime 22:18:10, final write (§2-补 addendum) 22:31:38.
- First run artifact in the tree = `__pycache__/*.pyc` at 22:47:03; `evidence/red_before.json` created 22:47:29 — both after the oracle freeze.
- First implementation write to any candidate file = `iso/…/store.py` 22:32:57 (guard 22:36:50, `processing_demand.py` 22:50:35), harness `w06a2_cases.py` created 22:43:21 — each postdates the oracle's final write.
- Nuance (benign): the attempt dir's literal first files are the `before/`+`iso/` base snapshot copies staged at 22:15:05 (copy operation, no runs, no code edits). The oracle claims precedence over the first *run* and over evidence/implementation, and that ordering holds on every relevant timestamp.

### 1.3 handoff status face — as required

`status=review_pending`, `implementer_signed=false`, `disclosure_adaptation=unmapped`, `accuracy=unproven`, `reviewer_status="PENDING independent review — implementer 未自签"`, `status_note` explicitly says not self-signed. Nine-step protocol block present. `changed_paths` = attempt tree as the sole write area.

---

## 2. Ratified-contract conformance map — SIX sampled clauses verified in code

**(a) Production migration shape + lifecycle exemption — VERIFIED.**
`_apply_additive_migrations` pre-exists in the production `before/…/store.py` at line 1072 (the decision's citation of ":1072 区域" is exact); iso calls it from `_initialize` (iso store.py:1169) and the WU-I06A block sits *inside* the production function (iso store.py:1286-1298: create table when missing, else `ensure_processing_demand_columns` backfill, plus events table). `_DDL` concatenates `processing_demands_schema + processing_demand_events_schema` (iso store.py:470). Retention comment iso store.py:116-130 states lifecycle exemption explicitly ("NO foreign key to documents/sources", explicit-transition-only, terminal rows never deleted); schema bodies (iso store.py:157-200) were read: no `REFERENCES` clause on either demand table — the no-FK claim is real, not just prose. `W06A2-P3` exercises both N-1 variants (missing table; narrow table missing `request_sha256`/`lease_until`) and `W06A2-N9` exercises full dependent-row purge with the demand row surviving.

**(b) demand_key formula — VERIFIED.** iso `processing_demand.py:425-445`: `sha256(canonical_json({source_sha256, review_policy, role_set: normalize_role_set(...), request_identity: validated}))` — exactly the OPEN-2A / OPEN-5 §4.5.1 shape; `_validated_request_identity` (376-395) rejects an empty identity (covered by N4's `{}` probe). `evidence/request-to-demand-binding.json` shows c1/c3/c10/c8-c9 rows each binding their own `request_sha256`. Nuance = finding 6 (any-of vs covers-three validation).

**(c) register_before_block order — VERIFIED by construction + cross-process probe.** iso `processing_demand.py:483-511`: the durable `demand_store.register(...)` call (line 500, inside a committed transaction) completes *before* the `DemandBlock` object is constructed (502-511); `security_verdict` is passed through untouched; failure branch returns `demand_store_error=` with `demand=None` and never `demand_queued` (N2 proves the branch: dropped table ⇒ `demand_store_error=DemandStoreUnavailable: OperationalError: no such table: processing_demands`, probe rows unchanged). Second-process readability is proven twice: `W06A2-P1` (child process sees exactly the 1 registered row, same durable id, `read_prompt_injection_review is None`) and evidence `demand.cross-process.json` p2. Note: no probe exists *mid-function* between register-commit and block-return (not externally instrumentable); the ordering property rests on code structure plus the post-hoc cross-process durability probes — accepted as sufficient.

**(d) c7 byte-pinning — VERIFIED.** `demand_queued_clause` (458-462) renders `demand_queued demand_id={id} gaps={n} next_action={text}`; `demand_store_error_clause` (465-466) renders `demand_store_error={type(error).__name__}: {error}`. `W06A2-C8` asserts equality against frozen literals (harness 727-738, including the `demand_queued ` / `demand_store_error=` prefix checks) and the raw GREEN file echoes both literals verbatim.

**(e) gaps three values only — VERIFIED.** `GAP_KINDS = frozenset({"missing","unsupported","not_applicable"})` (293); `_validated_gaps` (398-422) raises `DemandRegistrationError` for any kind outside the closed set with the sorted-set message; N7 loops `ok / clean / reviewed_ok / MISSING / None / "" / detected_and_ignored` — all refused; round-trip of the 3 distinct kinds proven; schema/record surface carries no clean/ok state.

**(f) zero receipt hooks — VERIFIED in both directions by grep + behavior.**
- Demand side: `iso/processing_demand.py` contains 3 comment lines about receipt independence (280-282) and *zero* code references to `receipt` / `evaluate_review` / `documents` / `prompt_injection`. iso `store.py` demand surface has no receipt/close hooks (its sole `receipt` hits are the pre-existing `activation_journal` production DDL, unrelated vocabulary).
- Receipt side: `prompt_injection.py` and `prompt_injection_guard.py` contain zero references to `demand` / `CatalogDemandStore` / `processing_demand`.
- Behavioral: `W06A2-N6` checks both directions — receipt invalidation ⇒ demand row byte-identical and still `pending`; demand `complete` ⇒ `documents.metadata_json` byte-identical.

---

## 3. RED / GREEN / MUTATION / cross-process evidence (raw files re-read)

- **RED = 0/15**: `evidence/red_before.json` re-read in full — 15 cases, all FAIL, every error is an `AttributeError` on a surface absent from production originals (`CatalogDemandStore` ×12, `GAP_KINDS`, `RECEIPT_TTL_POLICY_CAP_SECONDS`, `ProcessingDemandRecord`, `state_domain_of`) — i.e. "no persistent surface", with `before/` byte-verified equal to the live production repo (§1.1). Scoreboard claim `0 passed / 15 failed` exact.
- **GREEN = 15/15**: `evidence/green_iso.json` re-read — 15 PASS with substantive measurements (clause strings, 4 distinct demand ids, event trail, thread lists, cap=2592000, pinned literals).
- **MUTATION = 12/15, red = P4/N1/N5**: `evidence/mutation_iso_mutant.json` re-read — exactly those 3 FAIL. Mutation integrity: byte-diff iso vs iso-mutant shows **one** differing source file and, newline-normalized, **one** differing line — removal of `"request_identity": identity,` from `compute_demand_key`'s payload (matches `MUTATION.json`'s declared before/after). Each of the 3 red tracebacks terminates in `DemandIdempotencyViolation` raised at the *second* identity-divergent `register(...)` in each fixture (harness lines 342 / 373 / 518) — the causal chain "key loses request identity ⇒ divergent requests collide ⇒ fixture's two-row/one-row expectation breaks" is exactly what decision.md's mutation note claims; P4/N5 collateral is the same guard, not a second flip. Mutation proves the cases are non-hollow. Newline caveat = finding 7.
- **Cross-process**: `w06a2_evidence.py:64-70` issues seven sequential `subprocess.run([sys.executable, w06a2_cases.py, --target iso, --child …])` calls (register/query/register/query/register/register/query) — the "7 real processes" claim is corroborated by the spawning code, the scenario list, distinct durable ids, and all 7 assertions true in the JSON. pids/argv are not recorded in the JSON = finding 3. The in-suite children (`child()` helper, harness 182-191) are used by P1/P2/N1 likewise.

---

## 4. ★ TTL clip-vs-REJECT adjudication INPUT (I-06-A scope)

### 4.1 This card's CLIP mechanism, traced

- `RECEIPT_TTL_POLICY_CAP_SECONDS = 86400*30` (iso guard:71) = 2592000.
- `effective_receipt_ttl(ttl)` (78-82): validates `isinstance` + `ttl >= 0`, returns `min(ttl, cap)` — CLIP.
- `effective_review_instant(now)` (85-98): parseable caller `now` earlier than the injectable policy clock (wall clock in production) ⇒ replaced by the policy clock (clip forward); later caller `now` kept; unparseable `now` passed through untouched so `_freshness` fails closed as `tampered`.
- `evaluate_review` (296-297) applies both clamps before binding/freshness evaluation.

### 4.2 The two mandated proofs — HOLD

1. **ttl=∞ / 超大 ⇒ effective=cap**: code `min(float(ttl), cap)`; live probe: `min(1e30, 2592000) = 2592000`, `min(inf, 2592000) = 2592000`. N8's raw GREEN check `effective_receipt_ttl(10**30) == 86400*30` measured true; stored measurement `cap=2592000`.
2. **past-now ⇒ policy clock ⇒ expired cannot revive**: N8 records a receipt aged `cap+120`s, then evaluates with caller `now = reviewed_at + 1s` (deep past) and `ttl=1e30` — with clamps the effective instant becomes the real wall clock, age `cap+120 > cap` ⇒ measured `expired`, `not_reviewed`. On the production original (no clamps: `before` guard `_freshness` at 159-174 / `evaluate_review` at 176-203 passes caller values raw) the same input would evaluate age=1s ⇒ `hit` — i.e. revival, confirming the clip is what enforces C6 for this input class. The 1h-tightening sub-check also measured `expired`.

Self-consistency of the CLIP design: consistent (clip-ttl + clip-forward-instant, no reject paths, `not_reviewed` fail-closed on every non-hit).

### 4.3 C6 completeness — FAILS on non-finite ttl (finding 1, the blocking item)

For caller `ttl = NaN`: `NaN < 0` is False ⇒ validation passes; `min(NaN, cap)` returns NaN (probe-confirmed for this argument order); `_freshness` computes `age > NaN` = False ⇒ the expiry branch never fires ⇒ the receipt is immortal ⇒ the caller has *widened* the freshness window, which is precisely what OPEN-6 C6 ("调用方 now/ttl 只能收紧、不能放宽", adopted by owner §十九) forbids. There is no `math.isfinite` anywhere in the iso guard. The sibling TTL-30D-POLICY card documents this same class as its DEF-3 ("NaN comparisons all False => immortal receipt") and closes it. This card's oracle N8 froze ∞/超大/past-now only, so the hole is oracle-unfrozen but contract-covered. A CLIP implementation can close it without becoming REJECT (reject non-finite, or clip non-finite to cap) — remediation choice does not presuppose the global CLIP-vs-REJECT ruling.

### 4.4 Cross-card divergence — RECORDED, not adjudicated (finding 2)

- This card (I-06-A iso): **CLIP** — `effective_receipt_ttl = min(caller, 2592000)`, `effective_review_instant = max(caller now, policy clock)`; no error raised for wide inputs.
- Sibling card `execution_runs/TTL-30D-POLICY/a20260922-01` (in flight): **REJECT** — its iso guard comment/code pins `ttl_seconds exceeds policy cap of 2592000s` via `PromptInjectionGuardError`, plus `math.isfinite` rejection of NaN ("ttl_seconds must be a finite number" in its evidence files).
- Both branches sit inside the ruling's "被拒或被策略上限截断" wording; the sibling's own decision.md already logs the coexistence as its open item U-3 ("归一权在父"). Standardization of the mechanism (and of finding 1's fix) belongs to the parent; this review takes no side.

---

## 5. state_domain disambiguation (boundary-note-6) — VERIFIED

- **Field exists**: `ReviewEvaluation.state_domain` (iso guard:176) with `__post_init__` → `require_state_domain(cache_state, state_domain)` (178-179).
- **Fail-closed**: illegal domain value ⇒ `PromptInjectionGuardError` (140-143); value outside both vocabularies ⇒ error (133-135); domain mismatch ⇒ error with the "'ignored' senses must never be conflated" text (146-149). Missing-field semantics: an omitted `state_domain` defaults to `cache` and is then *verified* against the actual vocabulary — a review-domain `cache_state` with omitted field is therefore rejected (the N10 probe `require_state_domain("detected_and_ignored", "cache")` exercises exactly the call `__post_init__` makes), while an unambiguous cache-domain value with omitted field is accepted as cache. That is the "most-strict interpretation" branch of the oracle's "拒收/最严解释" wording rather than blanket literal rejection; nothing can land in the wrong domain (vocabularies are disjoint). Exact semantics recorded here so the parent reads the claim precisely.
- **Both semantic negatives present** (N10 lines 752-757): `("detected_and_ignored", "cache")` rejected **and** `("ignored", "review")` rejected — cache state ≠ review conclusion, each direction asserted; plus bogus-domain and wrong-domain `ReviewEvaluation` constructions rejected.
- **Rename-rejection rationale documented** in two places: iso guard comment 109-118 and decision.md §4.7 — `CACHE_STATES={hit,ignored,expired,tampered,absent}` frozen by frozen contract tests *and* the ruling vocabulary (OPEN-5 §6.3 cites tampered/ignored/expired/absent), so rename is unavailable ⇒ sanctioned assertion-field fallback. Spot-check of the test-freeze claim: live CW `tests/unit/test_prompt_injection_guard.py` asserts each of the five literal cache states (lines 190-289), and CW tests pin `detected_and_ignored` in the receipt envelope/scan tests — the freeze claim is real (the ZR-507-labelled contract test itself pins demand statuses, so the vocabulary freeze evidence lives in the guard unit tests + ruling text).

---

## 6. Boundaries — verified, with notes = findings 9–11

- **Zero production writes on this card's surface**: the 4 frozen CW files re-hash byte-identical to `before/` AND to the live repo (§1.1); iso-vs-before tree compare shows exactly 3 changed files, zero added, zero removed (no CLI file exists in iso that is absent from before; pre-existing `source_contract/cli.py`/`announcement_cli.py` are byte-identical copies). RF product `src/`+`tools/` show zero in-window modifications.
- **Porcelain substitute** (this review ran no `git`, per its own boundary — see finding 10): mtime-window scan of both repos found in-window activity *outside* this card's surface — CW: session commit on branch `fcap` 22:19-22:24 (`CLAUDE.md`, `README.md`, `artifact_dag.py`, `observability.py`, `tests/test_short_basetemp_convention.py`, `.git` refs), pytest/ruff caches 22:22, `.source_catalog/catalog.sqlite3-shm` 22:57:30; RF: session commit 22:24:40 (+60 `.git` files), `scripts/__pycache__` 22:24:52, `origin/main` reflog 22:39:26, `tests/test_message_contract_pins.py` 23:12:33 and `tests/test_fc905b_trusted_receipt.py` 23:15:07 (both *after* this attempt's last write). None of these paths are in this card's frozen surface; none appear in this card's 9 logged commands (all target the attempt dir + `%TEMP%` dbs); timing/shape matches the session's owner-commit pattern plus concurrent sibling cards. Parent's stated expectation ("only pre-existing dirty + our committed state") should be confirmed by the parent's own porcelain run.
- **Zero git by the card**: `commands.json` = 9 python-script invocations, no git verb anywhere in the attempt's command ledger; `.git` mtimes in both repos correlate with 22:19-22:40 session commits, not with this card's evidence runs (22:47-23:00) — attribution note, nothing beyond it.
- **Historical attempt a20260919-01**: every original file has mtime < 2026-09-22 ⇒ untouched; one NEW file `rulings_transcribed_2026-09-22.md` (Creation=Write=22:21:40, 139,717 bytes, byte-exact ratified-rulings transcription with sha256 pins) was added today — an identical-timestamp twin landed in I-06-B's `a20260919-01` in the same second, which points to one batch actor (parent-side staging) rather than this card (finding 9).
- **I-06-B attempt untouched by this card**: each in-window write under `execution_runs/I-06-B/**` belongs to I-06-B's own concurrent deliverables (its iso/evidence/scripts, 22:41-23:19); nothing in this card's command ledger targets that tree. Actor attribution itself not provable without git/porcelain — see unverified list.
- **No CLI file created** (card's no-guessing rule): confirmed by the zero-added-files tree compare; decision §4.2 + module docstring 284-288 record the rationale.
- **Scope honesty**: grep of the iso tree finds `resume` solely in boundary comments — no resume execution interface, no scheduler/thread path (N3 thread-list evidence); `handoff.scope_boundary.explicitly_out_of_scope` and decision §0/§6.2 state that resume/complete CLI testable face = I-06-B. Claim matches code.

---

## 7. Known open items parity — PRESENT (not dropped)

- `handoff.open_items[2]`: RF `scripts/source_preparation.py` caller-side wiring + CLI-level c8/c9/c10 re-probes → next carrier. Mirrored at decision §6.1.
- `handoff.open_items[3]`: P4-SCOPE cross-repo verbatim pinning of the RF blocked-message sentence (store-side c7 already pinned). Mirrored at decision §6.4.
- Also carried: I-06-B consumption face, CLI-adapter-file not frozen, OPEN-4/OPEN-6 留置① full-bytes runtime probe, P5-b identity chain (BLOCKED-on-external), production-promotion-after-review pattern — each mirrored between handoff and decision §6.
- The parent's "P7" label does not appear anywhere in this attempt's documents (grep `P7` = 0 hits) — closest logged opens are P4-SCOPE / 留置① / P5-b; parent should map its P7 entry to these (unverified list).

---

## Findings (numbered)

1. **BLOCKING — NaN ttl widening bypass in the iso CLIP guard (C6 fail-open).** `effective_receipt_ttl` accepts `ttl=NaN` (`NaN < 0` is False), `min(NaN, 2592000)` returns NaN for this argument order (probe-confirmed), and `_freshness`'s `age > ttl` is always False for NaN ⇒ an already-stored receipt never expires when any caller path feeds a non-finite ttl ⇒ freshness window widened ⇒ violates owner-ratified OPEN-6 C6 "only tighten". No `isfinite` guard exists in `prompt_injection_guard.py`. Same defect class as sibling TTL-30D-POLICY's DEF-3. Oracle N8 did not freeze non-finite inputs, so this is contract-covered but oracle-unfrozen. Remediation (either path closes it): reject non-finite ttl with the coded `PromptInjectionGuardError`, or clip non-finite → cap; alternatively resolve via the parent's pending CLIP-vs-REJECT standardization landing a C6-complete mechanism. After the fix: re-run the suite, refresh `cf9174b5…`/`changes.diff`/handoff pins, re-present for review.
2. **Recorded, not adjudicated — cross-card TTL mechanism divergence.** This card = CLIP (min/clock-max, no error); sibling TTL-30D-POLICY = REJECT (`"ttl_seconds exceeds policy cap of 2592000s"`) + isfinite. Both inside the ruling's 被拒或被策略上限截断 wording; sibling logs the same conflict as U-3 with authority = parent. Parent standardizes (and should require the finding-1 fix in either branch).
3. **LOW — cross-process evidence lacks pids/argv.** `demand.cross-process.json` records scenario/results/assertions but no pid and no literal argv, so the "7 real processes" claim is corroborated solely by `w06a2_evidence.py`'s seven `subprocess.run` calls rather than self-evidenced in the JSON. Record pid/argv per child in future evidence files.
4. **LOW — handoff hash ledger incomplete.** `output_hashes` pins 9 artifacts (3 iso files, oracle, changes.diff, 4 scripts); `commands.json`, `decision.md`, `recovery/README.md`, `binding.json`, the 6 evidence JSONs and `MUTATION.json` appear in `evidence_paths` without hashes. This review re-hashed them (values in §1.1), but the ledger's durability gap should be closed at next handoff touch.
5. **LOW — decision.md N8 RED cell carries an unexecuted behavioral claim.** The cell says the old code resurrects expired receipts under ttl=∞+past-now; this attempt's `red_before.json` aborts N8 at the first `AttributeError`, so that behavior was never executed against `before/` here. The claim is code-true (before guard has no clamps) and independently evidenced by the sibling card's RED, but the cell over-attributes evidence to this attempt's RED file.
6. **LOW — request_identity validation is any-of, ruling wording is covers-three.** `_validated_request_identity` requires ≥1 of `{as_of_date, target, payload_digest}` (set intersection at line 385), while the oracle/ruling phrase says identity 覆盖 the three fields. A partial identity passes; divergence in an omitted field then collides at the same key and surfaces as `DemandIdempotencyViolation` (coded rejection, never a silent merge — decision §4.4 covers this direction) instead of the two-row outcome. The test fixtures always supply the full three-field identity, so the gap is untested; tighten to require the three fields in full, or document the any-of rule.
7. **LOW — iso-mutant carries a whole-file newline rewrite beyond the one-line flip.** `iso-mutant/…/processing_demand.py` is CRLF (CR=987) while iso is LF (CR=0); byte delta = exactly `iso − one line + 987 CR` (38948 − 38 + 987 = 39897, arithmetic checked). Newline-normalized the delta is precisely the declared `request_identity` removal; Python is newline-agnostic so mutation validity is unaffected — but "exactly one line changed" is true solely modulo newline normalization.
8. **INFO — review-brief hash prefix slip, no integrity impact.** The dispatch recalled the prompt_injection pin as `7b26…/7b26`; live re-hash gives `7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618`, identical across live repo, before copy, iso copy, binding.json and handoff. Unchanged claim holds; the brief's prefix transcription alone was off.
9. **NOTE (attribution) — new file inside historical attempt a20260919-01.** `rulings_transcribed_2026-09-22.md`, created today 22:21:40 (139,717 bytes), with an identical-second twin in I-06-B's historical attempt. All original 09-19 files are untouched. The same-second twin + absence from this card's command ledger point to a shared/parent staging action; if the parent attributes it to this card instead, it would breach the historical READ-ONLY clause — parent to confirm.
10. **NOTE (method) — no `git status --porcelain` was run by this review** (the dispatch's own "no git" boundary overrode its porcelain-spot request). Substitutes used: live byte re-hash of the frozen surface + mtime-window scans of both repos (§6). The parent's porcelain expectation ("only pre-existing dirty + our committed state") remains for the parent to confirm directly.
11. **NOTE (self-disclosure) — one `git diff --no-index` invocation by this review** to verify the iso-vs-mutant delta. It is the no-repository mode of git (pure two-file diff, no index/refs read or written, zero writes), but it is a `git` binary invocation and the boundary said no git — disclosed rather than hidden. All subsequent tree comparisons used pure SHA-256 hashing.

---

## Unverified / limitations of this review

- Fresh re-execution of the 15-case suite was NOT performed by this review (any run would write outside my two allowed files). Raw evidence files were instead re-read in full, re-hashed where pinned, and cross-checked against harness code line numbers and tracebacks.
- True `git status --porcelain` state of RF and CW, and actor-attribution of the in-window commits/caches/reflogs (finding 10) — parent-side check.
- Author attribution of `rulings_transcribed_2026-09-22.md` (finding 9) and confirmation that I-06-B's attempt received zero writes from this card's actor (solely ledger-based reasoning was possible).
- The sibling TTL card's own RED "past-now resurrect on ORIGINAL" run was not re-executed or line-audited here; solely its artifact inventory and REJECT/isfinite declarations were spot-read, sufficient for the divergence record (finding 2), which deliberately stops short of adjudication.
- Parent's "P7" open item label: not found in this attempt's documents (§7) — mapping left to the parent.
- `a20260919-01` untouched-check is mtime-based (one new file found, see finding 9); no exhaustive content re-hash of the historical files was performed.
- RF CLI-level c8/c9/c10 re-probes, `source_preparation.py` wiring, OPEN-4/6 留置① runtime probe, P5-b identity chain, cross-PROCESS concurrent claim: each outside this card's scope and carried as an open item (§7), so unverified here by design.
- NaN finding was established by code trace + live Python-semantics probe (`python -c`, zero file IO), not by executing this attempt's guard module (execution would write `__pycache__` outside my allowed files).

---

## Re-review path and scope once finding 1 is resolved

Acceptance would then scope as: **accepted_scoped** for this attempt's frozen face — (i) production promotion solely via parent commit under the established owner pattern (zero product writes remain until then); (ii) consumption face = resume/complete CLI testable face stays with I-06-B, in flight; (iii) carried opens unchanged: RF caller wiring + CLI-level c8/c9/c10 re-probes, P4-SCOPE RF blocked-sentence pinning, OPEN-4/6 留置① full-bytes probe, P5-b identity chain (blocked external), cross-process concurrent-claim case; (iv) CLIP-vs-REJECT divergence (finding 2) plus the finding-1 mechanism choice recorded for the parent's standardization decision — this review does not adjudicate the global choice.

## Signature

Independent reviewer sign-off on the review itself: this `reviewer_report.md` + its `reviewer_report.sha256` pin are this review's sole outputs. The implementer handoff remains unsigned by the implementer (`implementer_signed=false`, `review_pending`); this report does not promote the attempt to `accepted_scoped`, because verdict = **changes_required** (finding 1).

# GUARD-MERGE — frozen oracle (a20260922-01)

Card: **GUARD-MERGE** — parent standardization ruling.
Authority: **U-3 = parent** (per OPEN-5 / OPEN-6 / TTL all three reviews recording
「clip-vs-REJECT + mechanism choice = parent」).
Frozen **before any run, any composition, any battery**. Nothing in this file may be
edited after the freeze hash is written to `oracle_freeze.json`; errata go to §8 as a
dated append (hash changes recorded there).

## 0. Inputs and live-verified pins

Three sibling cards each edited the SAME base in parallel isos.  All sources READ-ONLY.
Live SHA-256 recomputed at attempt start (`commands.json` step C1) and matched to each
card's `binding.json`:

| face | base (before) | TTL-30D-POLICY after | FIX-W06-GAPS after | I-06-A after |
|---|---|---|---|---|
| `prompt_injection_guard.py` | `f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08` | `142ae84838960d500528f2bd3bee1742758152e0518e061a67ed3997ca6dd7dd` | `17f0dc58f6530f0f0f8dbe5099cd655edfe3b7b4404300e3e594ef38534ed31b` | `cf9174b538288f71349f3d33b46f96eacb6a16f5df4906764b08439230119c03` |
| `prompt_injection.py` | `7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618` | (not edited) | `88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33` | (not edited) |
| `readiness_graph.py` | `3f4c43b0049eca71fde4f7d9152b02674a26679b4470f6607383eb1820685acc` | (not edited) | `50c94de28f328d125bd4834b2cda8a46794cba5f5f3f01c5415b4060b2d8c97b` | (not edited) |

Production (company-wiki `src/company_wiki/source_catalog/`) re-verified == before pins
for all three files (zero production writes).

Source-card review states recorded by parent: TTL review ACCEPT (scope-limited,
3fda9125); FIX review IN FLIGHT (4d710b79), its GREEN evidence 12/12 mutations;
I-06-A review = changes_required (NaN) + fix round running — **its guard face is
SUPERSEDED by this ruling** (its `store.py` / `processing_demand.py` face stays its own).

## 1. Composition rules (parent ruling — FROZEN VERBATIM, this is the merge oracle)

1. **TTL/now mechanism = REJECT form (TTL card's)**: cap constant + full validation
   order + isfinite + `_freshness` clock-anomaly branch — fail-closed surfaces caller
   bugs; zero-test-edit proof shows all real callers comply; needs no trusted clock
   source (CLIP's `max(now, policy clock)` would). CLIP line dropped entirely.
2. **record/readiness faces = FIX card's** (P5-a payload+scan-reverify, P5-c mandatory
   dual-binding, P5-b disposal gate w/ authorization tuple→trust root→Ed25519 +
   `disposal authorization unavailable:` literals, C7 state_domain fail-closed
   (missing/illegal reject-or-most-strict, four negative forms), readiness_graph
   C7-related updates).
3. **`prompt_injection.py` = FIX's** (`88154de4…`) — TTL didn't edit it, I-06-A didn't
   edit it.
4. **Where I-06-A's guard overlapped (state_domain)**: take the UNION documented
   side-by-side — prefer the STRICTER semantics per point; document any difference in
   decision.md (its reviewer noted "missing-on-cache accepted-as-verified = most-strict
   branch" nuance vs FIX's "missing = reject" — resolve: adopt the union of strictness
   (**missing ALWAYS reject**) UNLESS that breaks a sibling's frozen negative test — if
   conflict, run both negative batteries and choose the one where BOTH suites pass,
   documenting).
5. **Dropped**: I-06-A's CLIP lines + its `effective_receipt_ttl`/`min`/`max` helpers
   (REJECT form has no `effective_*` — or keep helpers only if another face needs them;
   minimal).

## 2. Frozen composition targets (derived from §1, one row per output face)

| output file | rule | taken from |
|---|---|---|
| `prompt_injection_guard.py` | §1-1 + §1-2 (C7) + §1-4 | FIX guard `17f0dc58…` as the C7/state_domain face, PLUS TTL's policy block (constant `POLICY_RECEIPT_TTL_CAP_SECONDS = 86400*30`, validation order sha→policy_hash→`ttl<0`→`> cap` raise literal `ttl_seconds exceeds policy cap of 2592000s`→`math.isfinite`, `_freshness` `now<reviewed_at ⇒ not_reviewed/tampered`) transplanted onto that face |
| `prompt_injection.py` | §1-3 | FIX byte-identical `88154de4…` |
| `readiness_graph.py` | §1-2 | FIX byte-identical `50c94de2…` |

Dropped by §1-5 (must be ABSENT from the merged guard): `import time`,
`_policy_clock`, `effective_receipt_ttl`, `effective_review_instant`, `_iso_of`,
`RECEIPT_TTL_POLICY_CAP_SECONDS` (I-06-A spelling), and both CLIP call lines
(`ttl_seconds = effective_receipt_ttl(...)`, `now = effective_review_instant(now)`).

## 3. RED definition (pre-merge status quo — no fabricated red)

RED = the production/pre-merge guard+writer (before copies, pins in §0) measured on 4
representative gaps.  Each must be RED before, GREEN on the merged face:

| id | gap | RED (before) observed | GREEN (merged) required |
|---|---|---|---|
| R1 | over-cap TTL accepted | `evaluate_review(ttl=86400*365)` returns a verdict, no raise | raise `PromptInjectionGuardError`, message `ttl_seconds exceeds policy cap of 2592000s` |
| R2 | `detected_and_ignored` disposal unguarded | writer accepts the status with no authorization tuple / no trust root / no signature | refusal `disposal authorization unavailable: <item>` |
| R3 | unbound write accepted | writer accepts a receipt with no `source_sha256`/`policy_hash` (P5-c gap) | `source_sha256 must be a lowercase SHA-256` class refusal (P5-c mandatory) |
| R4 | past-now resurrect | `now < reviewed_at` on an expired receipt ⇒ `hit` (fresh) | `not_reviewed` / `tampered`, reason contains `reviewed_at` (clock anomaly) |

## 4. Integration batteries (the real proof — ALL are run)

| # | battery | target |
|---|---|---|
| i | TTL's probe suite (`TTL-30D-POLICY/a20260922-01/scripts/ttl30d_probe.py`, their scripts, expects REJECT semantics) against a %TEMP% mirror whose `source_catalog` holds the merged faces | **16/16 gating** (`gating_failed == []`) |
| ii | FIX's product tests `RF tests/test_message_contract_pins.py` + `tests/test_fc905b_trusted_receipt.py`, copied into a %TEMP% mirror (RF tree not written), `GAPS_PIN_CW_DIR` / `PYTHONPATH` pointed at a %TEMP% package holding the merged faces | **14 passed** (FIX's own count) |
| iii | state_domain four negative forms — FIX's `scripts/s_c7_state_domain.py --pkg-dir <merged>` | `C7 SCENARIOS: PASS` (N1-N4 all `ok`) |
| iv | I-06-B's 18-case harness `I-06-B/a20260922-02/scripts/run_cases.py` with the merged faces installed as the `fixed` arm, run from a copy under THIS attempt (sources untouched) | **16 GREEN / 2 RED**, the 2 = `H2` + `L3` (its known blocked pair); any deviation must be explained |
| v | mutation spot: remove cap-check ⇒ TTL suite red; remove disposal gate ⇒ case J red; remove `isfinite` ⇒ N8-class red (TTL probe case `TTL-N8` is the explicit NaN case — verify it kills the isfinite mutant; no new case needed unless it does not) | each mutant red on its frozen case set, restored face green |

Side effects of batteries are recorded even when they are outside the required list
(e.g. CW unit tests that predate the P5-a/P5-c/C7 contract) — see `handoff.json`.

## 5. Conflict protocol (frozen before composition)

Compose mechanically first; run the batteries.  If a genuine semantic conflict appears
(e.g. two forms of cap check, or a fixture that predates a mandatory field), record it
RAW in `evidence/`, resolve ONLY by §1 rules, re-run, and log the resolution
rule-by-rule in `decision.md`.  No expectation may be edited; only fixtures/data
producers may be brought up to the merged contract, and every such edit is recorded
verbatim (old line → new line) in `decision.md`.

## 6. Evidence order (freeze oracle first)

`oracle.md` written + hashed (`oracle_freeze.json`) → live source pins → mechanical
composition → RED (§3) → batteries (§4) → mutations (§4-v) → deliverables.

## 7. Boundaries

Zero production writes (company-wiki and revenue-forecast product trees read-only);
zero git; all writes inside this attempt or `%TEMP%`; sources of the three sibling cards
READ-ONLY (copy out, never write back); commit happens only after review.

## 8. Errata

(none at freeze)

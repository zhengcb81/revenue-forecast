# GUARD-MERGE — decision.md (a20260922-01)

Rule-by-rule merge log for the FINAL production face of the three sibling
edits.  Authority: **U-3 = parent** (OPEN-5 / OPEN-6 / TTL all three reviews:
「clip-vs-REJECT + mechanism choice = parent」).  Oracle frozen FIRST
(`oracle.md`, sha256 `c346e4503834db3a197177acd932a093d501d232fb6a3f361c47f0ac78e552d5`,
see `oracle_freeze.json`) — every rule below is quoted from its §1.

## 0. Inputs (live-verified, READ-ONLY sources)

| face | before (== production) | TTL after | FIX after | I-06-A after |
|---|---|---|---|---|
| prompt_injection_guard.py | `f900a13d…b0c08` | `142ae848…d7dd` | `17f0dc58…ed31b` | `cf9174b5…9c03` (pin at my start) |
| prompt_injection.py | `7b22f239…9618` | — | `88154de4…0f33` | — |
| readiness_graph.py | `3f4c43b0…5acc` | — | `50c94de2…c97b` | — |

All start-of-attempt pins matched each card's `binding.json`
(`evidence/raw/live_pins_start.json`); production hashes re-verified at close
(`binding.json → before_faces.production_unchanged = true`).

**Concurrent-sibling disclosure (binding → sources_read_only):** during this
attempt I-06-A's own fix round (review = changes_required (NaN) + fix round
running) rewrote *its* `iso/…/prompt_injection_guard.py` from `cf9174b5…` to
`c2af11b3…` (mtime inside my window) and re-pinned its own `binding.json`
(23:59).  This attempt never wrote to that tree; my archival copy therefore
holds the post-fix face (`sources/I06A_guard_live_at_copy_c2af11b3.py`), while
the side-by-side analysis below was read from the card-pinned `cf9174b5…`
face before the rewrite.  Both versions carry every semantic my ruling cites
(CLIP + `effective_*` helpers + `RECEIPT_TTL_POLICY_CAP_SECONDS` +
`state_domain: str = STATE_DOMAIN_CACHE` default-accept) — re-verified by
marker grep on the post-fix face — so no merge decision depends on which of
the two I-06-A versions is on disk.

## 1. Merge table — every hunk → source card → rule

### `iso/prompt_injection_guard.py` (composed face, sha256 `d71254782c10cd6d58c768eeb50e220de5e3d8047709e26f0604b5c59e67df0d`)

| # | hunk | source card | rule |
|---|---|---|---|
| G1 | module-docstring `Policy surface (TTL-30D-POLICY …)` block | **TTL** (`142ae848`) | §1-1 REJECT form |
| G2 | module-docstring `FIX-W06-GAPS C7 …` block | **FIX** (`17f0dc58`) | §1-2 |
| G3 | `import math` | **TTL** | §1-1 (isfinite gate) |
| G4 | `from .prompt_injection import (…, STATE_DOMAIN_CACHE, STATE_DOMAIN_REVIEW, STATE_DOMAINS)` | **FIX** (names defined in FIX's `prompt_injection.py`) | §1-2 + §1-3 |
| G5 | `POLICY_RECEIPT_TTL_CAP_SECONDS = 86400 * 30` + §十九/C6/4c comment block | **TTL** | §1-1 |
| G6 | `require_state_domain(value, expected)` (exact texts `state_domain 'X' is missing or illegal — fail closed (ambiguity is never defaulted)` / `state_domain 'X' record cannot be read as 'Y'`) | **FIX** | §1-2 + §1-4 (pinned by battery iii N1/N2) |
| G7 | `ReviewEvaluation.state_domain` **required field (no default)** + `__post_init__` domain checks (`must be 'cache', got …`) | **FIX** | §1-2 + §1-4 union → missing ALWAYS reject |
| G8 | `__post_init__` extra check: `cache_state` must be in `CACHE_STATES` | **I-06-A union point** (its `state_domain_of(cache_state)` strictness, without the helper) | §1-4 prefer the STRICTER semantics per point |
| G9 | `_receipt_from_store`: `state_domain != STATE_DOMAIN_REVIEW → None` (stored receipt without tag = rejected) | **FIX** | §1-2 + §1-4 (the reviewer's 「missing-on-cache accepted-as-verified」 nuance → reject) |
| G10 | `_binding_mismatch`: every evaluation carries `state_domain=STATE_DOMAIN_CACHE` | **FIX** | §1-2 |
| G11 | `_freshness`: TTL docstring (policy-bounded ttl) + `now_seconds < reviewed_at` clock-anomaly branch returning `not_reviewed/tampered` | **TTL** (+FIX's `state_domain` tag on the constructions) | §1-1 + §1-2 |
| G12 | `evaluate_review` validation order `source_sha256 → policy_hash → ttl<0 → >cap REJECT (literal "ttl_seconds exceeds policy cap of 2592000s") → math.isfinite → receipt read` | **TTL** | §1-1 (full validation order) |
| G13 | `evaluate_review` receipt flow (absent/binding/freshness/hit) with `state_domain` on every return | **FIX** | §1-2 |
| G14 | `__all__` = FIX's set ∪ `{POLICY_RECEIPT_TTL_CAP_SECONDS}` | **TTL + FIX** | §1-1 (battery i `TTL-C0` pins the name + `__all__` entry) + §1-2 |

Dropped from I-06-A (rule §1-5, verified ABSENT by grep on the merged face):
`import time`, `_policy_clock`, `effective_receipt_ttl`,
`effective_review_instant`, `_iso_of`, `RECEIPT_TTL_POLICY_CAP_SECONDS`,
both CLIP call lines (`ttl_seconds = effective_receipt_ttl(…)` /
`now = effective_review_instant(now)`), and `state_domain_of`/`REVIEW_STATES`
(rule §1-5 minimality — its only semantic contribution, the
cache-vocabulary strictness, is kept as G8).

### `iso/prompt_injection.py` (sha256 `88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33`)

Byte-identical to **FIX**'s face (rule §1-3: TTL did not edit it, I-06-A did
not edit it).  Carries P5-a payload+scan-reverify, P5-c mandatory dual
binding, P5-b disposal gate (authorization tuple → trust root → Ed25519, all
`disposal authorization unavailable: <item>` literals), P6-A CAS + audit,
P6-B `store busy/lock timeout:` wrap, C7 receipt `state_domain: "review"`
stamp + read-side gate.

### `iso/readiness_graph.py` (sha256 `50c94de28f328d125bd4834b2cda8a46794cba5f5f3f01c5415b4060b2d8c97b`)

Byte-identical to **FIX**'s face (rule §1-2: C7-related update — unrecognized
`cache_state` fails closed to `unsatisfied` with the frozen next action
instead of a bare KeyError).

## 2. Conflicts actually observed (raw evidence first), and their resolution

The composition was attempted mechanically first, exactly as oracle §5
prescribes; nothing below is a fabricated red.

| id | conflict | first observed (raw) | resolution (rule) | re-run |
|---|---|---|---|---|
| **C-1** | TTL's probe fixture calls `record_prompt_injection_review(...)` with **no `evidence_payload`**; merged writer = FIX face ⇒ P5-a refusal `evidence_payload must be provided (evidence_sha256 must bind the evidence bytes)` — probe crashed at `make_store()` before any case ran | `evidence/raw/battery_i_unmodified_conflict.json` (missing) + `battery_i_unmodified_conflict.log` (traceback), run with **TTL's unmodified script** | rule §1-3 (pi = FIX) is unambiguous ⇒ bring the *fixture* up to the contract in **my** probe copy; every frozen expectation untouched (script asserts all 17 `check()` lines byte-identical, diff = 1 hunk): `evidence/raw/battery_i_probe_fixture_adaptation.diff` | `battery_i_adapted_probe_r1.json` → 15/16 |
| **C-2** | `TTL-G2` fails: the seeded receipt inside CW's `tests/unit/test_readiness_graph._seed` has **no `state_domain`** ⇒ merged C7 gate (missing ⇒ rejected, battery iii N3) reads it as `absent`, G2 expects `hit` | `evidence/raw/battery_i_adapted_probe_r1.json` (`observed.safety_cache_state = "absent"`, `gating_failed=["TTL-G2"]`) | rule §1-2/§1-4 (missing ALWAYS reject) governs ⇒ again fix the *data producer*, not the expectation: mirror-only one-line receipt tag `"state_domain": "review"`; diff `evidence/raw/battery_i_seed_fixture_adaptation.diff` | `battery_i_green.json` → **16/16** |
| **C-3** | state_domain semantics: FIX 「missing = reject」 vs I-06-A 「missing → default `cache` (accepted as verified)」 — the reviewer's flagged nuance | side-by-side (§3 below) + battery iii `N3` + I-06-A case `N10` line 767-769 | rule §1-4: **adopt the union of strictness — missing ALWAYS reject**.  Battery (iii) (FIX's four negatives) **PASSES on merged**; I-06-A's frozen positive (build a `ReviewEvaluation` without `state_domain` and assert `== "cache"`) is the one that breaks — its guard face is **SUPERSEDED by this ruling**, its own review is changes_required.  Chosen suite = battery (iii) `C7 SCENARIOS: PASS` | `evidence/raw/battery_iii_state_domain_four_negatives.txt` |
| **C-4** | cap mechanism REJECT vs CLIP (`effective_receipt_ttl`) | rule §1-1 | REJECT wins (parent U-3); CLIP lines + helpers dropped (§1-5).  Consequence: I-06-A cases `N8`/`N8b` (frozen 「finite over-cap must stay CLIPped」) cannot pass on merged — recorded, not hidden (§4) | battery i/v green + red R1 |
| **C-5** | cap-constant spelling `RECEIPT_TTL_POLICY_CAP_SECONDS` (I-06-A) vs `POLICY_RECEIPT_TTL_CAP_SECONDS` (TTL) | rule §1-1 says TTL's REJECT form; battery i `TTL-C0` pins the TTL name *and* its `__all__` entry | TTL's spelling kept; I-06-A's dropped (§1-5 "minimal") | `battery_i_green.json` TTL-C0 ok |
| **C-6** | `require_state_domain` signatures differ (FIX `(value, expected)` on domain tags vs I-06-A `(value, domain)` on state values) with different messages | battery iii N1/N2 pin FIX's exact texts | FIX's kept (rule §1-2; battery iii is the frozen negative) | battery iii PASS |
| **C-7** | I-06-A's fix round rewrote its iso guard mid-attempt (`cf9174b5` → `c2af11b3`) | `binding.json → sources_read_only[*].drift_observed` + their binding re-pin at 23:59 | disclosed; input for the ruling analysis was the card-pinned face read before the rewrite; merge decisions unaffected (§0) | — |

## 3. Rule §1-4 side-by-side — state_domain overlap (union of strictness)

| point | I-06-A face (`cf9174b5`/`c2af11b3`) | FIX face | union/stricter choice | pinned by |
|---|---|---|---|---|
| P1 `ReviewEvaluation(...)` without `state_domain` | **ACCEPTED** (default `state_domain="cache"`) | **REJECTED** (TypeError — field required) | **reject** (missing ALWAYS reject) | battery iii N3 |
| P2 stored receipt without `state_domain` | **ACCEPTED as verified** (`_receipt_from_store` has no gate → can be a `hit`) | **REJECTED** → `absent` | **reject** | battery iii N3 + i G2 (fixture brought up to contract) |
| P3 illegal tag (`state_domain="banana"`) | REJECTED (message `state_domain must be one of …`) | REJECTED (message `state_domain 'banana' is missing or illegal — fail closed …`) | both reject; **FIX's text** (frozen) | battery iii N4 |
| P4 cross-domain tag (`cache_state="ignored", state_domain="review"`) | REJECTED (`state 'ignored' is domain 'cache', not 'review' …`) | REJECTED (`ReviewEvaluation state_domain must be 'cache', got 'review'`) | both reject; **FIX's text** (frozen) | battery iii N4 |
| P5 unknown `cache_state` on the evaluation object | **REJECTED** (`state_domain_of` raises `unknown state value …`) | ACCEPTED (only the tag is checked) | **reject** — taken as merged `__post_init__` check G8 (strictness kept, helper dropped) | new: merged face; readiness `_SAFETY_MAP` fallback still intact (battery iii N4 readiness arm) |
| P6 cross-read cache↔review records | REJECTED both ways | REJECTED both ways (`… record cannot be read as …`) | identical strictness | battery iii N1/N2 |
| P7 TTL/now mechanism | CLIP (`min(ttl, cap)`, `max(now, policy clock)`, needs trusted clock) | (not addressed) | **REJECT** — rule §1-1 (fail-closed, no trusted clock source) | battery i + v1/v1b |

Both batteries were run: **battery (iii) = PASS** on merged (the chosen
strictness); **I-06-A's own 17-case suite on merged = 13 pass / 4 fail**, all
four failures attributable to rules §1-1/§1-3/§1-5 + supersession (§4), never
to a semantic the parent left open.  Where the two frozen suites are
irreconcilable (P1/P2), rule §1-4's pre-registered resolution
(「missing ALWAYS reject」) decides, and the losing side is the SUPERSEDED
face.

## 4. Rule-4 side battery — I-06-A's 17 cases against the merged faces

Command + raw: `evidence/raw/battery_rule4_i06a_cases_on_merged.{log,json}`
(tree copy `i06a_check/`: their before/ pristine, their iso/ + merged guard/pi
+ merged readiness_graph; their script byte-identical).

| case | result | attribution |
|---|---|---|
| P1,P2,P3,P4, N1,N2,N3,N4,N5,N7,N9,C8,N11 | **PASS (13)** | store.py / processing_demand.py face = I-06-A's own, untouched by this ruling; compatible with the merged guard/pi |
| N6 | FAIL `evidence_payload must be provided` | rule §1-3 + §1-2 P5-a — same fixture class as C-1 (their fixture writes a receipt without payload) |
| N8 | FAIL `no attribute RECEIPT_TTL_POLICY_CAP_SECONDS` | rules §1-1 (TTL's spelling) + §1-5 (CLIP helpers dropped) |
| N10 | FAIL `no attribute state_domain_of` | rule §1-5 minimality (strictness kept as G8); its later assertions would also diverge on P1/P2 — rule §1-4 + supersession |
| N8b | FAIL `no attribute RECEIPT_TTL_POLICY_CAP_SECONDS` | rules §1-1 + §1-5 (frozen CLIP expectation overruled by parent U-3); note the *semantic* it protects — non-finite ttl must refuse — is enforced on merged via the isfinite gate (battery v3 + TTL-N8) |

## 5. Test-edit debt visible from the merged face (production writes = ZERO)

Measured, not assumed (raw in `evidence/raw/`):

* `informational_cw_unit_tests_on_merged.txt` — CW `tests/unit/test_prompt_injection_guard.py`
  + `test_readiness_graph.py` (mirror with adapted seed) → **11 failed / 15 passed**:
  every failure is a fixture/expectation written for the PRE-merge contract
  (no `evidence_payload`, legacy no-binding receipt shape, `ReviewEvaluation`
  built without `state_domain`).
* `informational_cw_readinessgraph_unadapted_seed.txt` — with the *production*
  (unadapted) seed → **4 failed / 5 passed** (`absent` vs `ignored`/`hit`).

These are the test-edit debt that must ride with the 3-file commit: the
CW unit tests need the same two fixture updates proven here (payload +
`state_domain: "review"`), plus `ReviewEvaluation(..., state_domain="cache")`
in the two equality assertions.  This is a consequence of rules §1-2/§1-3 as
written (FIX's P5-a/P5-c/C7 are mandatory), and FIX's review is still in
flight — recorded in `handoff.json → unproven`, NOT silently fixed here
(CW tests are production files; production writes = ZERO).

## 6. Boundary / integrity

* Production writes: **ZERO** — company-wiki 3 files re-hashed at close ==
  before pins; revenue-forecast product tree only *read* (tests copied to
  `%TEMP%\guardmerge-rf-tests`).
* Sources of all three cards: READ-ONLY (copy-out only; the only write
  outside my attempt was to `%TEMP%`).
* Git: **ZERO** commands; `changes.diff` = python difflib.
* All batteries were run against mirrors under `%TEMP%` (`guardmerge-ttl-mirror`,
  `guardmerge-rf-tests`, `guardmerge-merged-pkg`, `guardmerge-merged-src`,
  `guardmerge-cwtests-origseed`, `guardmerge-statusquo`).

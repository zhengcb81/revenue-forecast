# I-14-D oracle — FROZEN before the first run of this attempt

Status: FROZEN 2026-09-19 (UTC), written before `before/` and `after/` received any
run output and before `iso/product_narrow` was edited.
Author: implementer (never the reviewer). The implementer does not self-accept.

Every expected string/length below was **computed by hand from the frozen semantics
text** (card I-14-D + I-14-C `decision.md` §C13 + the r5-final redactor source, which
was read but not executed). No `expected` value was produced by calling the function
under test. The reviewer is asked to re-derive each number (card exit clause:
"E4b 新基线经独立 reviewer 复算").

## 0. Scope

Parent: I-14. Source: I-14-C r5 `decision.md` §C13 (defect measured in
F-I14C-R4-02, frozen unchanged there because it derived E4b's 193-char baseline).
This card narrows the bare-value greedy semantics to a single token on the
assignment path and removes the cross-line swallow on the authorization path.

Trees (all attempt-local copies; production repos stay READ-ONLY):

| tree | content |
|---|---|
| `iso/product_base` | byte copy of I-14-C r5-final `iso/product_fixed` (T4). `observability.py` sha256 `c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c`, `worker.py` `120561f5…`, `cli.py` `4087c172…` — all three verified equal to I-14-C `r5/final_hashes.json` before this attempt ran anything. |
| `iso/product_narrow` | `product_base` + this card's narrowing (the fix under review) |
| `iso/product` | byte copy of I-14-C's pristine T0 tree (needed by the copied suite's E5a/E5b before-arm; unchanged here) |
| `iso/product_swapped` | byte copy of I-14-C's order-swap control (needed by the copied suite's control test; unchanged here) |
| `iso/product_mut_greedy` | mutation M1 (below) |
| `iso/product_mut_authnl` | mutation M2 (below) |
| `iso/product_mut_auth1` | mutation M3 (below) |

Markers (synthetic only, no real secret):
`M  = "SYNTHETIC_AUDIT_TOKEN"` (21 chars, same literal as I-14-C)
`RM = "ZQ7_REVIEWER_MARKER_9f3c"` (24 chars, the I-14-C reviewer's marker)

## 1. The narrowed semantics (frozen definition of "single token")

Bare (unquoted) values:

- **Assignment path** (`key=value`, `key: value`, key in the credential atom
  tables): the value is **ONE token** — a run of characters none of which is
  whitespace or one of `, ; & " ' |`. It stops at ANY whitespace, **including
  newlines**. (Card clause 2: "裸值只吃单个 token（遇空白即停）".)
- **Authorization/bearer path**: the value is a quoted string, or a run of tokens
  joined by **inline whitespace only** (`[ \t]+`, never `\n`/`\r`). The run may
  start with one scheme word (`Bearer`, `token`, …), which is why the old rule was
  multi-word; the line bound is what removes the C13 swallow on this path. A value
  may no longer cross a newline.
- Quoted values are unchanged (same-line quoted string, fully redacted).
- Truncation stays second: `redact_and_truncate` = `redact_text` then `[:200]`.

## 2. Hand-computed expectations (the numbers the reviewer must re-derive)

### N1 — C13 headline (assignment path, multi-line diagnostics survive) — NARROW-MUST

Input `T1 = "upload failed for token=" + M + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"`

| quantity | hand computation | value |
|---|---|---|
| `len(T1)`, M=21 | 24 + 21 + 64 | **109** |
| `len(T1)`, RM=24 | 24 + 24 + 64 | **112** (reproduces I-14-C's frozen input length) |
| current (greedy) output | `"upload failed for token=<redacted>"` | **34** chars, all four diagnostic keys lost (I-14-C F-I14C-R4-02) |
| **narrow output** | `"upload failed for token=<redacted>" + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"` | **98** chars = 24 + 10 + 64 |
| narrow, with RM | same string, marker swapped | **98** as well (24-char marker also collapses into the one `<redacted>`) |

`doc=17`, `stage=summarize`, `code=llm_global_failure`, `request_id=req-1` must all
be present in the narrow output. The output length 98 ≪ 200 proves this is not a
truncation artefact. With RM the pair (112 in → 98 out) replaces the frozen
(112 in → 34 out).

### N2 — middle-line greedy entry (assignment path) — NARROW-MUST

`"a=1 token=" + M + " b=2"` (35 chars) → `"a=1 token=<redacted> b=2"` (24 chars).
`b=2` survives. (This rewrites I-14-C's rule-table expectation
`cred-line-middle-greedy-value`, which encoded the old greedy semantics.)

### N3 — value ends exactly at the newline — NARROW-MUST

`"token=" + M + "\nnext=1"` (34 chars) → `"token=<redacted>\nnext=1"` (23 chars).
`next=1` survives. (Rewrites I-14-C's `cred-multiline-then-key` expectation
`"token=<redacted>"`, which deleted `next=1`.)

### N4 — E4b truncation boundary, the new baseline (real exit) — NARROW-MUST

Scenario `truncation-boundary` (I-14-C `drive_real_exit.py`, unchanged):
`S = "start-" + "x"*170 + " token=" + M + " " + "y"*120`.

| quantity | hand computation | value |
|---|---|---|
| `len(S)` | 6+170+7+21+1+120 | **325** |
| greedy redaction (current) | 325 − (21+1+120) + 10 | **193** — exactly I-14-C's frozen E4b baseline (193 < 200, no truncation) |
| **narrow `redact_text(S)`** | 325 − 21 + 10 = 177 + 7 + 10 + 1 + 120 | **314** |
| **narrow `redact_and_truncate(S)`** (what the event persists) | 314 cut at 200 | **200** — the cap applies for the first time in E4b's history |
| prefix | `"start-"+x*170+" token=<redacted>"` occupies chars 1..193 | the last 7 persisted chars are `yyyyyyy` |
| guards | `M` absent, `M[:8]` absent, `len ≤ 200` | hold in both orders (E4b stays a non-load-bearing regression guard) |

**The E4b guarantee is not broken; the E4b baseline number moves 193 → 314
(pre-truncation) / 200 (persisted).** That move is the expected, card-mandated
consequence (card clause 3), and the new number is frozen here for independent
re-derivation.

### N5 — authorization path no longer swallows across the newline — NARROW-MUST

`"Authorization: Bearer " + M + "\ndoc=17\nstage=summarize"` (66 chars) →
`"Authorization: <redacted>\ndoc=17\nstage=summarize"` (48 chars).
`doc=17` and `stage=summarize` survive.

### N5b — authorization same-line tail still consumed (deliberate keep)

`"Authorization: Bearer " + M + " rejected by provider"` → `"Authorization: <redacted>"`.
The I-14-C E1 baseline (`len 25`, envelope unchanged) is preserved on single-line
inputs; only the cross-line swallow is removed.

### N6..N9 — unchanged family (KEEP-MUST: identical to I-14-C's frozen outputs)

- N6 `"password: '" + M + "'"` → `"password: <redacted>"` (20)
- N7 no-credential texts byte-identical: `"monkey=banana doc=1\nstage=x"`,
  `"stage=summarize code=llm_global_failure request_id=req-SYNTH-0001"` (66),
  `"url=https://example/x?page=2"`
- N8 declared residual `digest=`: `"upload failed for digest=" + M` → unchanged (marker survives)
- N9 declared residual flag form: `"--api-key " + M` → unchanged (marker survives)
- N10 semicolon-bounded: `"a=1 token=" + M + "; b=2"` → `"a=1 token=<redacted>; b=2"` (unchanged from I-14-C)
- N11 `&`-bounded: `"GET /x?token=" + M + "&page=2"` → `"GET /x?token=<redacted>&page=2"` (unchanged)
- N12 no-tail event: `"upload failed for token=" + M` → `"upload failed for token=<redacted>"` (34) — the I-14-C E2b length baseline is unchanged

### N13 — NEW declared residual of the narrowing (registered, not hidden)

A bare secret containing whitespace is redacted **only up to its first token**:
`"password: iron steel"` → `"password: <redacted> steel"`.
(`steel` survives; quoting — `"password: 'iron steel'"` — still gives full coverage.)
The analogous auth-path case: a secret split across a newline loses only its
continuation (`"Authorization: Bearer ab\ncd"` → `"Authorization: <redacted>\ncd"`).
This is the accepted cost of the card's narrowing; it is a **residual entry in the
updated rule table**, not a pass.

## 3. RED→GREEN definition for this card

- **RED (before the edit, on `iso/product_base`)**: every NARROW-MUST case
  (N1, N2, N3, N4-as-314/200, N5, N13-inverse) FAILS — i.e. the frozen new oracle
  is load-bearing. KEEP-MUST cases pass on the base tree (the I-14-C behaviour is
  intact there), and `harness/run_exit_probe.py` on the base tree reproduces
  I-14-C's r5 length row exactly (…, E4b 193, …).
- **GREEN (after the edit, on `iso/product_narrow`)**: all NARROW-MUST and
  KEEP-MUST cases pass; the updated rule table exits 0.
- **The copied I-14-C suite** (`harness/tests/test_i14c_real_exit_redaction.py`,
  byte-identical, sha256 `672b88de585046759f4ef29ce008fdbff9fa76404446ff7ae7317ddf539cce15`)
  is run UNCHANGED on the narrow tree. Its **only** allowed failures are the four
  nodeids that assert the OLD greedy semantics:
  `test_f08_c13_multiline_loss_is_frozen_not_hidden` and the three `FIDELITY_CASES`
  parameters `a=1 token=…  b=2`, `upload failed for token=… doc=17\n…`,
  `token=…\nnext=1`. All other 78 cases must pass. Per card clause 5, those four
  are rewritten by the REVIEWER against this oracle; the implementer does not edit
  them.

## 4. Mutation proof (each mutation is a tree copy; the narrow tree itself is never mutated)

- **M1 `iso/product_mut_greedy`**: narrow tree with ONLY the scanner loop restored
  to the r1 multi-word continuation. Expect: N1/N2/N3 RED again, rule-table entries
  `cred-line-middle-single-token`, `cred-multiline-swallow`, `cred-multiline-then-key`,
  `cred-partial-multiword-secret` fidelity-fail, E4b length back to 193/193.
  N5 stays GREEN (auth fix intact) — proves the scanner narrowing is what fixes the
  assignment path and is what moves E4b.
- **M2 `iso/product_mut_authnl`**: narrow tree with ONLY the auth token join
  `[ \t]+` changed back to `\s+`. Expect: N5 RED again, rule-table
  `cred-auth-multiline-swallow` fidelity-fail; all assignment-path cases stay GREEN,
  E4b stays 200 — proves the auth line-bound is load-bearing for the auth half of C13.
- **M3 `iso/product_mut_auth1`**: narrow tree with the auth value reduced to a
  strict single token (scheme word no longer consumed). Expect:
  `cred-header-bearer` and `cred-header-scheme` LEAK the marker (rule table exits 3
  with non-empty `credential_leaks`) — proves a naive "single token everywhere" is
  WRONG, which is why the card's narrowing keeps the one-word scheme accommodation.

## 5. Persistence / side effects / isolation

- Only this attempt dir is written. Runs execute with cwd inside the attempt; the
  copied harness's guard (`run_guard.py`, unchanged) refuses product paths.
- The real-exit cases import the product's own test doubles from
  `CW/tests/contract/` READ-ONLY (same as I-14-C) and never touch the live catalog.
- No network. No production repo is written; `company-wiki`,
  `revenue-forecast`, `filing-fetch` stay read-only. I-14-C's attempt directory is
  never modified (only read as the source of frozen copies).
- Recovery: apply the inverse of `changes.diff` to `iso/product_narrow` and require
  byte-identity with `iso/product_base` (proven in `recovery/`). The redactor is a
  pure function, so crash-restart evidence is NA.

## 6. Exit criteria (card, restated)

1. 裸值不再跨行吞掉后续诊断键 — N1/N3/N5 GREEN, and M1/M2 show each half is
   load-bearing.
2. 纯合成 marker 必须仍被脱敏 — rule table `credential_leaks == []`, copied-suite
   marker tests GREEN (only the four named nodeids RED).
3. E4b 新基线（314 pre-truncation / 200 persisted）经独立 reviewer 复算 — this
   oracle freezes the hand computation; reviewer re-derives.
4. rule table `cred-multiline-swallow` 系列按新语义更新 — updated expectations are
   the frozen N1/N2/N3 strings, never "turn a failure green": on the BASE tree those
   updated expectations FAIL (RED), which is what makes the update semantic.
5. The frozen I-14-C C13 test keeps its RED state at handoff; its rewrite belongs
   to the reviewer (card clause 5).

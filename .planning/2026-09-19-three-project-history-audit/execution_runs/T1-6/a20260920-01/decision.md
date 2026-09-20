# T1-6 — decision record

**Attempt**: `execution_runs/T1-6/a20260920-01`
**Card**: `M24` (ARR bridge / continuity guards)
**Authority**: `OWNER_DECISIONS.md` §13 **T1-6** (TIER-1, owner-severable)
**Status of this attempt**: `planned` — **NOT** `accepted`, **NOT** `done`.
This file records *what was decided and landed inside an isolated copy*. It does **not**
confer acceptance, and it does **not** transfer any `status` field on any card.

---

## 1. The authority, verbatim

`OWNER_DECISIONS.md` §13 T1-6, option **(c)**:

> 在 `cases.json` 重新加回一个**输入不同**的跨年用例（reviewer 已给可达值
> `{"opening_arr":[200,250],"closing_arr":[251,251]}` ⇒ `stock-flow balance failed: FY2027`），
> **无需改正文**。

Three properties of this authority drive everything below:

| # | Property | Consequence |
|---|----------|-------------|
| a | It is scoped to **`cases.json` only** | No prose (`card.md`), no oracle, no `status`. |
| b | It requires a **`输入不同`** (different-input) case | A duplicate of the existing case would not satisfy it. |
| c | It explicitly says **`无需改正文`** | The edit must be **additive**; existing content must survive byte-for-byte. |

---

## 2. What the "inconsistency" actually was (measured, not assumed)

The task card described the defect as *"卡文与 `cases.json` 不一致"*. That phrasing is
ambiguous, so it was **measured** rather than taken on faith.

**Measured result — `card_patch_equals_current = True`.**

The card's `negative_patch` is **byte-identical** to the value currently frozen in
`cases.json` for `CONT-BREAK`. So the inconsistency is **not** a numeric mismatch.

**The real shape of the inconsistency** — `review.md:128-129` contains the reviewer's
*minimal repair prescription*, which has **two halves**:

1. Keep `CONT-BREAK`'s value as the card's L117–L122 patch, and **add**
   `expect_message_contains = "stock-flow balance failed: FY2027"` to it.
2. **Add** a separate `CONT-BREAK-CROSSYEAR` case whose value is
   `{"opening_arr": [200, 250], "closing_arr": [250, 251]}`.

**What actually landed**: only **half of half**. The file kept a single `CONT-BREAK` with the
**card's original value** (`{"opening_arr":[200,250],"closing_arr":[250,251]}`, i.e. the
*CROSSYEAR* value) and the **CROSSYEAR message** (`continuity failed: FY2028`). So:

* the reviewer's item-1 message requirement (`stock-flow balance failed: FY2027`) is **absent**;
* the reviewer's item-2 distinct case is **absent**;
* what exists is the *cross-year anchor* guard only — the **own-balance** guard is never reached.

**Corroborating (and false) on-disk claims** — both of these are written on disk and both are
**not true of the artifacts on disk**:

| File | Claim | Reality |
|------|-------|---------|
| `revision_r2.json` → `P2-3` | "implemented as `CONT-BREAK-CROSSYEAR`" | No such case id exists. |
| `revision_r2.json` → `card_specific` | "CONT-BREAK's refusal message was frozen to `'stock-flow balance failed: FY2027'`" | The frozen message belongs to the *cross-year* guard (`continuity failed: FY2028`). |

These are registered as drift items **D-7** in `binding.json` and are **not** corrected here
(they are outside T1-6's authority).

---

## 3. Why option (c) and not the alternatives

| Option | Content | Verdict |
|--------|---------|---------|
| (a) | Change `CONT-BREAK`'s value to the own-balance input | **Rejected** — destroys the only cross-year-anchor coverage, and *does* touch existing content ⇒ violates `无需改正文` in spirit. |
| (b) | Rewrite `CONT-BREAK` to the reviewer's item-1 message | **Rejected** — would make the frozen message disagree with the frozen input (the input breaks the *cross-year* anchor, not FY2027's own balance). Would encode a **false** pass condition. |
| **(c)** | **Append a new, different-input case for the missing guard** | **Chosen.** Satisfies `输入不同`, reaches the uncovered guard, and leaves every existing byte untouched. |

**Design constraint honoured**: the new case must reach a guard the **existing** case cannot.
The existing case makes **both years balance internally** and breaks only the cross-year anchor
(FY2027 close ≠ FY2028 open). Therefore the new case must break **FY2027's own bridge**, which
is what `{"opening_arr":[200,250],"closing_arr":[251,251]}` does: FY2027 opens 200, closes 251,
a 1-unit discontinuity *within the year itself*.

---

## 4. Reachability was measured before landing (not inferred)

Four probes, `scripts/t16_reachability_probe.py`, all four predicates **true**:

| Probe | Input | Observed |
|-------|-------|----------|
| control (positive) | `continuity_positive` | `ok [215.0, 250.0]` |
| existing `CONT-BREAK` | `[200,251]` / `[250,251]` | `opening_arr continuity failed: FY2028` |
| **T1-6 adjudicated value** | `[200,250]` / `[251,251]` | **`opening_arr stock-flow balance failed: FY2027`** |
| card `negative_patch` | card L117–L122 | **byte-equal to the current on-disk value** |

The two negatives raise the **same exception class** but carry **different messages** — that is
exactly why a type-only assertion is insufficient and the message must be frozen for the new case.

### 4.1 The message-prefix difference (registered honestly)

T1-6 as written names the expected string `stock-flow balance failed: FY2027`. The **measured**
full message is:

```
opening_arr stock-flow balance failed: FY2027
```

The adjudicated string is a **substring** of the measured one. Since `expect_message_contains`
is a *substring* test, the frozen assertion holds. This is recorded rather than silently
"fixed", because writing the longer string would put a value into the file that
`OWNER_DECISIONS.md` does not contain.

---

## 5. What was landed

**Into the isolated copy only** (`iso/cases_t16.json`). The frozen original is untouched.

| Item | Value |
|------|-------|
| Edit shape | **pure append** |
| New case id | `CONT-BREAK-OWNBALANCE` |
| `kind` | `set_driver_multi` |
| `expected` | `ModelRegistryError` |
| `base_input` | `continuity_positive` |
| `value` | `{"opening_arr": [200, 250], "closing_arr": [251, 251]}` |
| `expect_message_contains` | `stock-flow balance failed: FY2027` |
| `required_message_ids` | appended `CONT-BREAK-OWNBALANCE` (now 3 entries) |
| Δ bytes | **+1255** |
| Δ cases | **+1** (11 → 12) |

**Every other case is byte-identical** — verified by re-rendering each pre-existing case through
the same renderer and comparing (`renderer_is_faithful = True`,
`existing_cases_rendered_identically = True`).

**Only two top-level keys changed**: `cases` and `required_message_ids`
(`changed_fields_are_exactly_intended = True`).

---

## 6. Verification — frozen runner, two phases, OVERALL = PASS (7/7)

The **frozen** runner was invoked (not a re-implementation), once against the pre-image and once
against the post-image.

| Phase | rc | Note |
|-------|----|------|
| pre | `0` | baseline green |
| post | `0` | green with the new case in place |

```
negative: CONT-BREAK PASS_rejected ... - opening_arr continuity failed: FY2028
negative: CONT-BREAK-OWNBALANCE PASS_rejected ... message_requirement_met= True
                                                 - opening_arr stock-flow balance failed: FY2027
negative summary: {'total': 12, 'passed': 12, 'failed': []}
required_message_ids: ['NEG-CARD', 'CONT-BREAK', 'CONT-BREAK-OWNBALANCE'] ok= True
verdict: pass   exit_code: 0
```

Two independence checks also green:

* `shared_cases_unchanged = True` — the runner produced identical results for every *shared* case
  under both phases, so the new case changed no pre-existing verdict.
* `positives_unchanged = True`.

Note that `required_message_ids` is a **gate**: the runner asserts *before* running any negative
that each listed id exists in `cases` **and** carries a non-empty `expect_message_contains`; a
missing id makes the run **rc=3**. That is why the new case's id was added to the list — a case
that is present but not gated could be deleted without turning the run red.

---

## 7. Boundaries held

| Boundary | Check | Result |
|----------|-------|--------|
| Production anchor untouched | `scripts/model_registry.py` sha256 | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` — **matches** |
| Frozen evidence untouched | `M24/a20260919-01/evidence/M24/cases.json` | still `263b78b3…` / 6185 B — **not written** |
| No product files touched | `git diff HEAD --name-only` | all entries under `.planning/` — **0 product files** |
| All JSON parseable | 8 files through `json.load` | **OK** |
| No confusable characters | Cyrillic / homoglyph scan | **0 hits** |
| No status transition | — | **none performed** |
| No proxy signature | — | **none** |

**Per `T1-12` ①, this edit is a *landing*, and landings into frozen evidence require the
same additive discipline as errata** — hence the append-only shape and the untouched pre-image.

---

## 8. Pre-existing drift found (registered, NOT repaired)

While establishing the pre-image, eight on-disk inconsistencies were discovered. **All eight
predate this attempt** and **none** is within T1-6's authority, so they are **registered only**.

| id | Artifact | Registered | On disk |
|----|----------|-----------|---------|
| D-1 | `handoff.json` → `cases.json` | `df12c66a…` | `263b78b3…` |
| D-2 | `source_manifest.json` → `cases.json` | `df12c66a…` | `263b78b3…` |
| D-3 | `input.json` | `ccfc2f8e…` | `7f60e7d8…` |
| D-4 | `oracle.json` | `bab13806…` | `3da88501…` |
| D-5 | `after/rerun_sha256.json` | full set | all disagree with disk |
| D-6 | `recovery/selfcheck/selfcheck_result.json` | records `263b78b3…` **and** `frozen_hashes_unchanged=true` | cross-file inconsistent with D-1…D-5 |
| D-7 | `revision_r2.json` | claims do not hold of the artifacts (§2) | — |
| D-8 | `handoff.json` | `qualifications.formula = review_pending` while its own `status = accepted_scoped` | self-inconsistent |

**Working explanation** (not a conclusion): at least **two generations** of this attempt coexist —
an earlier one (`binding.json`, `after/rerun_sha256.json`) and a later one (`recovery/selfcheck`
plus what is actually on disk). `handoff.json` / `source_manifest.json` were evidently never
re-synced when the generation advanced. **Repairing this is a separate matter and is NOT done
here.**

---

## 9. What is deliberately NOT done

| Not done | Why |
|----------|-----|
| No `status` transition (`planned` → anything) | Acceptance is not the owner's to grant. |
| No write into `M24/a20260919-01/evidence/M24/cases.json` | Frozen evidence; landing there requires its own reviewed step. |
| No repair of D-1…D-8 | Outside T1-6's authority. |
| No edit to `card.md` prose | T1-6 says `无需改正文`; card clause 5 also forbids widening this card's allowlist to touch the 31 M-cards. |
| No claim that M24 is now "complete" | Only that the specific uncovered guard now has a case, **inside the copy**. |

---

## 10. Next action (handed off, not taken here)

1. An **independent reviewer** reviews this attempt and, if satisfied, performs the actual write
   into the frozen `cases.json` (or authorises it).
2. The drift items D-1…D-8 are handed to the owning tier for a decision — they are **not**
   self-healing and **not** covered by this card.
3. Until then, `status` stays `planned`, and M24 must not be described as closed.

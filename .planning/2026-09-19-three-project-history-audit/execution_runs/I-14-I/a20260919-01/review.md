# I-14-I review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; the implementer did NOT sign)

Status: **`accepted_scoped`** (conditional acceptance). The independent reviewer wrote their verdict in
`reviewer_report.md` (the byte-pinned carrier), **not** in this file. This file is the carrier-landing
bookkeeping landing of that verdict: it transcribes the reviewer's verdict, scope, rulings and findings
so the attempt's `review.md` slot is no longer a stub. **It is not a signature and it adds no acceptance
of its own.** Read `reviewer_report.md` itself for the reviewer's own words (§1–§10).

There was **no implementer stub** of `review.md` in this attempt: the file did not exist before this pass
(verified: the attempt root contained `binding.json`, `changes.diff`, `commands.json`, `handoff.json`,
`oracle.md`, `reviewer_report.md` and the evidence directories, and no `review.md`). This landing pass is
therefore a pure creation, not a replacement; there is no pre-image to preserve.

## Verdict block

- Card: **I-14-I** (container-basis per-case refusal + the two hardcoded-key derivations; the I-14-H
  mandatory RIDER / forced-closure card)
- Attempt: `a20260919-01` (`<PLAN>\execution_runs\I-14-I\a20260919-01`)
- Verdict: **`accepted_scoped`** — the reviewer's literal label is **ACCEPT（条件式，accepted_scoped）**,
  i.e. "ACCEPT, conditional" (`reviewer_report.md` line 10, which reads
  `## 结论：ACCEPT（条件式，` + a code span around `accepted_scoped` + `）`)
- Verdict author: an **independent reviewer session** (not the implementer). The reviewer states this at
  `reviewer_report.md` lines 5 and 388–389: "复核者：独立 reviewer（**非**实现者；实现者未自签，
  `implementer_signed=false` 已核实）" and "**reviewer 不自签实现者的工作**：本报告的 ACCEPT 是 reviewer
  对**证据**的裁定；实现者仍为 `implementer_signed=false` / `implementer_never_signs_acceptance=true`".
- Verdict round: round 1 of this card, and it is **conditional**, not clean: the reviewer upheld 9 of the
  implementer's 10 declarations outright and falsified the wording of one (declaration 4's second half →
  F-1), attaching **6 mandatory follow-ups** (`reviewer_report.md` §8, lines 362–377).
- What the conditionality is: the card's **exit criteria all hold on the merits** (14/14 frozen gate at
  rc 0; the xfail discharged as a *true* pass; both RED arms bidirectionally fail-able; `:241`/`:248`
  genuinely derived; zero production writes). The acceptance is conditional **only** on wording
  corrections and on the finding register (F-1, F-2, CF-I14I-3) being carried forward correctly.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256 | `525dbb138643d7a775142688ed4068519cd942e706ad7ad14403cf19224cbf71` |
| bytes | 32218 |
| lines | 416 (LF-only, no BOM, single trailing LF) |
| pin sidecar | `reviewer_report.sha256` (created by this landing pass; see Bookkeeping) |
| carrier region (all bytes except the single trailing LF) | bytes 0..32216 (32217 B), sha256 `cf91ea6e9ec424d2c9a526ff153386f9b37bf04b496e4b5e04655898fc8646e1` |
| verdict line | 10 |
| first line of verdict | `## 结论：ACCEPT（条件式，accepted_scoped）` (the code span around `accepted_scoped` is omitted in this quoting) |
| conclusion block lines (inclusive, 1-based) | 10–34 |
| per-card-item verdict table lines (inclusive) | 25–34 |
| recomputation table (R1–R15) lines (inclusive) | 43–59 |
| findings §2 lines (inclusive) | 74–210 |
| CF-I14I-2 scope ruling §3 lines (inclusive) | 213–243 |
| `SUT_VERSION` ruling §4 lines (inclusive) | 247–260 |
| 10-declaration adjudication §5 lines (inclusive) | 264–277 |
| unverified list §6 lines (inclusive) | 281–307 |
| numbers and hashes §7 lines (inclusive) | 311–358 |
| mandatory follow-ups §8 lines (inclusive) | 362–377 |
| boundary statement §9 lines (inclusive) | 381–389 |
| self-verifiability + self-correction record §10 lines (inclusive) | 393–416 |
| producer | independent reviewer (not the implementer) |

**Verification performed by this landing pass (not merely transcribed).** The pin was recomputed, not
trusted: the carrier measures **32218 B / 416 LF / sha256 `525dbb13…`** (full value
`525dbb138643d7a775142688ed4068519cd942e706ad7ad14403cf19224cbf71`), matching the task's pin exactly. A pin sidecar was absent from this attempt (unlike I-14-F, which has one); this pass created it
additively. The reviewer's §7 hash table was then re-derived file-by-file: **all 14 checked entries
matched byte-for-byte**, including `iso/natural_window.py` `9edb9515…` (23162 B),
`before/natural_window.i14b-after-2.py` `7fff6f0c…` (20293 B), `harness/run_cases.py` `f2a07d0b…` (8390 B),
`harness/cases.i14h.json` `40260c24…` (26630 B), `harness/frozen_expectations.i14h.json` `bffb11c2…`
(13100 B), the landed gate `cases_report.json` `e8925fdc…` (1647 B), the gate `sut_report.json`
`11f27c8e…` (21416 B), the pre-fix `cases_report.json` `91ff3a5d…` (1521 B), and `oracle.md`
`3842f2d4…` (17246 B, matching the reviewer's §6.3 disclosure that its current hash differs from the
frozen-at value). This pass also **re-ran the gate itself** and reproduced `sut_report.json` at exactly
**21416 B / `11f27c8e…`** — a three-way byte-identical agreement (implementer's landed artifact,
reviewer's independent re-run, this pass's re-run).

## Scope statement (binding — transcribed from the reviewer)

Acceptance is **conditional (`accepted_scoped`)**, not clean. Verbatim from `reviewer_report.md` lines
10–16 and 18–21:

> 卡片的**全部退出判据均经独立复算成立**：全 14-case 门 rc 0；xfail 已解除且经"字节未改的 I-14-H 套件"
> 证明为**真通过**；两个 RED 臂双向可失败；`:241`/`:248` 确为派生值；冻结正文与生产树零改动。
> 实现者第 1–10 项声明中，**9 项完全成立**，**1 项（第 4 项后半"判别力可见于冻结门内部"）措辞过强、
> 经变异测试证伪**（见 F-1）。该措辞不改变退出判据的成立，但会误导下游读者对"门本身能证明什么"的判断，
> 故本卡为**条件式验收**，附 6 项强制后续（见 §8）。
>
> **验收证据**：14/14 冻结用例端到端门 rc 0（`mismatch_count=0` / `accepted_ineligible=0` / SUT rc 0）
> + 45 例 rider 套件 45 passed / 0 xfailed。⇒ **I-14-H 的"12/14 冻结用例 + 12 例 pytest 套件"限定可以解除**，
> 但仅限该限定本身；I-14-H 的其余 NOT GRANTED 项（真实自然观察 / 真实 UI 即时性 / SLO / `disclosure_adaptation` /
> `accuracy`）一律不变。

**Independent re-derivation by this pass (the exit criterion, confirmed):** using the **unmodified**
`harness/run_cases.py` (`f2a07d0b…`) with the **unmodified** frozen material (`cases.i14h.json`
`40260c24…`, `frozen_expectations.i14h.json` `bffb11c2…`) against the fixed SUT (`9edb9515…`) gives

```
ok=true, case_count=14, mismatch_count=0, accepted_ineligible_count=0, sut_raw_returncode=0, rc 0
sut_report.json = 21416 B / 11f27c8ee0cb84a95ee82ffc90a3ba40633a7fb29bfda650a08405529bd26af3
```

with the gate case set measured as exactly `['W1','H1'…'H12','C2']` (14 cases).

## Reviewer rulings transcribed

### Ruling on CF-I14I-2 scope (`reviewer_report.md` §3, lines 213–243)

**KEEP inside I-14-I — do not split the card.** The reviewer gives three reasons (it falls inside card
item 1's authorisation because item 1's observable goal is "per-case decision, no batch abort", and a
`set` basis aborted the batch at the `json.dumps` step; it has zero externality — `basis` carries no value
constraint in any of the 14 frozen cases; the change is minimal and fail-closed). Two conditions attach:

- **(a) Wording correction (mandatory).** The acceptance text must state: "CF-I14I-2 fixed
  `computed["basis"]`; `classify()` still echoes `claim` verbatim, so a non-JSON-native basis still makes
  the **in-process** whole-batch report unserialisable (F-2). This path is unreachable inside the gate; it
  does not affect this card, but **that failure mode was NOT completely eliminated**."
- **(b) No scope widening.** This card does **not** authorise changing the `claim` echo. Doing that is a
  **new card** (reviewer §8 item 2), because it changes the public shape of `verdict` and needs its own
  expectations and red/green evidence.

The reviewer's preferred disposition of the finding's `class` wording: keep the finding id and change the
class from "NEW FINDING, disclosed" to **"IN-SCOPE CONSEQUENCE of card item 1"** (reviewer §3, lines
240–243). This landing pass applied that preference to `handoff.json.carried_findings[CF-I14I-2]`, with
the original class string retained as `class_before_bookkeeping_fix`.

### Ruling on `SUT_VERSION` (`reviewer_report.md` §4, lines 247–260)

**Not bumping is correct, but an explicit machine-checkable r3 identity is required.** `SUT_VERSION`
reads `"i14b-after-2"` for **both** the pre-fix and the fixed revision (measured at `:79` fixed vs the
pre-image's `:55`); r1 read `"i14b-after-1"`. The two cannot be distinguished by the version string, only
by sha256 (`9edb9515…` vs `7fff6f0c…`). Consequence recorded: **the gate report's `sut_version` field
carries zero revision information** — a downstream reader who looks only at that field will treat the
pre-fix and fixed revisions as the same revision, which is exactly what card item 7 set out to prevent.
The reviewer's remedy, adopted here: leave `SUT_VERSION` alone and write `sut_sha256=9edb9515…` plus
`revision="r3"` into I-14-I's `qualification.json` (reviewer §8 item 6). `run_cases.py:121` already
records `sut_sha256` independently, so the gate artifact was always able to distinguish the revisions; what
was missing was a machine-checkable field for downstream readers.

## Findings register (`reviewer_report.md` §2, lines 74–210)

Registered in `handoff.json.reviewer_findings` and `evidence/I-14-I/qualification.json`.

| id | severity | finding | disposition |
|---|---|---|---|
| **F-1** | **MEDIUM — wording correction required** | The claim that the derived-key discrimination is repaired "inside the frozen gate" is **FALSE**. A mutant with the two keys reverted to hardcoded `False` (all else identical) still passes the **unmodified** 14-case gate at **rc 0**. | **CORRECTED IN PLACE** in `handoff.json` (original wording retained and marked superseded); frozen `oracle.md` §9.3 registered as still-stale-but-frozen, erratum owed (see below). |
| **F-2** | low-medium | `classify()` still echoes the raw `claim` at `iso/natural_window.py:502`, so a non-JSON-native basis still makes the whole report unserialisable — measured on the **FIXED** SUT: `dumps(computed)=ok` but `dumps(verdict)=RAISE` for set/frozenset/bytes/object. The earlier wording ("`computed['basis']` echoed … so `json.dumps(report)` raised") is imprecise: there were **two** sources and only one is fixed. | **REGISTERED as a latent hardening item** (own card, reviewer §8 item 2). Structurally unreachable inside the gate: JSON input cannot express set/frozenset/bytes/object. |
| F-3 | info | The "list/dict-specific" attribution is exactly right, and the reviewer narrowed it further: the crash is **unhashable**-specific; list/dict are merely its only JSON-reachable forms (`("union_of_windows",)` does not crash, `(["union_of_windows"],)` does). | Recorded; no action. |
| F-4 | info | The set/tuple anti-overfitting proof holds: the fixed type guard neither over-fits (registered strings still decided on the merits) nor under-fits (list/dict/nested/unhashable-tuple all blocked). "这是本卡设计得最好的一处." | Recorded; no action. |
| F-5 | info | H12 passes as specified (double refusal codes, `union_seconds=2220.0`, `quick_check_overlap_seconds=480.0`). H12's pytest-coverage gap (I-14-H CF-I14H-3) persists but is now covered by the genuinely-passing frozen gate. | Recorded; no action. |
| F-6 | info | Derived semantics correct and all four combinations present, all fail-able — **but** `oracle.md` §4 names the `(True,True)`/`(True,False)` scenarios "W4/W5" while W4/W5 are **not in the 14-case gate** (the gate is `W1 + H1…H12 + C2`; W4/W5 belong to the r1 pre-image `cases.json` 20-case set). §4 does **not** assert `(T,T)` for those cases, so this is scenario-naming ambiguity, not an expectation error. | Registered; append-only naming fix recommended (reviewer §8 item 3), **not** applied here. |
| F-7 | info | The card's cited line numbers drifted after the fix: `:202` is now `if qc_started is not None and qc_finished is not None:`; downstream text must point by **symbol name** (`_basis_kind` / `quick_check_in_observation_intervals` / `sum_used_for_natural_duration`). | **Adopted**: this landing pass uses symbol names as primary. Exact measured positions recorded below. |
| **CF-I14I-3** | info | The implementer's own auditor had a transient operator-precedence bug (2 false failures, H11/H12), corrected to **44 checks / 0 failures** — **self-reported only**, no evidence survives (the corrected run replaced the defective one in place). | Registered as **self-reported / unverifiable-after-the-fact**, same class as I-14-H's CF-I14H-4. Impact: none — the auditor is a convenience checker; the gate is the unmodified `run_cases.py`. |

### F-1 independently reproduced by this landing pass (not just transcribed)

This landing pass rebuilt the reviewer's mutant from the fixed SUT by reverting exactly the two key lines
to `False`, leaving all other bytes untouched, and obtained a **byte-identical** mutant:

```
mutant sha256 = 2265bd0d7fe4a950d737e77ef6409991d9d30978b4eb61a54b33cb0cb71944f0   (23101 B)
reviewer's claimed mutant sha256 = 2265bd0d7fe4a950d737e77ef6409991d9d30978b4eb61a54b33cb0cb71944f0
```

Running the **unmodified** gate against it:

```
ok=true, case_count=14, mismatch_count=0, accepted_ineligible_count=0, sut_raw_returncode=0, rc 0
sut_report.json = 21419 B / ab2c4b7b61266cedd4c0bb9910c7bc86f7c27bc5c202bbc0ae478ef354103464
```

The mutated report differs in bytes yet the gate still reports `ok=true` — direct proof that the mismatch
checker never reads those two keys. Its four key values collapse to `W1=(F,F)`, `H10=(F,F)`, `H11=(F,F)`,
`H12=(F,F)`, whereas the fixed SUT yields `W1=(F,F)`, `H10=(F,T)`, `H11=(T,F)`, `H12=(T,F)`.

The mechanism was confirmed at source level, independently of the reviewer:

- `harness/run_cases.py:177-180` checks `REQUIRED_KEYS` for **presence only** (`if key not in computed`)
  and never compares the value.
- Of the 32 expectations in `frozen_expectations.i14h.json`, `quick_check_in_observation_intervals` is
  constrained in exactly **one** entry — W1, value `False` — and `sum_used_for_natural_duration` is
  constrained in **none** (15 distinct constrained computed keys; it is not among them).
- The gate's 14 cases are exactly `['W1','H1'…'H12','C2']`.

Running the **rider suite** (`harness/test_i14i_natural_window.py`) against the same mutant reproduces the
reviewer's R13 exactly — **4 failed, 41 passed** — and the four failures are precisely the four the
reviewer named:

```
test_d3_renamed_window_reports_quick_check_inside_observation
test_d3_overlapping_sum_claim_reports_both_keys_true
test_d3_overlapping_union_claim_reports_overlap_only
test_d3_disjoint_sum_claim_reports_sum_used_without_overlap
```

**Therefore the correct wording — adopted as authoritative in this attempt's carriers — is:**

> The derived keys' **fail-able criterion lives in the rider suite** (4 tests covering all four
> `(qc_in, sum_used)` combinations). The **frozen gate does NOT validate the values of these two keys**;
> the gate's rc 0 proves only that the other 14 cases are end-to-end consistent and that the batch no
> longer aborts. **"Gate rc 0" must NOT be read as "the derivation is gate-proven."**
> The gate never had discriminating power over these keys — neither before nor after the fix. Pre-fix, the
> gate failed for exactly one reason: **batch abort (SUT rc 4)**, not key discrimination.

### F-2 independently reproduced by this landing pass

On the **fixed** SUT (`9edb9515…`), calling `classify()` in-process with a non-JSON-native basis:

| basis | `computed.basis` | `dumps(computed)` | `dumps(full verdict)` |
|---|---|---|---|
| `"sample_span"` | `'sample_span'` | ok | ok |
| `list` | `'<non-string basis: list>'` | ok | **ok** |
| `dict` | `'<non-string basis: dict>'` | ok | **ok** |
| `set` | `'<non-string basis: set>'` | ok | **RAISE** `Object of type set is not JSON serializable` |
| `frozenset` | `'<non-string basis: frozenset>'` | ok | **RAISE** |
| `bytes` | `'<non-string basis: bytes>'` | ok | **RAISE** |
| `object` | `'<non-string basis: object>'` | ok | **RAISE** |
| `tuple` | `'<non-string basis: tuple>'` | ok | **ok** |
| `None` | `'<non-string basis: NoneType>'` | ok | **ok** |

The decision itself is correct — a `set` basis yields `refusals=['R-BASIS-UNKNOWN']` — only the **write**
fails. The residual non-serialisable set is exactly `{set, frozenset, bytes, object}` (and any other
non-JSON-native object); `list`/`dict`/`tuple`/`None` now serialise because `computed.basis` passes through
`_basis_repr()`. Confirmed at source: `iso/natural_window.py:502` is `"claim": case.get("claim"),` — the
raw echo. The reviewer's boundary holds: this is **structurally unreachable inside the gate** (the 14
cases come from JSON parsing, which cannot express set/frozenset/bytes/object), so the gate's rc 0 and
this card's exit criteria are unaffected. It is a **latent** item and must not be widened here.

### F-7 exact positions measured by this landing pass

The card's `:202` / `:241` / `:248` pointers are stale in the fixed revision. Measured on
`iso/natural_window.py` (`9edb9515…`, 554 lines):

| construct | card (pre-fix) | reviewer's F-7 | **measured (fixed revision)** |
|---|---|---|---|
| type guard (membership test) | `:202` | `:252` | **`:257`** (`if basis_kind != "str" or basis not in BASIS_REGISTRY:`) |
| `quick_check_in_observation_intervals` | `:241` | `:291` | **`:296`** |
| `sum_used_for_natural_duration` | `:248` | `:298` | **`:304`** |
| `_basis_kind()` / `_basis_repr()` definitions | — | — | `:116` / `:134` |
| `SUT_VERSION = "i14b-after-2"` | — | `:79` | `:79` (confirmed) |
| `claim` echo (F-2) | — | `:502` | `:502` (confirmed) |

The reviewer's F-7 **substantive point is confirmed** (`:202` in the fixed file is indeed
`if qc_started is not None and qc_finished is not None:`). The reviewer's replacement numbers are
themselves not exact: `:252` and `:293` are `changes.diff` hunk-region starts
(`@@ -198,8 +252,9 @@`, `@@ -238,14 +293,15 @@`), not the construct lines, and `:291`/`:298` land on
`observation_interval_count` and `union_seconds`. **The remedy the reviewer recommends — point by symbol
name — is therefore the correct one and is adopted throughout this attempt's carriers.**

## Reviewer self-corrections (recorded, not silently overwritten)

The reviewer preserved both of their own corrections in `reviewer_report.md` §10 (lines 405–416), and both
**weaken** their own accusations — which is why they are recorded here as part of the record:

1. **Withdrawn W4/W5 arithmetic errata.** The draft asserted that `oracle.md` §4's W4/W5 row
   (`2940 / 3480 / 540 / 480`) had `quick_check_overlap_seconds` and `overlap_seconds` transposed, and wrote
   a corresponding "erratum request" into §8. **The assertion was wrong.** Recomputing by hand from §4's own
   windows (`[00:00–00:29]`, `[00:20–00:49]`) plus quick_check `00:29–00:37` gives `sum=3480`,
   both-window overlap `=540`, `union=2940`, quick_check∩observation `=480` — matching the row item by item.
   The reviewer withdrew the claim in three places (F-6, §6.5, §8.3) and replaced it with a
   **scenario-naming ambiguity** only. **Downstream must not act on a non-existent errata requirement.**
2. **Initial over-statement of F-2.** The first probe called `json.dumps` on the **entire `classify()`
   return value**, conflating the `claim`-echo failure with the `computed` failure, and briefly suggested
   "set still aborts the whole batch after the fix". After checking the real serialisation object of this
   card's exit criterion — which is **`computed`** — the reviewer narrowed F-2 to
   **latent / gate-unreachable** as recorded above.

## I-14-H discharge — FLAGGED, NOT PERFORMED HERE

`reviewer_report.md` §6.6 (lines 305–307) and §8.5 (line 375) rule that **I-14-H's discharge condition is
now MET on the merits**: the 14-case end-to-end gate reaches **rc 0 / `mismatch_count=0` /
`accepted_ineligible_count=0` / SUT rc 0**, and the artifact is landed at
`execution_runs/I-14-H/a20260919-01/evidence/I-14-I/cases_report.json`
(sha256 `e8925fdcf3a99727b63401b29fe893588a1777e4a7361c6f8d66cdcfc327a288`, 1647 B — verified byte-for-byte
by this pass; the sibling `sut_report.json` is `11f27c8e…`, 21416 B). This discharges exactly one thing:
the conditional-scope wording that I-14-H's `review.md` line 192–193 imposes ("在补跑完成前，本卡的验收陈述
须限定为'12/14 冻结用例 + 12 例 pytest 套件'").

**This landing pass did NOT touch I-14-H's carriers.** Updating I-14-H's `handoff.json` /
`evidence/I-14-H/qualification.json` (`formula.state`, the `conditional_scope` block, `scope.granted`
"12/14 …" strings, `not_granted` entries) is a **separate bookkeeping act** that must be its own
carrier-landing pass against the I-14-H attempt. It is **flagged and requested** here, not done.
I-14-H's other NOT GRANTED items (real natural observation / real UI immediacy / SLO /
`disclosure_adaptation` / `accuracy`) are unchanged and are **not** discharged by this card.
I-14-H's carrier `review.md` was re-hashed by this pass and is unchanged at
`97997d6d26af5a1fd36e486c508a027642f4492af1f5415fe3f25bc929e130b2` (14691 B).

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; real natural-observation
eligibility, real UI immediacy and SLO/performance stay **NOT GRANTED**. All 14 gate cases and all 45 rider
cases are **SYNTHETIC-TIMER-ONLY** synthetic time input; no real natural period was observed, measured or
completed (reviewer §9, lines 383–385). No production-write authority is granted: the SUT is
attempt-local and `git status --porcelain -- scripts` was empty.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-21 22:43 local
  (2026-09-21T21:43:10Z).
- Status transition: `review_pending` → `accepted_scoped` (recorded as
  `status_before_bookkeeping_fix: "review_pending"`).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`.
- Authority: acceptance was written by an independent reviewer, never by the implementer.
- This pass wrote **only**: `review.md` (new), `handoff.json` (in-place correction with superseded wording
  retained), `evidence/I-14-I/qualification.json` (new), `reviewer_report.sha256` (new pin sidecar), and
  temporary verification scratch files under `%TEMP%\i14i-carrierland-verify\` (outside the attempt).
- This pass changed **no** byte of `reviewer_report.md`, `oracle.md`, `changes.diff`, `commands.json`,
  `binding.json`, `iso/natural_window.py`, any `harness/` file, any `before/` or `after/` evidence capture,
  or any file of the I-14-H attempt, and **no** production file.
- `reviewer_report.md` was verified **before and after** this pass at
  `525dbb138643d7a775142688ed4068519cd942e706ad7ad14403cf19224cbf71` / 32218 B — unchanged.
- **Frozen documents are deliberately left un-rewritten.** `oracle.md` §9.3 (line 194 heading, lines 205–207)
  still carries the falsified F-1 sentence, and §4 still uses the W4/W5 scenario ids (F-6). `oracle.md` is a
  hash-pinned artifact (its §1–§8 were frozen at `2026-09-21T19:59:53Z`, and its current hash `3842f2d4…`
  is recorded in `handoff.json`), so this pass did **not** edit it. Both corrections are registered in
  `handoff.json.wordings_requiring_append_only_correction` with the exact replacement text, as **OPEN**
  follow-ups requiring an append-only erratum — the same disposition I-14-F's landing used for its frozen
  documents. The authoritative corrected wording for F-1 lives in this file and in `handoff.json`.

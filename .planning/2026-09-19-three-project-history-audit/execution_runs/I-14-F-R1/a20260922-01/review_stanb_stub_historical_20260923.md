# I-14-F-R1 review.md — STUB (no verdict; the implementer does NOT self-sign)

Status: **`review_pending`**. No review of this attempt has been performed yet. Acceptance is
the exclusive responsibility of an independent reviewer (never the implementer, never the
owner, never this file's author). This stub must be replaced only by a reviewer's own verdict
block (or a carrier landing that transcribes a byte-pinned reviewer report, as happened on
I-14-F a20260919-01).

## What this attempt claims (for the reviewer to verify, not to believe)

- Card: **I-14-F-R1** — apply owner ruling `OWNER_DECISIONS.md` §16 E-1 (verbatim
  「E-1: 150/60」: `GENERATION_RESERVE = 150` ⇒ relocate threshold **60**) to the product-side
  short-basetemp convention, in a NEW isolated attempt. I-14-F's attempt
  (`execution_runs/I-14-F/a20260919-01`) is sealed/accepted and was read-only input.
- The oracle was frozen BEFORE any run: `oracle.md`, sha256 sidecar `oracle.sha256`.
- Expected evidence: 15-case unit suite with boundary 60/61 pinned; RED on the pristine tree
  (deep cwd → WinError 206); GREEN (deep cwd → relocated, passes); mutation
  (`CW_SHORT_BASETEMP_DISABLE=1` → both nodes fail, frozen signatures); size sweep
  (61/69/76/82/86 relocate + pass; 40/60 unrelocated).
- Errata registry for I-14-F's sealed doc defects F-2/F-3/F-4/F-6 lives in this attempt's
  `decision.md` (append-only; each cites the carried-finding ID).

## Reviewer checklist (suggested)

1. `oracle.sha256` pin predates every run artifact (mtimes under `before/`, `after/`).
2. Re-derive the criterion from `iso/tree/conftest.py`: `len + 150 > 210 ⇔ len > 60`.
3. Re-run the unit suite; confirm 15 passed, boundary 60/61 pinned, flips carry written reasons.
4. Re-run RED/GREEN/mutation at cwd 166/167 (driver `--target-root-len 140` guard).
5. Check the sweep table in `after/sizes/summary-placement.json` against oracle §8.
6. Confirm zero writes: production repos, and I-14-F's sealed attempt (compare against its
   `after/final_hashes.json`).
7. Confirm `commands.json` entries carry real argv/cwd (F-6 fixed for this attempt).
8. Confirm `handoff.json.status == "review_pending"` was true before your verdict, and that no
   acceptance language appears in any implementer-authored file.

## Boundaries

`disclosure_adaptation = unmapped`, `accuracy = unproven`; test-infrastructure only; promotion
to any production tree is a separate, ungranted step.

---

## CARRIER LANDING — verdict block (bookkeeping transcription, 2026-09-22)

This block supersedes the `review_pending` status declared by the implementer stub above; the
stub text is retained verbatim as implementer-authored history (append-only).

- **verdict**: `accepted_scoped`
- **reviewer**: 独立复核 — independent review; the verdict was authored solely by the
  independent reviewer, never by the implementer.
- **carrier**: `reviewer_report.md` — **15841 B**, sha256
  `8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c`, pinned by sidecar
  `reviewer_report.sha256` (`sha256:` + `bytes: 15841` + `verdict: accepted_scoped`,
  `pinned_at_local: 2026-09-22T09:29:07+01:00`).
- **byte proof**: re-hashed at carrier landing — 15841 B, digest matches the sidecar exactly.
- **carrier line ranges**: verdict L16; scoped residuals L35–48; Gap-5 ruling §6 L143–163;
  findings §7 L165–174; signature §9 L202–211 (`accepted_scoped`, N-1..N-3 + inherited CFs
  as scope).
- **nature of this block**: a bookkeeping transcription of a byte-pinned reviewer report. It
  adds **no acceptance of its own** — no verdict is authored or re-adjudicated here.
  `implementer_signed: false`; the implementer never signs acceptance.

### Scope as accepted (transcribed, not re-adjudicated)

- **threshold 150/60 adopted per owner §16 E-1** (`GENERATION_RESERVE=150` ⇒ relocate iff
  `len + 150 > 210 ⇔ len > 60`).
- **boundary 60/61 pinned**: 60 → unrelocated, 61 → relocated (unit cases + sweep halves).
- **size sweep**: 61/69/76/82/86 **relocate + pass**; 40/60 **unrelocated** (7/7 guard ok).
- **12 control flips, each under the verbatim superseded reason** 「owner §16 E-1 chose 150/60;
  this control's unrouted expectation is superseded」 — recorded as 8 flip rows in decision.md
  §4 (basetemps 69/68, 76/75, 82/81, 86 + unit 84/82/78 + `decide()` 64 = 11 datapoints) plus
  4 inline reason comments in the unit file = 12 flip records; the 52-char datapoint is
  deliberately NOT flipped; the reason sits at the §4 table head rather than restated per row
  (**N-1**).
- **RED / GREEN / MUT reproduced by the reviewer** in own deep-logon runs: RED rc 1 with
  literal `WinError 206` and no decision file; GREEN rc 0 with `relocated=true`,
  `generation_reserve=150`, `threshold=60`, `cleanup removed=true`; MUTATION
  (`CW_SHORT_BASETEMP_DISABLE=1`) rc 1 with `relocated=false`, `reason=disabled-by-env` and
  the literal `WinError 206` back.
- **unit suite: 15 passed, rc 0** (reviewer's own run).
- **sealed I-14-F attempt + production untouched**: I-14-F's 3 pinned files re-hash unchanged
  (`c22be9f3…`, `b0402b56…`, `2e6709e0…`); production `company-wiki` at HEAD `f39bd5a6` with
  exactly the 3 pre-existing user modifications.

Scope limits transcribed together with the verdict: CF-I14FR1-3 / Gap-5 ruled **not blocking**
⇒ promotion-time sampling obligation (the separate, ungranted promotion card must sample a
broader company-wiki suite before merge); **R-2 stands** (I-14-E scope, load band
unadjudicated by design); **N-1** (low), **N-2** (info, per-row env not in commands.json —
rerunner must read the harness for `PYTHONPATH`), **N-3** (info, tree-vs-red-tree import
asymmetry, immaterial); reviewer-disclosed unit-run1/run2 failures retained (harness
invocation + pathlib 63-vs-64 construction bugs; test fixed, not the oracle — mtime ordering
08:34 < 08:35 < 08:42); `disclosure_adaptation = unmapped`, `accuracy = unproven`;
promotion of `iso/` = separate owner decision, **ungranted**.

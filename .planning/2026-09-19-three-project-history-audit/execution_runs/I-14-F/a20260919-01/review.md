# I-14-F review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; the implementer did NOT sign)

Status: **`accepted_scoped`**. The independent reviewer wrote their verdict in
`reviewer_report.md` (the byte-pinned carrier), **not** in this file. This file is the
carrier-landing bookkeeping landing of that verdict: it transcribes the reviewer's verdict and
scope so the attempt's `review.md` slot is no longer a stub. **It is not a signature and it adds
no acceptance of its own.** Read `reviewer_report.md` itself for the reviewer's own words (§1–§12).

The implementer's original stub (sha256 `9d5207c083845a9b1be33d27c677989131975dcbba935373b8c1299371e44885`,
1433 B, 21 lines) is preserved byte-for-byte at `before/review-md-preimage/review.md`; its
successor here is written by the carrier-landing pass, not by the implementer and not by the
reviewer.

## Verdict block

- Card: **I-14-F** (deep-cwd WinError 206 → product-side short-basetemp convention)
- Attempt: `a20260919-01` (`<PLAN>\execution_runs\I-14-F\a20260919-01`)
- Verdict: **`accepted_scoped`** — the reviewer's literal label is **ACCEPTED — SCOPED**
  (`reviewer_report.md` line 10: `## VERDICT: **ACCEPTED — SCOPED**`)
- Verdict author: an **independent reviewer session** (not the implementer). The reviewer's own
  signature is at `reviewer_report.md` lines 304–305: "Reviewer signature: independent reviewer,
  card I-14-F, attempt a20260919-01. Implementer did not self-sign".
- Verdict round: round 1 of this card (single independent review round; the verdict is **scoped**,
  not clean).

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256 | `2e6709e0c6690c76d377dceec787c8de7722bd38c0d5cabc8fc49b0a37fc2af1` |
| bytes | 23191 |
| lines | 305 (LF-only, no BOM, single trailing LF) |
| pin sidecar | `reviewer_report.sha256` |
| sidecar bytes / sha256 | 328 / `24962193015b867b9e7ee4da52c9f9a916c5d65101212c0140d28e4fe58e85a1` |
| verdict line | 10 |
| first line of verdict | `## VERDICT: **ACCEPTED — SCOPED**` |
| scope statement lines (inclusive, 1-based) | 20–45 |
| findings table lines (inclusive) | 236–246 |
| unverified/not-covered lines (inclusive) | 248–266 |
| recommended-disposition lines (inclusive) | 295–305 |
| reviewer signature lines (inclusive) | 304–305 |
| carrier region (all bytes except the single trailing LF) | bytes 0..23189 (23190 B), sha256 `baed8f8766cbdf0603194756daf4ad13e3b3f289e11e683872b1791f5778f46c` |
| producer | independent reviewer (not the implementer) |

**Pin discrepancy recorded (bookkeeping only).** The sidecar `reviewer_report.sha256` states
`lines: 304`; the file actually has **305** lines and 305 LF bytes. The sidecar's pinned `sha256`,
`bytes` (23191) and verdict label are all correct — only its `lines:` field is off by one. No byte
of the carrier was changed by this landing pass (`reviewer_report.md` mtime is unchanged at
2026-09-21 21:18:28; this pass is read-only on it).

## Scope statement (binding — transcribed from the reviewer, `reviewer_report.md` lines 20–45)

Acceptance is **SCOPED, not clean**. The card's exit criterion is met and independently
reproduced: at the frozen deep geometry (cwd 166/167, basetemp 173/174) a pristine HEAD tree fails
with the literal `FileNotFoundError: [WinError 206]`, the same geometry with the shipped
`conftest.py` relocates the basetemp and passes, and disabling only the convention
(`CW_SHORT_BASETEMP_DISABLE=1`) restores the failure. Production is untouched (zero writes, HEAD
unchanged) and the change is a pure addition of two files, verified byte-for-byte against a fresh
`git archive` of company-wiki HEAD. Acceptance is scoped on three recorded residuals:

1. **R-1 (medium — CALIBRATION ACCURACY).** The frozen `GENERATION_RESERVE = 124` is the *child*
   node's longest generated suffix; the ***logon*** node's is **150** (measured on two **passing
   unrouted** runs, basetemps 74 and 81). The real unrouted maximum is therefore **236** chars,
   not the documented 210, and the "clear of the 240 degradation onset" claim has **4–5 chars** of
   headroom, not ~30. At the largest unrouted basetemp (86) the logon node generates **236**-char
   paths; the band **232–236 is untested for the logon node and is not rerouted**, so `oracle.md`
   Addendum C's assertion that everything ≥211 total is "rerouted conservatively" is **FALSE for the
   logon node**. The docstring's arithmetic is internally inconsistent (31 + 13 + 79 = 123 ≠ 124;
   the child's true value is 125). **This does not block**: the 206 class needs ~248 for directory
   creation and ~260 for files, while the unrouted maxima are 159 (child) / 184 (logon) for
   directories and 211 (child) / 236 (logon) for files — so the card's **206 criterion is still
   SAFE everywhere unrouted**. **Owner decision needed**: adopt `GENERATION_RESERVE = 150`
   (⇒ threshold 60) if the documented margin is to be the *real* margin, or keep 86 with the true
   numbers recorded. The numbers as written in `conftest.py`'s docstring, `decision.md` §1/§6,
   `oracle.md` Addendum C and `handoff.json` are factually wrong and must be corrected on the
   record.
2. **R-2 (low — child GREEN inferred, not demonstrated).** Under the *final* constants the 3 deep
   child runs at 167/166 **all** failed with the I-14-E load-band signature (**0/3 clean** — all in
   the I-14-E load band). The child's clean deep passes come from the falsified-constant era;
   relocation decision and effective path depth are identical, so they remain valid evidence for
   the path criterion, but **no final-era clean child pass at 167/166 exists**.
3. **R-3 (low — silent oracle substitution).** Frozen oracle E-G4 specified cwd `> 380`; the actual
   runs used **190/189** and the driver guard was re-declared to match, with **no addendum recording
   the deviation**. The substitution was forced (a >380-char directory is not creatable on this box;
   the mkdir edge is ~248) but unrecorded.

Gap (b) **does not block acceptance**: the child's thin GREEN is correctly scoped to **I-14-E**,
because the load band also hits short/unrouted placements and the path-family criterion is fully
adjudicated for that node (`reviewer_report.md` §7).

## Carried findings (all non-blocking; registered in `handoff.json.carried_findings`)

| id | severity | finding |
|---|---|---|
| R-1 / F-1 | medium | Reserve/limit derivation wrong for the logon node (124 vs measured 150); unrouted max is 236 not 210; "clear of 240" claim incorrect; false in `conftest.py` docstring, `decision.md` §1/§6, `oracle.md` Addendum C, `handoff.json`. Owner decision: adopt reserve 150 ⇒ threshold 60, or keep 86 with true numbers. |
| R-2 | low | Under the FINAL constants at 167/166 the child is **0/3 clean** (all in the I-14-E load band) — no final-era clean child pass. |
| R-3 / F-2-adjacent | low | Oracle E-G4's over-deep `>380` silently replaced by 190/189 with the guard re-declared; no addendum records it. |
| F-2 | low | `decision.md` §1/§6 still presents the Addendum-B calibration (240/124/116) as current while shipped code/tests use 210/124/86; frozen 20:14:58, before Addendum C (20:21:45), never superseded in-file. |
| F-4 | low | Cleanup holds for **terminated** sessions (26/26 `removed=true`) but **NOT killed** ones — 3 orphan `%TEMP%\cw-pytest-basetemp\*` dirs remain (2 empty; `…193155…` holds 61 KB from the explicitly interrupted run). `decision.md` §4's "unconfigure always runs" **overstates**. |
| F-5 | low | Unit-test comments misstate 4 of 7 case lengths (real: **174, 154, 119, 84, 82, 360, 78**); the **86/87 boundary pair is unpinned** (nearest cases are 84 and 119). All 7 outcomes match their expectations (0 mismatches) — a pinning-quality defect, not a wrong test. |
| F-6 | info | `commands.json` contains **no argv/cwd** (real argv lives in each `summary-placement.json`); `handoff.json`'s "2/7 deep-relocated child passes" does not match `evidence_index.json` (**12 runs / 3 passes**). Narrative only. |
| F-7 | info | `after/external-summaries/RED-short-control-attempt1-band.json` carries a mixed row (rc=1 with signature `pass`); already disclosed in `open_questions`; raw attempt-1 capture preserved and verified (`assert 3 == 2` restart band, not a path error). |
| **CF-I14F-X1 (for I-14-E)** | **actionable** | A `timeout15s-band` label **alone cannot discriminate load from path causation** for `child_without_runtime` (`reviewer_report.md` §3). In the mutation-disabled deep run the child surfaced as a 15 s launcher timeout, yet artifact-level measurement proved the failure was path-caused (the redirect/events paths at 264–299 chars are unreachable; dir creation succeeded at 247, failed at 253; file creation failed at 264). **Consequence: the I-14-E work must RETAIN basetemp artifacts — today's cleanup design deletes exactly the evidence it will need** (relocated artifacts are removed by design; see F-4). |

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; no production write
authority is granted. Qualification is **test-infrastructure only** (deep-cwd WinError 206
elimination for the two bootstrap worker nodes); no product runtime code changed.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-21.
- Status transition: `review_pending` → `accepted_scoped`.
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`.
- Authority: acceptance was written by an independent reviewer, never by the implementer.
- This pass changed **no** byte of `reviewer_report.md`, `oracle.md`, `decision.md`,
  `changes.diff`, `commands.json`, any `after/` or `before/` evidence capture, or any production
  file. It wrote only `review.md`, `handoff.json`, `evidence/I-14-F/qualification.json`, and the
  stub pre-image copy `before/review-md-preimage/review.md`.

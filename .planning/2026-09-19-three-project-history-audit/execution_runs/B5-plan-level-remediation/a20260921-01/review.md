# B5-plan-level-remediation review.md — VERDICT BACKFILL (the ORIGINAL rejection, transcribed by the bookkeeping executor; the implementer did NOT sign)

Status: **`changes_required`**. The independent review of this attempt produced a REAL
verdict that `handoff.json` never recorded: **NOT ACCEPTED AS-IS — measured core verified /
3 blocking findings**. **There is NO acceptance verdict on this card, and none is invented
here.** This file is pure bookkeeping: it transcribes the verdict the independent reviewer
already wrote in `reviewer_report.md`, adds a condition-disposition map (how each blocking
condition was later closed, by WHICH card or by WHICH owner ruling), and adds a
`superseded_by` pointer to the fix card that carries the line's accepted continuation.

**Explicit statement: this backfill records the original rejection faithfully; it does NOT
upgrade it.** `verdict_is_transcribed_not_authored: true`. This file is not a signature, adds
no acceptance of its own, and no byte of the reviewer's carrier was changed.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); it was
created by this verdict-backfill pass — not by the implementer and not by the reviewer.

---

## Verdict block (transcribed)

- Card: **B5-plan-level-remediation** (handoff `card: B5+B6` — REM-21 cross-batch runner
  propagation + REM-22 rc code table freeze)
- Attempt: `a20260921-01` (`<PLAN>\execution_runs\B5-plan-level-remediation\a20260921-01`)
- Verdict: **`changes_required`** — the reviewer's literal wording, `reviewer_report.md`
  **line 13**:

  ```
  **NOT ACCEPTED AS-IS — "measured core verified / 3 blocking findings".**
  ```

- Verdict author: an **independent reviewer** (explicitly "not the implementer, not the
  orchestrator", report lines 3 and 278-282: "I did not self-sign: this card remains
  `review_pending`").
- Line 15 (verbatim): `Returned to the implementer (not self-signed; this card stays review_pending).`
  — the reviewer deliberately left the machine status field at `review_pending` and wrote the
  verdict only in prose. The status was therefore never recorded in `handoff.json`. This
  backfill records the verdict as `changes_required` (the machine-readable equivalent of
  NOT ACCEPTED AS-IS) and retains `status_before_bookkeeping_fix = review_pending`.
- Blocking findings, **line 29** (verbatim):

  ```
  **Blocking findings: F-1 (G3 key rename), F-2 (G1/G2 frozen-rule override without owner sign-off), F-3 (`evidence.json` schema divergence on M13-M16).**
  ```

- Measured core verified (§0 verdict table, lines 19-24): REM-22 rc-table freeze **PASS**
  (pure append; prefix byte-identical to the frozen post-image `1bdfbd91…`, 9895 B, 10 frozen
  anchor lines intact); REM-21 four-arm propagation **PASS (measured)** — E=0 / F=3 / G=2
  uniform on all six batches and all 31 cards, arm B genuinely measured (0/2/3 across
  batches); "missing `expected` ⇒ rc=3" falsification **PASS** (reproduced: raw rc=1,
  uncaught `KeyError`, zero files written); ValueError decoy **PASS**; boundaries **PASS**
  (68/68 historical runner copies, 31/31 frozen `cases.json`, 37323/37323 historical files
  untouched, production `scripts\` untouched); both premise corrections confirmed
  (`5307d2cc…` on no file; M09-M12/M21-M24 already gated).
- The three adjudications behind the blocking set: **G1** (line 153) "the *deviation* is
  FORCED; the implementer's particular resolution is NOT the only compliant one, and it must
  not be accepted without owner sign-off"; **G2** (line 180) "there is NO fully compliant
  resolution that satisfies all three constraints; register the conflict as an owner item, and
  do NOT edit the frozen file"; **G3** (line 196) "CONFIRMED, and it is BLOCKING. Emit both
  keys."
- Note, transcribed as-is and NOT adjudicated here: line 29 lists **F-3** among the three
  blocking findings, while the §3 findings table (line 237) marks F-3's severity as "minor".
  Both wordings are retained verbatim; this backfill resolves neither.
- **No acceptance language exists anywhere in the carrier**; `accepted*` appears nowhere in
  this verdict. `verdict_is_transcribed_not_authored: true`.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256 (whole file, recomputed at landing time) | `0324bfdcc2eb6443693419a9e718b241b25c6c290ff12abb5fb96de0b6d2eee0` |
| bytes | 34764 |
| lines | 307 (UTF-8 without BOM, LF-only, single trailing LF) |
| verdict line | 13 |
| verdict line text | `**NOT ACCEPTED AS-IS — "measured core verified / 3 blocking findings".**` |
| verdict-line byte region | bytes 590..663 inclusive (74 B, without the LF), sha256 `3488d12a6d6429a8c477563cb2350b83b81f511e53a8f1a3331878168afad9b4` |
| "returned to implementer" line | 15 (bytes 665..744 inclusive, 80 B, sha256 `b684c7f3751769209bb4bf12b3e498d0f3c26b27a94cbfc41d742b0be1cef25b`) |
| blocking-findings line | 29 (bytes 3102..3253 inclusive, 152 B, sha256 `510cc0e5325426a5caf22a504df865b7211a45c4574a81d4796f6d200e9e124f`) |
| VERDICT section (§0) | lines 11-29 |
| adjudications (§2) | G1 lines 149-176; G2 lines 178-192; G3 lines 194-212; G4 lines 214-228 |
| findings section (§3) | lines 231-242 (table rows F-1..F-8 at 235-242) |
| required-before-acceptance (§5) | lines 268-274 |
| reviewer independence statement (§6) | lines 278-282 |
| pin section (§7) | lines 286-307 |
| pin sidecar (`reviewer_report.md.sha256`) | **ABSENT** in this attempt — the pin is the report's own embedded **self-excluding** pin (§7), not a sidecar file |
| embedded pin (payload = every byte before `## 7. Report pin`) | `payload_bytes 34071`, `payload_sha256 600c9e7b71ee201b6c10aab2a2ce79705f9449b96ac4535a02d3310a5c49f27d` — **independently reproduced at landing time (pin OK)** |
| region definition | byte offsets are 0-based against the file as it stands at the recorded sha256; region lengths exclude the terminating LF |
| producer | independent reviewer, not the implementer |

Zero bytes of the carrier were written by this backfill pass: `reviewer_report.md` (and its
embedded pin) was read-only here, as were `before/`, `changes.diff`, `commands.json`,
`decision.md`, `oracle.md`, `PROPAGATION_CONTRACT.md`, `binding.json`, `evidence\` and
`_reviewer_verify\`.

---

## condition disposition

The original verdict stands as issued: **`changes_required` / NOT ACCEPTED AS-IS**. The table
below records, per blocking condition, how the card LINE (not this attempt) subsequently
closed it. Closing a condition does not retro-accept this attempt; this attempt's status
remains the faithful rejection.

| condition | original finding (this report) | disposition | carrier / authority |
|---|---|---|---|
| **G1** (M25-M28 whole-set `case_contract` gate split; F-2's G1 half) | FORCED deviation, implementer's resolution not the only one, owner sign-off required (line 153; options G1-a/G1-b at lines 173-174) | **closed by FIXCARD** — implemented the reviewer's preferred **G1-a routing** (structural rc=1 unchanged / declaration unusable → rc=2 + `no_verdict` decided before judging / usable-but-different → rc=3), accepted by the fix card's independent review | FIXCARD `B5-fix-g1a-g3\a20260922-01`, status `accepted_scoped`, carrier `reviewer_report.md` sha256 `69ea3b033d2278977b6956b953e1f9113dc45c0ee5da0fd72fa4e8a81620130e` (16710 B, sidecar `reviewer_report.md.sha256`); measurement: **G1-a routing measured over 128 raw-rc child processes** (`_scratch/arms_raw.json`; `commands.json` = "all 128 arm units with real raw rc"), reviewer's own fresh M25-M28 re-run 20/20 raw rcs match (E=0, F=3, G=2 `no_verdict`, S=1, B=1) |
| **G3** (M13-M16 key rename; F-1) | "CONFIRMED, and it is BLOCKING. Emit both keys." (line 196); breaks `M14\...\recovery\consolidated_report.py:75` | **closed by FIXCARD** — patched runner emits **both keys** (`declared_expectations` + `declared_expectations_in_cases_json`, same value) | FIXCARD `handoff.json` `g3_both_keys` + `evidence/g3_reader_proof.json` sha256 `3aba66d14042386ebdeb6de73d7713e2435fecb1bbeba3255cf50362e368968e`, `PASS=true`, **3-leg reader proof**: (1) frozen baseline `run_result.json` → OK `["ModelRegistryError"]`; (2) B5's patched output → **`KeyError: 'declared_expectations'`** (the original break, reproduced); (3) fix card's fresh patched output → OK, both keys present and equal. The fix reviewer re-executed leg extraction independently (`reviewer_report.md` §2) |
| **G2** (anchor conflict inside a frozen artifact; F-2's G2 half) | "register the conflict as an owner item, and do NOT edit the frozen file" (line 180) | **owner ruled 留置 — closure-by-RULING, not a fix.** The conflict stays permanently registered; **no precedence is asserted** between the frozen `case_contract.rule` text and the frozen rc table | `OWNER_DECISIONS.md` **§16** (line 374): `**D-G2 = 留置** | 冲突**永久留置登记**，owner **不裁定**哪个冻结件优先`, from the owner's verbatim line 365 `D-G2: 留置/（或给取舍）`; mirrored in FIXCARD `handoff.json` `g2_conflict_record` (`status: "known conflict - owner ruling 留置 (permanently registered; unresolved by design)"`, `no_precedence_asserted: true`, `precedence_claim_made_anywhere: false`) and FIXCARD `decision.md` D-F3 |
| F-3 (`evidence.json` schema divergence on M13-M16) | listed as blocking at line 29; severity "minor" in the §3 table (line 237) | closed by FIXCARD — all six batches' `evidence.json` `arms.{E,F,B,G}` rebuilt from real runs, no nulls (FIXCARD `findings_dispositions["F-3"]`), verified by the fix reviewer (§4) | FIXCARD `reviewer_report.md` sha256 `69ea3b03…` |
| F-4 / F-5 / F-6 / F-7 | minor / informational in §3 | registered or fixed by the FIXCARD (`findings_dispositions`), F-8 explicitly out of the fix card's scope (CF-B5FIX-3) | FIXCARD `handoff.json` |

Residual after all dispositions: **G2 stays OPEN by owner ruling (留置)** — registered, not
resolved, and deliberately so.

---

## superseded_by

The accepted continuation of this card's line is the fix card (which, unlike this attempt,
carries the acceptance):

- **`<PLAN>\execution_runs\B5-fix-g1a-g3\a20260922-01`** (card `B5-fix-g1a-g3`)
- fix-card status: **`accepted_scoped`** + **landed** (`handoff.json` `status: "accepted_scoped"`,
  sha256 `b071ff9b85a8551a69544fca7ac380a4c853f3b587d9e05fa184eaf3681db548`) — that value
  belongs to the FIX CARD, never to this card.
- accepted carrier: `reviewer_report.md` sha256
  **`69ea3b033d2278977b6956b953e1f9113dc45c0ee5da0fd72fa4e8a81620130e`** (16710 B; pin sidecar
  `reviewer_report.md.sha256`, sidecar sha256 `f15f60eaf40f8a9b857563e8564a0657cd88fd43528a34c7a94ba4938ec73a0b`)
- its landing registered carried findings **CF-B5FIX-1 / CF-B5FIX-2 / CF-B5FIX-3**
  (`handoff.json` `carried_findings`), including the external STALE-SUPERSEDED erratum against
  THIS attempt's sealed `binding.json` record (do-not-edit disposition: this attempt's stale
  record stays stale).

`superseded_by` means: for the card LINE's forward state, read the fix card. It does **not**
mean this attempt's verdict changed. This attempt stays `changes_required`.

---

## Not granted / declarations

- `disclosure_adaptation` = **unmapped**; `accuracy` = **unproven** (neither is addressed,
  improved, or claimed by this backfill).
- **No `accepted_scoped` is written anywhere for this card** — the fix card carries the
  acceptance; this card carries the faithful rejection plus the disposition map.
- Production is READ-ONLY; zero production bytes written, zero git writes, no historical or
  frozen artifact touched, `before/`, `changes.diff` and the 34764-byte `reviewer_report.md`
  untouched.
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`; the executor of
  this backfill authored no verdict.

---

## Bookkeeping

- Landed by: verdict-backfill bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → **`changes_required`** — a transcription of the
  reviewer's already-written NOT ACCEPTED AS-IS verdict (line 13), performed on the parent's
  dispatch. Not an acceptance; not authored here.
- Files written (exactly three, all inside this attempt): `review.md` (created, this file),
  `handoff.json` (status + appended bookkeeping fields; pre-existing content otherwise
  untouched), `evidence/B5-plan-level-remediation/qualification.json` (created).
- Files NOT written: `reviewer_report.md` and its embedded pin, `before/`, `changes.diff`,
  `commands.json`, `decision.md`, `oracle.md`, `PROPAGATION_CONTRACT.md`, `binding.json`,
  everything under `evidence\` as it stood, `_reviewer_verify\`, `_scratch\`, all `M**` batch
  directories, the FIXCARD, production, git.

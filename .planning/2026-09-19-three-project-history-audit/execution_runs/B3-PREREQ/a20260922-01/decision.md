# B3-PREREQ (a20260922-01) — Decision

Card: close the three promotion-prerequisite findings **REM-47 / REM-48 / REM-49** from B3's
ACCEPT review (register rows map them to review findings **RF-1 / RF-5 / CF-1**), so B3's iso
fix (`7D1BD8F9…`) can later be promoted as batch 2. `oracle.md` was frozen before any run
(one pre-run amendment, recorded in the oracle itself).

Per-finding status: **F1 = fixed, F2 = fixed, F3 = fixed.** Details and rejected alternatives
below.

---

## D0 — finding verification first (the brief's premises vs B3's report)

| brief premise | what B3's report actually says | action |
|---|---|---|
| F1: conftest guard + provenance | **RF-1** (§5): prepend order inverted; `find_spec_origin` computed but never checked; `module_provenance.json` last-writer-wins delivering PRODUCTION bytes | verified against `iso/conftest.py:36-40,66-84` and the delivered `scratch/module_provenance.json` (reports `225FECDD…`/19364) — premise **correct**, fixed |
| F2: "B3's `decision.md` says every hash compared" | **RF-5** (§5): the claim is in **`handoff.json:188`** (`frozen_artifacts_untouched.verification`), *not* in `decision.md` | `decision.md` grepped: **0 matches** — nothing to correct there (**that sub-premise is already-closed / not present**). The real carrier `handoff.json:188` corrected — fixed |
| F3: `source_preparation.py:134-138` comment double-error | **CF-1 / §4**: "doubly wrong … producer_events is neither a downstream DAG closure nor 'of the non-reusable roles' — it is the ancestor-closure of the *requested* roles" | verified verbatim against the file; reviewer also warned promotion-while-standing **rebuilds the REM-13 defect class** — premise **correct**, fixed |

## D1 — REM-47: how the guard and the provenance record must work

**Choice**: (a) apply the path order as ONE prefix assignment `sys.path[:0] = PATH_ORDER` so the
tuple's stated order is the actual order (fixed copy first in `B3_BYTES=fixed` mode,
production-first in `B3_BYTES=production` mode); (b) make `pytest_collection` compare the
resolved `find_spec_origin` against the mode's expected origin (and, in fixed mode, that
`sys.path[0]` really is the fixed copy) — i.e. check what the docstring claims; (c) write
`scratch/module_provenance.json` through `record_module_provenance()`: merge, flag
`conflict=true` on differing bytes, keep the FIRST write as the reported value, retain every
write under `writes`.

**Why**: RF-1 showed B3's per-entry `insert(0)` loop reverses its own tuple (production ends up
ahead of the fixed copy), the guard only asserted "fixed dir on sys.path", and the provenance
file — cited by `handoff.json` as binding proof — reported production bytes because the last
conftest-loaded run was the production control.

**Rejected alternatives**:
1. *Fix only the docstring (delete the guard claim) and drop the provenance file from
   `evidence_paths`* (reviewer's option (b)). Rejected: the card's premise is to fix the
   mechanism, and a weaker-but-honest guard still cannot tell a reviewer which bytes ran.
2. *Raise in `pytest_sessionfinish` on conflict (hard "refuse")*. Rejected: it would fail
   unrelated sessions at teardown and destroy the ability to *record* the conflict; flagging +
   first-writer retention + full `writes` history refuses the silent overwrite while keeping
   the evidence. The property test pins this behaviour in both write orders.
3. *Mode-blind always-fixed-first prepend*. Rejected: it would make B3's legitimate
   `B3_BYTES=production` control runs fail the new origin check; mode-aware ordering keeps
   "docstring = reality" true in both modes.

**C2 (explicit non-claim, per the reviewer)**: this fixed guard is a runtime binding check for
*this attempt's* suites. It is **NOT** the REM-12 prevention mechanism and must never be
presented as "the mechanism that prevents REM-12 recurring". Recorded in the conftest module
docstring, in this file, and in `handoff.json`. The operative REM-12 proof remains the in-test
explicit binding + hash assertions inside the carriers.

## D2 — REM-48: how to resolve the record contradiction

**Choice**: correct `handoff.json:188` in place, replacing the false "compares every frozen
hash … all matched" with the counted truth — `after/integrity.json` **records 4**
`expected_frozen` entries; **3** were compared and matched; **1** (`I-05-C:oracle.md`) carries
the literal `NOT_REHASHED` and was never re-hashed by the attempt (flag at
`after/integrity.json:23`; reviewer independently re-hashed it as `E4004563…`, matching,
git-clean since `8b7229c3`) — and retain the superseded wording + pre-edit file
(`evidence/rem48_superseded/handoff.json.pre-correction`, sha `CEE4B0DD…`).

**Why in place rather than append-only**: append-only applies to *frozen carriers*
(`before/**`, `oracle.md`, the I-05-B/I-05-C frozen attempts). `handoff.json` is an attempt
deliverable record, not a frozen carrier, so the "correct with superseded retention" branch
applies. The flag itself is **not** deleted — a post-correction recount still finds it
(`evidence/rem48_verification.txt`), and the corrected sentence explicitly cites it.

**Rejected alternative**: *edit `after/integrity.json` to fill in the missing hash*. Rejected:
that would rewrite recorded run output after the fact — the exact inversion the protocol
forbids; the reviewer's independent re-hash is cited instead.

**Scope note**: the correction is the attempt's **only** write outside its own directory
(git shows exactly ` M …/a20260921-01/handoff.json`). No status/verdict field of B3's handoff
was touched; this attempt never signs anything.

## D3 — REM-49: comment wording and behaviour-delta proof

**Choice**: comment-only edit in `iso/fixed2/rf_scripts/source_preparation.py` (a copy; B3's
accepted bytes untouched) using the reviewer's verbatim suggested wording:
`producer_events = requested missing roles + their non-reusable ancestors` (matches the
implementation docstring at `company_wiki_source.py:174-175`).

**Pre-run amendment (recorded in oracle.md before any execution)**: the oracle's first draft
paraphrased this as "requested roles + their ANCESTOR closure"; that paraphrase drops
"missing"/"non-reusable" and would itself overstate the implemented rule — the accuracy class
REM-49 is about — so the exact reviewer wording was pinned before any run and `oracle.sha256`
recomputed.

**Proof of zero behaviour delta** (all green, `evidence/rem49_comment_fix_GREEN.txt`):
byte diff touches only comment lines; `ast.dump` identical; `tokenize` stream identical
outside COMMENT tokens; `py_compile` succeeds on both; and the relevant suite — FC-904, which
binds and executes the live `source_preparation.py` — gives **identical per-node results**
baseline vs fixed2 (`15 passed / 1 failed` on both sides; `evidence/rem49_fc904_parity.json`,
`per_node_identical=true`).

**The one failing FC-904 node (both runs, declared in advance)**: RF-3's location-dependent
assertion `test_fc904_artifact_selection.py:379` (`"B3-I05C-delivery-fixes" in str(resolved)`).
This attempt relocates the carrier, so it fails **identically before and after** — RF-3 is P4
and not in this card's scope. It was deliberately NOT edited (editing a carrier assertion to
make a run green is out of scope and would taint the accepted payload).

**Rejected alternative**: *stage the runs under a directory literally named
`B3-I05C-delivery-fixes` so the path probe passes*. Rejected: that games RF-3's probe instead
of reporting it.

## D4 — scope decisions

- The fix lives in **`iso/fixed2/`** + this attempt's `iso/conftest.py`; B3's accepted
  `iso/fixed/**` was copied first and never mutated (21/21 baseline files hash-identical
  throughout, `evidence/tree_integrity.txt`).
- **No product change outside `iso/`**: production RF/CW are git-clean at their pins
  (`evidence/production_readonly_check.txt`); no git write was performed; frozen `before/`
  material untouched; REM-49 is deliberately NOT landed in production (production
  `source_preparation.py` still equals the B3 accepted copy, `37A3EEAE…`).
- B3's W05B/W05C vendored suites were **not** re-run: this card's changes are the conftest,
  one comment, and one record line — none of them is an input to those suites' bindings, and
  B3's reviewer already reproduced them (35/16/23). Recorded as a bounded gap in
  `handoff.json`.
- Mutation discipline: 3 mutations, each restored and hash-verified; two superseded mutation
  attempts (encoding artifact, patch-string SyntaxError) are listed honestly in
  `commands.json` — the authoritative RED evidence is the re-run of each.

## Boundaries (restated)

Production read-only; no git writes; frozen `before/` untouched; never self-sign
(`handoff.status = review_pending`); `disclosure_adaptation = unmapped`; `accuracy = unproven`;
promotion of `7D1BD8F9…` (now `91A6DC32…` for the SP comment line only) remains a separate
owner decision, not taken here.

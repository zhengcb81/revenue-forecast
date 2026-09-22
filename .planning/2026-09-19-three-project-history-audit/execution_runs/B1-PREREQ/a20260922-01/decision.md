# B1-PREREQ a20260922-01 — decision record

- Card: **B1-PREREQ — close REM-40…44 (B1 review F1–F5), promotion prerequisites**
- Attempt: `execution_runs/B1-PREREQ/a20260922-01`
- Status written here: work product of a delegated prereq session — **does NOT
  self-sign accepted**; `handoff.json.status = review_pending`.
- Boundaries observed: production READ-ONLY (re-verified, `git status
  --porcelain --untracked-files=all -- scripts tests config artifacts` EMPTY);
  **zero** writes to `iso/fixed/rf/**`, `iso/rf/**`; B1's frozen `before/` and
  every B1 carrier file untouched; the **only** write into B1's attempt is the
  append-only `oracle.md` Revisions r5+r6 this card was commissioned to make;
  no git write of any kind; frozen `before/` untouched.

---

## D-1 (F1/F2 placement) — the corrections go into B1's OWN oracle, by append

The card allowed either (a) append-only corrections in SRC's `oracle.md`
(`CORRECTION n` form + prefix proofs) or, if SRC's oracle is not
append-revisable per its own rules, (b) corrections in this attempt's oracle
with cross-reference pins — "prefer whichever SRC's own conventions dictate".

**Chosen: (a), in SRC's own convention (`## Revision r5`, `## Revision r6`).**
Reason: SRC `oracle.md` §9 *is* the governing rule and it explicitly permits
append-only revision — "Any revision must be appended under a clearly labelled
`## Revision rN` heading with the reason, and the r1 byte range must remain
byte-untouched with a hash proof" — and it does not restrict *who* may append.
The independent reviewer independently prescribed exactly this ("append oracle
revision r5", report §9.1). SRC's convention (`Revision rN`, not
`CORRECTION n`) wins per the card's preference clause. Cross-reference pins to
the pre-append bytes (39287 B / `fadf8a5e…`) are in `freeze.json` entries
`src_oracle_pre_r5` (prefix-pinned) and `snap_oracle_pre_r5_copy` (byte copy),
and in `changes.diff` §1 (pre → post diff).

## D-2 (F2 node placement) — the node lives HERE, B1's frozen test file stays pinned

B1's reviewer suggested folding the node into "the card's test file". This
card does **not** edit `SRC/test_b1_rem.py`: that file is hash-pinned in B1's
own `binding.json`/`after/frozen_artifacts_r3.json` (`636b43c8…`) and in this
attempt's `freeze.json` (`src_frozen_test_12node`), and rewriting a frozen
proof set to grow it would invalidate every pin that makes the 12-node result
auditable. Instead `test_r13_equiv_rem41.py` (this attempt, frozen pre-run)
**imports the frozen file's own fixtures/helpers**, so the new arms run on the
identical setup, and SRC `oracle.md` Revision r6 points at the new node. Net
proof surface: 14 nodes, all pins intact.

## D-3 (freeze history, disclosed) — three pre-execution freeze builds, one final

`freeze.json` on disk is the **final** build, chain head
`8f3d35ccaf503cb918a9b5881f3f401212f7920b1869457677b771bab82d9b4b`, 24
entries. Two earlier builds were superseded **before any pytest/probe
execution**, for disclosed reasons: build 1 (head `e177d719…`) was rebuilt
when the evidence capture method was finalized to raw `cmd /c` byte
redirection; build 2 (head `eb90c1a0…`) was rebuilt after `runner/run_arm.ps1`
was made encoding-independent (`$PSScriptRoot`; the harness shell reads `.ps1`
files with the ANSI codepage, which mangled the hardcoded path and made the
first `arm1` invocation abort **before pytest started** — no evidence label was
consumed). Strict sequencing facts: build 2 preceded the r5/r6 appends and the
M6 patch; build 3 (final) precedes **every** pytest and probe execution. The
expectation-bearing artifacts (oracle.md, node, probe, apply_m6, append tool,
revision texts) were byte-stable across all three builds except `commands.json`
capture *method* fields and `run_arm.ps1` — **expected outcomes never changed**
across builds. `commands.json`'s PR-c0 note ("BEFORE any pytest/probe/append/
mutation step") is accurate for pytest/probe and one step too strong for the
append/mutation pair; that wording is frozen (editing it post-run would break
the very chain it describes), so the correction is recorded **here**. Ordering
claims rest on the hash chain, never on mtimes (F5).

---

## F1 / REM-40 — **FIXED** (append-only SRC oracle Revision r5)

- Correction text frozen in this attempt (`freeze.json`
  `my_oracle_revision_r5`, 4010 B) **before** it was appended.
- Appended: marker `## Revision r5` at byte **39288 = 39287 + 1** (pure suffix
  append; r1–r4 bytes untouched).
- Proof: `scratch/append_oracle_r5.stdout.json` + raw
  `evidence/append_r5.*` — `frozen_prefix_untouched: true`; post-r5 oracle =
  43298 B / `910ca4a8109b28afb739f4a7463dbf26e13fe85c296e115d806768bcb3bd3231`;
  prefix hashes re-checked: 27697→`81af1240…`, 31081→`60ecbca7…`,
  35840→`231e7976…`, 39287→`fadf8a5e…` all match.
- The corrected truth (executed set = **10 fields**, no `result_sha256`) was
  re-measured three independent ways, all in evidence:
  static AST of `PUBLICATION_ATTESTATION_FIELDS` (exactly the 10);
  static AST of the frozen test's `ATTESTATION_FIELDS` (same 10);
  **runtime** `record_field_count = 10` from a real handshake in
  `evidence/probe_e21.stdout.txt` (`setup.record_fields`).
- Why r3's "11" was wrong is stated in the revision itself (r3 removed
  `receipt_sha256` but not `result_sha256`, although its own fixpoint reason
  covers both; the request pins `result_sha256` to the sentinel instead).

## F2 / REM-41 — **FIXED** (node + M6 into the table; arms measured)

- **Node frozen before running**: `test_r13_equiv_rem41.py` pinned in
  `freeze.json` (`my_node_r13_equiv_rem41`); expectations for all four arms
  pre-registered in this attempt's `oracle.md` §3.2; the M6 mutation bytes
  themselves frozen verbatim there and enforced by `apply_m6.py`'s pre-hash
  assertion.
- **M6 into the table**: SRC `oracle.md` Revision r6 (marker at
  `43299 = 43298 + 1`), appending the M6 row to §5's lineage with declared red
  sets, plus the node pointer. Proof `scratch/append_oracle_r6.stdout.json` +
  `evidence/append_r6.*`: `frozen_prefix_untouched: true`; post-r6 oracle =
  47538 B / `a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d`.
- **Mutant**: attempt-local copy of `iso/fixed/rf`; patch applied only after
  asserting pre-hash `bc2bb4a3…`; post-hash
  `ffc782ac77caf83995373659d69b157ed7c1b146d223fc2987428bcff83c2ab4`;
  `scratch/mutations/m6_delta_proof.json`: 197 vs 197 files, **exactly one**
  changed (`scripts/revenue_publication.py`), none added/removed.
  (Line-ending note: my mutant keeps the fixed tree's LF bytes; the reviewer's
  M6 copy was CRLF-converted (25588 B) — same 3-line semantic mutation,
  different EOL, both attempt-local.)
- **Arms (raw bytes in `evidence/`, write-once):**

| arm | expected (frozen) | observed | verdict |
|---|---|---|---|
| arm1 node @ `iso/fixed` | 2 passed, rc 0 | **2 passed, rc 0** | ✅ as frozen (GREEN) |
| arm2 node @ M6 | 1 failed + 1 passed, rc 1 | **1 failed (`DID NOT RAISE ForecastInputError`) + 1 passed (control), rc 1** | ✅ as frozen (RED on the M6 gate, control GREEN) |
| arm3 frozen-12 @ M6 | 12 passed, rc 0 (`{}`==`{}`) | **12 passed, rc 0** | ✅ as frozen — blind spot re-measured, now declared |
| arm4 node @ `iso/rf` | 1 failed + 1 passed, rc 1 | **2 failed, rc 1** | ⚠️ node(a) as frozen (structural RED: no record exists); **control deviated** — see below |

- **Arm4 control deviation (disclosed, not re-run):** the positive control
  asserts `isinstance(_record_of(ok), dict)` — a fixed-tree property. On the
  unfixed tree the REM-01 defect itself means `host_signed` carries **no**
  record, so after the label flip `_record_of` is `None` and the control fails.
  This is a test-strength defect in my control for the *bonus* arm (same class
  as B1's r2), discovered by the run. Corrected expectation: **arm4 = node RED
  (structural) + control RED (record absent), rc 1.** It is recorded here
  rather than appended to this attempt's `oracle.md` because that oracle is
  byte-frozen at `freeze.json` and full-chain re-verifiability (F5) outranks an
  in-oracle correction of a bonus arm; the raw arm4 evidence is preserved
  unedited, the node was NOT re-run or edited (its freeze pin stands), and the
  control's intended job is demonstrated where it matters — arm2: node RED +
  control GREEN side by side. Nothing in the REM-41 evidence (arms 1–3) is
  affected.
- Declared vs observed red sets, 14-node surface under M6: declared
  `{test_rem41_a…}` = observed `{test_rem41_a…}` (frozen-12 contributes `{}`);
  isolation holds exactly as r6 requires.

## F3 / REM-42 — **FIXED as documented-not-bindable-here** (no silent drop)

Measured (`evidence/probe_e21.stdout.txt`, rc 0, executed against `iso/fixed/rf`
with source hashes printed at run time):

- **Q1:** `_trusted_signer_public_keys()` returns `dict[str, bytes]`
  (32-hex fingerprint → raw Ed25519 key); `issuer_present_in_loader_output:
  false`, `key_id_present_in_loader_output: false` — while the trust **file**
  entry does carry `issuer`/`key_id`
  (`trust_file_entry_keys: [fingerprint, issuer, key_id, name, public_key]`).
  **The identity bytes exist on disk but the loader drops them: an E21
  comparison has nothing to read.**
- **Q2:** `record["issuer"] := "revenue-forecast/evil"` with all self-hashes
  recomputed ⇒ `validate_publication_receipt` **ACCEPTED** *and*
  `validate_forecast_output` **ACCEPTED**; `record["key_id"] := "evil-key-id"`
  ⇒ **ACCEPTED**; negative control (corrupt signature) ⇒ **REJECTED**
  (`attestation_signature_invalid … (E14)`) — so the probe does exercise
  verification, and F3's measurement reproduces with a control the original
  finding lacked.

**Why it cannot be bound HERE (all three are product changes, forbidden by
this card):**

1. **Loader must expose identity:** `scripts/contracts/evidence.py:242-267`
   maps fingerprint→key bytes only. Binding needs a per-fingerprint
   `{issuer, key_id}` (or the I-08-A 12-field entry object) returned — an
   edit to a READ-ONLY product file.
2. **A comparison site must exist:** issuance-side, in
   `revenue_core._validate_attestation_response` (E21 is defined as a
   provider-handshake code in the oracle's code table: response `issuer`/`key_id`
   vs the resolved trust entry); consumption-side, in
   `revenue_publication.validate_publication_attestation` (record
   `issuer`/`key_id` vs the trust entry the fingerprint resolved to). Neither
   comparison exists; writing either is an edit to READ-ONLY product files.
3. **Trust entries with identity must actually exist:** the fixture's entries
   carry `issuer`/`key_id`, but the production anchor
   `config/trusted_signer_public_keys.json` is **ABSENT by design** (I-08-A
   R-PROV-2: adding one is a capability grant, not a fix), and the I-08-A
   12-field entry schema + fail-loud loading (E25) are declared NOT closed in
   SRC oracle §7.3. No real entry exists for #1/#2 to compare against.

**What would bind it (for the owner's follow-up card):** (i) extend the loader
return to carry `issuer`/`key_id` (or full entries) per fingerprint with a
versioned schema; (ii) raise `E21 issuer_key_binding_mismatch` at BOTH sites
in #2 when the comparison fails (fail-closed on entry-missing = today's
zero-trust default); (iii) ship an actual trust anchor whose entries carry the
identity triple — an explicit owner capability decision. Until all three
exist, E21 remains documented-but-unraised and `issuer`/`key_id` remain
unbound labels whose forgery is limited to *rename-by-a-key-holder* (the label
itself still cannot be forged: fingerprint trust-domain + Ed25519 both hold —
arm/probe Q2 negative control). Disposition: **closed for this card as a
documented, evidenced, non-silent finding; the binding work itself is a
product card, deliberately not performed here.**

**Related measurement (F6 cross-check, pre-registered both readings):**
arbitrary `result_sha256 := "ab"*32` ⇒ receipt layer **ACCEPTED** (nothing
there checks it) but `validate_forecast_output` **REJECTED**
(`forecast result hash mismatch`), restored value ⇒ both ACCEPTED. This
**diverges from review F6's "both ACCEPTED" sentence** for the arbitrary
rewrite — the code reading I pre-registered won: the strong consumer does pin
`result_sha256 == canonical(everything-but-itself)`
(`revenue_report.py:507-509,343-347`). What remains true and unchanged:
the **record/attestation layer** can never bind the live result digest
(sentinel fixpoint — `record` has no `result_sha256` field, confirmed at
runtime: 10 fields). Logged for the reviewer; F6's "no action required"
disposition is unaffected, but its ACCEPTED/ACCEPTED claim should be read as
receipt-layer-only. Not silently dropped: raw bytes in `evidence/probe_e21.*`.

## F4 / REM-43 — **FIXED (protocol established) + historical gap DISCLOSED as unclosable**

- Protocol frozen before any run (this attempt's `oracle.md` §3.4,
  `evidence/README.md`, enforced by `runner/run_arm.ps1`):
  every new RED/GREEN arm keeps raw stdout/stderr/rc byte-for-byte under
  `evidence/<label>.*` via raw `cmd /c` redirection; **labels are write-once**
  (collision → exit 99); re-runs need a new label and a disclosure;
  `evidence/SHA256SUMS.txt` pins every byte stream.
- Labels used: `arm1_node_on_fixed`, `arm2_node_on_m6`, `arm3_frozen12_on_m6`,
  `arm4_node_on_unfixed`, `probe_e21`, `append_r5`, `append_r6`, `m6_build`,
  `final_integrity_check`, `final_integrity_check_v2`. Disclosures:
  (a) `final_integrity_check` (the frozen tool) burned its label on a tool
  defect (`ast.literal_eval` on a `frozenset(...)` call node) — rc 1 +
  traceback preserved verbatim; successor ran under the NEW label
  `final_integrity_check_v2` (14/14 checks ok, rc 0) with the defect class
  fixed and everything else identical — never an overwrite;
  (b) arm4 was **not** re-run after its deviation (write-once + see F2).
- **Unclosable historical gap (not claimed closed):** B1's r1 RED stdout
  ("10 failed / 2 passed" — the warrant for oracle r2) and the r1 test file
  (18236 B / `e6c0949c…`) were overwritten/removed before archiving and cannot
  be recreated by this or any later card. The surviving
  `before/b1_unfixed.stdout.txt` (30580 B / `58863ffb…`, pinned in
  `freeze.json`) is the final 11/1 output, not r1's. Recorded here, in
  `oracle.md` §3.4/§4, `handoff.json`, and the register row it closes — REM-43
  closes as *protocol + disclosure*, explicitly leaving the historical loss
  open.

## F5 / REM-44 — **FIXED** (hash-pin freeze with ordering chain; mtime order demoted)

- `freeze.json`: 24 entries; each `{seq,id,path,bytes,sha256,role,
  prev_entry_sha256,entry_sha256}` where each entry commits to the previous
  entry's canonical JSON (genesis prev = 64 zeros) — **ordering is derivable
  from hashes alone**; timestamps are present but declared non-normative.
  Chain head `8f3d35ccaf503cb918a9b5881f3f401212f7920b1869457677b771bab82d9b4b`.
- The chain covers every expectation-bearing artifact of this attempt plus the
  SRC pins (oracle pre-append by prefix, report, frozen 12-node file, the four
  fixed-tree product files, the two `before/` artifacts), and it **re-verifies
  end-to-end** after all runs (`evidence/final_integrity_check_v2.stdout.txt`,
  check `freeze_chain_verifies: ok=true`).
- Unlike B1's freeze, `decision.md`'s own hash is pinned at write-completion by
  `binding.json` (no "recorded elsewhere after the final edit" gap), and the
  policy statement required by the finding is frozen in this attempt's
  `oracle.md` §3.5: **future proofs in the B1 line must use hash-pin order;
  mtime or "written-before" prose alone is no longer accepted as ordering
  evidence.**

---

## Not done here (unchanged scope)

- Promotion of `iso/fixed/rf/scripts/**` (batch 2) — separate owner decision.
- E21 implementation (product change — see F3 disposition).
- Re-creating the r1 RED stdout (impossible — disclosed).
- F7/REM-02's (a)/(b)/(c) caller-trap decision — not one of the five findings;
  stays with its owner.
- I-08-C's verdict, the invest-core consumer, I-08-A's full provider protocol —
  out of scope exactly as SRC oracle §7 states.

---

## r2 — record-only correction round (reviewer verdict `changes_required`; findings F-REV-B1P-01…05)

**Round scope.** Reviewer report `reviewer_report.md` (25883 B, sha256
`e25a2c837009aebf4be542a89cafa13e78a0dae59b3556a7766ae8bb397376f6`), verdict
**changes_required**, blocker F-REV-B1P-01. This round is **record-only**: no
product / iso / production / git write of any kind (git used read-only);
F1/REM-40, F2/REM-41, F3/REM-42, F5/REM-44 were **confirmed** by that review
and are untouched; `handoff.json.status` stays `review_pending`; nothing is
self-signed. Every fact re-measured for this round has raw output under
`evidence/r2/` with its own `evidence/r2/SHA256SUMS_r2.txt` (the r1
`evidence/SHA256SUMS.txt` and all r1 labels stay byte-untouched).

### r2.1 F-REV-B1P-01 (BLOCKER) — the F4 "unclosable r1 stdout" disclosure is retracted and corrected

**Superseded:** the §F4 "Unclosable historical gap" bullet above, this
attempt's frozen `oracle.md` §1/§2/§3.4/§4 F4 text, and
`handoff.json.findings.F4.unclosable_historical_gap` — all of which assert that
the r1 RED stdout was lost and that the surviving file is "the final 11/1
output". `superseded_reason: "refuted by reviewer F-REV-B1P-01 with byte
evidence"`. Nothing is deleted: §F4 above keeps its bytes, the handoff keeps
the original string under a `…__superseded` key, and SRC oracle Revision r7
quotes every false sentence verbatim as superseded.

**Measured independently this round (raw outputs in `evidence/r2/`):**

- `r2_01_b1_unfixed_stdout_facts.json`: `before/b1_unfixed.stdout.txt` =
  **30580 B / `58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335`**,
  UTF-16LE+BOM → **10 `FAILED` / 2 `PASSED`**, summary exactly
  `10 failed, 2 passed in 8.18s`; the string `11 failed, 1 passed` occurs
  nowhere ⇒ **it IS r1's RED stdout** — the warrant for oracle r2 — **not** "the
  final 11/1 output".
- `r2_01b`: failure-block line refs `268, 296, 323, 348, 372, 407, 438, 460`
  — the r1 test file's refs (an r2-era file's last three would sit +6).
- `r2_02*`: exactly **one** commit touches the path — `980c9b7a`
  (2026-09-21 21:16:24); its blob = `HEAD` blob = working bytes = the same
  30580 B / `58863ffb…`, and that is the **only** blob state git ever stored at
  the path; porcelain clean. For `test_b1_rem.py`, reachable content blobs are
  18611 B / `da3d29bf…` (at `980c9b7a`) and 20631 B / `636b43c8…` (HEAD) —
  **no 18236 B / `e6c0949c…` blob is reachable**.
- `r2_03_provenance.json`: stdout mtime 21:15:12; run stderr 21:14:45 (first
  pytest run); r2 warrant `scratch/oracle_revision_r2.md` written 21:15:35;
  B1's sealed `handoff.json:137` = `red_r1 {label before/b1_unfixed, failed 10,
  passed 2}`, `:198` `red_r1_stdout = before/b1_unfixed.stdout.txt`, `:110`
  "The r1 RED stdout is preserved and was NOT overwritten by the r2 run" —
  **the handoff's preservation claim is TRUE.**
- genuine 11/1 outputs: `before/b1_unfixed_r2.stdout.txt` (21:18) and
  `before/b1_unfixed_r3.stdout.txt` (21:56), each "11 failed, 1 passed".

**Corrected disclosure (current truth):** the genuinely lost artifact is ONLY
the **r1 test file — 18236 B / `e6c0949c3b7d0d9c3bad101dc90a62cb8702dc4616715adfc2227dda60aa8f75`**
(absent from the working tree, from every reachable commit, and by size from
the reviewer's 1294 reflog-unreachable blobs — reviewer domain §4.4/§5.3; per
§5.3 other recovery routes were not exhausted). The **r1 RED stdout SURVIVES**
at `before/b1_unfixed.stdout.txt` — byte-pinned, in git, line-refs matching the
r1 test file — and is auditable right now.

**REM-43 re-scope:** protocol half ✅ **closed** (established + evidenced:
write-once labels, raw byte capture, 31-entry manifest recomputed by the
reviewer); historical gap = **r1 test file only**. No "unclosable stdout gap"
claim stands anywhere in this record.

**Where the correction lives:** this `## r2` (F4 section above kept verbatim,
superseded here); `handoff.json.findings.F4` (original retained under
`…__superseded`); SRC `oracle.md` **Revision r7** (append-only under its §9).
This attempt's `oracle.md` stays byte-frozen (freeze entry `my_oracle_md`) —
editing it would destroy the F5 chain, so its §1/§2/§3.4/§4 false text stays
and is neutralised by r7 §R7-2 (verbatim supersession) + this section.

**Location measurement (`r2_06_false_claim_locations.json`, whitespace-
normalized):** the review's location note does not fully reproduce: SRC
`oracle.md` never mentions `b1_unfixed.stdout`/`58863ffb` at all — its R2-4
states the *true* position ("the r1 RED stdout is **not** overwritten"), and
SRC `decision.md`/`handoff.json` state it too. The false sentence actually
lives in exactly: SRC `reviewer_report.md` F4 (sealed origin), this attempt's
frozen `oracle.md` (§1/§2/§3.4/§4), my §F4 above, and my `handoff.json` F4.
Disclosed by measurement.

**Full-carrier addendum (`evidence/r2/r2_14_false_carrier_addendum.json`,
scanning every text file of this attempt):** two further carriers exist —
(1) **`evidence/README.md` lines 5 and 23–30** ("its stdout was overwritten
before archiving" / "is the **final** 11-failed/1-passed output, not r1's" /
"No later card can recreate those bytes"): **freeze-pinned** (entry
`my_evidence_readme`) *and* pinned in `evidence/SHA256SUMS.txt`, so it cannot
be edited without destroying F5 — superseded by this section and SRC oracle
Revision r7, disclosed here; (2) **`recovery/README.md` lines 29–35** (not
freeze-pinned): **corrected in place in r2** with the old wording retained
verbatim under a superseded note (binding pins the r1 bytes `6fe88d7b…` and the
r2 bytes in `r2_rebinding`). `binding.json`'s own `open_disclosures` item and
`changes.diff`'s diff context also echo the old wording; the former is retained
+ superseded inside `binding.json.r2_rebinding`, the latter is a regenerated
artifact. `commands.json` (frozen) carries no such claim.

**SRC oracle Revision r7 (review required-correction #1 + parent commission):**

- before: **47538 B / `a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d`**
  → after: **57911 B / `6e344a208f8fc43992d339693d74c51122b505d17c368a67f5899dbd43a222dc`**
- marker `## Revision r7 …` at **47539 = 47538 + 1**, occurs exactly once;
  dry-run first (`evidence/r2/r2_07_append_r7_dryrun.json`,
  `dry_run_would_pass: true`, no write), then the frozen append tool
  (`scratch/append_oracle_r7.stdout.json`, copied to `evidence/r2/r2_08_…`).
- **four-prefix recompute on the POST-append bytes — `r2_09`: 27697 →
  `81af1240…`, 31081 → `60ecbca7…`, 35840 → `231e7976…`, 39287 → `fadf8a5e…`
  ALL match; additionally 43298 → `910ca4a8…` (post-r5) and 47538 →
  `a8f192f1…` (post-r6 / freeze-time state) match ⇒ r1–r6 pins untouched.**
- boundary re-check with the frozen tool immediately after the append (probe
  still at its pinned bytes): `evidence/r2/r2_11_final_integrity_check_post_r7_prefixefix.json`
  → **rc 0, all 14 checks ok, `freeze_chain_verifies: ok=true`** ⇒ **the r7
  append breaks no F5 check** (the chain's `src_oracle_pre_r5` entry verifies
  by its prefix pin, which r7 preserves).

**Register actions deliberately NOT taken here (owner/parent):** erratum /
annotation for the sealed SRC `reviewer_report.md` F4 refuted sentence in
`REMEDIATION_REGISTER.md` (review required-correction #3); the REM-40…44
closure rows; batch-2 promotion — see §r2.6.

### r2.2 F-REV-B1P-02 (MEDIUM) — F6 wording now carries its procedure domain (REM-79)

Old over-claim (retained verbatim under
`handoff.json.findings.F6.divergence__superseded`; `superseded_reason:
"procedure-mismatched comparison corrected per reviewer F-REV-B1P-02"`):
"F6's 'both ACCEPTED' does not reproduce for the arbitrary rewrite … its claim
should be read receipt-layer-only."

Verified against the probe sources first (`evidence/r2/r2_05_f6_procedure_sources.json`):
this card's probe lines 225–251 = rewrite-only (variant a) + restore-original
control (variant b); SRC `reviewer/scratch/probe_attest.py:225-231` = rewrite
**then** `canonical_sha256({k: v … if k != "result_sha256"})` recompute with the
code comment "a fully-informed attacker recomputes it, so emulate the strongest
real move"; `iso/fixed/.../revenue_report.py:343-347 + 507-509` = `require(
result_sha256 == canonical_sha256(hash_payload))` with `hash_payload` = all
keys except `result_sha256`.

**Replacement wording (required form, recorded verbatim):**

> 本卡探针变体(a)=**不重算**任意改写 ⇒ receipt ACCEPTED / forecast REJECTED（`revenue_report.py:343-347 + 507-509`）；**F6 原测量 = 改写+一致重算**（其原文 "recomputing it consistently"）⇒ both ACCEPTED，**本卡未复测该变体**；不重算者被拒=对 F6 的**附加强化**而非反证。

**Reviewer's explicit ruling registered: NO erratum to B1's F6** — B1 stays
sealed, F6's conclusion and "no action required" disposition stand unchanged.
Optional one-line clarification text (registered HERE for the parent to place
in the plan register; not written into B1's attempt):

> Clarification (not an erratum): an **unrecomputed** arbitrary `result_sha256`
> is accepted at the receipt layer but **rejected** by `validate_forecast_output`
> — a case F6 did not state; the fully-informed (consistently-recomputing)
> attacker case is exactly as F6 described.

### r2.3 F-REV-B1P-03 (LOW) — probe module docstring fixed (record-only; byte history disclosed)

- old line 19: `      (b) full self-consistent recompute of every self-hash chain.`
- new line 19: `      (b) the original value restored — a control, NOT a recompute (oracle §3.3).`
- byte history (`evidence/r2/r2_10_probe_docstring_fix.json`,
  `all_checks_pass: true`): frozen/executed state **10365 B / `5c9f4508…`**
  (= `freeze.json` entry `my_probe_e21`; preserved byte-exact at
  `evidence/r2/probe_e21_binding.py.frozen_pre_r2_5c9f4508.py`) → r2 state
  **10383 B / `5f53f5bbdbb439d5422da354ae6771d4541ebf9afeda716d64f5701a690b22b7`**;
  bytes before/after the old line identical, suffix from `from __future__`
  identical, `no_other_byte_changed: true`, file still parses. The executed
  evidence (`evidence/probe_e21.*`, `SHA256SUMS.txt`) is untouched; no probe
  re-run (reviewer: "no re-run needed").
- **disclosed consequence (the one deliberate freeze-pin divergence of r2):**
  `freeze.json`'s `my_probe_e21` entry pins the old bytes, so the boundary tool
  now reports exactly one mismatch — `evidence/r2/r2_12_final_integrity_check_post_docstring_fix.json`:
  `failures = ["freeze_chain_verifies"]`, detail `my_probe_e21: live 5f53f5bb…
  != 5c9f4508…`; the other 13 checks (production porcelain empty, fixed-tree
  and SRC pins, 10-field checks, runtime record) still pass. Contrast
  `r2_11_…` (same tool, probe at pinned bytes): `all_ok: true`. If the owner
  prefers strict chain re-verification over the docstring fix, the frozen bytes
  are restorable byte-exactly from the preserved copy.

### r2.4 F-REV-B1P-04 (LOW) — ordering-evidence disclosure carried forward (no action)

This attempt's freeze-before-run ordering still rests on mtimes + the D-3
prose: the hash chain proves content integrity and entry order, not that
`freeze.json` existed before the runs (superseded builds 1/2 exist only in
prose). Accepted as disclosed for this attempt; carried explicitly in
`handoff.json.r2.freeze_ordering_disclosure_F_REV_B1P_04`, pointing at the
§3.5 policy that binds **future** freezes (hash-pin / self-timing mechanism).
No action taken in r2, as commissioned.

### r2.5 F-REV-B1P-05 (cosmetic) — `changes.diff` boundary comment corrected

- generator header, old: `# Boundary: … NOT CHANGED (see
  evidence/final_integrity_check.stdout.txt)` — that is the **burned** label
  (empty stdout, rc 1, `ast.literal_eval` traceback);
  new: `… NOT CHANGED (see evidence/final_integrity_check_v2.stdout.txt:
  14/14 ok; r2 re-checks: evidence/r2/r2_11_… all_ok=true, r2_12_… sole
  expected failure = freeze entry my_probe_e21 after the commissioned
  F-REV-B1P-03 docstring fix)`.
- generator header, Section 1 line, old: `append-only Revisions r5 (F1/REM-40)
  + r6 (F2/REM-41); r1-r4 bytes untouched` → new adds `+ r7 (r2 round,
  F-REV-B1P-01 F4 gap re-scope)` and the r5/r6/r7 proof pointers.
- `scratch/make_changes_diff.py` 2961 B / `8167bbfe…` → 3776 B /
  `f7be074e…` (AUTHORED list also gains the r7 revision text + the five r2
  record tools); `changes.diff` regenerated by that script afterwards
  (`changes.diff` is a generated artifact — disclosed edit, recorded here).

### r2.6 Scope notes registered verbatim from the review §6 (this card cannot write them)

- **REM-40…44 register closure = parent/owner register update.** With
  F-REV-B1P-01 corrected, REM-43 may be recorded as: protocol ✅ closed;
  historical gap = r1 test file (18236 B / `e6c0949c…`) only. The register
  erratum for the sealed SRC review's F4 sentence is likewise the owner's.
- **E21 implementation = separate product card** (loader identity return +
  two comparison sites + owner-approved trust anchor); this card is read-only
  on product by design.
- **B1 promotion (batch 2) = owner decision**, unchanged; this round proposes
  no `iso/fixed/rf/scripts/**` byte and authorizes none.

### r2.7 Files touched this round (before → after; final pins in `binding.json.r2_rebinding`)

| file | before (bytes / sha256) | after (bytes / sha256) |
|---|---|---|
| SRC `oracle.md` (append-only Revision r7) | 47538 / `a8f192f10215642d…` | 57911 / `6e344a208f8fc439…` |
| `scratch/probe_e21_binding.py` (docstring line 19 only) | 10365 / `5c9f4508198963d2…` | 10383 / `5f53f5bbdbb439d5…` |
| `scratch/make_changes_diff.py` (F-REV-B1P-05 + r7 header) | 2961 / `8167bbfe9a9cd32f…` | 3776 / `f7be074e7e493c83…` |
| `decision.md` (this `## r2` append) | 16330 / `1a295207f70e4a5f…` | after this append — pinned in `binding.json.r2_rebinding` |
| `handoff.json` (r2 fields, superseded retention) | 19073 / `4460c91ea0974a56…` | written after this file — pinned in `binding.json.r2_rebinding` |
| `changes.diff` (regenerated) | 135696 / `844b3c72e1e35c46…` | regenerated after this file — pinned in `binding.json.r2_rebinding` |
| `binding.json` (`r2_rebinding` appended) | 10789 / `dd11d8537a615c55…` | appended last; binding is not self-signed |
| new files | — | `scratch/oracle_revision_r7.md` (10372 / `c99bc69e…`), `scratch/r2_*.py` (5 record tools), `evidence/r2/**` — see `evidence/r2/SHA256SUMS_r2.txt` |

Untouched by design this round: `freeze.json`, `commands.json`, this
attempt's `oracle.md`, `test_r13_equiv_rem41.py`, `conftest.py`, `runner/`,
`recovery/`, `evidence/SHA256SUMS.txt` and every r1 evidence label, SRC
attempt except the commissioned `oracle.md` r7 append (B1's sealed
`handoff.json:137` etc. cited read-only), all product/iso/production bytes,
and git (read-only subcommands only). No arm and no probe was re-executed.

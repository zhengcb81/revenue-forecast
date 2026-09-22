# B1-PREREQ — promotion prerequisites for B1 (REM-40…44 / B1 review F1–F5) — FROZEN ORACLE (r1)

- Plan: `2026-09-19-three-project-history-audit`
- Card: **B1-PREREQ — close the five promotion-prerequisite findings of B1's
  `accepted_with_conditions` review**
- Attempt: `execution_runs/B1-PREREQ/a20260922-01`
- Implementer: delegated prereq session (**does NOT self-sign accepted**)
- Source findings (verified against B1's own report before writing this oracle):
  `execution_runs/B1-I08C-product-fixes/a20260921-01/reviewer_report.md`
  on-disk sha256 `6bfd2922cdf3418416731e62098567d20ab1dcdc98429d8cc1e899e721e7951b`
  (37224 B; its self-pinned final-byte digest is
  `73feb0593b44ffeb448bc5f5b1cea9800f4cc9fb59f40ca19e9aae8038c104fa`, §10),
  findings F1–F5 at report lines 323–421, required-before-promotion list at
  §9 (lines 536–553); register entries REM-40…44 in
  `REMEDIATION_REGISTER.md` lines 68–72 + summary line 432.
- Isolation: this oracle is frozen **BEFORE** any run of this attempt. No pytest
  process, no probe, and no mutation copy has been executed at the moment of
  freezing. Freeze = `freeze.json` (hash-pin chain, no mtime ordering — see §5).

## 0. Scope, boundaries, and what this oracle does NOT claim

- **No product changes.** `iso/fixed/rf/**`, `iso/rf/**`, production
  `scripts/ tests/ config/ artifacts/` are READ-ONLY for this card. The only
  write into B1's attempt is the append-only `oracle.md` correction this card
  is explicitly commissioned to make (§3 F1/F2); every other B1 file
  (`test_b1_rem.py`, `binding.json`, `handoff.json`, `before/`, `after/`,
  `reviewer/`, `scratch/`) is untouched.
- **Promotion is not performed and not authorized here.** Whether B1's iso fix
  becomes "batch 2" is a separate owner decision; this card closes the five
  prerequisite findings only.
- `disclosure_adaptation = unmapped`, `accuracy = unproven`. Nothing here is
  evidence of forecast accuracy or of disclosure adaptation.
- Nothing here is self-signed: no `accepted` status is written by this card;
  `handoff.json.status = review_pending`.
- Frozen `before/` (B1's) untouched; no git write of any kind (read-only
  `git status` / `git diff --no-index` only).

## 1. SRC inputs pinned at freeze (re-measured, not quoted)

| SRC input | bytes | sha256 |
|---|---|---|
| `SRC/oracle.md` **pre-append** (r1–r4, = reviewer §1.2 bytes) | 39287 | `fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae` |
| `SRC/oracle.md` r1 prefix `[0:27697]` | 27697 | `81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281` (re-verified this session) |
| `SRC/reviewer_report.md` (on disk) | 37224 | `6bfd2922cdf3418416731e62098567d20ab1dcdc98429d8cc1e899e721e7951b` |
| `SRC/test_b1_rem.py` (frozen 12-node file) | 20631 | `636b43c8d8e1dc59ccfa36d7c71125ea9b8665222f587510444a3656b6700c16` |
| `SRC/iso/fixed/rf/scripts/revenue_publication.py` (M6 target) | 24917 | `bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0` |
| `SRC/iso/fixed/rf/scripts/revenue_core.py` | 25842 | `8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883` |
| `SRC/iso/fixed/rf/scripts/revenue_report.py` | 73973 | `212f00598feca408dc429d4c7a5332131ce25f1165b079347e4b295345df7d3b` |
| `SRC/iso/fixed/rf/scripts/contracts/evidence.py` | 15232 | `054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561` |
| `SRC/before/b1_unfixed.stdout.txt` (the OVERWRITTEN r1 artifact, F4) | 30580 | `58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335` |
| `SRC/before/frozen_artifacts.json` | 631 | `4721d1fbcb620346fe19c93ef793d527e644bd3e096bd5a014f576caab82b1f4` |

Closure check done BEFORE writing this oracle (each finding re-verified as
still open, none `already-closed`):

- **F1**: `SRC/oracle.md` contains revisions r2/r3/r4 only; `grep -r "r5"`
  over the SRC attempt finds only the reviewer's *prescription* of r5
  (`reviewer_report.md:353,538`). The r3 R3-2/R3-3 "11 fields" text is still
  the live frozen text ⇒ open.
- **F2**: `SRC/test_b1_rem.py` still defines exactly 12 nodes (10 `def test_`,
  one parametrized ×3); no node measures "present record verified under an
  `unattested` label" ⇒ open.
- **F3**: `E21`/`issuer_key_binding_mismatch` appears in `iso/fixed` only in
  the `validate_publication_attestation` docstring
  (`revenue_publication.py:235`); `_trusted_signer_public_keys() ->
  dict[str, bytes]` (`contracts/evidence.py:242-267`) drops `issuer`/`key_id`
  ⇒ open.
- **F4**: no `evidence/`-style raw-stdout protocol exists in SRC; the r1 RED
  stdout remains unrecoverable ⇒ open (protocol + disclosure only; the
  historical loss is **unclosable** — see §4).
- **F5**: no hash-pin `freeze.json` exists; ordering still rests on mtimes
  (`reviewer_report.md:403-421`) ⇒ open.

## 2. The five findings (verbatim substance, each verified against B1's report)

- **F1 / REM-40 (MEDIUM, documentation)** — `oracle.md` r3 says the record set
  is **11 fields incl. `result_sha256`** (R3-2) and that
  `PUBLICATION_ATTESTATION_FIELDS` has **11 members** (R3-3), while the
  executed set is **10** (`result_sha256` absent; the request pins it to
  `SIGNED_RESULT_SHA256_SENTINEL = "0"*64`). `handoff.json`/`decision.md`/
  `binding.json` state the correct 10; the frozen oracle prose is wrong.
  Fix: append-only oracle revision **r5**.
- **F2 / REM-41 (MEDIUM, evidence)** — the frozen 12-node proof set cannot see
  mutation **M6** (label-gated short-circuit): every node that carries a
  record carries the `host_signed` label, so M6 passes 12/12 while making any
  present record under an `unattested` label ignorable — the clause frozen at
  r1 §3.1 ("a record that does not verify must never be present-but-ignored")
  is load-bearing but unmeasured. Fix: R13-equivalent node + M6 into the §5
  mutation table.
- **F3 / REM-42 (LOW, documentation)** — E21 is documented but never raised;
  `issuer`/`key_id` are not cryptographically bound (reviewer renamed
  `record["issuer"]` to `revenue-forecast/evil`, recomputed, and
  `validate_publication_receipt` ACCEPTED). Impact bounded: label forgery
  still blocked by fingerprint trust-domain + Ed25519. Fix: bind it if bindable
  without product change, else document precisely why not and what would bind
  it — no silent drop.
- **F4 / REM-43 (LOW, evidence)** — the r1 RED stdout ("10 failed / 2 passed")
  was overwritten by a later run and the r1 test file (18236 B / `e6c0949c…`)
  is gone from disk and git ⇒ the disclosed r1 incident (the warrant for r2)
  is not independently auditable, contrary to the handoff's "preserved and
  NOT overwritten" claim. Fix: byte-preserved raw stdout for **every new**
  RED/GREEN arm under `evidence/` + record the r1 loss as a disclosed,
  **unclosable** historical gap.
- **F5 / REM-44 (LOW, pre-registration)** — freeze order rests on
  producer-controlled mtimes (git cannot order the first commit's files);
  `decision.md` had no freeze-time hash. Fix: hash-pin freeze records
  (`freeze.json`: content hashes + ordering chain); future proofs in this line
  use hash-pin order.

## 3. FROZEN FIXES and EXPECTED OUTCOMES (this section is the pre-registration)

### 3.1 F1 / REM-40 — append-only `SRC/oracle.md` Revision r5

- Form: SRC's own convention (`oracle.md` §9): a pure suffix append beginning
  `\n## Revision r5`, marker at byte `39287 + 1 = 39288`; r1–r4 bytes untouched.
  (Decision D-1 in `decision.md`: corrections go in **SRC's** oracle because
  SRC §9 permits append-only revision by an explicitly labelled `## Revision rN`
  heading with a hash proof and does not restrict the reviser; the generic
  "CORRECTION n" wording of the card yields to SRC's own convention per the
  card's "prefer whichever SRC's own conventions dictate".)
- Frozen content of the correction (normative statement, stated here before
  the append): the executed `publication_attestation` record set is **exactly
  10 fields** — `{attestation_payload_schema_version, domain_separator, issuer,
  key_id, algorithm, fingerprint, request_id, payload_sha256, signed_at,
  signature}` — with **no** `result_sha256` and **no** `receipt_sha256`.
  Why r3's "11" was wrong: r3 removed `receipt_sha256` but left `result_sha256`
  in the bullet list and in R3-3's member count, although the same fixpoint
  reason r3 itself gives for `receipt_sha256` applies to `result_sha256` too —
  `result_sha256` covers the receipt, and the receipt contains the record, so
  no consistent value exists at record-assembly time. The executed design
  instead pins the **request's** `result_sha256` to
  `SIGNED_RESULT_SHA256_SENTINEL = "0"*64`
  (`iso/fixed/rf/scripts/revenue_publication.py:330`), which keeps the signed
  request reconstructible at validation time. The fixed tree's
  `PUBLICATION_ATTESTATION_FIELDS` and the frozen test's `ATTESTATION_FIELDS`
  both have **10** members (test file lines 66–77; re-measured in
  `evidence/final_integrity_check.txt`).
- Expected proof outcome: `scratch/append_oracle_r5.stdout.json` reports
  `frozen_prefix_untouched: true`, `sha256(bytes[0:39287]) ==
  fadf8a5e…`, marker offset `39288`, and the three earlier prefix hashes
  (`81af1240…`, `60ecbca7…`, `231e7976…`) still matching.

### 3.2 F2 / REM-41 — R13-equivalent node + M6 into the §5 table

**Node file (frozen here before any run):** `test_r13_equiv_rem41.py` in THIS
attempt (sha256 pinned in `freeze.json`). It deliberately does **not** edit
B1's hash-pinned `test_b1_rem.py`; it imports that frozen module's own
fixtures (`fake_provider`, `trusted_domain`, `workdir`, `public_key_bytes`,
`isolated_env`) plus `_rehash`/`_receipt_of`/`_record_of`/`_with_provider`/
`_clear_provider`, so nothing is re-implemented and the setup is byte-shared
with the 12-node proof set. Two nodes:

1. `test_rem41_a_present_record_is_verified_even_when_label_is_unattested` —
   build an honestly `host_signed` package with a real record; flip the label
   to `unattested`; corrupt `record["signature"]` to `"0"*128`; `_rehash`;
   assert `validate_publication_receipt` **raises** with an `attestation`
   message (the frozen §3.1 clause: present-but-invalid ⇒ rejected).
2. `test_rem41b_positive_control_valid_record_unattested_is_accepted` — the
   SAME shape with a valid signature and consistent hashes must be **accepted**
   (label `unattested`, record present), so node 1 measures verification and
   not the label.

**M6 mutation frozen verbatim (the exact bytes `scratch/apply_m6.py` inserts):**

```
    if not claims_signed:
        # MUTATION M6: only a labelled claim is held to its record.
        return
```

inserted immediately after the comment line
`# record's bound fields, so any change to a bound value breaks the signature.`
and immediately before
`    require(\n        record["payload_sha256"] == receipt.get("validated_payload_sha256"),`
in `scripts/revenue_publication.py` (pre-hash `bc2bb4a3…` asserted by the
script; single occurrence of the anchor asserted). Semantics: after the
closed-set/structural checks, verification short-circuits whenever the label is
not `host_signed`, so a present-but-invalid record becomes ignorable under an
`unattested` label — exactly the reviewer's M6. The mutant exists ONLY under
this attempt's `scratch/mutations/M6/rf`; `iso/fixed/rf` stays byte-stable.

**Frozen arms and expectations (declared BEFORE running):**

| arm | label | tree | test file | expected nodes | expected rc |
|---|---|---|---|---|---|
| 1 | `arm1_node_on_fixed` | `SRC/iso/fixed/rf` | `test_r13_equiv_rem41.py` | **2 passed** (both GREEN) | 0 |
| 2 | `arm2_node_on_m6` | `scratch/mutations/M6/rf` | `test_r13_equiv_rem41.py` | **1 failed** (node 1 RED — M6 makes the corrupt record ignorable ⇒ `pytest.raises` gets no exception) **+ 1 passed** (control GREEN) | 1 |
| 3 | `arm3_frozen12_on_m6` | `scratch/mutations/M6/rf` | byte-identical copy of `SRC/test_b1_rem.py` (sha256 `636b43c8…` asserted before run) | **12 passed** — declared red set `{}` == observed red set `{}`: the blind spot, re-measured | 0 |
| 4 | `arm4_node_on_unfixed` | `SRC/iso/rf` | `test_r13_equiv_rem41.py` | **1 failed** (no record exists under `host_signed` ⇒ setup assert RED) **+ 1 passed** (control GREEN) | 1 |

M6 declared red set for the **whole 14-node proof surface** (12 frozen + 2 new):
`{test_rem41_a}` only; declared green: the other 13 including the control.
Isolation requirement: no extra red node, no missing red node (B1 §5 strength).
This row is appended into `SRC/oracle.md` §5's lineage as **Revision r6**
(marker = r5-post byte count + 1), pointing at this attempt's node + evidence.

### 3.3 F3 / REM-42 — E21 / `issuer`+`key_id` binding: read-only investigation

Frozen plan (no product change): run `scratch/probe_e21_binding.py` against
`SRC/iso/fixed/rf` (read-only execution; registry redirected into this
attempt). Pre-registered expectations:

- **Q1 (loader shape)**: `_trusted_signer_public_keys()` returns
  `dict[str, bytes]` keyed by 32-hex fingerprint → raw Ed25519 public key;
  `issuer`/`key_id` are **not** retrievable from its output, even though the
  trust **file** entries carry them (the isolated fixture writes
  `{name, key_id, issuer, public_key, fingerprint}`). Expected: loader output
  has no identity fields ⇒ nothing exists for an E21 comparison to read.
- **Q2 (rename attack re-measured)**: rewriting `record["issuer"]` to
  `revenue-forecast/evil` (and separately `record["key_id"]`) with all
  self-hashes recomputed ⇒ `validate_publication_receipt` **ACCEPTED**
  (F3's measurement). Control: corrupting `record["signature"]` ⇒ REJECTED
  (proves the probe still exercises verification).
- **Q3 (`result_sha256`, F6 cross-check)** — two readings exist and BOTH are
  measured, separately per entry point; whichever occurs is recorded verbatim
  (no silent drop):
  - **variant (a) arbitrary rewrite**: `pkg["result_sha256"] := "ab"*32`,
    nothing else touched. Expected: `validate_publication_receipt`
    **ACCEPTED** (the receipt layer contains no `result_sha256` check — the
    payload hash and the receipt hash both exclude it, and the record carries
    none). For `validate_forecast_output` the report (F6: "both ACCEPTED")
    and the code (`_validate_receipt_blocks` requires
    `result_sha256 == canonical_sha256(hash_payload)` with
    `hash_payload` = everything *except* `result_sha256`,
    `revenue_report.py:507-509,343-347`) point in opposite directions; the
    probe decides and any divergence from F6 is logged as a deviation with
    the exact error message.
  - **variant (b) control**: the honest value restored ⇒ both ACCEPTED.

**Frozen conclusion path (why E21 cannot be bound HERE):** binding issuer/
key_id requires bytes that do not exist and that producing would be a product
change, which this card forbids:

1. a trust loader that RETURNS the identity per fingerprint (today
   `contracts/evidence.py:242-267` maps fingerprint→key bytes only) — a change
   to `scripts/contracts/evidence.py`;
2. a comparison site — in `revenue_core._validate_attestation_response`
   (issuance-side E21 as the code table defines it) and/or in
   `revenue_publication.validate_publication_attestation` (consumption-side) —
   changes to `scripts/revenue_core.py` / `scripts/revenue_publication.py`;
3. trust **entries** that actually carry `issuer`/`key_id` in a schema the
   loader accepts, in a real anchor file: `config/trusted_signer_public_keys.json`
   is ABSENT by design (I-08-A R-PROV-2) and the I-08-A 12-field entry schema
   + E25 fail-loud loading are declared NOT closed in SRC oracle §7.3.

All three are product changes outside this card's boundary (and #3 is an
explicit capability grant, not a fix). What would bind it is written into
`decision.md` §F3 with the exact code sites and required entry bytes; the
finding is therefore **closed as documented-not-bindable-here, not silently
dropped** — acceptance of that disposition belongs to the reviewer/owner.

### 3.4 F4 / REM-43 — evidence protocol (frozen here, applies to every arm of this attempt)

1. Every new RED/GREEN arm gets a **distinct label** and preserves raw stdout,
   raw stderr and rc **byte-for-byte** under `evidence/` as
   `evidence/<label>.stdout.txt`, `.stderr.txt`, `.rc.txt`. Labels are
   write-once: `runner/run_arm.ps1` refuses to run a label whose outputs
   already exist (exit 99); a re-run must use a new label and be disclosed.
2. `evidence/SHA256SUMS.txt` pins every evidence byte stream after the runs.
3. Probe and append-proof stdout are evidence by the same rule.
4. **Disclosed unclosable historical gap (r1):** B1's r1 RED stdout
   ("10 failed / 2 passed", warrant for oracle r2) and the r1 test file
   (`e6c0949c…`, 18236 B) were overwritten/removed before archiving and cannot
   be recreated by this or any later card; the surviving
   `before/b1_unfixed.stdout.txt` (`58863ffb…`) is the **final** 11/1 output,
   not r1's. This gap is recorded here and in `decision.md` as **open,
   disclosed, unclosable** — it is not claimed closed by this card.

### 3.5 F5 / REM-44 — hash-pin freeze, ordering by hash chain

- `freeze.json` records, for every frozen input, `{seq, id, path, bytes,
  sha256, role, prev_entry_sha256, entry_sha256}` where
  `prev_entry_sha256 = sha256(canonical JSON of previous entry)` (genesis
  prev = 64 zeros) and `entry_sha256 = sha256(canonical JSON of this entry)`.
  **Ordering is derived from the chain, not from mtimes**; timestamps may
  appear as data but are declared non-normative for order.
- The freeze chain covers: this `oracle.md`, the node file, the M6 patch
  script, the probe, `commands.json` (frozen **with** expected outcomes so
  expectations cannot be edited post-run), `conftest.py`, `runner/run_arm.ps1`,
  `evidence/README.md`, the SRC oracle pre-append copy, and the SRC pins of §1.
- **Policy for future proofs in this line:** any freeze/re-freeze in the
  B1 line must be hash-pin based (`freeze.json` chain); mtime or
  "written-before" prose alone is no longer accepted as ordering evidence.

### 3.6 Run protocol

- Interpreter `C:\Miniconda\python.exe` (3.13.9; B1-bound), argv shape copied
  from B1: `-X utf8 -B -m pytest -p no:cacheprovider -q --no-header -rA <file>`,
  env `B1_REPO_ROOT=<tree>`, `PYTHONDONTWRITEBYTECODE=1`,
  `REVENUE_PUBLICATION_REGISTRY=<THIS_ATTEMPT>/runner/registry/publications.jsonl`,
  `PYTHONPATH=<tree>/scripts;<tree>/tests`. Network disabled (no command
  reaches the network). rc legend = SRC oracle §8 (copied).
- Sequence: freeze → SRC appends (r5, r6) → M6 build → arms 1–4 → probe →
  integrity check → deliverables. `commands.json` freezes argv + expectations;
  observed values are recorded in `handoff.json`/`evidence/`, never by editing
  `commands.json`.

## 4. Explicitly NOT closed by this card

1. The r1 RED stdout / r1 test file loss (F4) — **unclosable**, disclosed.
2. E21 binding itself (F3) — documented, not implemented; needs product change.
3. F6's disclosed residual (`result_sha256` unbound by the record) — no action
   required per the reviewer; re-measured only.
4. F7/REM-02 adjudication (caller-trap residual, (a)/(b)/(c) decision) — not
   part of this card's five findings; stays with its owner.
5. Promotion of `iso/fixed/rf/scripts/**` — separate owner decision.
6. I-08-C's verdict, the invest-core consumer, I-08-A's full provider protocol —
   unchanged, out of scope, exactly as SRC oracle §7 states.

## 5. Freeze declaration

This file, in the state hashed by `freeze.json` entry
`my_oracle_md`, is FROZEN before any run of this attempt. Revisions after
freeze, if ever needed, must be append-only under `## Revision rN` with a
prefix hash proof, per SRC convention. `freeze.json`'s chain — not filesystem
order — is the ordering evidence (F5).

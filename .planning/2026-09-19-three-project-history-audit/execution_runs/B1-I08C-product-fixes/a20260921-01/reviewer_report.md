# B1 — I-08-C product defects REM-01/02/03 — INDEPENDENT REVIEWER REPORT

- Plan: `2026-09-19-three-project-history-audit`
- Card: **B1 — I-08-C product defects REM-01/02/03**
- Attempt reviewed: `execution_runs/B1-I08C-product-fixes/a20260921-01`
- Reviewer role: independent (read-only on production; every action confined to
  `<ATTEMPT>/reviewer/**`; no production file, no git write, no promotion)
- Date: 2026-09-21
- Source of the defects: `execution_runs/I-08-C/a20260919-01/review.md`
  sha256 `c1a8fd11b20f911c7407943dabe70bc493a9cb2959719c13beef21f8e7f1f2a3` (re-verified)

---

## VERDICT

**`accepted_with_conditions` — the card's security claims are CONFIRMED; three
non-security documentation defects and two evidence-completeness defects are
recorded below and must be closed before/at promotion.**

| # | claim from the handoff | reviewer verdict |
|---|---|---|
| 1 | Production unchanged (3 hashes, registry, trust file ABSENT, clean `git status`) | **CONFIRMED, re-verified twice** |
| 2 | Oracle frozen before first run; r1 byte range survives 4 append-only revisions | **CONFIRMED (hash proof); freeze *order* only partially evidencable — F5** |
| 3 | RED 11 failed/1 passed (rc 1) → GREEN 12 passed (rc 0) | **CONFIRMED by my own re-runs on both arms** |
| 4a | REM-01 label requires a verifying record | **CONFIRMED — the exploit is dead at both consumer entry points** |
| 4b | REM-01 `attestation_capability()` is a bounded provider handshake (security-critical) | **CONFIRMED — `.txt` / bare `.py` / `sys.executable` all yield `unattested` with no record; verified by my own run and by code reading** |
| 4c | REM-02 documented as non-security, no behaviour change | **CONFIRMED as implemented; the *decision* is acceptable but a residual caller trap remains — see F7 (adjudication)** |
| 4d | REM-03 two gates; reviewer's original exploit now rejected | **CONFIRMED — original F3 exploit rejected at `validate_forecast_output`, `validate_published_forecast` and `render_markdown`** |
| 5 | Mutation proof M1–M5 isolated, declared red == observed red | **CONFIRMED — reproduced independently, all five exactly** |
| 6 | Regression 100 pass → 99 pass + exactly 1 required failure; that test NOT rewritten | **CONFIRMED — `tests/` is byte-identical across production, iso and iso/fixed; 129/129 files** |
| 7 | Disclosed deviation (`receipt_sha256`/`result_sha256` out of the record) leaves nothing unbound | **PARTIALLY CONFIRMED — nothing that was independently checkable is now unbound; `result_sha256` is provably unbindable and stays unbound (F6). The oracle revision r3 *text* is wrong about the resulting field count (F4).** |

The three defects the I-08-C reviewer confirmed are closed **in the product**,
against the isolated fixed tree. The reduction in scope the card declares
(reduced provider protocol; label binding only in *this* repo; no production
trust anchor; no promotion) is honest and correctly stated. **Nothing in this
report authorizes promotion**: promoting
`iso/fixed/rf/scripts/{revenue_core,revenue_publication,revenue_report}.py` is a
separate owner decision, and F1–F5 below should be closed first.

---

## 1. What I executed myself (raw evidence, reviewer-owned)

Every command below was run by me against reviewer-owned copies. Source paths are
recorded because the whole card turns on *which bytes were imported*.

| run | tree | command | result | artifact |
|---|---|---|---|---|
| RED | `<ATTEMPT>/iso/rf` | `python -X utf8 -B -m pytest -p no:cacheprovider -q --no-header -rA <ATTEMPT>/test_b1_rem.py` | **11 failed, 1 passed, rc 1** (4.37 s) | `reviewer/RED.stdout.txt` sha256 `33dd115e7313839cbe081e5ae7cf2b99c1d863a5cf2c342175664cbd7701d8c1` (30360 B) |
| GREEN | `<ATTEMPT>/iso/fixed/rf` | same | **12 passed, rc 0** (8.35 s) | `reviewer/GREEN.stdout.txt` sha256 `b9fb998f60e00fe7eb57247bf8d6f1653b4ef23441cb54329ad4730c7558a6ad` (2424 B) |
| regression pre-fix | `iso/rf` | 11-module subset, `runner/regression_targets.txt` | **100 passed, rc 0** (62.76 s) | `reviewer/SUITE_unfixed.stdout.txt` sha256 `70a7d3b2f7275e5c11cb74be9bbac7e71264e1c52534a416d7015e3687ec5069` |
| regression post-fix | `iso/fixed/rf` | same | **1 failed, 99 passed, rc 1** (67.43 s) | `reviewer/SUITE_fixed.stdout.txt` sha256 `bbd57e5fe5b087faf2886d23666515c85dc3b1ee9692f035727bb4382869fb93` |
| mutation proof | `M1..M6` fresh copies | `reviewer/scratch/probe_mutations.py` | M1–M5 declared==observed; M6 → **{}** | `reviewer/scratch/mutations/reviewer_mutation_proof.json` sha256 `e872e9d2381b32c62e779b1b2c2a44220833127f72fd4b903d0cb1989a92aa37` |
| R13 (reviewer node) | `iso/fixed/rf` | pytest on `reviewer/test_r13_reviewer_node.py` | **2 passed** ×3 runs (4.67 / 5.61 / 12.04 s) | `reviewer/test_r13_reviewer_node.py` sha256 `90abc1dd02088f00082a6bd2d2aacbfae5d7cd31d3e67186f816daa6f76a8f17` |
| R13 vs M6 | `M6/rf` | same | **R13 RED, positive control GREEN** | in transcript |

The RED node set matches the frozen oracle §4 exactly: R1, R2×3, R3, R4, R5, R6,
R7, R8, R9, R10, R12 RED; only
`test_rem03_honest_package_still_accepted` (the deliberate positive control)
GREEN.

### 1.1 Byte-level production zero-write (claim 1) — CONFIRMED

Re-hashed before, during and **after** all reviewer activity:

```
183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba  10681  scripts/revenue_publication.py
a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f  69765  scripts/revenue_report.py
1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae  14136  scripts/revenue_core.py
054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561  15232  scripts/contracts/evidence.py
29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344  10599  scripts/publication_registry.py
bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91  46369  artifacts/registry/publications.jsonl
ABSENT                                                                 config/trusted_signer_public_keys.json
```

`git status --porcelain --untracked-files=all -- scripts tests config artifacts`
→ **0 entries** (checked with `--untracked-files=all`, which is stricter than the
command the card recorded). `after/production_status.txt`
sha256 `e09d80ea2933324af82dda198f5a9f82db7012d8792537a75a5c8af653d102e8`
records the same table plus `git_head f6f8bde12d229da3bf79b64f59163c5474021db2`
with empty porcelain.

**Correction to the card's isolation narrative (minor, honest):** the handoff
says `iso/` was copied "with robocopy /E, `__pycache__` excluded". Both `iso/rf`
and `iso/fixed/rf` in fact contain **23 `.pyc` files** copied from production
(`scripts/**/__pycache__`). This is harmless and I verified it does not mask the
fix: the RED arm reproduces the unfixed 11/1 split, so the fixed sources were
genuinely imported on the GREEN arm, and re-running RED with
`--ignore-glob="*__pycache__*"` gives the same 11 failed / 1 passed. The
`.pyc` files differ between the two trees (they embed the source mtime), which is
expected for a copy. No property is affected; the claim's wording is inaccurate.

### 1.2 Append-only proofs (claim 2) — hash proofs CONFIRMED

`oracle.md` is 39287 B / `fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae`.
Hashed by me on the current bytes:

| prefix | expected (frozen) | my measurement | marker offset on disk | marker offset recorded |
|---|---|---|---|---|
| `[0:27697]` (r1) | `81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281` | **match** | `## Revision r2` at byte **27698** | 27698 |
| `[0:31081]` (r1+r2) | `60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4` | **match** | `## Revision r3` at byte **31082** | 31082 |
| `[0:35840]` (r1+r2+r3) | `231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523` | **match** | `## Revision r4` at byte **35841** | 35841 |

Each marker begins exactly one byte after the previous frozen prefix (a single
`\n`), i.e. every revision is a pure suffix append. All three proof files are
internally consistent and their `pre_append_*` values equal the previous
`document_*_after` values:

```
scratch/append_oracle_r2.stdout.json  1189 B  b3b0f92b2bcb10def425814346247b45d524525ad063f04648dafc9f9943c45d
scratch/append_oracle_r3.stdout.json   926 B  6fdc95b2d2f1d404b39cadb22669d562a904c62317caae85431cbc997be19679
scratch/append_oracle_r4.stdout.json   910 B  598ac7702e014f6163a7c336b62ec0e832fc17bfd228740d52d20786b3cf44e5
```

`before/frozen_artifacts.json` (631 B / `4721d1fb…`) still holds the r1 values
(`oracle.md` 27697 / `81af1240…`, `test_b1_rem.py` 18236 / `e6c0949c…`), and
`after/frozen_artifacts_r3.json` records the same r1 values alongside the final
ones — so the freeze-time record of r1 genuinely predates the appends. **All 30
entries in `after/frozen_artifacts_r3.json` re-hash OK (0 mismatch, 0 missing)**,
including `decision.md` 16236 / `4a1d39b42d9787e506ae36e47fa9aa68d082e96c5149e3ad41645c468fe968a1`,
`changes.diff` 41639 / `203ea42b…` and `scratch/mutations/mutation_proof.json`
6596 / `df29d706…`.

---

## 2. REM-01 — the security-critical claim, attacked directly

### 2.1 What the fixed code actually does (code reading)

`revenue_core.attestation_capability()` now (lines 118-153):
1. requires `REVENUE_ATTESTATION_PROVIDER`; resolves it with
   `shutil.which(provider) or Path(provider).expanduser()`;
2. **refuses to spawn** when the resolved path is not a file
   (`provider_path_unopenable`);
3. spawns it once via `subprocess.run([str(resolved)], input=<one JSON request>)`
   with `timeout=10.0`, `capture_output=True`;
4. caps stdout at 65536 B **before** parsing (a truncated prefix is never parsed);
5. requires exactly one JSON object whose key set is **exactly**
   `ATTESTATION_RESPONSE_FIELDS` (10 keys), schema-version `1.0`,
   `algorithm == "ed25519"`, 32-hex `fingerprint`, 128-hex `signature`,
   RFC3339-Z `signed_at`, non-empty `issuer`/`key_id`;
6. requires **byte-identical echo** of `request_id`, `payload_sha256`,
   `domain_separator`;
7. verifies **Ed25519 over `canonical_sha256(request)`** against
   `contracts.evidence._trusted_signer_public_keys()` — i.e. the fingerprint must
   resolve in the trust domain (reused loader, unchanged);
8. every failure path records a coded diagnostic and returns `False`.

The provider file is never read, never imported, never executed as a script — it
is only spawned, and only when it exists as a file. `run_forecast` stamps
`host_signed` **only** from a completed handshake that produced a record.

### 2.2 My own negative results (the exact three cases named in the task)

Verified by my GREEN run (nodes
`test_rem01_b_to_d_file_existence_is_not_signing_capability[plain_txt|bare_py|sys_executable]`,
all PASSED) — these nodes assert **both** sides: issuance
(`attestation_capability() is False`, a coded failure exists, the emitted label is
`unattested`, no `publication_attestation` key) **and** consumption
(`validate_publication_receipt` and `validate_forecast_output` both accept the
honest unattested package). `plain_txt` is exactly the reviewer's 5-byte
`.txt`; `sys_executable` is a real `sys.executable` file. So the I-08-C F1
mechanism ("any operator can mint host-signed artifacts by pointing an env var at
a text file") is dead, and it is dead at a **consumer entry point**, not at a
helper.

### 2.3 My own additional attacks on the label (all reject)

Built with a reviewer-authored isolated Ed25519 provider and an isolated trust
file (private key never leaves my scratch dir), label `host_signed`:

| move | result |
|---|---|
| delete the record, keep `host_signed`, recompute all self-hashes | **REJECTED** `attestation_missing_record … (E27)` |
| keep the record, replace `request_id` (moves the signature onto another request), rehash | **REJECTED** `attestation_signature_invalid … (E14)` |
| add one extra key to the record | **REJECTED** `attestation_payload_fields … extra=['extra_note']` |
| record present, label flipped to `unattested`, **signature corrupted**, rehash | **REJECTED** (`attestation…`) — see §2.4 |
| label flipped to `host_signed` on an honest unattested package, rehash | **REJECTED** `attestation_missing_record` (frozen node R1) |
| correct handshake, key not in the trust domain | capability **False**, label `unattested`, no record, code `provider_key_untrusted` (frozen node R6) |

### 2.4 My own mutation the oracle did not list — M6 (as requested in the handoff)

The frozen 12-node set never exercises "a record that **is present** is verified
**even when the label says `unattested`**": R2/R3/R4 carry no record at all, and
R1/R7 carry the `host_signed` label. I therefore wrote both the mutation and the
node that measures it.

- **M6 (reviewer-authored, absent from oracle §5 and r4):** short-circuit
  `validate_publication_attestation` after the closed-set checks when the label
  is not `host_signed`, so a present-but-invalid record becomes ignorable.
- **Prediction declared before running:** the frozen 12-node set cannot see M6
  (`{}` red), because every node that carries a record also carries the
  `host_signed` label.
- **Observed:** `M6 rc=0 observed=[] declared=[] isolated=True` — the full frozen
  12-node file **passes 12/12 on the M6 mutant**. The frozen suite is blind to
  this regression.
- **My 13th node closes the gap:** `reviewer/test_r13_reviewer_node.py` (imports
  the frozen file's own fixtures so nothing is re-implemented) asserts that an
  `unattested`-labelled package whose record has a `"0"*128` signature must still
  be rejected, plus a positive control. Fixed tree: **2 passed** (3/3 runs). M6
  mutant: **R13 RED, control GREEN**.
- **Conclusion:** the clause *is* load-bearing in the implementation (the fixed
  tree rejects the move), and the frozen proof set has a measurable blind spot
  here. F2.

---

## 3. REM-03 — the reviewer's original exploit, and what the gates really cover

### 3.1 The original F3 exploit is dead (CONFIRMED)

I rebuilt the I-08-C reviewer's own construction myself (not the implementer's
test): keep `input_document`, `input_sha256` and `parameter_trace` **completely
unchanged**, inflate only `segments[0].base_revenue` (`100 → 1100`), recompute the
public self-hashes.

```
receipt layer                : ACCEPTED   (documented non-security, by design)
validate_forecast_output     : REJECTED  <segment base revenue mismatch: Segment A opening base 1100.0 does not match segment_a_base (100)>
validate_published_forecast  : REJECTED  <same>
render_markdown              : REJECTED  <same>   (the honest package renders 12490 B of markdown)
```

The forgery no longer renders. Additional moves, all rejected:
`+0.5` (G-A, so the gate is not a magnitude detector), all-segments +1.0 (G-A),
name-preserving swap of two segment bases (G-A), company `base_revenue`+1000 with
segments untouched (**G-B**: `segment opening base does not reconcile:
segments=150.0, reported=1150.0`). So **both** new gates are reachable and
load-bearing, which the implementer's own test (delta `+1000` with no model
rebuild) does not demonstrate — it never reaches G-B.

### 3.2 The strongest attack I could construct: still rejected, for a reason worth recording

I granted the attacker everything a hash-recomputing insider can do — mutate
`parameter_trace`, re-run the engine's own `calculate_model_path`, rebuild
recognition/effective revenue, rebuild the consolidated paths, re-anchor
`input_sha256` — i.e. the coherent full-story forgery. Result:

- re-anchoring the embedded `input_document` without touching `parameter_trace`
  → **REJECTED** `parameter_trace must match the validated input parameters`;
- re-anchoring both → **REJECTED** `segment opening base does not reconcile`
  (G-B), because the forged segment base no longer matches the declared company
  base;
- negative-base redistribution (`A = A + 950`, `B = B − 950`, sum unchanged, so
  G-B is silent and G-A skips the untraced segment) → **blocked structurally**:
  `model_registry.calculate_registered_model` raises
  `direct_revenue.base_revenue cannot be negative`, so a negative opening base is
  not a reachable state of this engine.

**Residual (recorded, not a defect of this card):** an attacker who edits the
embedded `input_document` *and* re-anchors `input_sha256` presents a
hash-consistent artifact whose only remaining anchor is the caller's own copy of
the original input — `validate_published_forecast(result, original_input)` and
`verify_input_binding` reject it. That is the pre-existing input-binding contract,
not something REM-03 weakened, and the oracle's scope narrowing ("the per-segment
opening-base column becomes bound" — nothing about totals) remains accurate. It
does mean G-B is a weaker sibling of G-A rather than the independent backstop the
oracle's §3.6 rationale calls "the stronger presentation claim": with
`parameter_trace` honest and all bases non-negative, G-B can only fire when the
declared company base moves — a forgery the *existing* `_recompute_consolidated_paths`
already rejects.

---

## 4. Mutation proof (claim 5) — reproduced exactly, independently

Each mutation applied as one exact literal revert to a fresh copy of the fixed
tree; the same frozen test file then run; declared red set required to equal
observed red set exactly.

| mutation | declared red | observed red (mine) | isolated |
|---|---|---|---|
| M1 (drop the whole record check) | {R1, R7} | {`test_rem01_a_label_only_flip_is_rejected`, `test_rem01_g_replayed_record_is_rejected`} | **yes** |
| M2 (restore file-existence capability) | {R2 plain_txt, R2 bare_py, R2 sys_executable, R6} | exactly those four | **yes** |
| M3 (drop G-A) | {R10, R12} | exactly those two | **yes** |
| M4 (remove the REM-02 non-security docstring clause) | {R9} | exactly that one | **yes** |
| M5 (remove the record-verification tail) | {R7} | exactly that one | **yes** |
| **M6 (reviewer-authored, not in the oracle)** | **{}** (declared) | **{}** observed on the frozen set; **{R13}** on my added node | **yes** |

So the implementer's mutation table is **independently reproduced**, including
the two honestly declared dependencies (R7 red under M1 because M1 removes the
whole record check; R6 red under M2 because file-existence capability never
reaches the trust check). `scratch/mutations/mutation_proof.json` is unchanged
(6596 B / `df29d706…`), and I did not write into it — my results are in
`reviewer/scratch/mutations/reviewer_mutation_proof.json`.

---

## 5. Regression (claim 6) — CONFIRMED, and the expected failure is genuine

```
before (iso/rf)          : 100 passed, rc 0
after  (iso/fixed/rf)    : 1 failed, 99 passed, rc 1
the single failure       : tests/test_attestation.py::AttestationTests::test_configured_provider_means_host_signed_publication
failure text             : os.environ["REVENUE_ATTESTATION_PROVIDER"] = sys.executable
                           >  self.assertTrue(attestation_capability())
                           E  AssertionError: False is not true
```

- `tests/test_attestation.py` is **byte-identical** in production, `iso/rf` and
  `iso/fixed/rf`: `d1b7cf036b22867d62e235002e1d1736586ec45a2f888e84896504b7b7915404`,
  6947 B. `tests/` differs in **0 of 129** files between the two iso trees (the
  only byte differences in the whole copy are the three fixed `scripts/*.py` and
  the `__pycache__` artifacts). `git status --porcelain -- tests/` is empty.
- The test is exactly the I-08-A §7.1 false-green source (`sys.executable` as
  provider ⇒ `host_signed`), and the fix breaks it **by design**. It was **not**
  rewritten: the intent is intact and the assertion fails on the product change,
  not on an edited expectation.
- `tests/test_zr907_drift_patrol.py` is excluded from the subset for the stated
  pre-existing `No module named 'drift_patrol'` reason; the subset file lists 11
  modules and both runs collected the same 100 nodes, so the before/after
  comparison is apples-to-apples.

---

## 6. Findings

Severity: **F1/F2 = documentation/evidence defects (block promotion until
corrected); F3–F5 = bookkeeping; F6 = disclosed residual (no action required);
F7 = adjudicated decision with a residual to track.**

### F1 (MEDIUM, documentation) — the frozen artifact contradicts itself on the attestation field count

`oracle.md` Revision r3 R3-2 says the record set is **11 fields** and explicitly
keeps `result_sha256`: *"`receipt_sha256` is removed … The set remains closed and
exact"* with `{attestation_payload_schema_version, domain_separator, issuer,
key_id, algorithm, fingerprint, request_id, payload_sha256, result_sha256,
signed_at, signature}`. R3-3 then says *"`PUBLICATION_ATTESTATION_FIELDS` in the
fixed tree has 11 members; the frozen test's `ATTESTATION_FIELDS` mirrors that
exactly"*.

The delivered artifact has **10** fields: `result_sha256` is *absent* from the
record, and instead the request's `result_sha256` is pinned to
`SIGNED_RESULT_SHA256_SENTINEL = "0"*64` so the signed object is reconstructible.
My measurement of the executed bytes:

```
PUBLICATION_ATTESTATION_FIELDS = 10 members:
  algorithm, attestation_payload_schema_version, domain_separator, fingerprint,
  issuer, key_id, payload_sha256, request_id, signature, signed_at
set(record) == PUBLICATION_ATTESTATION_FIELDS  →  True
```

This is exactly the fixpoint reason r3 itself gives for removing `receipt_sha256`
— `result_sha256` covers the receipt, the receipt contains the record — so r3's
bullet list is internally inconsistent, and `handoff.json` (line 121),
`decision.md` (§3, "carries **10** fields, not the 12 r1 first froze") and
`binding.json` (line 104) all state the correct 10-field outcome. **The
implementer's claim to me ("closed 10-field set") is accurate; the frozen
oracle's revision prose is wrong.** A reviewer or implementer who trusts the
oracle's field list would expect a key that must not be there. Correct
`oracle.md` with a further append-only revision (r5) — do not edit r1–r4 bytes.

### F2 (MEDIUM, evidence) — the frozen proof set cannot see the "present record is ignored" regression

Demonstrated in §2.4: M6 (label-gated short-circuit) leaves the frozen 12-node
file at **12/12 PASS** while disabling verification of any record carried by an
`unattested`-labelled receipt. The implementation is correct today (my R13 passes
on the fixed tree and fails on M6), but the card's own proof set does not measure
the clause the oracle's §3.1 freezes ("a record that does not verify must never be
present-but-ignored"). Recommendation: fold a node equivalent to R13 into the
card's test file, and add M6 to the mutation table.

### F3 (LOW, documentation) — a rejection code is documented but never raised

`validate_publication_attestation`'s docstring lists
`issuer_key_binding_mismatch (E21)` and the oracle freezes E21 as "`issuer` != the
trust-domain entry's `issuer`, or `key_id` mismatch". No E21 is raised anywhere:
`grep` over `scripts/` finds the string only in that docstring line, and
`contracts/evidence._trusted_signer_public_keys()` returns a
fingerprint → public-key map with no issuer/key_id fields. Consequently
`issuer` / `key_id` are **not cryptographically bound**: I changed the record's
`issuer` to `"revenue-forecast/evil"`, recomputed everything, and
`validate_publication_receipt` **ACCEPTED** it (the signature verifies because
`canonical_sha256(request)` covers `attestation_request_schema_version`,
`domain_separator`, `request_id`, `payload_sha256`, `result_sha256`,
`canonical_payload_sha256` — not the identity labels). Impact is limited: the
label still cannot be forged because the *fingerprint* must be in the trust
domain and the signature must verify, and an E21-free binding only lets a party
who already holds a trusted key *rename itself* in the record. Report it as a
documentation-vs-behaviour mismatch: either implement E21 (compare the record's
`issuer`/`key_id` with the trust entry it resolved), or delete the claim from the
docstring and record E21 as not-closed in §7.

### F4 (LOW, evidence) — the r1 RED run's raw output is not independently auditable

`before/b1_unfixed.stdout.txt` is 30580 B / `58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335`
and git records the **same blob** (30580 B) as added in commit `980c9b7a`, with no
later commit touching it. But the handoff/binding record its mtime as the r1 run's
artifact whose content is *"10 failed / 2 passed"*, while the file on disk is the
final 11-failed/1-passed output (mtime 21:15:12, `before/b1_unfixed_r3.*` written
at 21:56) — and the r1 test file (18236 B / `e6c0949c…`) is no longer in the
attempt directory or in git. I therefore **cannot reproduce the disclosed r1
"10 failed / 2 passed, R8 passed trivially" incident**, which is the entire stated
warrant for oracle revision r2. The disclosure is honest, the incident does not
change any security expectation, and I independently confirmed the *r2/r3*
baseline (11/1) is real — but the r1 artifact that would let a reviewer audit the
claim was overwritten rather than preserved, contrary to `handoff.json`'s
"the r1 RED stdout is preserved and NOT overwritten". Preserve raw run outputs
under distinct labels in future attempts.

### F5 (LOW, pre-registration) — the freeze *order* rests on mtimes, and `decision.md` had no freeze hash

The oracle freeze order is supported by filesystem mtimes
(`before/production_anchors.json` 21:12:35 → `before/frozen_artifacts.json`
21:14:27 → `before/probe_unfixed.txt` 21:14:35 → first RED stdout 21:15:12) and by
the fact that `git log --diff-filter=A` shows `oracle.md`, `test_b1_rem.py` and
`before/b1_unfixed.stdout.txt` all first appearing in **one** commit
(`980c9b7a`, 21:16:24), i.e. git cannot order them. The r1 **hashes** are recorded
in two independent artifacts and both agree, which is the substantive protection;
the *ordering* is an mtime argument, and mtimes are producer-controlled. Two
smaller points in the same area: `binding.json` records
`decision.md` as *"sha256 recorded in after/frozen_artifacts_r3.json (rewritten
after the final edit)"* (14 988 B at freeze → 16 236 B now, final hash
`4a1d39b4…`), so `decision.md` itself is post-hoc; and `before/production_anchors.json`
(2782 B / `01e7ab52…`) vs `before/production_anchors.txt` are the inline/scripted
pair whose command-id was corrected in oracle r4. None of this weakens the RED→GREEN
result — every input I could hash is intact — but the card's strongest ordering
claim is weaker than its wording suggests.

### F6 (INFORMATIONAL, disclosed residual) — `result_sha256` is provably unbindable and remains unbound

The deviation disclosure is accurate as far as `receipt_sha256` goes: a receipt
cannot contain its own hash, and removing it leaves nothing that was independently
checkable. For `result_sha256` I verified the stronger statement: because
`result_sha256` covers the receipt which contains the record, and the record is
signed over the request (which pins `result_sha256` to the sentinel), the record
**cannot** bind the live result digest. Measured: rewriting `result_sha256` to any
value and recomputing it consistently leaves both `validate_publication_receipt`
and `validate_forecast_output` **ACCEPTED**. This is not a regression — the record
never bound it, and `result_sha256` is a self-hash of a payload the receipt already
binds via `validated_payload_sha256 == _payload_sha256(result)` (which excludes
`result_sha256` and `publication_receipt` **by design**). The claim "nothing is left
unbound" should be read as "nothing that was independently verifiable is now
unbound", which holds; the sentinel design is a reasonable way out of the fixpoint
and is documented in the code. **No action required**, but the r3 text should stop
listing `result_sha256` as a record field (F1) so the residual is unambiguous.

### F7 (adjudication) — REM-02 "documented, no runtime warning": acceptable, with a residual caller trap

**Decision reviewed.** Oracle r1 §3.5(c) froze, *before any run*, that
`validate_publication_receipt` must state in its docstring that it is a
hash-consistency check and **not** a security boundary, must name
`revenue_report.validate_forecast_output` as the consumer entry point, must export
a `PublicationReceiptOnlyWarning` marker, and must **not** emit a runtime warning
because `_validate_receipt_blocks` calls it on every strong validation and
`test_zr701`/`test_zr705` assert clean runs.

**Verified as implemented:** the docstring contains both literal phrases; the
module docstring repeats the contract; `PublicationReceiptOnlyWarning(UserWarning)`
is exported with a real docstring; the function's behaviour is otherwise
unchanged (my probes reproduce "self-consistent forgery accepted" exactly, on
purpose). **The decision is acceptable.** Reasons: (i) the I-08-C reviewer's
disposition for F2 was "document or deprecate" and the severity was assessed
MEDIUM precisely *because* both in-repo consumers already run the strong path;
(ii) nothing in the codebase calls this function as a gate
(`revenue_report._validate_receipt_blocks` calls it *after* the strong gates, and
`render_markdown` routes through `validate_forecast_output`); (iii) the freeze
predates the implementation, so this is a design choice under audit, not a
post-hoc excuse.

**Residual (track, do not treat as closed):** a marker class that is *never
raised* emits no runtime signal at all. A future caller who writes
`validate_publication_receipt(pkg)` believing it validates a publication gets
silence, a docstring they may not read, and a passing return. That is exactly the
harm the I-08-C reviewer described in its own F2. Because the honest-attested and
`unattested` paths both stay
legitimate (the oracle forbids a "reject unattested" gate), the *behavioural* fix
is not available; the affordable mitigations are (a) a
`publication_receipt.receipt_schema_version` bump so consumers must opt in, (b) a
one-time `warnings.warn(..., PublicationReceiptOnlyWarning, stacklevel=2)` guarded
by module-level state — but note this would break `test_zr701`/`test_zr705` and
must therefore be deliberate, or (c) a follow-up card that renames/deprecates the
symbol. My recommendation: **(a) plus a follow-up item**, and record REM-02 as
"documented limitation, consumer-side guardrail not yet in place" rather than
"closed". This is a **condition on promotion**, not a security failure of this
card: no boundary moved that was previously held.

---

## 7. Claim-by-claim cross-check against the implementing agent's brief

| brief claim | verdict | evidence |
|---|---|---|
| production `183803bb…` / `a85fb484…` / `1821fd2a…`; trust file ABSENT; registry `bc3256bb…`; clean porcelain | **CONFIRMED** | §1.1 (re-verified after all my activity) |
| oracle r1 = 27697 B / `81af1240…`, prefix hash stable after 4 append-only revisions | **CONFIRMED** | §1.2 |
| RED 11 failed/1 passed rc 1 → GREEN 12 passed rc 0 on `iso/fixed/rf` with the three stated hashes | **CONFIRMED** | §1; fixed hashes `8a761498…`/`bc2bb4a3…`/`212f0059…` match exactly |
| REM-01: 10-field closed record + Ed25519 vs trust domain + E16 binding | **CONFIRMED** | §2.1–2.3; field set measured = 10 |
| REM-01: 5-byte `.txt`, bare `.py`, `sys.executable` ⇒ `unattested`, no record | **CONFIRMED (my own run, both issuance and consumption sides)** | §2.2 |
| REM-02: documented, marker exported, **no behaviour change**, frozen decision | **CONFIRMED as implemented**; decision adjudicated acceptable with residual | F7 |
| REM-03: two gates on pre-existing fields; original exploit rejected | **CONFIRMED** | §3.1 |
| mutation proof M1→{R1,R7}, M2→{R2×3,R6}, M3→{R10,R12}, M4→{R9}, M5→{R7} | **CONFIRMED, reproduced exactly** | §4 |
| regression 100 → 99 + exactly 1 required failure; test NOT rewritten | **CONFIRMED** | §5 |
| deviation: `receipt_sha256`/`result_sha256` removed, nothing unbound | **PARTIALLY CONFIRMED** | F6 (accurate in substance; r3's text wrong — F1) |

---

## 8. Unverified / not closed by this review

1. **Promotion is not performed and not authorized here.** No production file was
   written by me; `iso/fixed/rf` is attempt-local state.
2. **The invest-core consumer** (`~/.claude/skills/invest-core/scripts/invest_contracts.py:1130-1142`)
   was **not** read or executed. REM-01 binds the label *in this repo*; whether
   that consumer verifies the record is out of scope and unverified. This remains
   the decisive consumer for REM-01 per the I-08-C review.
3. **The full I-08-A provider protocol is not implemented** and I did not test it:
   E18 (`issued_at`/`expires_at`/replay window `W`), E19 (`request_id` reuse
   ledger), E22, E23, E24, E25, E29, the 12-field trust entry schema, and the
   L1/L2/L3 proof domain. Also **E10** (`provider_signing_unavailable`) is matched
   only by a substring heuristic on stderr (`"cannot sign"` / `"no private key"`),
   which I did not exercise with a real refusing provider.
4. **No CLI / transaction entry point** was exercised; coverage is the dispatcher
   chain (as declared).
5. **The r1 RED run ("10 failed / 2 passed")** could not be reproduced or audited
   — F4.
6. **The r1 test file** (18236 B / `e6c0949c…`) no longer exists in the attempt
   directory or in git; only the r2/r3 revision is auditable.
7. **I did not re-run the I-08-C frozen 13-node file** against either tree (the
   card reports 13/13 on the unfixed tree and 2 expected failures on the fixed
   tree, and correctly predicts that I-08-C's oracle must be re-frozen). I read
   the claim; I did not measure it.
8. **`config/trusted_signer_public_keys.json` remains absent by design
   (I-08-A R-PROV-2).** I verified its absence; I did not test any deployment in
   which a trust anchor exists in production.
9. **Concurrency note:** during this review a sibling session committed to the
   repository (HEAD moved `f6f8bde12d` → `3c4a738e…`) and rewrote the attempt's
   `test_b1_rem.py` and `oracle.md` (r4) in the working tree. All of that is
   `.planning` scope; `git status --porcelain --untracked-files=all -- scripts
   tests config artifacts` was re-verified **empty** afterwards, and the hashes I
   report for `oracle.md`, `test_b1_rem.py`, `decision.md`, `handoff.json`,
   `binding.json`, `commands.json` are the bytes I actually read and executed.

---

## 9. Required before promotion (in order)

1. **F1** — append oracle revision r5 correcting the §R3-2/R3-3 field-count text
   to 10 fields and explaining that `result_sha256` is carried in the *request*
   only, pinned to the sentinel. Append-only: r1–r4 bytes untouched.
2. **F2** — add the "present record is verified even when the label is
   `unattested`" node (an R13 equivalent) to the card's test file, and add the
   corresponding mutation (M6) to the mutation table. Without it the card's own
   proof set does not measure a clause its oracle freezes.
3. **F3** — either implement E21 (`issuer`/`key_id` vs the resolved trust entry)
   or delete the E21 claim from the docstring and list it under "not closed".
4. **F7** — record REM-02 as a documented limitation with the caller-side trap
   still open, and decide (a)/(b)/(c). Do not describe REM-02 as fully closed
   while the only runtime artefact is a class nobody raises.
5. **F4/F5** — preserve raw run outputs under distinct labels, and give
   `decision.md` a freeze-time hash, in the next attempt's protocol.
6. Only then: the owner decides on promoting the three files from
   `iso/fixed/rf/scripts/`.

---

## 10. Report pinning

This report is byte-pinned. `reviewer/report_pin.json` records the digest and
byte count of the report, and `reviewer/REPORT_PIN_VALUE.txt` holds the digest on
one line. **Pinning rule (a hash cannot contain itself):** the hashed bytes are
this file with the final `REPORT_SHA256` line reduced to exactly
the literal sentinel line described in `reviewer/REPORT_PIN_VALUE.txt`
(digest substituted), i.e. the final-byte form, which is
the file as it stands when that last line reads `PENDING`. That single-line swap
is the only permitted difference between the hashed bytes and the bytes on disk.
Verify by reconstructing, not by hashing the file as it stands:

```powershell
$a="C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\B1-I08C-product-fixes\a20260921-01"
$t=[IO.File]::ReadAllText("$a\reviewer_report.md")
$pinned=(Get-Content "$a\reviewer\REPORT_PIN_VALUE.txt").Trim()
$recon=$t -replace ('REPORT_SHA256: `'+[regex]::Escape($pinned)+'`[^\r\n]*','REPORT_SHA256: `PENDING`')
$tmp=[IO.Path]::GetTempFileName(); [IO.File]::WriteAllText($tmp,$recon,(New-Object Text.UTF8Encoding($false)))
[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash([IO.File]::ReadAllBytes($tmp))).Replace('-','').ToLower()
# must print $pinned
```

REPORT_SHA256: `73feb0593b44ffeb448bc5f5b1cea9800f4cc9fb59f40ca19e9aae8038c104fa` (37135 bytes with the line reading PENDING; this line is the substituted digest)
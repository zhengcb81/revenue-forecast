## Revision r6 — F2/REM-41: mutation M6 joins the proof surface; R13-equivalent node pointer

**Appended by the B1-PREREQ card** (`execution_runs/B1-PREREQ/a20260922-01`)
under this oracle's §9 revision policy, on commission of review finding F2
(`reviewer_report.md` §9.2: fold an R13-equivalent node into the card's proof
set and add M6 to the mutation table). Revisions r1–r5 are untouched; the
prefix proof is
`execution_runs/B1-PREREQ/a20260922-01/scratch/append_oracle_r6.stdout.json`
(`frozen_prefix_untouched: true`, marker at `(post-r5 bytes) + 1`).

### R6-1. The measured blind spot (adopted as measured, not re-argued)

The independent reviewer authored mutation **M6** — short-circuit
`validate_publication_attestation` after the closed-set/structural checks
whenever `attestation_status != "host_signed"`, so a present-but-invalid
record becomes ignorable — declared its red set **before running**, and
measured the frozen 12-node file **12/12 GREEN on the M6 mutant**
(declared `{}` = observed `{}`). Every node that carries a record also
carries the `host_signed` label (R2/R3/R4 carry no record; R1/R7 carry the
label), so the r1 §3.1 clause *"a record that does not verify must never be
present-but-ignored"* was load-bearing in the implementation yet unmeasured
by this card's own proof set. F2.

### R6-2. §5 mutation table — appended row (§5 itself is frozen, so the row lives here)

| mutation | revert target | must go RED | must stay GREEN |
|---|---|---|---|
| **M6** | insert `if not claims_signed:` / `# MUTATION M6: only a labelled claim is held to its record.` / `return` immediately after the comment `…so any change to a bound value breaks the signature.` and before the `require(record["payload_sha256"] …)` check in `validate_publication_attestation` — exact bytes frozen in the B1-PREREQ attempt's `oracle.md` §3.2, applied by hash-asserted script (pre-hash `bc2bb4a3…`) **only to an attempt-local copy** | the new node `test_rem41_a_present_record_is_verified_even_when_label_is_unattested` | all 12 frozen nodes (their declared red set under M6 is `{}` — the blind spot, now declared explicitly rather than discovered) and the new node's positive control |

Isolation requirement unchanged in strength: on the 14-node surface (12
frozen + 2 new) the declared red set under M6 is exactly
`{test_rem41_a_present_record_is_verified_even_when_label_is_unattested}` —
no missing red, no extra red; measured red sets are recorded in the
B1-PREREQ attempt's `evidence/arm2_node_on_m6.stdout.txt` and
`evidence/arm3_frozen12_on_m6.stdout.txt`.

### R6-3. The node, frozen BEFORE execution

- File: `execution_runs/B1-PREREQ/a20260922-01/test_r13_equiv_rem41.py`,
  sha256 pinned in that attempt's `freeze.json` (entry
  `my_node_r13_equiv_rem41`), written and frozen before any run.
- It imports **this** attempt's frozen `test_b1_rem.py` fixtures and helpers
  (`fake_provider`, `trusted_domain`, `workdir`, `public_key_bytes`,
  `isolated_env`, `_rehash`, `_receipt_of`, `_record_of`, `_with_provider`,
  `_clear_provider`) so nothing is re-implemented; **neither this oracle's
  §4/§5 text nor `test_b1_rem.py` is edited** — the 12-node file keeps its
  pin `636b43c8d8e1dc59ccfa36d7c71125ea9b8665222f587510444a3656b6700c16`.
- Pre-registered arms (declared before running; B1-PREREQ `oracle.md` §3.2):
  fixed tree ⇒ 2 passed / rc 0; M6 mutant ⇒ node RED + control GREEN / rc 1;
  frozen 12-node file on the M6 mutant ⇒ 12 passed / rc 0; unfixed tree ⇒
  node RED + control GREEN / rc 1. Raw stdout of every arm is preserved
  byte-for-byte under that attempt's `evidence/` (evidence protocol, its
  finding F4).

### R6-4. What this revision does NOT change

No §4 case, no §3 design point, no E-code, no security expectation changes.
M6 is an **addition** to the mutation proof surface (strengthening it); it
does not amend the declared red sets of M1–M5 measured in r4.

### R6-5. Append-only proof

`execution_runs/B1-PREREQ/a20260922-01/scratch/append_oracle_r6.stdout.json`:
`append_marker_offset` = (post-r5 byte count) + 1, `structural_ok: true`,
`frozen_prefix_untouched: true` with re-checks of the 27697, 31081, 35840,
39287 and post-r5 prefix hashes.
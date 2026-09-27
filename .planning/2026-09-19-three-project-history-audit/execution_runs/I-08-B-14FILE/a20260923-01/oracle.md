# ORACLE — I-08-B-14FILE (frozen BEFORE any run of this card)

- card: **I-08-B-14FILE** (authorization-execution card, 14-file face)
- attempt: `a20260923-01`
- plan: `2026-09-19-three-project-history-audit`
- parent: session-bfecd191-fbc3-4a66-8ed1-6562479bf102
- frozen at: 2026-09-23, after source investigation, **before any test/pytest run of this card**
- human confirmation: unavailable (subagent of a live agent; same basis as RF-STEP9-TRIAGE oracle 追认 — pending confirmation question carried in the final report)

## 0. Authorization lineage (what this card executes)

1. **I-08-B accepted attempt** `execution_runs/I-08-B/a20260919-01/handoff.json`
   (`status = accepted_scoped`, round-4 independent verdict), `next_action` verbatim:
   > "HANDOVER to plan/owner: the round-4 independent verdict is accepted_scoped on the technical and
   > delivery surfaces. **Apply the SAME 14 files (9 edited + 5 added) to the product repo from a card
   > authorised to write it**, and carry the 8 OPEN items (E31, OPEN-D1/D2/D3/D5/D6/D7 and the
   > UNRESOLVED-BY-DESIGN registry anchor field names) plus the three P3 items (R4-1/R4-2/R4-3) forward."
   `changed_paths.production_patch_required_later` repeats: "the SAME 14 files (9 edited + 5 added) must be
   applied to the product repo by a card/owner authorised to write it". **That card is this card.**
2. **RF-STEP9-TRIAGE** `execution_runs/RF-STEP9-TRIAGE/a20260923-01/decision.md` §1 row #2 (finding #2):
   the false-green `tests/test_attestation.py::AttestationTests::test_configured_provider_means_host_signed_publication`
   is `family-card-needed (本卡不动)` → "落 I-08-B `a20260919-01` 14 文件（其 handoff.next_action:
   'from a card authorised to write it'）"; §3: "B1 decision.md §5 原文 'rewriting it is I-08-B's item' …
   **本卡改它=越权 → STOP**". handoff receipt: "① #2 → `I-08-B-14FILE/a20260923-01` 已派".
3. **B1** `execution_runs/B1-I08C-product-fixes/a20260921-01/decision.md` **§4 item 5**: the test "is now RED
   on the fixed tree. This is the false-green source I-08-A §7.1 identified by name and required to be broken
   before the new semantics land; **rewriting it is I-08-B's item**, and its expected failure reason is the
   frozen E32 (`provider_capability_unproven`), observed here as `attestation_capability() is False`."
   §5.3: 100-test collateral sweep — the ONLY failure is that node, "the repo's only false-green source".
4. **I-08-A §7.1** (`execution_runs/I-08-A/a20260919-01/decision.md` L355-377): frozen acceptance preconditions
   for I-08-B — (1) RED first with the same assertion/input (capability False, unattested, E32);
   (2) **不得直接改写该断言来让它变绿**; rewrite the TEST INTENT to "bound provider completed one successful
   handshake" with an isolated fake provider + isolated trust domain (test key never into repo `config/`);
   (3) a reverse-case table E01/E02/E32/E03/E04/E08 with "never host_signed, never use existence as capability";
   (4) raw rc+stdout into evidence.

**Acceptance face of this card = I-08-B's own oracle conditions** (`I-08-B/a20260919-01/oracle.md` §0, §7, §9)
and its accepted handoff's frozen measurements. This card changes no expected value of that oracle.

## 1. The 14 files (frozen list — count is unambiguous: 9 edited + 5 added)

Column `before@carrier` = I-08-B's patch base (`before/baseline_tree/rf` = current product for 7/9 files;
`before/source_hashes.txt` values noted where they differ). Column `before@RF` = this card's measurement of the
live RF product tree at freeze time. Column `after` = carrier after-sha from
`I-08-B/binding.json.post_run_measurements.artifact_hashes`, independently re-measured from `iso/rf` this session
(all 14 matched byte-for-byte).

| # | file (product path) | role | before@carrier (patch base) | before@RF (live tree) | after (authorized bytes) |
|---|---|---|---|---|---|
| 1 | `scripts/contracts/constants.py` | edited | 278e3e02df15e556f4851b46711a2f36aac5b7e6a9820c27e0ca31b02858d0ae | 278e3e02… (SAME) | a299e95055f22f3d97967e2fdab0522120a9011d6bd9fda213b000904a7f2564 |
| 2 | `scripts/contracts/evidence.py` | edited | 054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561 (carrier `source_hashes` says older bc5e4c53 — patch was generated from baseline_tree) | 054e364a… (SAME as patch base) | 4b422cd431c117047b7452cce9c756e9f8719c99c65b2b395c021f3da54af807 |
| 3 | `scripts/publication_registry.py` | edited | 29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344 (source_hashes older 44662744 — same note) | 29aaae4f… (SAME) | 172092e067f0e830e2e9c887b274b4560c7c4b300c5ac5088e7ff98920cda003 |
| 4 | `scripts/revenue_core.py` | edited | 1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae | **8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883 — DRIFT (B1 ec307d20)** | aec1cf69a386b779a5b339e56a106062ceffa401152839d00153d99ba3e9d12f |
| 5 | `scripts/revenue_publication.py` | edited | 183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba | **bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0 — DRIFT (B1 ec307d20)** | e311b2bb5079e1a211c8ae7e35ad716fce0b0c8c6208f5e0a24cdfdf3da50aba |
| 6 | `scripts/trust_anchor.py` | edited | 9abdcec55a524574b55e0111f513338f79a486f536985d036b94b4a71ba1310c | 9abdcec5… (SAME) | a6049b580182ee99b6e02cb501562af2239c89ffa115a0aca6b1cd332bf9151f |
| 7 | `tests/test_attestation.py` | edited (the false-green rewrite) | d1b7cf036b22867d62e235002e1d1736586ec45a2f888e84896504b7b7915404 | d1b7cf03… (SAME) | 17934e28a894ff1d3d95cb14d1665fb3ba27f7e6c587d916f2cdd4d2f547f5c4 |
| 8 | `tests/test_single_owner_guard.py` | edited (CONFLICT-1 hardening) | ae6f158c8a4b421e0393a5c7fcf3cab2ebce40b3d50a20e852cc73b2c5e26c2d | ae6f158c… (SAME) | b5969ba6397fbe2d37f3000bf0ca301f505bfd056ee7cbbe9ba9b8f691774a65 |
| 9 | `tests/golden_behavior_hashes.json` | edited (documented refresh) | 4e68b98cc16027bc370900e346f8554245e2e2155d0e22edc4beadba5f2933b5 | 4e68b98c… (SAME) | c6b13adabefac751e3f494cb229041f828f92ef59d782744b3b555ef8fda0c54 |
| 10 | `scripts/attestation_protocol.py` | **added** | ABSENT | ABSENT | 6e58cde211bbf53557c89bcb1db31bcb77bdad5f678a1725520ebc1565b28db4 |
| 11 | `tests/test_attestation_provider_protocol.py` | **added** | ABSENT | ABSENT | 8e535d805cd1d09b75bfd31954e2c98ef56c0fbfdfc737d83df4619f40be6ddb |
| 12 | `tests/test_attestation_legacy.py` | **added** | ABSENT | ABSENT | 729d49cbf4bfb72fcb00b948c16fa699a48069efe96104282444836a243797ae |
| 13 | `tests/test_publication_attestation_contract.py` | **added** | ABSENT | ABSENT | 306407ec2f2b0ffa2220ab7518624051e6a31b7559b56541d1a46e97c51306a2 |
| 14 | `tests/e2e_support/i08b_fake_provider.py` | **added** | ABSENT | ABSENT | e715ca8a34c3fc817a1a06cf9f961118a6f515afe35bdaaff94ea0548bd6d92a |

**Ambiguity check (task §2): NOT ambiguous.** Count (14 = 9+5), file list and per-file bytes are triple-pinned
(carrier handoff `changed_paths`, carrier `changes.diff` headers, carrier `binding.json` after-hashes). No STOP.

## 2. Drift finding + frozen disposition (the only base drift on the 14)

`before/baseline_tree/rf` (the carrier's patch base) vs the **live** RF tree: **7 of 9 edited files are
byte-identical**; exactly **2 drifted**: `scripts/revenue_core.py` (327 changed lines) and
`scripts/revenue_publication.py` (314 changed lines). The drift content is **B1's promoted subset implementation
(commit ec307d20, REM-01(a)(b) + REM-02 doc)** — measured by diff this session: spawn/handshake moved INTO
`revenue_core.py` (`_run_attestation_provider`, L223/230 subprocess), record placed IN the receipt,
`PUBLICATION_ATTESTATION_SCHEMA_VERSION="1.0"`, plus B1-only APIs `attestation_last_failure()`,
`PublicationReceiptOnlyWarning`, `SIGNED_RESULT_SHA256_SENTINEL`.

**Frozen disposition (Option A — verbatim authorized set):**
- The authorization is "the SAME 14 files". This card lands the carrier `after` bytes verbatim for **all 14**
  into a `%TEMP%` scratch copy of the live tree; **RF itself is never written**; delivery = `changes.diff`
  (live-tree → after-tree, exactly these 14 paths).
- Consequence, frozen for disclosure in `decision.md`: the authorized after-bytes of files 4 and 5 **supersede**
  B1's promoted 2-file implementation of the same I-08-A design (fuller accepted_scoped implementation replaces
  the deliberately-reduced review_pending subset; E27 host_signed-without-record stays enforced — at validator
  level per I-08-B T-N46 instead of at builder level). B1-only surface lost: `attestation_last_failure`,
  `PublicationReceiptOnlyWarning`, sentinel constant — measured this session: **no product test/tool imports any
  of them** (grep = only the two files themselves), so no dangling consumer is expected; the regression census
  verifies this empirically.
- **Merge/rebase into B1's 2 files is REJECTED as a frozen option**: the two implementations rewrite the same
  functions with architecturally incompatible record placement (top-level record vs in-receipt) and schema
  (2.0 vs 1.0); the other 12 authorized files assert the top-level/2.0 shape, so a hybrid would break the
  authorized set's internal consistency (its own green face).
- `tests/golden_behavior_hashes.json` exception rule (pre-authorized by the carrier handoff: "requires the same
  reviewed refresh that this attempt performed"): if the carrier's frozen golden values (after column) do not
  match artifacts produced by the live base tree, this card refreshes them with the repo's documented command
  `python tests/test_golden_behavior_lock.py --update-golden`, run twice (determinism = both runs byte-identical),
  and discloses before/after values + count in `decision.md`. Values are never hand-edited.

## 3. Overlap with RF-STEP9-TRIAGE's 7-file changes.diff (frozen)

- TRIAGE 7 files: `tests/adversarial/test_receipt_attacks.py`, `tools/mutation_patrol.py`,
  `tests/test_zr601_asset_facts.py`, `tests/test_zr708_backtest_reverify.py`, `tests/test_fc1102_t2_runner.py`,
  `tests/test_fc1302_scan_health.py`, `tools/daily_t2_runner.py`.
- My 14 files: table §1. **Intersection = ∅** (verified file-by-file). TRIAGE's H1 (receipt_attacks
  host_signed→unattested) and H2 (mutation_patrol `_resign` host_signed→unattested) are therefore NOT in my
  scope; this card's `changes.diff` will not touch those 7 paths (any overlap would fail the diff generator's
  completeness/uniqueness check).
- **Relationship (for `decision.md`)**: H1/H2 adapt tests/tool to E27 (host_signed without a record is rejected)
  as promoted by B1. My after-state keeps E27 enforced (validator-level, I-08-B oracle T-N46); H1's adapted
  build-with-`unattested` stays valid, and (measured, see §4 R10) the *current* product version of
  `test_context_fabrication_is_rejected_by_final_validation` also passes on my after-state (build no longer
  raises; validation raises E27 → `ForecastInputError` as the node asserts). Adoption rule: **TRIAGE's bytes
  stay TRIAGE's** — used verbatim only in a separate compat arm, never copied into my `changes.diff`.
- `tests/test_single_owner_guard.py` (#8 owner-ruling) IS in my 14 (carrier CONFLICT-1/D-08B-08): my after-state
  moves spawn out of `revenue_core.py` into the exempted `scripts/attestation_protocol.py` with the carrier's
  two AST hardening assertions. Effect on TRIAGE #8 is an empirical question, frozen as R4/R6 below and reported
  to the parent either way (this card does NOT close #8's owner ruling; it reports what the authorized bytes do).

## 4. Red → Green → Mutation protocol (frozen expectations, per family)

Interpreter: system `python` 3.13.9 (Anaconda) with pytest 9.1.1 + cryptography 50.0.1 (same stack the carrier
bound). Env for every run: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`, `--basetemp` inside this
attempt, cwd = scratch tree. Scratch root: `%TEMP%\i08b14file\a20260923-01\{before_tree,after_tree,mut*,compat}`.
Every run saves raw stdout + rc under `evidence/`. No network, no git commands, RF read-only.

**Family F1 — attestation false-green (finding #2, the named node)**
- **R1 RED (before_tree, live product bytes)**: `pytest tests/test_attestation.py` → frozen expectation:
  failure SET = **exactly** `{AttestationTests::test_configured_provider_means_host_signed_publication}`,
  reason `AssertionError: False is not true` on `assertTrue(attestation_capability())` — i.e. B1 broke the
  false-green exactly as I-08-A §7.1 precondition 1 required (E32 face). Carried companion evidence (not re-run):
  carrier `before/cmd-run-red1-pytest.stdout.txt` = "1 passed, rc=0" = the pre-B1 **false-green passing** state
  this rewrite exists to kill. Any deviation from the exact-1-failure expectation is recorded, not smoothed.
- **R2 GREEN (after_tree)**: `pytest tests/test_attestation.py tests/test_attestation_provider_protocol.py
  tests/test_attestation_legacy.py tests/test_publication_attestation_contract.py` → frozen: **rc=0, 0 failed**.
  The rewritten intent asserts the TRUE semantics (bounded fake provider + isolated in-temp trust domain →
  `host_signed` + verifiable top-level record; reverse table E01/E02/E32/E03/E04/E08 fail closed;
  `provider_invocations==0` for non-spawned cases; test key never in `config/`).
- **R3 MUTATION (after_tree + original `tests/test_attestation.py` restored, bytes d1b7cf03)**:
  frozen: `test_configured_provider_means_host_signed_publication` **FAILS** (the old "configured ⇒ host_signed"
  assertion cannot pass under handshake semantics — the false-green is dead, RED returns). Additional failing
  nodes from the L2 whitelist-schema drift of the original file are ENUMERATED, not hidden.
  Second mutation leg (product side): after_tree with files 4+5 reverted to the live pre-landing bytes while the
  rewritten test file stays → frozen: R2's handshake node FAILS (the rewrite depends on the landing, and the
  landing depends on the rewrite). False-green can only reappear if BOTH sides revert to the pre-B1 baseline —
  that state is the carrier's documented red1 evidence, cited rather than re-created.

**Family F2 — single-owner guard (CONFLICT-1 / TRIAGE #8 face)**
- **R4 RED (before_tree)**: `pytest tests/test_single_owner_guard.py` → frozen: ≥1 failure, containing
  `test_only_canonical_client_may_use_subprocess_download_adapters` (`revenue_core.py imports subprocess`),
  matching TRIAGE #8.
- **R5 GREEN (after_tree)**: frozen: **rc=0, 0 failed** (spawn lives in exempted `attestation_protocol.py`;
  both carrier AST hardening nodes present and passing).
- **R6 MUTATION (after_tree + original guard file restored, bytes ae6f158c)**: frozen: ≥1 failure —
  `attestation_protocol.py` imports `subprocess` with no exemption → guard fires (red returns).

**Family F3 — golden refresh (CONFLICT-2 face)**
- **R7 RED (after_tree built from only 13 of 14 files — carrier golden NOT yet applied)**: `pytest
  tests/test_golden_behavior_lock.py` → frozen: **FAIL** (artifact shape changed by schema 2.0 + new keys).
- **R8 GREEN (after_tree, carrier golden c6b13ada applied)**: frozen: **PASS**; if it FAILS, apply §2's
  exception rule (documented `--update-golden`, run twice, disclose delta) and record the deviation with hashes.
- **R9 MUTATION (after_tree + original golden 4e68b98c restored)**: frozen: **FAIL** (refresh is load-bearing).

**Compat arm — TRIAGE coexistence (not a family; overlap §3)**
- **R10**: copy of after_tree + TRIAGE `changes.diff` applied verbatim (own minimal unified-diff applier, exact
  context match; no git). Frozen: `tests/adversarial/test_receipt_attacks.py` **3/3 pass** (H1 compatible) and
  `tests/test_zr1102_adversarial_audit.py::test_c4_mutation_patrol_capabilities` **pass** (H2 compatible,
  patrol CLI accepted==0). Also frozen: applying TRIAGE's diff touches ZERO of my 14 paths (applier asserts it).

**Regression surface (scope frozen honestly)**
- **R11 census**: run a curated publication/attestation/report surface on before_tree and after_tree and compare
  failure SETS: `test_attestation*`, `test_single_owner_guard`, `test_golden_behavior_lock`,
  `adversarial/test_receipt_attacks`, `adversarial/test_anchor_attacks`, `test_publication_pipeline`,
  `test_publication_registry`, `test_recognition_bridge`, `test_output_report`, `test_zr1008_new_chain_cutover`,
  `test_zr710_publication_txn`, `test_backtest`, `test_zr1102_adversarial_audit`, `test_zr601_asset_facts`,
  `test_zr708_backtest_reverify`. Frozen rule: **no NEW after-failure** outside the declared families' red
  nodes and nodes pre-declared here; TRIAGE's unapplied-by-me reds (#1/#9 pre-R10, #10-12, #3-7) appear
  IDENTICALLY in both arms or are excluded by name. A full `tests/` census is attempted only if runtime allows;
  its scope (or absence) is disclosed in `handoff.unproven` either way.

## 5. Frozen constraints (failure-stop conditions)

- **RF production tree READ-ONLY**: zero writes outside this attempt dir; before/after content hashes of the
  14 live files re-measured at close; no `git` command of any kind (no add/commit/checkout/apply/status);
  delivery = `changes.diff` only.
- No network. Scratch only under `%TEMP%` + this attempt dir. `PYTHONDONTWRITEBYTECODE=1` (no `__pycache__`
  litter in RF if a run ever points there — all runs point at scratch copies).
- **Zero product-source changes beyond the authorized 14 paths**: `changes.diff` generator fails if any other
  path differs between before_tree and after_tree.
- Test private keys: ephemeral, in-process / temp-dir trust domain only; never into repo `config/`, never into
  a schema-validated document, never logged (carrier rule, carried verbatim).
- No expected value of I-08-B's oracle is changed by this card; OPEN-D1…D7, E31, OPEN-D6, registry-anchor field
  names, R4-1/2/3 stay OPEN/carried (`closed_by_this_card = []`).
- Anti-death living docs: `binding.md`, `commands.md`, `decision.md`, `handoff.md`, `recovery.md` written
  incrementally as evidence lands; the final report goes to the parent via `send_message`.

# B3 — I-05-C delivery/evidence gaps (REM-11/12/13/14) — Independent Reviewer Report

- Plan: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`
- Attempt under review: `execution_runs\B3-I05C-delivery-fixes\a20260921-01`
- Reviewer: independent (not the implementer, not self-signed)
- Reviewed at: 2026-09-21 (reviewer turn following handoff `status = review_pending`)
- Reviewer boundary: read-only. No production file was written; no historical artifact was
  modified. Every re-run was executed in a throwaway copy of the attempt tree under
  `%TEMP%\b3-review-r2\execution_runs\B3-I05C-delivery-fixes\a20260921-01\` (the directory
  basename `B3-I05C-delivery-fixes` was preserved on purpose — see **RF-3**).
  Interpreter: `C:\Miniconda\python.exe` 3.13.9 / pytest 9.1.1, `-X utf8 -B -p no:cacheprovider`.
- The byte pin of this file is recorded in `reviewer_report.sha256` (same directory).

---

## 1. VERDICT

**ACCEPT — with one new P3 finding (RF-1) and four documentation/precision findings
(RF-2..RF-5), and with CF-1 accepted only as a *registered* carry.**

All nine implementer claims are substantiated. Every RED/GREEN/mutation number was
reproduced from scratch, in a copy, with identical failing-node sets. The most
load-bearing claim — the M4b vacuity proof — is **confirmed and strengthened**: I completed
the 2x2 myself and showed the untouched 20-test carrier passes 20/20 on *both* the stale
`A55602E5` bytes and the production `225FECDD` bytes, so the original I-05-C
`w05b-regression` record was vacuous as regression evidence about production.

Two conditions attach to acceptance (neither is a defect in the fix itself):

- **C1 (blocking for promotion, not for this verdict)** — CF-1 must be entered in
  `REMEDIATION_REGISTER.md` before `iso/fixed/rf_scripts/company_wiki_source.py`
  (`7D1BD8F9…`) is promoted into `RF:scripts/`. The register currently has **no CF-1 row**
  and still lists REM-11..14 as `待修`; as it stands CF-1 exists only inside this attempt
  directory and will be lost exactly the way the original I-05-C reviewer report was (CF-4).
- **C2 (recommended before this conftest is reused)** — RF-1: the attempt's own
  `iso/conftest.py` binding guard does not check what its docstring says it checks, and its
  `sys.path` prepend order is the inverse of its stated intent. It is contained here by
  in-test explicit binding, so it does not invalidate any recorded result, but it must not be
  carried forward as "the mechanism that prevents REM-12 recurring".

**Do not promote `7D1BD8F9…` from this verdict.** Promotion is an owner decision; this report
only adjudicates the evidence.

---

## 2. CLAIM-BY-CLAIM VERIFICATION

Independent recompute (my own reads + SHA256, not the attempt's JSON):

| artifact | reviewer-computed SHA256 | bytes | claim | verdict |
|---|---|---|---|---|
| `RF:scripts/company_wiki_source.py` | `225FECDD7E48938A97C68724318F0860602A4B86A8D9E834A257243480094294` | 19364 | unchanged | **MATCH** |
| `RF:tests/test_fc904_artifact_selection.py` | `8C0B8E390307C33B8C03D51FD742CA984BA6774B84638500FD8D7CDD7D46BF3F` | 10666 | unmodified | **MATCH** |
| `CW:…/source_catalog/artifact_dag.py` | `0C8B1D6D1A28C94F27EA8FFE52A98D67B84F0A49653931B9C9317E27DA6C20D1` | 2814 | copied not edited | **MATCH** |
| `iso/fixed/rf_scripts/company_wiki_source.py` | `7D1BD8F9D9122DC4A99465A8F9201E855417A5D0756F5BFDD6D404F7CA9E48CE` | 20545 | fixed | **MATCH** |
| `iso/fixed/tests/retry-count-vs-artifact-count.json` | `F3B9A9B22BBAA869B21C4E7871BB74C06F747EEB69F6063C9648622437B58531` | 3264 | fixed | **MATCH** |
| `iso/fixed/cw_source_catalog/artifact_dag.py` | `0C8B1D6D…6C20D1` | 2814 | verbatim copy | **MATCH** |
| `iso/pristine/rf_scripts/company_wiki_source.py` | `225FECDD…094294` | 19364 | pre-image | **MATCH** |
| `iso/pristine/tests/retry-count-vs-artifact-count.json` | `A3DD418F31B75753FB60F5C1E00AE386C4F33FBF02E6F72A5D74807C794FE326` | 1408 | frozen pre-image | **MATCH** |
| `I-05-C:oracle.md` | `E4004563B8BBC403D7C8E3856A5FCB95AC3107E57FE891D7B848C5E9834CB34B` | 4454 | frozen | **MATCH** |
| `I-05-C:retry-count-vs-artifact-count.json` | `A3DD418F…4FE326` | 1408 | frozen | **MATCH** |
| `I-05-B:iso/tests/test_w05b_verified_artifact_read.py` | `F9845F170E0EFF4B705993A3659CC0D88EE7C476AE019641B712E4968DF9595D` | 22928 | frozen | **MATCH** |
| `I-05-B:iso/checkout_scripts/company_wiki_source.py` | `A55602E5C2881E64F888F39A224F82DB918190009DF3901497A5CD1E252E94AE` | 18651 | stale, untouched | **MATCH** |
| `I-05-C:iso/tests/test_w05c_minimal_production.py` | `D13BF505E49D9DC1A49907EAE9BDA4590692E2EECFC331CD5D9053C5917AAB82` | 31640 | frozen | **MATCH** |

### Claim 1 — production unchanged: **VERIFIED, with a stronger proof than the attempt's**

- `after/integrity.json` matches my recompute for all three production files, and its
  `expected` values are independent of the observed values for the two RF files.
- **Independent proof by git (stronger):** `RF` is a git repo and both
  `scripts/company_wiki_source.py` and `tests/test_fc904_artifact_selection.py` are tracked
  and `git diff HEAD` is **empty**; `git status --porcelain -- scripts tests` is **empty**.
  So no tracked production source or test was written.
- mtimes corroborate: `company_wiki_source.py` 2026-09-20 16:34:39, `test_fc904_…py`
  2026-09-20 16:23:44 — both predate the attempt window (2026-09-21 21:48–22:25).
- `CW:artifact_dag.py` shows as ` M` against **CW's own HEAD**, but that is a 2-line
  comment-only working-tree change (`# historical compatibility only`,
  `# D-W05: direct from normalized, not markdown`) that is the already-landed I-05-C change,
  not a B3 write. B3's copy is byte-identical (`0C8B1D6D…`). Correctly described as
  "copied not edited".

### Claim 2 — fixed artifacts: **VERIFIED** (table above).

### Claim 3 — REM-11: **VERIFIED**

- `_production_scope(roles, reusable, artifact_read)` is defined at `iso/fixed/…:128-151` and
  is called from **both** branches: `bundle=None` → `_production_scope(roles, set(), [])`
  (line 193); bundle-present → `_production_scope(roles, reusable, artifact_read)` (line 227).
  The helper body is semantically identical to the old bundle-present inline block
  (`if role in artifact_read: continue; needs.add(role); for ancestor … if ancestor not in
  reusable: needs.add(ancestor); return sorted(needs)`), so the accepted I-05-C behaviour is
  preserved by construction.
- `_dag_closure` is **absent** from the fixed file (grep: 0 hits); the production file still
  has it. The deletion is safe: it is private, unprefixed by `__all__`, and the only reference
  in production was the `bundle=None` line that was replaced.
- **RED arm re-run by me:** `8 failed, 27 passed` — failing set is byte-identical to the
  recorded `CTRL-C-prod-w05c` set (5 parametrized `test_no_bundle_scope_is_request_closure`
  ids + `…normalized_only…` + `…subset_never_exceeds…` + the REM-13 docstring test).
- **GREEN arm re-run by me:** `35 passed`. `19` I-05-C carrier nodes + `16` B3 nodes = 35 ✔.
- 31-subset invariant present and real: `for mask in range(1, 1 << len(roles))` (line 973) over
  5 roles = 31 non-empty subsets; it asserts both directions
  (`set(producers) <= allowed` and `set(requested) <= set(producers)`), and it is RED under M1.
- **Minor imprecision (RF-2):** the claim's "**8 new tests**" is the *RED count*, not the new
  test count. The attempt actually adds **16** W05C nodes (11 in `TestW05CXBundleNoneScoping`,
  2 docstring, 3 retry-evidence), of which 8 are RED on unfixed bytes. The claim as written in
  `handoff.json`/the brief reads as if only 8 tests were added.

### Claim 4 — REM-13: **VERIFIED**

`iso/fixed/…:161-187`: the docstring now states the request-closure readability rule, the
AR-03 ancestor gate, the provenance condition for `consumer_analysis`, and
`producer_events = requested readable-excluded roles + non-reusable ancestors`. The stale
phrases are gone: grep for `"DAG closure"` → 0 hits, `"transitive dependents"` → 0 hits in the
fixed file. The `bundle=None` rule is explicitly added ("…follows the SAME request-scoped rule
with an empty reusable set… So a `normalized`-only request produces only `normalized`, while a
request naming all roles still produces all of them."). Both docstring tests pass GREEN and
the wording test is exactly 1 RED under M2.

### Claim 5 — REM-14: **VERIFIED — and the diagnosis is independently correct**

I re-derived the numbers from the frozen carrier source (not from the attempt's JSON):

| frozen test (in `I-05-C:iso/tests/test_w05c_minimal_production.py`) | `fail_count` | `max_retries` | calls | artifacts | JSON row |
|---|---|---|---|---|---|
| `test_llm_fails_first_succeeds_second` | 1 | 3 | 2 | 1 | row 1 ✔ correct |
| `test_parser_fails_no_artifact` | 999 | 3 | 3 | 0 | row 2 ✔ correct |
| `test_invocation_trace_accuracy` | 3 | 4 | **4** | **1** | row 3 ✔ **CORRECTED** |
| `test_retry_count_vs_artifact_count_diverge` | 2 | 3 | 3 | 1 | row 4 ✔ added |

So row 3's `4 / 1` really do belong to `test_invocation_trace_accuracy`; the named diverge test
is `fail_count=2 → 3 calls`. **The record was wrong, not the test.** Frozen test code untouched:
the production FC-904 file is git-clean, and no test file was edited to fit the record.
The frozen I-05-C JSON still carries the misattribution — verified by reading it
(`row 3.test = "test_retry_count_vs_artifact_count_diverge"`, `retry_count: 4`, no
`_correction` key) and by git (tracked, `git diff HEAD` empty). The new test
`test_retry_evidence_frozen_source_was_not_edited` asserts exactly that, so append-only
discipline is now *pinned by a test*, which is better than a prose claim.

### Claim 6 — REM-12 re-pointed, not refreshed: **VERIFIED**

- `iso/fixed/tests/test_w05b_verified_artifact_read.py` = frozen carrier (F9845F17) + a
  binding block + 3 B3 tests. Diff vs the frozen carrier: **1 line removed** —
  `sys.path.insert(0, str(ISO_ROOT / "checkout_scripts"))` — and 118 lines added. Source
  coverage 99.83%; all 20 carrier test bodies and assertions are intact.
- **My re-runs:** `23 passed` on production bytes (`B3_BYTES=production`) **and** `23 passed`
  on fixed bytes. Both match the record.
- The binding is real: the fixed-run provenance assertion
  (`test_bound_bytes_match_the_declared_hash`) compares the loaded module's SHA256 against
  `7D1BD8F9…`/`225FECDD…` depending on mode, and M4a shows it is not vacuous (2 RED).

### Claim 7 — mutation proof: **VERIFIED, all four reproduced with identical node sets**

| # | my run | declared | node set identical? |
|---|---|---|---|
| M1 (revert REM-11) | `9 failed, 26 passed` | `9 failed, 26 passed` | **yes** (all 9, incl. `default_request_is_universe_scope` + `explicit_all_roles_matches_default`) |
| M2 (revert REM-13) | `1 failed, 34 passed` | `1 failed, 34 passed` | **yes** (exactly the docstring node) |
| M3 (revert REM-14) | `2 failed, 33 passed` | `2 failed, 33 passed` | **yes** |
| M4a (bind stale iso) | `2 failed, 21 passed` | `2 failed, 21 passed` | **yes** (both `TestB3W05BProductionBinding` nodes) |

### Claim 7b — M4b VACUITY PROOF: **CONFIRMED, and independently strengthened**

This was my highest-priority check, because it is the claim that retroactively invalidates the
I-05-C `w05b-regression` evidence.

What the implementer ran: a probe (`test_aaa_provenance_probe.py`, 2 passed) that binds the
I-05-B stale file by explicit location and records it, then — in a **separate pytest process** —
the frozen carrier with `-k TestW05B` (20 passed). I re-ran both: `2 passed` / `20 passed`.

Because those are two separate processes, the probe's `bound_bytes.json` is *not* literally the
carrier's binding. So I built my own faithful reproduction from frozen bytes only:

- `<tmp>\vacuity_repro\iso\tests\test_w05b_verified_artifact_read.py` = frozen `F9845F17` (verified)
- `<tmp>\vacuity_repro\iso\checkout_scripts\` = full byte-identical copy of the I-05-B
  `iso\checkout_scripts\` (all 5 files hash-MATCHED against the I-05-B originals, including
  `company_wiki_source.py` = `A55602E5…`)
- result: **20 passed** against `A55602E5…`
- then, same untouched carrier, with production `225FECDD…` placed in `checkout_scripts\`:
  **20 passed** as well.

**2x2 established: the 20 carrier tests cannot distinguish the stale bytes from production
bytes. ⇒ The I-05-C `w05b-regression` "20/20" was vacuous as regression evidence about
production. Claim confirmed.**

Two fidelity notes that *bound* the proof rather than weaken it:
1. The I-05-B checkout carries no `artifact_dag.py` (only `artifact_handle.py`), so
   `ROLE_DEPENDENCIES` resolves through the namespace-package merge to `CW/src` — the *same*
   DAG in both arms of my 2x2, so the comparison is apples-to-apples and the conclusion holds.
2. The probe's `bound_file` field names the I-05-B original path while the carrier actually
   loads the byte-identical copy staged under `scratch/vacuity/checkout_scripts/`. Same SHA256,
   so the reading is unaffected; the recorded path is one indirection removed from the binding.

### Claim 8 — FC-904 conflict is not real: **VERIFIED (see §3 adjudication)**

### Claim 9 — extra regression (`zr706`, `fc905b`): **VERIFIED**

- My re-run: production `10 passed` / `6 passed`; fixed `10 passed` / `6 passed` — 16/16
  identical on both byte sets, matching the record.
- The vendored copies are **additive-only**: diff vs the production suites = **0 lines removed**,
  29 lines added (the `_B3` binding preamble). No production assertion was loosened.
- The fixed-mode preamble binds by explicit file location and asserts `__file__`; the
  production-mode preamble asserts only `basename(__file__) == "company_wiki_source.py"` — a
  weak assertion, but harmless here because the only `company_wiki_source.py` reachable on that
  `sys.path` is the production one (I verified the production hash). Recorded as an observation,
  not a defect.

### Baseline reproduced

Pristine `before/tests/` carriers against untouched production bytes: **W05C 19 passed /
FC-904 11 passed / W05B 20 passed** — identical to the I-05-C record, so the starting point is
reproduced independently.

---

## 3. ADJUDICATION — FC-904 `test_no_bundle_all_produced` vs the I-05-C scoping rule

**Ruling: "not a genuine conflict" is CORRECT. No owner ruling is required.**
**Ruling: the recorded residual semantic shift is ADEQUATE.**

Reasoning on the merits (independently derived, then compared with the frozen oracle):

- FC-904 requests the **default** tuple, which names all five roles. Under the new rule the
  result is *requested ∪ transitive ancestors of requested*; because all five are requested,
  the result is all five. The frozen assertion `read == [] and produced == sorted(ALL_ROLES)`
  therefore holds with **zero** edits. Confirmed mechanically: the re-hosted FC-904 copy is the
  production file with **0 assertion lines removed** (only the 8-line module docstring and the
  `ROOT = Path(__file__).resolve().parents[1]` constant line differ — see RF-3), 11 frozen test
  defs preserved, and `GREEN-fc904 = 16 passed` (11 frozen + 5 B3).
- The conflict was genuinely *assessed* rather than assumed away, and I can now confirm the
  counterfactual empirically. **My independent mutation M5** narrowed the default tuple to the
  four active-DAG roles (dropping compatibility-only `markdown`), a change no listed mutation
  covers:

  | M5 result | detail |
  |---|---|
  | `fixed/tests/test_fc904_artifact_selection.py` | **10 failed, 6 passed** |
  | frozen nodes that go RED | `test_no_bundle_all_produced`, `test_prepare_source_unavailable_envelope_all_produced`, `test_ar01_valid_roles_read`, `test_ar02_only_summary_missing`, `test_ar03_normalized_missing_dag_invalidation`, `test_ar04_nothing_reusable`, `test_ar06_consumer_analysis_provenance_mismatch`, `test_prepare_source_receipt_sourced_from_bundle` |
  | `test_w05c_minimal_production.py` | 2 failed — `test_no_bundle_default_request_is_universe_scope`, `test_no_bundle_explicit_all_roles_matches_default` |

  So the oracle's advance prediction was **accurate**: narrowing the default *would* have been a
  genuine conflict. The conflict was avoided by resolving it the right way (keep the frozen
  default tuple; close the subset hole), not by wishful reading. This materially raises my
  confidence in the D1a verdict.

- **Residual semantic shift — adequacy.** Recorded in `oracle.md` D1a, `decision.md` D1a,
  `handoff.json:fc904_conflict_resolution`, and — best of all — pinned by a test docstring
  (`test_no_bundle_default_request_is_universe_scope`). The statement is accurate: pre-fix the
  no-bundle result was independent of `roles` (a global produce-everything constant); post-fix
  it is a function of `roles`. Two additions I record as part of the ruling rather than as
  defects:
  1. The shift makes the **default tuple load-bearing as a contract**: it, not the no-bundle
     branch, is what keeps FC-904 green. This is now positively mitigated — the two new tests
     above fail if the default tuple is narrowed, i.e. the contract is pinned by B3's own tests,
     not only by FC-904's incidental semantics. That is the right mitigation and I accept it.
  2. On the **live path** the shipped behaviour is unchanged: `source_preparation.py:139` calls
     `select_artifact_roles(handle)` with no `roles=`, so requested == the full default tuple and
     old and new rules agree. REM-11 therefore closes a *latent* hole (any future subset caller,
     or a narrowed default) rather than fixing an observed production defect. The implementer
     states this in `handoff.json:open_questions`; I confirm it is true and that no
     receipt-level behaviour change is claimed anywhere.

  No owner ruling needed. The one thing an owner *should* be told explicitly at promotion time
  is addition 2 — that the fix is preventative — so that it is not oversold as fixing an
  observed defect.

---

## 4. ADJUDICATION — CF-1 (`RF:scripts/source_preparation.py:134-138`)

**Ruling: ACCEPT AS CARRIED — conditional on registration (C1). Do not require the edit now;
do require it before promotion.**

The text I verified at those lines:

```
134:  # FC-904: artifact selection is DAG-minimal and SOURCED from the envelope
135:  # bundle (FC-902) via the selector — the unsourced
136:  # payload.get("selected_artifacts") path is removed.  artifact_read =
137:  # roles with a verified artifact (producers do not run); producer_events =
138:  # the DAG closure of the non-reusable roles (never a blind full recompute).
```

CF-1 is accurate, and the comment is now **doubly** wrong: `producer_events` is neither a
downstream "DAG closure" nor "of the non-reusable roles" — it is the ancestor-closure of the
*requested* roles. It is the only in-file explanation at the live call site.

Why I accept the implementer's discipline rather than requiring the edit:

- REM-13 as scoped names the `select_artifact_roles` docstring only. `source_preparation.py` is
  inside card I-05-C's allowlist, but widening *this* card's allowlist by convenience is exactly
  the step the execution protocol forbids. Refusing to widen scope to fix a P3 comment is
  correct reviewer-facing behaviour, and the alternative (silently editing a file outside the
  named scope) would be worse.
- `source_preparation.py` mtime is 2026-09-20 16:34:41 — untouched; the stale wording predates
  this attempt. Nothing was made worse here.
- Both `decision.md` (D3, with the rejected alternative spelled out) and `handoff.json`
  register it with the exact line range. The reasoning is auditable.

Conditions attached:

1. **C1 (required):** add CF-1 to `REMEDIATION_REGISTER.md`. I checked: the register has rows
   for REM-11..14 and a B3 row, but **no CF-1 row**, and REM-11..14 still read `待修` with no
   reference to B3's resolution. A carried finding that lives only in an attempt directory is
   not carried — CF-4 in this same attempt is the proof of that failure mode.
2. **Required before promotion:** either fold the comment fix into the batch that next touches
   `source_preparation.py`, or fix it at promotion time. Promoting `7D1BD8F9…` while the
   neighbouring call-site comment still asserts the old rule reproduces the REM-13 defect class
   in the very file pair the fix exists to make consistent.
3. Suggested wording, for the eventual editor (a comment-only change; no behaviour):
   `producer_events = requested missing roles + their non-reusable ancestors`.

---

## 5. FINDINGS

### RF-1 — NEW, P3: the attempt's `iso/conftest.py` binding guard does not implement its own claim, and its `sys.path` order is inverted

`iso/conftest.py:66-84` says it will "fail the session if the fixed sources are not the ones
the importer will find". It does not: it only asserts `FIXED_RF in sys.path` and
`fixed_cws_exists`. The value it actually computes, `find_spec_origin`, is recorded but never
checked.

And the prepend loop (`conftest.py:36-40`) inserts in the order
`(FIXED_CW, FIXED_RF, RF/scripts, CW/src)`, each at position 0 — so production ends up
**ahead** of the fixed copy, the inverse of the docstring's stated intent ("attempt-local fixed
sources first … then the production repos").

**Evidence (my own isolated run).** A single fresh `B3_BYTES=fixed` W05C run in a clean copy:

- `scratch/binding_state.json` → `sys_path_head = [CW/src, RF/scripts, iso/fixed/rf_scripts,
  iso/fixed/cw_source_catalog, iso, …]` — production at index 1, fixed at index 2.
- `find_spec_origin = C:\…\revenue-forecast\scripts\company_wiki_source.py` (**production**),
  while `fixed_rf_on_path: true`; **the session did not raise**.
- `scratch/module_provenance.json` → `company_wiki_source` = `7D1BD8F9…` / 20545 in that run
  (correct), because the *test module* binds explicitly. In the **attempt as delivered**, the
  same file records `225FECDD…` / 19364 — it is a last-writer-wins file and the last
  conftest-loaded run was the production control `CTRL-D`. `handoff.json` lists
  `scratch/module_provenance.json` in `evidence_paths` and in `isolation.how_binding_is_proven`,
  so as delivered **the file cited to prove which bytes ran reports the production bytes.**

Why this is P3 and not P2: the operative byte proof in this attempt is *in-test* and
hash-pinned (`iso/fixed/tests/test_w05c_minimal_production.py:71-76` binds by
`spec_from_file_location` and raises unless `__file__ == _TARGET_ORIGIN`;
`TestB3ProductionProvenance::test_bound_bytes_match_the_declared_hash` asserts the SHA256;
`TestB3W05BProductionBinding` asserts identity + the stale-hash exclusion; the vendored
`sibling suites do the same for fixed mode). I re-ran every arm and obtained the recorded
results, so no recorded number is wrong. But had any suite relied on `sys.path` instead of
explicit binding, the fixed run would have silently executed production bytes — the REM-12
failure mode one layer up — and the guard would not have caught it.

Recommended remediation (whichever the owner prefers, but not "leave as is"):
either (a) make the hook assert `find_spec_origin == FIXED_RF/company_wiki_source.py` in fixed
mode and fix the prepend order (reverse the tuple, or build `sys.path[:0] = [...]`), or
(b) delete the guard claim from the docstring and remove `scratch/module_provenance.json` from
`evidence_paths`, replacing it with the in-test provenance nodes. **(a) is preferred if this
conftest is to be reused.**

### RF-2 — NEW, P4: "8 new tests" is the RED count, not the added-test count

REM-11 adds **16** W05C nodes (11 + 2 + 3), of which **8** are RED on unfixed bytes. The brief
and `handoff.json:28` say "8 new tests incl. the reviewer's `normalized`-only counterexample +
a 31-subset exhaustiveness invariant". Documentation precision only.

### RF-3 — NEW, P4: the re-hosted FC-904 carrier is *not* literal-verbatim, and one new assertion is location-dependent

Two distinct points:

1. Diff of `iso/fixed/tests/test_fc904_artifact_selection.py` against production FC-904:
   **0 assertion lines removed**, but **10 lines removed** overall — the 8-line module docstring
   and `ROOT = Path(__file__).resolve().parents[1]`. The hard-coded `ROOT` is *required* for
   re-hosting (under `iso/fixed/tests/`, `parents[1]` is `iso/fixed`, not the RF root) and
   restores the original line's effect, so the change is sound. But the file's own docstring
   says the original is preserved "byte-for-byte in spirit and unmodified in content", which is
   a hedge. The precise, defensible statement is: **every frozen test body and assertion is
   unmodified; the module docstring and the import-scaffolding constant were adapted for
   re-hosting.** (The W05B/W05C re-hosts are cleaner: exactly one removed line each — the
   `ISO_ROOT/checkout_scripts` `sys.path` insert that REM-12 is about.)
2. `iso/fixed/tests/test_fc904_artifact_selection.py:379` asserts
   `"B3-I05C-delivery-fixes" in str(resolved)`. That is a path-string probe, not a byte probe:
   it **fails if the tree is relocated** (I hit it when first staging my copy under a different
   directory name; it passes in place and passes again once the directory basename is
   preserved). The preceding line (`resolved == expected`) already proves binding, and
   `test_bound_bytes_match_the_declared_hash` proves the bytes, so the extra string check adds
   no assurance and adds a false-failure mode. Recommend deleting line 379's string assertion.

### RF-4 — NEW, P4: the REM-14 test re-derives from a hand-maintained duplicate, not from the source

`TestW05CXRetryEvidenceAttribution.TEST_ARGS` (lines 1089-1094) hard-codes
`fail_count`/`max_retries` per test name. Its docstring claims it "re-derives each row's numbers
from the real test source", which overstates it: a future change to the carrier's `fail_count`
would move the real numbers while `TEST_ARGS` stayed put, and the test would keep passing against
the corrected JSON. I verified all four `TEST_ARGS` entries against the carrier source today —
they are **correct** (1/3, 999/3, 3/4, 2/3) — so no evidence is wrong. Optional hardening: parse
the carrier with `ast`/regex, or reference the numbers via the same constants.

### RF-5 — NEW, P3 (bounded): `after/integrity.json` does not verify the I-05-C oracle

`handoff.json:188` says `after/integrity.json` "compares every frozen hash against its recorded
expectation; all matched". For `I-05-C:oracle.md` the `expected_frozen` value is the literal
string `"NOT_REHASHED"` — recorded but never compared. Minor in effect: I re-hashed it
(`E4004563…`, matching the recorded value) and git confirms it is unmodified since commit
`8b7229c3`, so the artifact is provably intact; only the claim's "every" is wrong. Also note
`after/integrity.json` does not cover the `I-05-C/**`/`I-05-B/**` `iso/**` carriers at all
(see §6), which is the more consequential gap.

### RF-6 — NEW, P4 (bookkeeping, owner-side): the attempt directory was partially committed mid-flight, so git cannot baseline it

Commit `980c9b7a` (2026-09-21 21:16) already contains part of this attempt (`binding.json`,
`decision.md`, `oracle.md`, `before/**`, some `scratch/**`), while the attempt ran 21:48–22:25.
Consequences visible now: a committed scratch file
(`scratch/after_w05c/test_select_only_produces_requ0/alpha_normalized.txt`) is ` D` (deleted
from the tree), and `scratch/module_provenance.json` is ` M` versus the commit (it was rewritten
by a later run). Not an implementer product defect, but it means the attempt's git state is not
a coherent freeze baseline, and `iso/**` is gitignored by plan policy
(`execution_runs/.gitignore`, `*/a*/iso/`).

---

## 6. UNVERIFIED / CANNOT VERIFY

1. **No external baseline exists for the frozen `iso/**` carriers.** `I-05-B/a20260919-01/iso/**`
   and `I-05-C/a20260919-01/iso/**` are gitignored (`*/a*/iso/`) and therefore untracked;
   `git diff HEAD` being empty for them is vacuous. Append-only for those files rests on
   (a) the attempt's own recorded hashes, which I reproduced exactly, (b) the attempt's
   `before/**` copies agreeing with the current `iso/**` reads, and (c) my own reproduction of
   the I-05-B carrier run from the current bytes. The two *tracked* I-05-C artifacts
   (`oracle.md`, `retry-count-vs-artifact-count.json`) **are** proven unmodified by git.
2. **The historical I-05-C `w05b-regression` invocation itself.** I verified its *consequence*
   (stale bytes pass 20/20, so the record was vacuous), not the original command's binding. I
   did not execute the I-05-C attempt's harness, and executing it would have written into frozen
   material, which the boundary forbids.
3. **That `A55602E5…` was genuinely the I-05-B-era production pre-image.** No pre-B3 attestation
   of that hash exists that I could find: `I-05-C/oracle.md` and `I-05-C/handoff.json` do not
   name it. It is consistent (18651 vs 19364 bytes, and it lacks the I-05-C bundle-present
   scoping fix), and commit `980c9b7a`'s message ("I-14-I complete … reviewer dispatched") places the CW
   `artifact_dag.py` comment change before this attempt, but the specific claim "one generation
   behind production" is corroborated by content, not by a recorded hash.
4. **Real-repo behaviour of the promoted fix.** No production write was performed and no
   integration/CLI path was exercised; `prepare_source` end-to-end behaviour is asserted only
   through the monkeypatched receipt test in the carriers.
5. **CF-3** (`scripts/run_card.py` never validates `cases.json` `expected`) — inherited, not
   inspected by me. **CF-2/CF-4** — inherited, not re-adjudicated here.
6. **The original I-05-C reviewer report** — still not archived (CF-4); I could not compare the
   findings against the reviewer's own words, only against the carrier-landing transcription.
7. **The M4b probe's recorded `bound_file` path vs the carrier's actual binding.** The probe and
   the carrier run in separate processes; the staged copy is byte-identical to the I-05-B
   original (hash-verified), so the reading holds, but the recorded path is not literally the
   file the carrier loaded.

---

## 7. FINDINGS I DID *NOT* FIND (negative results worth recording)

- No frozen test assertion was edited anywhere: production FC-904 git-clean and 11/11 test defs
  preserved with 0 assertion lines removed; the W05B/W05C carriers lose exactly one
  `sys.path` scaffolding line each; the vendored `zr706`/`fc905b` copies are additive-only.
- No production write: git-clean tracked sources and tests in RF; CW's only dirty file is a
  pre-existing 2-line comment change unrelated to B3.
- No test-only RED->GREEN attribution: CTRL-C/CTRL-D run the *same* new tests against unfixed
  production bytes and produce exactly the 8 + 1 new-test RED sets, with all frozen assertions
  still green — reproduced by me.
- The bundle-present path is genuinely protected: my oracle-unlisted **M6** (restore the
  downstream closure in the *bundle-present* branch only) → W05C **7 failed, 28 passed**
  (`test_full_sections_pipeline`, `test_dag_compliance_new_active_dag`,
  `test_normalized_sections_still_valid`, `test_second_run_zero_production`,
  `test_select_summary_only`, `test_no_bundle_does_not_regress_bundle_present_scoping`,
  `test_docstring_wording_is_backed_by_behaviour`) and FC-904 **4 failed, 12 passed**
  (`test_ar01_valid_roles_read`, `test_ar02_only_summary_missing`,
  `test_prepare_source_receipt_sourced_from_bundle`, plus the hash-pin node). So the claim that
  REM-11 did not disturb the accepted I-05-C semantics is not merely asserted — it is pinned.

---

## 8. EVIDENCE PRODUCED BY THIS REVIEW (outside the attempt directory)

All under `%TEMP%\b3-review-r2\` (throwaway; nothing written into the plan tree except this
report and `reviewer_report.sha256`):

| file | contents |
|---|---|
| `run_arms.py` / `review_core.json` | core arms with full failing-node lists |
| `run_arms.py baseline` / `review_baseline.json` | pristine-carrier baseline (19/11/20) |
| `run_arms.py vacuity` / `review_vacuity.json` | M4b re-run (probe 2, carrier 20) |
| `run_arms.py zr` / `review_zr.json` | extra selector regression, both byte sets |
| `run_mutations.py` / `review_mutations.json` | M1-M4a re-run + my M5, M6 |
| `carrier_diff.py` / `carrier_diff.json` | re-host vs frozen-carrier diff (removed/added lines) |
| `vacuity_repro\` | my from-frozen-bytes I-05-B reproduction (stale bytes → 20 passed) |
| `prod_repro\` | same untouched carrier on production bytes → 20 passed |
| `M5-reviewer-narrow-default-roles\` | independent mutation: default tuple narrowed |
| `M6-reviewer-bundle-present-closure\` | independent mutation: bundle-present closure restored |

---

## 9. REVIEWER'S REQUESTS — STATUS

| request (from `handoff.json:reviewer_requests`) | status |
|---|---|
| 1. Confirm production byte-identical + nothing written outside the attempt | **CLOSED** (claim 1, git-based) with the CW-pre-existing-change note |
| 2. Confirm `oracle.md` was frozen before the first edit | **CLOSED for content** — `changes.diff` has no `oracle.md` hunk; git shows it unmodified since `8b7229c3`. The *timing* claim ("frozen before implementation") is only attestable by the attempt's own record, since the file was first committed at 21:16 by an unrelated sweep |
| 3. Adjudicate D1a (FC-904) | **CLOSED** — §3, verdict "not a genuine conflict" upheld; counterfactual demonstrated by M5 |
| 4. Re-run the three fixed suites | **CLOSED** — 35 / 16 / 23 reproduced |
| 5a. Re-run CTRL-C/CTRL-D and confirm RED node sets | **CLOSED** — 8 + 1, identical node sets; frozen assertions still pass on unfixed production |
| 5b. Confirm vacuity reading + adequacy of the replacement | **CLOSED** — vacuity confirmed (2x2), replacement adequate (in-test identity + SHA256 assertions; M4a is a real RED) |
| 6. Choose an oracle-unlisted mutation, declare the RED set before running | **CLOSED** — M5 (narrow default tuple): declared *before* running as "FC-904 must go RED on `test_no_bundle_all_produced` and the AR-* default-tuple nodes"; observed 10 failed on FC-904 + 2 failed on W05C, exactly as declared. Bonus M6: declared "the accepted bundle-present semantics must be pinned by ≥1 RED"; observed 7 + 4 |
| 7. Decide whether CF-1 must be fixed before this batch closes | **CLOSED** — §4: accept as carried, but require register entry (C1) and require the edit before promotion |
| 8. Confirm the extra selector regression | **CLOSED** — 10/6 on both byte sets, additive-only copies |

---

## 10. ONE-LINE VERDICT

**ACCEPT.** All nine claims verified by independent re-execution; the M4b vacuity proof is
confirmed and strengthened; the FC-904 "no genuine conflict" ruling is correct and its
counterfactual is now demonstrated; four of my five new findings are documentation/precision
issues. The two things that must not be lost are **RF-1** (the conftest guard is weaker than
advertised and one cited provenance file reports production bytes) and **CF-1's registration**
(a carried finding that is not in the register is not carried).

---

## 11. BYTE PIN

Sections 1-10 above (the reviewed body, before this section was appended):

- `sha256 = 71761E8E589C75BA89AF48DA0A5022309358ECAA2D3D0C388DF349970D9C253F`
- `bytes  = 35345`

The pin of this file **as delivered** (including this section) is written to
`reviewer_report.sha256` in the same directory, together with the body pin above, so the exact
reviewed bytes are recoverable either way.

Reviewer read-only attestation: no file under `RF:scripts/`, `RF:tests/`,
`CW:src/`, `execution_runs/I-05-C/**` or `execution_runs/I-05-B/**` was written by this review;
all re-runs executed in a throwaway copy under `%TEMP%\b3-review-r2\`. The only files this
review created inside the plan tree are `reviewer_report.md` and `reviewer_report.sha256`.

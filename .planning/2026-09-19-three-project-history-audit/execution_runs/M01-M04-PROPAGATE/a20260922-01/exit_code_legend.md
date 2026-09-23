# exit_code_legend — M01-M04-PROPAGATE patched runner copies (T1-19 requirement)

Applies to: `iso/run_card.py` (sha256 `f671732d4860404a925ab544b41b6fe2c6e62b9c65400b010aad2d7388ae3e0b`)
— the REM-21-form gate patch of the historical M01–M04 runner
(`b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816`).
Frozen rc table source: `execution_v2/START_HERE.md` §"rc 码表" (T1-19). **Exit-code
numbers are NOT renumbered by this patch**; only routing of declaration faults is new.

| rc | meaning (patched copies) | measured arm |
|---|---|---|
| **0** | pass: positive matched the independent oracle within tolerance AND continuity positive passed AND every **judged** negative was rejected with `ModelRegistryError` **and** its raised exact type name equals the case's declared `expected` | **E = 0** ×4 |
| **1** | harness / **STRUCTURAL** failure — fail loud. This runner has no rc=1 branch of its own: rc=1 is reached only via an uncaught crash, e.g. a structurally broken `cases.json` fixture (a case entry missing a required member such as `kind`). Never issued for a value difference or a declaration problem | **S = 1** ×4 (`KeyError: 'kind'`, no out.json) |
| **2** | **NO VERDICT, decided BEFORE any case can be judged**: the frozen per-case `expected` declaration is missing/unusable → reason `cases_json_declared_expectation_missing:<ids>` (verdict `no_verdict`), or the positive path raised so there is nothing to compare. Such a case is `NOT_JUDGED_declaration_unusable` and is **never** counted as a mismatch | **G = 2** ×4 (reason `…:NEG-CARD`) |
| **3** | a judgement WAS possible and did not hold: positive mismatch, continuity failure, unrejected negative, wrong exception type, or raised exact type name ≠ declared `expected` (`FAIL_declared_expectation_mismatch`) | **F = 3** ×4 |

**missing-expected → 2** (the T1-19 wording this legend implements): deleting a case's
`expected` key used to crash the historical runner with `KeyError: 'expected'` → rc=1;
on the patched copies it now yields **rc=2 + `no_verdict`** with
`cases_json_declared_expectation_missing:<ids>`, evaluated before any case is judged.

Control (arm **B**, historical byte-copy runner, same mutated fixture): **rc=0** ×4 —
the historical runner has no gate and fabricates green on a usable-but-different
declaration (REM-80); rc=1 on a deleted `expected` (KeyError crash) remains the
**historical** behaviour, recorded in B5-fix and left byte-untouched.

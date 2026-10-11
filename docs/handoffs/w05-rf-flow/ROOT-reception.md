# Correlated price period root repair — final frozen handoff

## Latest freeze; prior typed reception is historical

Independent review found 3 genuine P1s: a stock times the same/like annual price ratio was accepted as annual income at validation, forecast and both strong readers. Original inputs and accepted outputs remain untouched in independent-typed-final. This freeze supersedes the earlier typed freeze; it is engineering delivery for nonauthor review, not already merged acceptance or real-company research quality PASS.

## Shared root and repair

The old period_powers={0,1} Cartesian products chose different spot/annual meanings for repeated prices. The single contracts/period_flow.py owner now carries **affine period expressions with shared symbols and equations** through actual AST operands and recursive aliases. Multiplication/division add/subtract original symbols; addition/subtraction and each intermediate annual revenue impose equations. All equations must have one consistent interpretation, rather than choosing each occurrence independently. Like raw temporal prices of one existing price dimension share a role. Original unit/currency/scale responsibilities remain unchanged; the 3 price dimensions bound inference to at most 8 assignments, independent of leaf/alias count.

This is NOT an x/x name special case. Same symbol, derived ratio, nested alias, equivalent expression, distinct prices with different amounts and scalar coefficients all preserve actual stock/flow type. A price ratio scales existing income and cannot supply duration to a stock. Actual AST references carry constraints; an unused input does not independently constrain the formula. Derived prices keep actual income/quantity ancestry. Real turnover flow/stock, point quantity times annual ARPU, real dated/annual quantity times transaction price, and native subscription/fee/bank yield controls remain legitimate.

No new schema, source/identity store, authorization, review receipt, consumer exception or gate was added. Source/annual consumers reuse the same owner. Schema3.9/earlier wiring and defaults remain unchanged. If one generic formula genuinely needs both raw ARPU and transaction price of the same dimension, use actual flow-derived ARPU or existing native model roles; free text does not prove distinct roles. Source economic truth, dates, scopes and buy-side assumptions remain independently audited responsibilities. Generic dated stock-pricing is not a sum of evidenced interval contribution flows.

## Formal tests and execution

- exact-red.json: unchanged 3 independent inputs/outputs accepted at all 12 boundaries, actual FAIL retained.
- business-red.log: 6 stock cancellation/alias/equivalent/coefficient cases FAILED; 7 real-income scaling and annual quantity controls passed. Negative assertions were not changed.
- focused-green.log: 158 tests +33 subtests PASS in3.19s across common rules and prior period/consumer/reader suites. One additional requested dated quantity positive control then joined the existing final gate.
- final-node-before-host-fixture.*: first gate retained, 386 tests +36 subtests passed/4 failed. One NEW positive fixture had a revenue-helper currency field on quantity; repaired with the existing quantity contract helper, original business assertion unchanged. Three existing CLI integration cases were given explicit FF_V2_CODE_ROOT/CWP_V2_CODE_ROOT after this runner omitted their configured roots. No source dependency or gate code changed.
- final-node.log/json: ruff and public mypy11 files PASS; **390 tests +36 subtests PASS**, pytest42.00s/entry46.311s. The single existing daily gate was used; no added gate.
- exact-final-green.json: the same 3 frozen inputs and outputs now reject with actual typed-flow errors at all **12 boundaries**, not publication-environment errors.
- Two native forecast JSON/Markdown outputs plus C1 immutable snapshot (5 files) are **full-byte equal** to the earlier legitimate frozen outputs. Date/currency rehash checks pass. Owned scratch absent before and after.
- 0 provider calls, 0 LLM calls, $0. Canonical assurance/output WIP unchanged; original worker clean. No commit, push, main merge or installed-file write.

## ROOT handoff

Latest root-product-inventory.json carries exact current product SHA/bytes; latest install-readonly-plan.json carries current 17 runtime source files and old target SHA at 2 real targets (.claude junction deduplicated). Only --plan ran. ROOT should perform nonauthor replay in a NEW evidence directory, then normal hooks/merge/selective install/push, preserving canonical WIP. Original earlier FAILs and the 8 frozen legitimate artifacts must remain unchanged.

---

## Previous typed repair receipt (historical)

# ROOT reception hardening — W05-RF-FLOW

## Latest: independent P1 typed ancestry repair

The earlier reception is preserved in ROOT evidence `typed-boundary-pre-P1/`.
The nonauthor review exposed an annual-only alias of a point monetary stock:
the original independent input was accepted at validation, forecast and both
strong readers (FY2026 low 150 ->170). Do not treat the earlier freeze as final
acceptance; this section supersedes it.

The shared `validate_derived_flow_ancestry` now recursively preserves actual
formula **unit dimensions and period algebra**, even without dated ancestry:

- Monetary/operating stocks, scalar or ratio-only aliases cannot become income
  by changing an annual/time-basis/definition label. Nested aliases keep their
  actual origin; literal/unused/zero-weight evidence does not create an amount.
- Stock and period money cannot be added, even with a zero true-income anchor.
  `flow*(stock/flow)` remains stock after actual period cancellation. A genuine
  annual turnover `flow/stock` can convert a stock; raw generic scalar ratios
  only scale an existing flow and do not independently supply annual duration.
- Point operating quantities times annual ARPU and derived annual ARPU from
  actual annual income remain legal with matching dimensions. A raw annual
  price can be a transaction price or an annual operating rate; the matched
  formula/native/source role establishes that interpretation. Derived prices
  retain their actual origin, so a stock-per-unit number cannot become ARPU.
- Source composition and actual annual consumers reuse this one pure helper.
  Native subscription, bank, asset-management and stock-flow driver roles are
  unchanged. Earlier schema3.9 and legacy structural drafts remain unchanged.
  Generic stock-flow additions require a native bridge; arbitrary dated
  stock-pricing formulas are not a sum of evidenced interval contributions.

No schema fields, permissions, registry, review receipts or additional gate
were introduced. Economic truth of reported facts/perimeters remains source
and investment audit responsibility; this mathematical type proof does not
replace reading the underlying sources.

### New formal tests and final node

- Initial generalized typed RED: 10 failed /4 positive controls passed. Includes
  exact point/annual money-stock, quantity-stock, rate, scalar, nested alias,
  zero-weight source and direct shared annual-consumer boundary.
- Period-algebra RED: 3 unsafe mixed/cancelled-money cases plus one wrongly
  rejected legitimate turnover control failed; 2 derived-price controls passed.
  The same arithmetic root repaired both directions; negative assertions did
  not change. Every original failure is retained.
- Concentrated supplement: **158 tests +33 subtests PASS**, 3.29s, including
  original 3.10/3.9 window/consumer/strong-reader suites and new native controls.
- Final existing gate: **376 tests +36 subtests PASS**, pytest36.41s / whole
  entry40.049s; ruff and public mypy11 files PASS. First type attempt stopped at
  a real Any|None dimension index before pytest; a proper domain shape error
  fixed it, with original log retained, no cast/default/type waiver.
- Exact independent P1 input rejects at all four native boundaries. Two frozen
  native CLI results/Markdown and C1 immutable snapshot are **byte-identical**
  to the prior legitimate outputs. Date/currency rehash tamper checks still pass.
- 0 provider calls, 0 LLM calls, $0; owned typed scratch initial/final ABSENT.

The current root-product-inventory SHA receipt and install plan supersede prior
source hashes; the 8 legitimate frozen artifact hashes remain unchanged. No
commit, push, install or canonical WIP mutation was performed by this line.

---


## Status and provenance

Original delivery is `7b22bca8d6aa87f643780100832daec2836ed558` +
`f1a782a478d255b9b4b8f531e7a3961134e257ba`, based on
`1b616622763ece6549676f2a74f596e6c65244af`. The original handoff, manifest and
logs remain a historical worker receipt. This document and `e2e/frozen/manifest.json`
describe ROOT fixes; old handoff file hashes do not certify modified files.
ROOT performs final independent acceptance, merge/commit/push and installation.

## Common roots fixed

1. A derived annual alias previously hid a partial dated flow. The common temporal
   composition rule now applies to dated derived flows **and** annual wrappers
   with dated ancestry, across actual nonzero formula inputs.
2. Any rationale previously bypassed containment and overlap. Explanation now
   describes a real scope gap/independent business scope/residual subtraction;
   it cannot move a 2026 input into 2027 or add H1 and its own Q2.
3. Dated aliases preserve original leaf identity and semantic definition, so
   renaming an output/intermediate definition does not launder double counting.
   Unused/zero-weight operands do not manufacture year coverage. A point stock or
   rate alone cannot establish a recognized flow.
4. The old mixed-recognition lagged-activity input reached a dependency walker
   before shape validation and raised KeyError. One shared recognition validator
   now checks supplied metadata before DAG indexing; no carry-in defaults are
   fabricated. Legacy omitted-recognition draft structural validation is unchanged;
   actual forecast execution still requires a recognition contract.
5. The C1 sealed 1,291,902.08 CNY is retained as 1.29190208 CNY million in an
   entirely CNY synthetic surrounding fixture. No USD relabeling or assumed FX.
6. Compatibility unit tests no longer infer physical sibling repositories. Pure
   manifest/hash validation is separate from explicit read-only Git/document
   integration; nine tiny temporary Git commits test actual descendant/regression.

## Interfaces and responsibility

- `validate_period_flow_fields(..., schema_version="3.9")` keeps its old call shape
  and strict 3/6/12-month 3.9 semantics; only 3.10 admits arbitrary inclusive dates.
- `validate_windowed_composition` keeps the original public signature. Its formula
  lineage follows additive/subtractive sums and scalar/rate/price factors. Products
  of two flow amounts, division by a flow and non-unit-preserving powers are not
  temporal compositions; use the existing explicit assumption/native model fields.
- Original source economic identity/definition/perimeter is the authored evidence
  layer's responsibility. Hashes/string definitions cannot prove real subsidiary
  membership or detect a self-consistent rewrite of all reported facts. Independent
  economic/source audit remains necessary; no review receipt/permission is added.
- `contracts.recognition.validate_recognition_metadata` owns recognition shape;
  `forecast.segments` reexports the old entry for compatibility.
- `compatibility_manifest.validate_manifest(data)` is a pure registry/manifest
  check. Real integration explicitly calls `validate_repository_ancestry(data,
  repo_dirs)` after structural validation. `contract_registry.validate_canonical_documents`
  receives explicit repository roots. Neither unit tests nor production infer the
  current user's Projects directory.

## Engineering acceptance performed

- Formal ROOT RED: 3 real temporal exploits + preexisting mixed KeyError failed;
  the unrelated zero-weight guard already rejected and is not claimed as RED.
- Separate stock RED: a point monetary balance relabeled as revenue was accepted
  before the common typed precondition; original negative assertion retained.
- First final node exposed 2 legacy draft regressions; FAIL logs retained and the
  validator responsibility corrected. Tests were not loosened.
- Final existing `tools/pre_push_gate.py`: ruff PASS, public mypy 11 files PASS,
  **356 tests + 36 subtests PASS**, pytest 33.20s / full entry 38.043s.
- Portable compatibility plus 3.9 field/engine semantics: **52 tests + 7 subtests
  PASS**, pytest 3.90s. Counts overlap some daily tests; do not sum as unique tests.
- Native 3.10 template, two validation/forecast/Markdown chains, immutable snapshot,
  native strong readers, rehashed window/currency tamper rejection and full forecast
  JSON determinism PASS. Actual cross-repo ancestry and canonical docs checked with
  explicit read-only roots. No provider/LLM calls, no fees.
- Generated author guidance was clarified after the engine node; one bounded native
  template regeneration checked its wording. Business code/assertions unchanged.

The existing SMOKE_TESTS list includes the three dated contribution suites, ROOT
temporal lineage and old mixed recognition tests. No new gate script or per-commit
wide suite was created. These proofs are **offline engineering**, not real-company
economic quality or paid-provider acceptance.

## Frozen replay and test isolation

Eight small JSON/Markdown artifacts live under `e2e/frozen/`, not ignored global
`artifacts/`. Verify each byte SHA/size against its manifest. C1 preserves only the
sealed amount/unit/dates; its surrounding facts, sources and forecasts are synthetic.
C2 is a synthetic 06-30 fiscal-year partition `7+10+3=20` and a ten-day observation.
No binary raw original was copied.

To replay with this engine, create your own temporary directory and set
`REVENUE_PUBLICATION_REGISTRY` to a file in it. Run the native forecast CLI on each
frozen input, with JSON/Markdown outputs in that temporary directory. Compare full
forecast JSON with the frozen result, then use `e2e/read_and_tamper.py` on the new
output (`window`, and C1 `currency`). For C1 snapshot use native
`revenue_backtest.py create ... --version w05-root-cny-v1 --output <tmp snapshot>`
and `validate_snapshot`. Do not overwrite frozen files, production registries or
raw/config/install files. Restore only your owned test directory afterward.
The generated template is a FIXME skeleton, not a runnable real-company forecast.

ROOT external evidence includes exact command logs, checkpoints, failed rounds,
scratch initial/final state and the final file SHA inventory. The owned E2E scratch
and template documentation scratch started absent and ended absent. The ROOT
worktree is intentionally retained for independent review until ROOT commits it.

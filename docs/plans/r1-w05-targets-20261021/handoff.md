# R1 W05 engineering candidate

**Status: engineering GREEN, pending ROOT independent acceptance and live W06 use.** This is not a company/forecast quality PASS.

Code commit: `364330472e2f7ecc263400f8daa0f29ffcfd897f` on `codex/r1-targets`, base `9669c4d7`. Main and installed skills were not modified.

## What changed

- One native member resolver for typed segment-group validation, actual DAG ancestry and annual/base effective revenue. No new segment or forecast calculator.
- Exact group members, duplicate/base aliases, nested/unknown members and unsupported adjustment fields have named validation. Missing member-period data never becomes zero; missing/nonpositive denominators remain comparison gaps.
- Typed raw YoY currency must be dimensionless, even for unmodeled typed targets. Canonical comparison currency/scale are null; the raw input remains immutable and derived revenue benchmarks retain model monetary units. Legacy qualitative and partial arithmetic helper semantics remain compatible.
- Group membership is displayed explicitly in the report. Six actual runtime/reference install files, including new `target_scope.py`, are enumerated with old observed installed SHA in JSON. No bulk sync.

## Evidence

Valid pre-product RED:19 failures /1 control PASS. Final:171 PASS +81 subtests in8.76s;31 new cases. Two new real offline CLI chains validate→publish/render→snapshot, alongside existing quarterly recipe. ruff and public mypy11 sources PASS. See `test-receipt.json`, `red-valid.*`, `final2.*`, `mypy.log`. A first environment failure and a cloned fixture naming error are recorded separately, not counted as product defects.

Independent arithmetic anchor retains initial four continuing-segment bases and the external reviewer ratios (~9.29157/17.48437/25.18577%) with an explicit tiny rounded-component-base tolerance. A different three-business synthetic company checks subset/perimeter, actual effective paths, missing periods and amount units; no company branch exists in code.

0 network /model /downloads /charges. Original/config/installed copies unchanged. Owned test temp and caches cleaned, initial absence restored; sampled checkout21.79MB→37.03MB→22.18MB (sample is a lower bound on peak, not a peak upper-bound claim). Intermediate logs single-copy local-only, compact receipts committed.

## ROOT next actions

1. Independent content-bound review and fresh counterexamples; fix before acceptance.
2. Integrate with W02, centrally add `tests/test_r1_target_scope.py` to existing smoke manifest (worker did not race-edit tools), and coordinate any runtime/version pins.
3. Old-SHA checked selective install of the six listed files; no config/output copying.
4. W06 real new attempt must actually use the group and dimensionless endpoints. It is not complete solely because this engineering suite is green.

The native segment list is flat and already reconciled. Exact name/base-alias checks cannot prove real economic disjointness; source-supported perimeter remains a research/independent-review responsibility. No hierarchy is invented from names.

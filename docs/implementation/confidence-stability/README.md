# Confidence root-cause repair, 2026-10-08

Base: 08673cf87b8a58fc25982b695a9d14e28c6818d3. Independent worktree; canonical owner logs/output untouched.

Root cause: set-derived parameter order changed dictionary reduction order; ordinary sequential additions dropped small contributions or changed final bits. Same-process recalculation tests missed process hash seed and equivalent input order. The first three minimal cases reproduced those mechanisms on the base; six additional contract cases were RED for the missing revision/compatibility API (9 RED in 2.03s).

Repair: accumulate contributions by parameter, compensated sum with canonical keys; use compensated quality/freshness/model-share/sensitivity/score reducers. `stable-fsum/1` is an explicit numeric revision in new artifacts. New output is exact; unmarked legacy roundoff is bounded to 64 binary64 ULPs only in named dimensionless reducers. Unknown revisions and substantive changes are refused, history and input/source/hash semantics remain checked. This is not a company/ticker/weight whitelist.

Validation: 61 affected responsibility tests passed (2 unittest subtests) in 4.01s, including cross-process formal publication. 64/65-ULP boundary, non-finite/bool, changed coverage/concentration/count/score rejection tests are included. One initial golden failure was expected from the new revision; before refreshing, isolated original HEAD reproduced all five old golden hashes and strong-validated all old/new results. Zero non-confidence economic differences; dependent receipt SHA initially omitted by the audit helper was explicitly accounted for and remains publicly validated. See golden_compatibility_audit.json.

Daily CI adds only this small synthetic responsibility file; full market/provider/LLM suites stay at milestones. Full first-cohort replay and installation publication are recorded by MAIN's PWF after candidate commit. All test registries are owned TEMP. No original source or archived forecast/snapshot bytes changed.

Integration environment finding: the first fast-gate run used an obsolete sibling Temp/filing-fetch checkout (89c8bdb2), which lacks the current SourceRef v2 compatibility flag. Explicit FF_V2_CODE_ROOT/CWP_V2_CODE_ROOT select current committed dependencies; the contract assertions are unchanged. Do not infer a production defect or skip the real CLI test from this harness location issue. Historical observation counts additionally reject bool, even though Python equates False with zero.

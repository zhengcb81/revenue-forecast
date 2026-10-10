# P7-RF MAIN reception repair — stable handoff

Status: **implementation_complete_source_stable**. Date: 2026-10-11.

Working tree: `C:/Users/郑曾波/.codex/worktrees/m3-acceptance-20261010/revenue-forecast`. Branch: `codex/p7-rf-calibration-binding`. Actual HEAD remains `183c9534b90549c094fc32a51ff6ada1e9cb5227`. Original delivery source: `05aa2661c9cdc34cb7e9ce3cf7e83b43bee7f556`; original base: `6883bf00548abb9891eab6762aeaa89e3898b202`.

## Root cause and implementation

The previous calibration checked parameter/claim/observation self-consistency without relating the conversion's applicability period to the output it actually scales. Mutating all three together to FY2031 therefore still marked actual FY2026 revenue as supported.

- `research.native_dependencies.direct_parameter_cells(data, parameter_id, *, scope, scenario)` returns actual direct revenue/recognition roots with their segment/scenario/FY cell. It reuses existing `segment_roots`; it does not flatten a legitimate cross-period DAG bridge.
- `research.evidence_roles._calibration` now diagnoses each consumed conversion's `parameter.period` against the actual output period, and a direct output's period against its actual consumed cell. Mismatch downgrades optional support to `unverified`; native arithmetic still runs.
- New reasons carry the actual IDs/periods: `conversion_output_period_mismatch:PARAM:PARAM_PERIOD:OUTPUT:OUTPUT_PERIOD:CLAIMS` and `calibration_output_consumption_period_mismatch:OUTPUT:OUTPUT_PERIOD:SEGMENT:SCENARIO:CELL_PERIOD`.
- Reference input x0 is excluded from the conversion applicability check. Historical FY2025 range/reference evidence, an unused upper endpoint, old claim disclosure periods, and an explicit FY2025→FY2026 native derived conversion bridge remain valid.
- Observation `measurement_period` binding and claim observation/disclosure context retain their existing behavior. No new source-date equality rule was added.

### Actual period contract

`scripts/contracts/document.py:415` validates every `parameter.period` using existing `scripts/contracts/evidence.py:131–136`: `re.fullmatch(r"FY\d{4}", value)`, with the existing error `must use strict FYyyyy format`. Plain `2026`, quarters and ranges are not equivalent legal parameter-period spellings. Schema3.9 dated flows also retain this FY label and separately validate dates. The comparisons therefore operate on the existing validated canonical spelling; period contracts and normalization were not changed.

## Version integration and compatibility

Applied the original `MAIN_INTEGRATION_PATCH.patch` by actual `git apply --check` then `git apply`, with inherited GIT variables removed. Patch SHA256: `9335ad102f8c8764bdaa55ff6c669a9cb9b423e562edfd1429062df2e6848338`. Its five files restore documented old4.2.0/current4.2.1 emitter compatibility for native schemas3.7/3.8/3.9 and update five current-engine assertions in four test files. Existing sealed old outputs were not re-signed or altered. This is compatibility with archived4.2.0 output, not a claim that4.2.1 recomputation reproduces old engine semantics.

`economic-support-diagnostics/1` remains optional and read only, with `economic_truth_inferred=false`. No schema, permission, source identity, period contract, forecast calculator, confidence formula or legacy absent-optional-input behavior was changed. Structural support does not prove economic plausibility, accurate estimates or a complete buy-side model. R16/R17/R18/W09 remain separate research work.

## TDD and actual acceptance

| Check | Actual result |
|---|---|
| Responsibility RED before implementation | 4 failed / 10 passed, 0.69s; synchronizedFY2027/FY2031 and wrong direct-cell relation reproduced |
| Concentrated responsibility + compatibility | **119 passed, 7 subtests passed, 25.35s**; subtests are not added to119 |
| Ruff | 9 Python files, exit0 |
| mypy | 3 source files, exit0 |
| Actual public offline pipeline | **4 cases accepted, 11.143s**; no vendor or model calls |

The public driver performs real `build_auditable_case.py` → `run_target_measurement_e2e.py` (native validate/compute/Markdown/snapshot) → `research_support_diagnostics.py`, using versioned synthetic source-read/ref evidence and isolated registry. It neither depends on canonical customer directories nor calls provider/LLM. The final cases are:

1. Legitimate historical range → FY2026 SegmentA low/base/high supported; futureFY2027 and other segment not spuriously supported.
2. Observation-only future-period mismatch → unverified; native path still completes.
3. Synchronized parameter+claim+observationFY2031 with actualFY2026 output → unverified/unsupported; native exits0; consolidated arithmetic, confidence score and each confidence component exactly match the positive.
4. Real native FY2025→FY2026 derived conversion bridge → referenced_range without reasons; historical provenance retained; arithmetic equals the positive.

Null/unknown range remains unverified and stress remains stress. Scenario/output crossborrow and stale claim excerptSHA remain rejected by existing contracts with diagnostic CLI exit2. All final cases produced real snapshot and Markdown results agreeing with native diagnostics.

Reproduction: use the exact argv in `concentrated.json` and `public_e2e.py` from this directory. Each creates owned TEMP, disables pytest auto plugins/cache/bytecode, uses an isolated publication registry and removes all test products on completion. Do not run against installed copies or canonical production directories. The public script does not re-run the concentrated suite.

## Protection and restoration

All23 protected original RF config/fixtures/HANDOFF/old logs/original PWF bytes are unchanged. Canonical owner's3 dirty assurance files and Git status are unchanged. Public CLI's107 runtime/dependency file SHA values are unchanged. Both concentrated-test and public-pipeline owned TEMP directories were removed; environments restored; original documents untouched. Total provider calls0, model calls0, new costUSD0. HEAD unchanged. No commit/merge/push/install performed by this agent.

ROOT's later `.gitattributes` change is known: only this card's `attempts/**` and `main_reception/**` preserve native evidence bytes (`-text/-eol/-diff`). ROOT also added its archive rule to `main_reception_fix.md`. This agent has not staged, committed or reverted either change. Original evidence working bytes remain untouched; ROOT will check newly archived Git blob SHA separately without whole-repo renormalization.

## Exact source/test/reference SHA256

These10 working-file hashes were checked again at handoff and exactly equal `protected-after.json`, the verified source snapshot. They are working bytes; normal Git LF normalization may give a different source blob hash.

| File | SHA256 |
|---|---|
| `references/economic-support-diagnostics.md` | `12c89a1b5925e5790d2cdfa76e6b26a94ff3eb2f15f9c16e9726c1594402ca09` |
| `references/evidence-role-calibration.md` | `dc386bee001fa8872c36c4a0ef8526a66b38e508dea5e21cda3a6cc5b8421cb9` |
| `scripts/research/evidence_roles.py` | `a3efbf813492c2a9a838a0ff8679c810ee9b0ffb51c7877d322aea3bf47a758d` |
| `scripts/research/native_dependencies.py` | `5e224d141d677525112ee4f4bc749bb8534d0fe4749f78fc220682139b1be16f` |
| `scripts/schema_compatibility.py` | `1df2f419152fdf50da2555417952cb9fd028e6e85a5f5d1e39ca4f46e4e8707a` |
| `tests/test_data_contract.py` | `1737d73c68d98cc0298896fc0e714d6c5281708015aeb9d3367df23563595202` |
| `tests/test_m3_period_flow_contract.py` | `875830d8601c8079a2f940ef79c8b6455b54ee2acf45d692e92e62592efeb0b5` |
| `tests/test_m3_schema_compatibility.py` | `d5048857e75db26f902c7449c41815e1c55d534ed57619f97ef2551de3b16850` |
| `tests/test_schema_compatibility.py` | `290eb0fe28b7c9b6f54759a7f149baa10b311e62cc3498c47722356d54d68fad` |
| `tests/test_scoped_calibration_support.py` | `eb6097bd302b692ce2e56d015f0be779331e85d46a87a473ae232b6ea14178b9` |

## Native evidence SHA256

| File | SHA256 |
|---|---|
| `red.json` | `07f98b9d9da8881bddd8de607991394a5047e385079cb147a34f6ec05abc2e09` |
| `red.log` | `8571320e191cb58acbba0a6d1fff9dadef286f458f235097c64166b7b773539e` |
| `concentrated.json` | `1a836ead7f8cf53b3dd2205b1c353b2e8145b1749d18b0efe01cbeb4236059a4` |
| `responsibility-compatibility.log` | `370df654f0aa1f7947ffba9285d726920c51481fdb402e52e7687d1c392ddc21` |
| `ruff.log` | `a4443afdcfb6d7363adb285762515ccf7cf50473b1a05c20c1a50f6bed4d26b0` |
| `mypy.log` | `281a094c39385b4d7b53e5db635f52158036861433c2a4975b9039e77a627a24` |
| `public_e2e.py` | `93a4994a68864996d784457e33e638d5ac017d47ac7ea27a8932146aeaa7f030` |
| `main-e2e-receipt.json` | `a8a5d9f77bef212f2b9d8c217c6175b7c745c0574ca9ee164167ca993460fd9b` |
| `protected-before.json` | `127fbe23e64c330c65f19f94a66751798bfbc697f748df4cef5d98ff8eef13b2` |
| `protected-after.json` | `3615b9d7743f8aac5f3b9364cc18fbdfef7ed075feb5c4f8c27dd4909c00f329` |
| `implementation.diff` | `857504f22bd722e028520ad0cd9466e695dba2a0e07961824e5966637ad6d602` |

## MAIN continuation

ROOT owns normal hooks/commit, exact native evidence blob verification, exact-HEAD CI, push/merge and any scoped installation. No new small-step approval or signing gate is required. Read `handoff.json` for machine-readable interface/results/SHA. This repair is source stable; no further writes or optional tests will be made by this agent.

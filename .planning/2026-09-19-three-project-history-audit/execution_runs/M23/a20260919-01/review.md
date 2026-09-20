# M23 · insurance_service · 保险服务披露映射 - implementer review record

Card M23 (`insurance_service`), Parent I-10. Attempt `execution_runs/M23/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M23/source_manifest.json` |
| B positive | actual `[110.0]` vs independent oracle `[110.0]`, within `1e-9*max(1,|e|)` | `evidence/M23/formula_result.json` |
| continuity positive | actual `[110.0, 300.0]` vs oracle `[110.0, 300.0]` | `evidence/M23/negative_results.json` |
| defaults case | actual `[200.0]` vs oracle `[200.0]` (not gating) | `evidence/M23/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M23/negative_results.json` |
| D mapping | **NOT DONE** - needs a signed industry/accounting review | `evidence/M23/qualification.json` |
| E probe | **NOT DONE** - belongs to I-10-A | `evidence/M23/qualification.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M23/qualification.json` |

Raw exit code of the product run: **0** (0=pass / 2=no-verdict / 3=negative not rejected as
expected / 1=harness error). stderr is 0 bytes.

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M23.py`, which imports only `argparse`,
  `hashlib`, `json`, `os`, `sys` and `decimal` - see the `import_lines` list inside
  `evidence/M23/oracle_selfcheck.json`; `product_import_present` is `false`.
- The oracle document `oracle.md` (sections 0-11) was written **before** any product run. Its
  frozen body is 10481 bytes, sha256
  `ccd6fb673607521bbd524e9de08bd0e1e7f6d1335af35cf41cfa74a912a4b64f`; the exact reconstruction identity
  `oracle.md == frozen_body + b"\n---\n\n" + run_section` is verified by
  `scripts/verify_prefix_chain.py` in all four attempts of this batch.
- `evidence/M23/oracle.json` is **byte-identical when regenerated** (re-run performed).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations
  only from `evidence/M23/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `d02057debe8d34df8a472e83aa3771f5c90fb77d58b3c0eee2237e35593b2953`) was used for
  M05-M08 and for all four attempts of this batch; there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = coverage_units * revenue_per_coverage_unit * timing_factor + other_revenue`
- Registry required: `['coverage_units', 'revenue_per_coverage_unit']`; optional: `['timing_factor', 'other_revenue']`; defaults: `{'timing_factor': 1.0}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - `driver insurance_service.timing_factor must be between 0.0 and 1.0: FY2027`
- `N01a`: ModelRegistryError - `insurance_service.coverage_units.FY2027 must be numeric`
- `N01b`: ModelRegistryError - `insurance_service.coverage_units.FY2027 must be finite`
- `N01c`: ModelRegistryError - `insurance_service.coverage_units.FY2027 must be finite`
- `N01d`: ModelRegistryError - `insurance_service.coverage_units.FY2027 must be finite`
- `N02`: ModelRegistryError - `driver insurance_service.coverage_units must contain one value per forecast year`
- `N03`: ModelRegistryError - `missing drivers for insurance_service: coverage_units`
- `N04`: ModelRegistryError - `unsupported drivers for insurance_service: unknown_driver`
- `N05a`: ModelRegistryError - `insurance_service.years must contain fiscal years`
- `N05b`: ModelRegistryError - `insurance_service.years must contain fiscal years`
- `CONT-BREAK`: ModelRegistryError - `insurance_service.years must be consecutive and increasing`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[110.0]
- `OBS-DEFAULT-EQUIV`: raised=None actual=[200.0]
- `OBS-TIMING-BOUND-11`: raised=ModelRegistryError actual=None - driver insurance_service.timing_factor must be between 0.0 and 1.0: FY2027

## 5. Judgement calls the reviewer should attack first

1. The card's own negative is WEAKER than it looks: because the frozen positive input has a 1-year `years` list, the only reachable slot is index 0, and replacing the whole array `[1.1]` also changes the LENGTH. The observed rejection is therefore the length guard (`must contain one value per forecast year`) and NOT the value-domain guard. This attempt covers the value guard separately with the non-gating observation OBS-TIMING-BOUND-11 (timing_factor = [1.1, 0.5] on a 2-year path), which was rejected with `must be between 0.0 and 1.0: FY2027`. A reviewer who wants the card's negative to be GATING for the value domain must say so.
2. `timing_factor` defaults to 1.0, which is exactly the inclusive upper edge of the ratio domain - so the documented default sits ON the boundary. A reviewer should confirm that is intended rather than an accident of the bound being [0,1].
3. the non-gating observation OBS-TIMING-BOUND-11 is based on `continuity_positive`, whose FY2027 `revenue_per_coverage_unit` is 2 (not the positive case's value), so the observation is not a drop-in replay of the card input.
4. coverage_units and revenue_per_coverage_unit are both unmapped; nothing in this attempt claims the card is a complete IFRS17 engine (the card says it is not).

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review
  plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated
  specification, the existing implementation is retained.
- It does **not** claim that a formula pass on this card implies anything about the other 30
  models: the parent card explicitly forbids extrapolating accuracy from formula passes.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M23.py --card M23 --out-root <scratch>` and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` against
   `iso/checkout_scripts` and diff `run_result.json`.
2. Re-run `scripts/verify_prefix_chain.py <plan>` to confirm the oracle.md frozen-body chain.
3. Confirm the isolated copy hashes still equal production
   (`evidence/M23/source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running it.
5. Re-run `scripts/enumerate_oq_rulings.py` and compare the counts with
   `evidence/M23/oq_rulings_enumeration.json`.
6. Adjudicate the OQ items in `decision.md` and `handoff.json`.

## 8. Exit-code mutation self-check (red then green)

Scratch tree: `recovery/selfcheck/` (the frozen evidence is never mutated).

| probe | raw rc | expected rc |
|---|---|---|
| D_pristine_uncorrupted | 0 | 0 |
| A_corrupted_positive_expectation | 3 | 3 |
| B_corrupted_negative_assertion | 3 | 3 |
| C_corrupted_positive_input | 2 | 2 |
| F_corrupted_expected_type | 3 | 3 |
| G_corrupted_message_requirement | 3 | 3 |
| H_message_requirement_points_at_another_guard | 3 | 3 |
| D_restored_uncorrupted | 0 | 0 |

`frozen_hashes_unchanged` = `True`. Full record:
`recovery/selfcheck/selfcheck_result.json`.
<!-- BEGIN independent-review verdict (round 2, transcribed verbatim) -->

> **独立复核裁决（revision r2 后）：`accepted_scoped`（仅 formula）。由 `changes_required` 转正。**
> 同 M22：NEG-CARD 现为 `timing_factor = [1.1]`，我独立构造并调用隔离快照得到 **`driver insurance_service.timing_factor must be between 0.0 and 1.0: FY2027`**（值域守卫），消息要求已冻结；三个变异探针（expected 翻转 / 消息要求不可能 / 消息要求指向长度守卫）全部 rc=3。
> 我另在 2 年路径上双向证实值域守卫可达：`timing_factor=[1.1,0.5]` → `... must be between 0.0 and 1.0: FY2027`；`[0.5,1.1]` → `... FY2028`；`[1,1]`（含端点的文档默认值）→ 通过 `[210.0, 300.0]`。原 `OBS-TIMING-BOUND-11` 保留为非判定性交叉核对，定位不变。
> 无回归：`rc=0`、`stderr` 0 字节、正例 `[110.0]`、连续性 `[110.0, 300.0]`、defaults `[200.0]`、11/11 负例；我自造输入另证 coverage×rpc×timing 边界（`7×13×1=91.0`；`coverage=0` → `42.0`；`timing=0` → `0.0`；总收入为负 → 拒绝）。
> 正文改动经我逐节复算：改 NEG-CARD 行 + 改观察项行（`OBS-TIMING-BOUND-ONE` → `OBS-TIMING-BOUND-11`，与上一轮 obsfix 快照一致）+ 新增第 12 节，共 8 行；`## 2./3./4./8./10.` 与全部既有期望值逐字节未变；前像 sha256 `d27cfbda…`。
> 签收边界：**仅 `formula`**。`disclosure_adaptation` 保持 `unmapped`，`accuracy` 保持 `unproven`。第 12 节写"本卡不是存量桥，桥平衡比较不适用"——与第 1 节 `not_applicable_with_reason` 自洽 ✓。
> 遗留（时间性）：同 M22 的消息闸门完整性。

<!-- END independent-review verdict -->

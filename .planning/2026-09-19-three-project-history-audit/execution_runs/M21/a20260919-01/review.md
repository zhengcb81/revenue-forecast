# M21 · delivery_pipeline · 实物订单交付桥 - implementer review record

Card M21 (`delivery_pipeline`), Parent I-10. Attempt `execution_runs/M21/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M21/source_manifest.json` |
| B positive | actual `[122.0]` vs independent oracle `[122.0]`, within `1e-9*max(1,|e|)` | `evidence/M21/formula_result.json` |
| continuity positive | actual `[122.0, 0.0]` vs oracle `[122.0, 0.0]` | `evidence/M21/negative_results.json` |
| defaults case | actual `[120.0]` vs oracle `[120.0]` (not gating) | `evidence/M21/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M21/negative_results.json` |
| D mapping | **NOT DONE** - needs a signed industry/accounting review | `evidence/M21/qualification.json` |
| E probe | **NOT DONE** - belongs to I-10-A | `evidence/M21/qualification.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M21/qualification.json` |

Raw exit code of the product run: **0** (0=pass / 2=no-verdict / 3=negative not rejected as
expected / 1=harness error). stderr is 0 bytes.

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M21.py`, which imports only `argparse`,
  `hashlib`, `json`, `os`, `sys` and `decimal` - see the `import_lines` list inside
  `evidence/M21/oracle_selfcheck.json`; `product_import_present` is `false`.
- The oracle document `oracle.md` (sections 0-11) was written **before** any product run. Its
  frozen body is 12234 bytes, sha256
  `0a1b9a2b4a6ff900ef2dacce662768a350fbaf3f83ccc3e1124c75a148e059e0`; the exact reconstruction identity
  `oracle.md == frozen_body + b"\n---\n\n" + run_section` is verified by
  `scripts/verify_prefix_chain.py` in all four attempts of this batch.
- `evidence/M21/oracle.json` is **byte-identical when regenerated** (re-run performed).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations
  only from `evidence/M21/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3`) was used for
  M05-M08 and for all four attempts of this batch; there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = deliveries * unit_revenue * timing_factor + other_revenue`
- Registry required: `['opening_orders', 'new_orders', 'cancellations', 'deliveries', 'ending_orders', 'unit_revenue']`; optional: `['timing_factor', 'other_revenue']`; defaults: `{'timing_factor': 1.0}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - `driver delivery_pipeline.timing_factor must be between 0.0 and 1.0: FY2028`
- `N01a`: ModelRegistryError - `delivery_pipeline.opening_orders.FY2027 must be numeric`
- `N01b`: ModelRegistryError - `delivery_pipeline.opening_orders.FY2027 must be finite`
- `N01c`: ModelRegistryError - `delivery_pipeline.opening_orders.FY2027 must be finite`
- `N01d`: ModelRegistryError - `delivery_pipeline.opening_orders.FY2027 must be finite`
- `N02`: ModelRegistryError - `driver delivery_pipeline.opening_orders must contain one value per forecast year`
- `N03`: ModelRegistryError - `missing drivers for delivery_pipeline: opening_orders`
- `N04`: ModelRegistryError - `unsupported drivers for delivery_pipeline: unknown_driver`
- `N05a`: ModelRegistryError - `delivery_pipeline.years must contain fiscal years`
- `N05b`: ModelRegistryError - `delivery_pipeline.years must contain fiscal years`
- `CONT-BREAK`: ModelRegistryError - `delivery order continuity failed: FY2028`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[122.0]
- `OBS-DEFAULT-EQUIV`: raised=None actual=[120.0]
- `OBS-CARD-NEG-ENDING`: raised=ModelRegistryError actual=None - delivery order bridge failed: FY2027

## 5. Judgement calls the reviewer should attack first

1. the frozen GATING card-specific negative is NOT the card's literal one: the card names `ending_orders=[36]` on the 1-year input, which is rejected by the FY2027 bridge-balance guard, not by a value-domain guard. NEG-CARD was deliberately moved to a 2-year `card_neg` base so the ratio value-domain guard is the reason for rejection, and the card's literal change was kept as the non-gating observation OBS-CARD-NEG-ENDING (which was also rejected). A reviewer who wants the card's literal case to be GATING must say so explicitly.
2. `card_neg` is an input this attempt ADDED (identical to the continuity positive base). It is frozen in evidence/<card>/input.json and its expected output is the same as continuity_positive; a reviewer should confirm that adding an input is acceptable rather than a way to dodge the card's own negative.
3. `other_revenue` is optional with default 0 and is silently zero-filled when omitted (registry line 335). For this model that asserts 'no other revenue' with no disclosure saying so.
4. the defaults case is NOT part of the exit code; it is recorded for falsifiability only.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review
  plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated
  specification, the existing implementation is retained.
- It does **not** claim that a formula pass on this card implies anything about the other 30
  models: the parent card explicitly forbids extrapolating accuracy from formula passes.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M21.py --card M21 --out-root <scratch>` and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` against
   `iso/checkout_scripts` and diff `run_result.json`.
2. Re-run `scripts/verify_prefix_chain.py <plan>` to confirm the oracle.md frozen-body chain.
3. Confirm the isolated copy hashes still equal production
   (`evidence/M21/source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running it.
5. Re-run `scripts/enumerate_oq_rulings.py` and compare the counts with
   `evidence/M21/oq_rulings_enumeration.json`.
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
| R4_required_message_ids_gate_removed | 3 | 3 |
| D_restored_uncorrupted | 0 | 0 |

`frozen_hashes_unchanged` = `True`. Full record:
`recovery/selfcheck/selfcheck_result.json`.

<!-- BEGIN independent-review verdict (round 2, transcribed verbatim) -->

> **独立复核裁决（revision r2 后）：`accepted_scoped`（仅 formula）。维持不变。**
> 我独立重跑本 attempt 的冻结夹具：`rc=0`、`stderr` 0 字节、正例 `[122.0]`、连续性 `[122.0, 0.0]`、defaults `[120.0]`、11/11 负例 `ModelRegistryError`、`tolerances_ok=True`。我自造的桥/收入分离输入（`deliveries=7, unit_revenue=11, timing=0.5, other=3` → `41.5`；仅改 `unit_revenue` → `80.0`；改 `deliveries` 破坏桥 → `delivery order bridge failed: FY2027`）确认桥约束与收入计算相互独立且各自生效。本卡 NEG-CARD 原本即落在**值域守卫**（2 年 `card_neg` 上 `timing_factor[1]=1.5` → `must be between 0.0 and 1.0: FY2028`），无需升级。
> 本轮正文改动为**纯增量**：只有新增第 12 节 8 行，0 行既有内容被改；`## 2./3./4./8./10.` 逐字节未变；前像 = 上轮冻结体。第 12 节明确写"本卡未对该分辨率做数值探针，不复制 M24 结论"，未越界外推。
> 我复算了冻结链：`oracle.md` 冻结体自 0–11 节起逐字节未变（11454 → 12234 字节，增量全在第 12 节），`prefix_sha`、`reconstruction_identity`、`oracle_json_mtime` 三项仍为 true。
> 签收边界：**仅 `formula`**。`disclosure_adaptation` 保持 `unmapped`，`accuracy` 保持 `unproven`；不得由此外推到其他 30 个模型。
> 遗留时间性事项（不阻塞签收）：P3-1 建议在第 12 节标题下补一句"本节于运行后加入，0–11 节未改"；P3-2 建议把"未对本分辨率做数值探针"保留为显式限制。

<!-- END independent-review verdict (round 2) -->

<!-- BEGIN independent-review verdict (round 3, transcribed verbatim) -->

> **独立复核裁决（round 3 终裁）：`accepted_scoped`（仅 formula）。**
>
> 本卡 formula 资格**签收**。依据：①独立重跑冻结夹具 rc=0、stderr 0 字节、正例/连续性/defaults 与 11/11 负例全部符合冻结预期；②`oracle.md` 0–12 节自 round 2 起**逐字节未改**（冻结体 `0a1b9a2b…`/12234 B），未触及"第三轮再改正文即 blocked"的阈值；③`verify_prefix_chain.py` 四卡 ALL-OK；④本卡未冻结任何消息要求，`required_message_ids` 为空集合，NEG-CARD 依"异常类型 + 2 年路径 FY2028 值域守卫消息"判定（我独立复现 `must be between 0.0 and 1.0: FY2028`）。
>
> 签收边界：**仅 `formula`**。`disclosure_adaptation` 保持 `unmapped`，`accuracy` 保持 `unproven`；不得据此外推到其他 30 个模型、其他公司或行业。建议（不阻塞）：删掉空的 `required_message_ids` 或注明"故意为空"，以免被误读为闸门存在；`before/run_card_preround2.py` 留档内容有误（实测等于新 runner），可择机重归档。

<!-- END independent-review verdict (round 3) -->

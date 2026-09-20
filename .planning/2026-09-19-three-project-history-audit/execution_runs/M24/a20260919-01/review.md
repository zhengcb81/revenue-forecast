# M24 · subscription_arr_bridge · ARR 存量与收入时点 - implementer review record

Card M24 (`subscription_arr_bridge`), Parent I-10. Attempt `execution_runs/M24/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M24/source_manifest.json` |
| B positive | actual `[215.0]` vs independent oracle `[215.0]`, within `1e-9*max(1,|e|)` | `evidence/M24/formula_result.json` |
| continuity positive | actual `[215.0, 250.0]` vs oracle `[215.0, 250.0]` | `evidence/M24/negative_results.json` |
| defaults case | actual `[210.0]` vs oracle `[210.0]` (not gating) | `evidence/M24/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M24/negative_results.json` |
| D mapping | **NOT DONE** - needs a signed industry/accounting review | `evidence/M24/qualification.json` |
| E probe | **NOT DONE** - belongs to I-10-A | `evidence/M24/qualification.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M24/qualification.json` |

Raw exit code of the product run: **0** (0=pass / 2=no-verdict / 3=negative not rejected as
expected / 1=harness error). stderr is 0 bytes.

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M24.py`, which imports only `argparse`,
  `hashlib`, `json`, `os`, `sys` and `decimal` - see the `import_lines` list inside
  `evidence/M24/oracle_selfcheck.json`; `product_import_present` is `false`.
- The oracle document `oracle.md` (sections 0-11) was written **before** any product run. Its
  frozen body is 13382 bytes, sha256
  `9c8f6b238d38841704acd7de305038190b18b93062eaff55fe74bb6bf41b3e9f`; the exact reconstruction identity
  `oracle.md == frozen_body + b"\n---\n\n" + run_section` is verified by
  `scripts/verify_prefix_chain.py` in all four attempts of this batch.
- `evidence/M24/oracle.json` is **byte-identical when regenerated** (re-run performed).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations
  only from `evidence/M24/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3`) was used for
  M05-M08 and for all four attempts of this batch; there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = opening_arr - opening_arr*(1-gross_retention_rate)*lost_arr_revenue_fraction + expansion_arr*expansion_revenue_fraction + new_arr*new_arr_revenue_fraction + usage_revenue`
- Registry required: `['opening_arr', 'expansion_arr', 'new_arr', 'closing_arr', 'gross_retention_rate', 'lost_arr_revenue_fraction', 'expansion_revenue_fraction', 'new_arr_revenue_fraction']`; optional: `['usage_revenue']`; defaults: `{}`
- Rejections and their messages:
- `NEG-CARD`: ModelRegistryError - `opening_arr stock-flow balance failed: FY2027`
- `N01a`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be numeric`
- `N01b`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be finite`
- `N01c`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be finite`
- `N01d`: ModelRegistryError - `subscription_arr_bridge.opening_arr.FY2027 must be finite`
- `N02`: ModelRegistryError - `driver subscription_arr_bridge.opening_arr must contain one value per forecast year`
- `N03`: ModelRegistryError - `missing drivers for subscription_arr_bridge: opening_arr`
- `N04`: ModelRegistryError - `unsupported drivers for subscription_arr_bridge: unknown_driver`
- `N05a`: ModelRegistryError - `subscription_arr_bridge.years must contain fiscal years`
- `N05b`: ModelRegistryError - `subscription_arr_bridge.years must contain fiscal years`
- `CONT-BREAK`: ModelRegistryError - `opening_arr continuity failed: FY2028`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[215.0]
- `OBS-DEFAULT-EQUIV`: raised=None actual=[210.0]
- `OBS-GRR-ONE-SECOND-YEAR`: raised=None actual=[215.0, 250.0]
- `OBS-BRIDGE-TOL-1E-7`: raised=None actual=[215.0]
- `OBS-BRIDGE-TOL-1E-6`: raised=ModelRegistryError actual=None - opening_arr stock-flow balance failed: FY2027

## 5. Judgement calls the reviewer should attack first

1. The card's CONT-BREAK patch is documented in the card as 'each year balances individually, but year-2 opening is 1 above year-1 closing'. With the frozen numbers (`opening_arr=[200,251]`, `closing_arr=[250,251]`) that description is not what happens: FY2027's closing was also moved to 251, so FY2027's BALANCE check fires first. The observed message is `opening_arr stock-flow balance failed: FY2027`, not a continuity message. The frozen requirement is the exception TYPE, and it was met; a reviewer should confirm that satisfying the type is enough, or ask for a case whose numbers make the card's prose literally true.
2. Because of that, the product's cross-year CONTINUITY guard (`opening_arr continuity failed`) is NOT exercised by this case set. The guard exists in the code but is a change the implementer did not run; the parent agent was told.
3. the continuity positive relies on `gross_retention_rate = 1` in FY2028; the retained-ARR guard (`opening_arr * gross_retention_rate == 0 and expansion_arr > 0`) is therefore not triggered, but a zero opening ARR with positive expansion would be. The non-gating observation OBS-GRR-ONE-SECOND-YEAR only records that the input replays.
4. `usage_revenue` is optional with no explicit default and is silently zero-filled.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review
  plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated
  specification, the existing implementation is retained.
- It does **not** claim that a formula pass on this card implies anything about the other 30
  models: the parent card explicitly forbids extrapolating accuracy from formula passes.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M24.py --card M24 --out-root <scratch>` and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` against
   `iso/checkout_scripts` and diff `run_result.json`.
2. Re-run `scripts/verify_prefix_chain.py <plan>` to confirm the oracle.md frozen-body chain.
3. Confirm the isolated copy hashes still equal production
   (`evidence/M24/source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running it.
5. Re-run `scripts/enumerate_oq_rulings.py` and compare the counts with
   `evidence/M24/oq_rulings_enumeration.json`.
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
| R5_required_message_requirement_emptied | 3 | 3 |
| D_restored_uncorrupted | 0 | 0 |

`frozen_hashes_unchanged` = `True`. Full record:
`recovery/selfcheck/selfcheck_result.json`.

<!-- BEGIN independent-review verdict (round 2, transcribed verbatim) -->

> **独立复核裁决（revision r2 后）：`changes_required`。仍有 1 项阻塞 + 1 项闸门缺口。**
> 先说进展，两点均已独立证实：①**跨年 continuity 守卫首次有了失败样本**——我自行构造并四次独立复现 `opening_arr=[200,251], closing_arr=[250,251]` → `opening_arr continuity failed: FY2028`，且 FY2027 桥确实自平（`200−200×(1−0.9)+30+40 = 250 = closing_arr[0]`）；②上轮 P2-1 的 runner 缺陷已修好，`expected` 类型比较与消息子串比较都生效，我自己写的 3 个变异探针（expected→ValueError、消息→不可能子串、消息→长度守卫措辞）分别得到 rc=3/3/3，我自己重跑 `selfcheck_mutations.py --card M24` 得到 rc 序列 `[0,3,3,2,3,3,3,0]`、`frozen hashes unchanged: True`。
> 阻塞项：**`CONT-BREAK` 与 `CONT-BREAK-CROSSYEAR` 的输入逐字节相同**。二者 `id`/`kind`/`expected`/`base_input`/`value` 五项完全一致，我按 `cases.json` 重建 `value` 后 canonical sha256 均为 `adcca43833ee685b0bf0c6d621b52120f39e618d14e0d82b2158ffe18913d67f`。因此 `negative_summary.total = 12` 实为"11 个不同输入 + 1 个重复输入"，12/12 被重复计一次；更要紧的是两个用例的冻结消息要求（`stock-flow balance failed: FY2027` 与 `continuity failed: FY2028`）落在**同一个输入**上、彼此互斥，目前只因 `CONT-BREAK` 恰好没写消息要求才没变红。这不产生错误接受（产品行为正确），但用例集"每个反例独立"的前提被破坏，且 `oracle.md` 第 5 节现在同时展示这两行，读者会读出矛盾。
> **最小修法（无需编辑正文，只改 `cases.json`）**：`CONT-BREAK` **保持卡片 L117-L122 的原文 patch 不动**（`opening_arr=[200,251]`、`closing_arr=[250,251]`），只**补上** `expect_message_contains = "stock-flow balance failed: FY2027"`；`CONT-BREAK-CROSSYEAR.value` 改为 `{"opening_arr": [200, 250], "closing_arr": [250, 251]}`，消息要求保持 `continuity failed: FY2028`。此时二者输入 distinct、两条消息要求各自可达，而且卡片 L116"两个年度各自平衡"的散文第一次在用例集里成为可执行事实（我已在隔离快照上验证：`opening_arr=[200,250], closing_arr=[250,251]` 的实测消息正是 `continuity failed: FY2028`，FY2027 桥自平 `200−20+30+40=250=closing[0]`）。
> 闸门缺口：runner 的 `message_requirement_met = None if requirement is None else ...`，即**删除** `expect_message_contains` 字段不会被判失败。我实测把 M24 两个带要求的用例去掉该字段后，`rc=0`、`message_requirements_checked=[]`。建议在 `cases.json` 增冻结字段 `required_message_ids: ["NEG-CARD","CONT-BREAK-CROSSYEAR"]`，runner 断言其存在且非空，缺失即 rc=3。
> 其余均已核：`rc=0`、`stderr` 0 字节、正例 `[215.0]`、连续性 `[215.0, 250.0]`、defaults `[210.0]`；P3-2 的两条非判定性探针我复算一致（`closing_arr=250+1e-7` → 通过 `[215.0]`；`+1e-6` → `stock-flow balance failed: FY2027`）；我自造输入另证桥/收入分离（同一桥下 `fraction=[1,0,0]` → `80.0`，`fraction=[0,1,1]` → `130.0`；`closing=111` → 桥拒绝；全零桥 + `usage=9.5` → `9.5`）。正文改动经我逐节复算：17 行，`## 2./3./4./8./10.` 与全部既有期望值逐字节未变，前像 sha256 `fbef9d54…`。
> 补充：`revision_r2.json` 仍写 `state=not_started`、`trigger="…has not yet been received"`、`review_verdict_received=None`，而同一文件已列出六项复核处置并引用我的结论——请一并更正（不影响数值）。
> 签收边界：即便修完，签收范围也只能是 **`formula`**；`disclosure_adaptation` 保持 `unmapped`，`accuracy` 保持 `unproven`。两条产品侧待裁项（保留 ARR 守卫 `==0` 精确比较；`retail_franchise.recognized_fee_rate` 同时是 optional-without-default 与 ratio）继续登记，不阻塞本卡。

<!-- END independent-review verdict (round 2) -->

<!-- BEGIN independent-review verdict (round 3, transcribed verbatim) -->

> **独立复核裁决（round 3 终裁）：`accepted_scoped`（仅 formula）。`changes_required` 予以解除——实现者的偏离经我独立复核成立，我 round-2 清单的字面值在本卡基座上不可执行。**
>
> 偏离裁定（我逐条独立实测，非采信）：
> 1. 冻结 `continuity_positive` 为 `opening_arr=[200,250]`、`closing_arr=[250,250]`，故卡片 L117–L122 原文 patch（`opening=[200,251], closing=[250,251]`）在 FY2027 **自平**（`200−20+30+40=250=closing_arr[0]`），失败发生在 FY2028 跨年锚定 → 我实测 `opening_arr continuity failed: FY2028`。**我 round-2 要求的 `stock-flow balance failed: FY2027` 在该输入上确实不可达**；
> 2. 我 round-2 给出的 CROSSYEAR 新值 `opening_arr:[200,250]` 与冻结基座**逐字节相同**（空操作）→ 我实测该"改动"后与 control 完全一致（`[215.0, 250.0]`）。**是我的清单写错，不是实现者的实现错**；
> 3. 在该基座上，不改 `closing_arr[0]` 则 FY2027 平衡守卫代数上不可达（代入 `opening[1]=closing[0]` 后 index-1 平衡期望恒为 `closing[0]`）；我另实测 `closing_arr=[251,251]` 可让它可达，故"改任何 driver 都不可能"这一措辞过强，但其结论对本裁定成立。
>
> 处置是否满足实质要求：**满足**。①跨年锚定守卫有判定性失败样本（`CONT-BREAK` 用卡片原文 patch，消息要求冻结为 `continuity failed: FY2028`）；②两个守卫分属不同输入——平衡守卫由 `NEG-CARD`（`closing_arr=[251]` → `stock-flow balance failed: FY2027`）覆盖，跨年连续性守卫由 `CONT-BREAK` 覆盖；③M24 回到 **11 个用例 / 11 个互不相同的输入**（我独立重建每个用例输入并做 canonical sha256，无重复），上轮"12/12 含一个重复输入"的问题消除。
>
> 闸门：`required_message_ids = ["NEG-CARD","CONT-BREAK"]` 已闭合；我实测"删掉成员的消息要求"→rc=3、"成员要求置空"→rc=3、"连闸门字段一起删"→rc=3。9 个探针序列 `[0,3,3,2,3,3,3,3,3,0]`（我核对了 registry 的 tag 列表与 code）。
>
> 冻结与留档：`oracle.md` 0–12 节自 round 2 起逐字节未改（`9c8f6b23…`/13382 B）；`splice_oracle_md_r2.py` 本轮未运行；`final_verify.txt` False 计数 0；`verify_prefix_chain.py` ALL-OK；`stderr.txt` 0 字节。
>
> 关于 FY2027 桥平衡守卫的 2 年路径样本：**判定为不需要**。若 owner 仍要，只需在 `cases.json` 冻结 `{"opening_arr":[200,250],"closing_arr":[251,251]}`（我实测 → `stock-flow balance failed: FY2027`），**无需改 `oracle.md` 正文**，也无需改 `continuity_positive`。
>
> 签收边界：**仅 `formula`**。`disclosure_adaptation` 保持 `unmapped`，`accuracy` 保持 `unproven`。两条产品侧待裁项（保留 ARR 守卫 `==0` 精确比较；`retail_franchise.recognized_fee_rate` 同时是 optional-without-default 与 ratio）继续登记，不阻塞本卡。

<!-- END independent-review verdict (round 3) -->

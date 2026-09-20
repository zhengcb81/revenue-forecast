# M19 · implementer review record — gaming（活跃用户付费变现）

Card M19（`execution_v2/card_M19.md`），Parent I-10，model_id `gaming`，
attempt `execution_runs/M19/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`decision.md`、
`handoff.json` 一致。

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts and issue its own verdict.

## 1. 做了什么（可复核的清单）

| 步骤 | 结果 | 证据 |
|---|---|---|
| A 绑定 | 只读复制进本 attempt，副本与生产 hash 相等 | `binding.json`、`evidence/M19/source_manifest.json` |
| 冻结 | `oracle.md`（手算）→ `oracle.json`（独立 stdlib 脚本）→ 首次产品 stdout，mtime 顺序成立 | `source_manifest.json` → `mtime_ordering` |
| B 正例 | 实测 `[1010.0]` vs 手算 `[1010]`，abs_diff 0.0，容差 1.01e-06 | `evidence/M19/stdout.txt` |
| B 保真 | 扁平 `list`、长度 1 = `len(years)` = `len(expected)`、普通有限 `float` | `run_result.json` → `fidelity` |
| B 连续性 | 实测 `[1010.0, 1584.0]` vs 期望 `[1010, 1584]` | `run_result.json` |
| B 默认值 | 实测 `[1000.0]` vs 期望 `[1000]`（**不参与判定**） | `run_result.json` |
| C 负例 | 11/11 以 `ModelRegistryError` 拒绝 | `evidence/M19/negative_results.json` |
| 端点保真 | `OBS-PAYER-BOUNDARY`：`payer_conversion=[1.0]` → 实测 `20010.0` = 手算期望 | `run_result.json` → `observations` |
| 保真重生成 | `input/oracle/cases.json` 重生成后 sha256 **逐字节相同** | `evidence/M19/oracle_regen_proof.json` |
| 变异证明 | 副本篡改 → rc 3 / 3 / 2 / 1；未篡改 → rc 0；冻结件 hash 未变 | `evidence/M19/mutation_selfcheck.json` |
| 边界探针 | `active_users=[0]` → 实测 `10.0`，数量域含下端点 | `evidence/M19/extra_probes.json` |
| D/E/F | **未做**（D 需专业决策；E 属 I-10-A；F 需 I-12 冻结设计） | `decision.md`、`handoff.json` |

## 2. oracle 的独立性（本卡要害）

- 期望值来自 `scripts/oracle_M19.py`（stdlib only），`evidence/M19/oracle_selfcheck.json` 记录
  `product_import_present = false`。
- runner 只调用一个产品函数，期望只从 `evidence/M19/oracle.json` 读。
- 负例全部由新的内存 deepcopy 构造，不经 JSON 解析器；`PASS_rejected` 要求
  `isinstance(exc, ModelRegistryError)`，导入/文件错误记 FAIL。
- 卡片引用的行号（入口 308、注册 239）在隔离副本上逐行复核（两个 anchor 均为 true）。
- `OBS-PAYER-BOUNDARY` 测的是**卡片自己写的域**（L8「付费率0–1」）在实现里是否含端点：
  运行前把手算后果 20010 写进 oracle 脚本，运行后实测一致，因此"0–1"这句话在本实现下是被验证的，
  而不是被引用的。

## 3. 结果明细（含实际异常消息）

- registry formula：`revenue = active_users * payer_conversion * revenue_per_payer + other_revenue`
- required `['active_users', 'payer_conversion', 'revenue_per_payer']`；optional `['other_revenue']`；declared defaults `{}`
- effective bounds：`active_users [0.0, inf]`、`payer_conversion [0.0, 1.0]`、
  `revenue_per_payer [0.0, inf]`、`other_revenue ['-inf','inf']`（signed driver）
- 11 个负例消息：
  - `NEG-CARD`：driver gaming.payer_conversion must be between 0.0 and 1.0: FY2027
  - `N01a`：gaming.active_users.FY2027 must be numeric
  - `N01b/c/d`：gaming.active_users.FY2027 must be finite
  - `N02`：driver gaming.active_users must contain one value per forecast year
  - `N03`：missing drivers for gaming: active_users
  - `N04`：unsupported drivers for gaming: unknown_driver
  - `N05a/b`：gaming.years must contain fiscal years
  - `CONT-BREAK`：gaming.years must be consecutive and increasing
- 负例计数：`rejected_with_ModelRegistryError=11`、`not_rejected=0`、`wrong_exception_type=0`、
  `import_or_file_error=0`。
- 退出码：`B-product-run` 原始 rc = **0**（= 期望 0）；runner 回读校验
  `printed_matches_evidence_file: True`。

## 4. 观察项与探针（均**不**参与退出码）

- `OBS-BASE-IGNORED`：`base_revenue=999` → `[1010.0]`（`_rowwise` 丢弃 `base_revenue`）。
- `OBS-DEFAULT-EQUIV`：显式 `other_revenue=[0]` 与省缺相同（`[1000.0]`）。
- `OBS-PAYER-BOUNDARY`：`[20010.0]`，与冻结的数值期望一致。
- `PROBE-ACTIVE-ZERO`：`[10.0]`（数量域含 0 端点）。

## 5. 请 reviewer 优先攻击的点

1. **期间口径完全不可运行时拒绝。** DAU × 年度 ARPPU 这类错配在数值上"看起来正常"。
   请确认 `disclosure_adaptation = unmapped` 没被公式通过稀释（`DEC-M19-1`）。
2. **流水 ≠ 收入同样不可拒绝**。渠道费/递延不在模型内（`DEC-M19-2`）。
3. **`payer_conversion=1.0` 被接受**（实测 20010.0）：`[0,1]` 域内正确，但"100% 付费率"业务上可疑，
   属专业裁定。
4. **`other_revenue` 允许负数**（signed driver）。
5. **静默 0**：`other_revenue` 无显式 default，被静默补 0（`OQ-02`；注册表级 31 个可选 driver 同现象）。
6. **连续性用例的性质**：逐年独立模型，`CONT-BREAK` 只是财年不连续拒绝，不是存量桥证据。
7. **隔离绑定来源**：I-00-B 未物化 checkout，本 attempt 自行物化只读快照（hash 与生产相等），
   需 owner 裁定（`OQ-01`）。
8. **pytest 未安装**：`A0b` 离线探测 rc = 1（无本地 wheel、网络禁用）；本卡无命令需要 pytest。

## 6. 本卡**不**主张什么

- 不主张模型准确，也不主张一家公司的映射可外推（`accuracy = unproven`）。
- 不主张 `disclosure_adaptation`（D 未作，属专业决策）。
- 不重写公式（本卡零产品改动）。

## 7. 建议 reviewer 动作

1. 在 scratch 重跑 `scripts/oracle_M19.py --card M19 --out-root <scratch>`，逐字节比对冻结的三个文件。
2. 重跑 `scripts/run_card.py`（argv 见 `commands.json` 的 `B-product-run`），比对 `run_result.json`。
3. 确认隔离副本 hash 仍等于生产。
4. 复算一个本卡未使用的 oracle：建议 `active_users=[2500]`、`payer_conversion=[0.04]`、
   `revenue_per_payer=[12]`、`other_revenue=[0]`，手算 2500×0.04×12 = 1200，先冻结再运行。
5. 裁定 `evidence/M19/oq_rulings.json` 的 OQ-01…OQ-05。

---

退出码自检（本卡自带）：见 `evidence/M19/mutation_selfcheck.json`。

| case | 篡改（仅作用于 `recovery/selfcheck/` 的副本） | 实测 rc | 期望 rc | 证明 |
|---|---|---|---|---|
| A | `oracle.json` 正例期望每个值 +1 | **3** | 3 | 篡改的期望无法躲在 rc=0 后面 |
| B | `cases.json` 的 N04 驱动名换成已注册的 `other_revenue` | **3** | 3 | 未被拒绝的负例会被判为负 |
| C | 正例 `expected_float`/`tolerances` 各多一项 | **2** | 2 | 保真不符 → 拒绝给判定 |
| D | scratch 副本删除 `cases.json` | **1** | 1 | harness 失败与判定失败可区分 |
| E | 未篡改副本 | **0** | 0 | 绿可恢复 |

冻结件在 A–E 之后重新 hash，与运行前一致（`frozen_evidence_unchanged: true`）。

### 记录收尾单元（不产生任何产品行为）

`H-write-handoff`（生成 `handoff.json`）与 `Z-close-attempt`（写 `commands.json` 与
`after/final_deliverable_hashes.json`）在测量流水线（A0…G，14 个单元）之后**单独**由
`scripts/run_closing.py` 执行，各有独立 command-run-id 记录：
`evidence/M19/runs/H-write-handoff/`、`evidence/M19/runs/Z-close-attempt/`。
`commands.json` 由 Z 自己写，所以 Z 自己的 rc.json 是在它返回**之后**才刷新的：`commands.json` 中
Z 的 `raw_rc`（当前为 0）来自**同 argv 的上一次执行**，该口径写在该单元的 `raw_rc_note` 里；
**最近一次执行**的 raw rc 始终在 `evidence/M19/runs/Z-close-attempt/rc.json`（自述其
stdout/stderr 的 sha256）与 `pipeline_run.json`。
`after/final_deliverable_hashes.json` 按构造排除它自己与 `runs/Z-close-attempt/**`
（原因见该文件的 `excluded_from_the_table`）。

---

状态：`formula = review_pending`；`disclosure_adaptation = unmapped`；`accuracy = unproven`。

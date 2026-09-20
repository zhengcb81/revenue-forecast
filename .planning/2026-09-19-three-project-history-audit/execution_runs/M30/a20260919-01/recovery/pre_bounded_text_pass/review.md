# M30 · finite_adoption · finite market adoption — review.md（实现者自述 + 待 reviewer 攻击点；**未自签**）

状态：`review_pending`。本文件由实现者撰写，**不含任何 accepted**；独立 reviewer 的结论应另写并覆盖/追加本节。生成时间 2026-09-20T03:00:30.315400+00:00。

## 1. 本 attempt 实际做了什么

1. 绑定：`binding.json` 在同一隔离副本上读回模型契约，并断言 `declared_drivers_match_registry_contract = true`；卡片引用的入口行 `model_registry.py:308` 与注册行 `model_extensions.py:216` 都在跑产品之前核对过。
2. 冻结期望：`oracle.md`（手算）与 `evidence/M30/{input,oracle,cases}.json`（由`scripts/oracle_M30.py` 生成，只用标准库、从不 import 产品）。
3. 唯一产品调用：`calculate_registered_model(**input)`，经 `--code-root iso/checkout_scripts`（与生产逐字节相同）。
4. 负例：11 个，每个都在**新的 deepcopy** 上执行；只有 `model_registry.ModelRegistryError` 记为通过。
5. 变异自证与重生成证明：`mutation_selfcheck.json`、`oracle_regen_proof.json`。
6. 枚举与边界探针：`registry_enumeration.json`（`oq_rulings.json` 的所有计数来源）、`extra_probes.json`（非门控）。

## 2. 关键测量（全部取自证据文件，未在此重述第二遍）

- 正例：期望 [600]，实测 [600.0]（手算：500 + 100 - 50 - 200 = 350 (bridge) ; 200 x 3 = 600）
- 连续性正例：期望 [600, 0]，实测 [600.0, 0.0]
- 结构/长度保真：`fidelity_ok = True`，`len(output) == len(years)` = True
- 负例：11/11 拒绝；runner 原始退出码 0（判定 `pass`）
- 变异自证（先红后绿）：见 evidence/M30/mutation_selfcheck.json
- oracle 逐字节可重生成：见 evidence/M30/oracle_regen_proof.json

## 3. 请求独立 reviewer 攻击的点

1. **手算复算**：从 `card_M30.md` 原文独立重算正例与两年连续性，不看本 attempt 的`oracle.json`；再看 `evidence/M30/oracle.json` 的 `hand_work` 是否与你的算式一致。
2. **负例语义**：确认 11 个负例的**期望错误原因**与卡片/共用规则一致，特别是卡片专属负例（closing_unserved_market = [351] (stock-flow balance)）与 CONT-BREAK（opening_unserved_market = [500, 351] with closing_unserved_market = [350, 351] (continuity: year 2 opens 1 above year 1 closing)）——注意：this model DOES have the stock-flow bridge, so CONT-BREAK is a genuine cross-year continuity break and the card's own two-year case is used verbatim as the continuity positive。
3. **是否只测了目标异常**：`negative_results.json` 记录了 `is_target_type` 与`is_import_or_file_error`，请确认没有任何一条以 ImportError/FileNotFoundError 混过。
4. **变异证明是否真的先红后绿**：`mutation_selfcheck.json` 的 5 次运行分别是 rc 3 / 3 / 2 / 1 / 0；请尤其确认 B 例（把 CONT-BREAK 改成完全平衡的输入后 runner 必须报`FAIL_not_rejected`）不是同义反复，且 `B0_unpatched_continuity_break` 先证明了原负例确实被拒。
5. **oracle 是否真的独立**：`oracle_selfcheck.json` 只列 import 行；请自行确认生成器没有间接 import 产品，并确认 `oracle_regen_proof.json` 的逐字节一致是**重新生成**而非复制。
6. **mtime/新鲜度**：请检查 `source_manifest.json` 的 `mtime_ordering`、`oracle_document.freshness_claim` 与 `revision_r2.json`，特别是本 attempt 已自曝的OQ-05（`oracle.md` 事后按同内容恢复）。请裁定该自曝是否足以支撑“冻结先于运行”，或要求重跑一个新 attempt。
7. **卡片正文与注册表的一致性**：请独立核对 `card_M30.md` 的必填清单与注册表，并对任何分歧给出裁定。
8. **未被本卡证明的东西**：披露适配（`unmapped`）与准确性（`unproven`）**没有**因为本卡通过而获得任何证据；请确认 `qualification.json` 只动了 `formula`。
9. **隔离与生产零改动**：请核对 `integrity.json`、`before/`+`after/` 的 `git status --porcelain` 与 `source_hashes.txt`，并确认 `changes.diff` 为空是**真实**的。

## 4. 实现者已知的弱点（主动列出，便于攻击）

- 三个 attempt 的 `scripts/oracle_*.py` 是**同一份**生成器（都含 M29/M30/M31 三个 builder），因此 `oracle_selfcheck.json` 的 `script_sha256` 三卡相同；独立性来自“不 import 产品”，不来自“三份不同的脚本”。
- `defaults` 用例与 `positive` 用例逐字节相同（这三个模型确实没有可选驱动器），因此该用例不提供额外证据，只用于证明“无默认值”这一契约事实。
- `extra_probes.json` 是非门控的：它的期望值不进入 runner 退出码，reviewer 不应把它当作通过条件，但可以质疑其中任何一条 probe 的设计。
- `iso/oracle_card.md` 的名字有历史误导性（它不是 markdown，而是 `--emit-script` 写出的生成器副本）；`source_manifest.json` 的 `naming_note` 已声明。

## 独立验收结论（独立 reviewer session）

- card_id: M30 · model_id: finite_adoption · attempt: a20260919-01
- 结论：**accepted_scoped**
- 授予：**仅 `formula`**
- 未授予：`disclosure_adaptation`（保持 `unmapped`）、`accuracy`（保持 `unproven`）；
  D–E/F 的后续产物均未产出，按卡文不阻塞 A–C，也不得虚填。

复核方式与结果：
1. 从 `card_M30.md` 原文手算正例：桥 `500+100−50−200 = 350`（与卡片给定 closing 一致）、
   收入 `200×3 = 600`；两年连续性预期 `[600, 0]`。隔离解释器实测 `[600.0]` / `[600.0, 0.0]`。
2. 自造卡外正例 4 个（含 `adopted_units×price` 与未服务市场桥**分离**的用例：
   adopted 300 × 2.5 = 750 而 closing 由桥独立定为 600；两年版 250×2.5 = 625 而 closing 500；
   饱和年 adopted==pool → closing 0）。全部与手算一致。
3. 自造卡外负例 21 个（字符串数字、`years=[2027.0]`、NaN/±Inf 落在最后驱动、负值越界、
   `reviewer_unknown`、重复/跳跃年、长度不符、负 `base_revenue`、`drivers` 非映射、bool 元素、
   年份 0/10000、池透支至 closing=-50）——**全部**以 `ModelRegistryError` 被拒。
4. **桥与连续性都拿到了失败样本**：
   - 卡片 NEG-CARD `closing_unserved_market=[351]` →
     `opening_unserved_market stock-flow balance failed: FY2027`（**桥平衡守卫**，非长度守门；
     长度问题报的是 `must contain one value per forecast year`，message 可区分）；
   - 我自造"各年自平、仅第二年 opening≠上一年 closing"（`opening=[500,351]`、`closing=[350,351]`）→
     `opening_unserved_market continuity failed: FY2028`（**跨年连续性可触发**）；
   - 仅第二年桥不平 → `stock-flow balance failed: FY2028`。
5. 复现 11 个冻结负例与 6 子运行变异自证（rc 序列 3/0/3/2/1/0）。
6. 独立重跑生成器：`input.json`/`oracle.json`/`cases.json`/`oracle_selfcheck.json` 与冻结件**逐字节相同**。
7. 重跑 `enumerate_registry.py`：计数与冻结件逐字段相同；本模型 `optional=() defaults={}`，
   `model_registry.py:335` 静默补 0 **不可达**（实测缺失必填即拒）。
8. 生产三锚点 hash 一致；`iso/checkout_scripts` 与生产逐字节相同；`<PLAN>\reviews` 未被写。
9. 产品入口重放 rc=0/verdict=pass，门控字段与冻结 `run_result.json` 逐字段相同。

**OQ-05 裁定（对 formula 不阻断）**：同 M29 —— 链 ② 锚定的是**生成器代码**而非 `oracle.md` 文本，
管线从不校验 `oracle.md`；`oracle.md` 与 `oracle.json` 在全部门控期望上逐条一致，但一致性 ≠ 事前性；
A–C 门控期望由可逐字节重生成的 `oracle.json` 承载，故 formula 不依赖 `oracle.md` 的 mtime。
我显式不采信 `oracle.md` 字节，也不接受"oracle 文本事前冻结"主张。
`oracle.md` §4 的两年用例系**卡片原文照抄**（`card_M30.md` L52–106），我已逐字段核对与 `input.json` 相同。

**保留的反例与缺陷（不改变本次 verdict）**：
- P2：`run_card.py` 不比较 `cases.json[*].expected`。把逐例 `expected` 改成 `"ValueError"`/`42`/
  全部 `"ImportError"` 后重跑仍 **rc=0 pass**（对照反例：no-op 补丁 → rc=3；篡改 `oracle.json` 正例 → rc=3）。
- P2：`source_manifest.json` 同文件内 freshness 自相矛盾（flag 为 true，注释称 mtime 更晚）。
- P3：`evidence/M30/exit_code.json` 不存在却被 docstring 引用；`evidence_hashes.json` 94/97 通过；
  `runs/A0-iso-venv-create/rc.json` 的创建 argv 用占位符。

**待 owner / 提级项**：OQ-01（隔离绑定来源）；P2 的 `source_manifest.json` 文字更正的批次级处置；
若要把 `oracle.md` 当作事前冻结证据，则须按 OQ-05 最小范围重跑。

- 我**未**授予：D/E/F 任何资格；真实公司适配；准确性。
- 我**未能验证**：pass-1 是否调用过产品；`oracle.md` 运行前字节；仓库整体"零写入"。

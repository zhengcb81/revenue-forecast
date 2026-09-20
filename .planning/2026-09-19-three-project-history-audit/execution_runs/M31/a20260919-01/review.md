# M31 · inventory_sellthrough · inventory and sell-through bridge — review.md（实现者自述 + 待 reviewer 攻击点；**未自签**）

状态：`review_pending`。本文件由实现者撰写，**不含任何 accepted**；独立 reviewer 的结论应另写并覆盖/追加本节。生成时间 2026-09-20T03:00:31.038124+00:00。

## 1. 本 attempt 实际做了什么

1. 绑定：`binding.json` 在同一隔离副本上读回模型契约，并断言 `declared_drivers_match_registry_contract = true`；卡片引用的入口行 `model_registry.py:308` 与注册行 `model_extensions.py:220` 都在跑产品之前核对过。
2. 冻结期望：`oracle.md`（手算）与 `evidence/M31/{input,oracle,cases}.json`（由`scripts/oracle_M31.py` 生成，只用标准库、从不 import 产品）。
3. 唯一产品调用：`calculate_registered_model(**input)`，经 `--code-root iso/checkout_scripts`（与生产逐字节相同）。
4. 负例：11 个，每个都在**新的 deepcopy** 上执行；只有 `model_registry.ModelRegistryError` 记为通过。
5. 变异自证与重生成证明：`mutation_selfcheck.json`、`oracle_regen_proof.json`。
6. 枚举与边界探针：`registry_enumeration.json`（`oq_rulings.json` 的所有计数来源）、`extra_probes.json`（非门控）。

## 2. 关键测量（全部取自证据文件，未在此重述第二遍）

- 正例：期望 [160]，实测 [160.0]（手算：100 + 60 + 10 - 5 - 80 = 85 (bridge) ; 80 x 2 = 160）
- 连续性正例：期望 [160, 0]，实测 [160.0, 0.0]
- 结构/长度保真：`fidelity_ok = True`，`len(output) == len(years)` = True
- 负例：11/11 拒绝；runner 原始退出码 0（判定 `pass`）
- 变异自证（先红后绿）：见 evidence/M31/mutation_selfcheck.json
- oracle 逐字节可重生成：见 evidence/M31/oracle_regen_proof.json

## 3. 请求独立 reviewer 攻击的点

1. **手算复算**：从 `card_M31.md` 原文独立重算正例与两年连续性，不看本 attempt 的`oracle.json`；再看 `evidence/M31/oracle.json` 的 `hand_work` 是否与你的算式一致。
2. **负例语义**：确认 11 个负例的**期望错误原因**与卡片/共用规则一致，特别是卡片专属负例（closing_inventory = [86] (stock-flow balance)）与 CONT-BREAK（opening_inventory = [100, 86] with closing_inventory = [85, 86] (continuity: year 2 opens 1 above year 1 closing)）——注意：this model DOES have the stock-flow bridge, so CONT-BREAK is a genuine cross-year continuity break and the card's own two-year case is used verbatim as the continuity positive。
3. **是否只测了目标异常**：`negative_results.json` 记录了 `is_target_type` 与`is_import_or_file_error`，请确认没有任何一条以 ImportError/FileNotFoundError 混过。
4. **变异证明是否真的先红后绿**：`mutation_selfcheck.json` 的 5 次运行分别是 rc 3 / 3 / 2 / 1 / 0；请尤其确认 B 例（把 CONT-BREAK 改成完全平衡的输入后 runner 必须报`FAIL_not_rejected`）不是同义反复，且 `B0_unpatched_continuity_break` 先证明了原负例确实被拒。
5. **oracle 是否真的独立**：`oracle_selfcheck.json` 只列 import 行；请自行确认生成器没有间接 import 产品，并确认 `oracle_regen_proof.json` 的逐字节一致是**重新生成**而非复制。
6. **mtime/新鲜度**：请检查 `source_manifest.json` 的 `mtime_ordering`、`oracle_document.freshness_claim` 与 `revision_r2.json`，特别是本 attempt 已自曝的OQ-05（`oracle.md` 事后按同内容恢复）。请裁定该自曝是否足以支撑“冻结先于运行”，或要求重跑一个新 attempt。
7. **卡片正文与注册表的一致性**：请独立核对 `card_M31.md` 的必填清单与注册表，并对任何分歧给出裁定。- **卡片正文与注册表的分歧（已被记录而非被静默解决）**：card_M31.md L9 omits net_revenue_per_unit from the required list while the registry declares it required; the binding asserts against the registry and records the divergence

8. **未被本卡证明的东西**：披露适配（`unmapped`）与准确性（`unproven`）**没有**因为本卡通过而获得任何证据；请确认 `qualification.json` 只动了 `formula`。
9. **隔离与生产零改动**：请核对 `integrity.json`、`before/`+`after/` 的 `git status --porcelain` 与 `source_hashes.txt`，并确认 `changes.diff` 为空是**真实**的。

## 4. 实现者已知的弱点（主动列出，便于攻击）

- 三个 attempt 的 `scripts/oracle_*.py` 是**同一份**生成器（都含 M29/M30/M31 三个 builder），因此 `oracle_selfcheck.json` 的 `script_sha256` 三卡相同；独立性来自“不 import 产品”，不来自“三份不同的脚本”。
- `defaults` 用例与 `positive` 用例逐字节相同（这三个模型确实没有可选驱动器），因此该用例不提供额外证据，只用于证明“无默认值”这一契约事实。
- `extra_probes.json` 是非门控的：它的期望值不进入 runner 退出码，reviewer 不应把它当作通过条件，但可以质疑其中任何一条 probe 的设计。
- `iso/oracle_card.md` 的名字有历史误导性（它不是 markdown，而是 `--emit-script` 写出的生成器副本）；`source_manifest.json` 的 `naming_note` 已声明。

## 独立验收结论（独立 reviewer session）

- card_id: M31 · model_id: inventory_sellthrough · attempt: a20260919-01
- 结论：**accepted_scoped**
- 授予：**仅 `formula`**
- 未授予：`disclosure_adaptation`（保持 `unmapped`）、`accuracy`（保持 `unproven`）；D–E/F 产物未产出。

复核方式与结果：
1. 从 `card_M31.md` 原文手算正例：桥 `100+60+10−5−80 = 85`、收入 `80×2 = 160`；
   两年连续性 `[160, 0]`。隔离解释器实测 `[160.0]` / `[160.0, 0.0]`。
2. 自造卡外正例 4 个（含 `sold_units×price` 与库存桥**分离**的用例：sold 300 → 450 而 closing 由桥独立定为 80；
   三年版每年把 production/purchase/scrap 改动只作用于桥、收入只随 sold 变），全部与手算一致。
3. 自造卡外负例 21 个——**全部**以 `ModelRegistryError` 被拒（字符串数字、`years=[2027.0]`、
   NaN/±Inf 落在最后驱动、负 `sold_units`、负 `opening_inventory`、未知驱动、重复/跳跃年、
   长度不符、负 `base_revenue`、非映射 `drivers`、bool 元素、年份 0/10000）。
4. **桥与连续性都拿到了失败样本**：
   - 卡片 NEG-CARD `closing_inventory=[86]` →
     `opening_inventory stock-flow balance failed: FY2027`（**桥平衡守卫**，非长度守门）；
   - 我自造"各年自平、仅第二年 opening≠上一年 closing"（`opening=[100,86]`、`closing=[85,86]`）→
     `opening_inventory continuity failed: FY2028`；
   - 仅第二年桥不平 → `stock-flow balance failed: FY2028`。
5. 复现 11 个冻结负例与 6 子运行变异自证（rc 序列 3/0/3/2/1/0）；
   非门控探针 `PROBE-CONTINUITY-TOLERANCE` 也复现（1e-10 不平衡被容差接受）。
6. 独立重跑生成器：`input.json`/`oracle.json`/`cases.json`/`oracle_selfcheck.json` 与冻结件**逐字节相同**。
7. 重跑 `enumerate_registry.py`：计数与冻结件逐字段相同；本模型 `optional=() defaults={}`，
   `model_registry.py:335` 静默补 0 **不可达**。
8. 生产三锚点 hash 一致；`iso/checkout_scripts` 与生产逐字节相同；`<PLAN>\reviews` 未被写。
9. 产品入口重放 rc=0/verdict=pass，门控字段与冻结 `run_result.json` 逐字段相同。

**OQ-05 裁定（对 formula 不阻断）**：同 M29/M30。

**关于"卡片正文与注册表分歧"——不接受该前提（必须勘误）**：
`card_M31.md` L9 **确实列了** `net_revenue_per_unit`，原文为
`- 必填：`opening_inventory`、`saleable_production`、`purchased_units`、`scrapped_units`、`sold_units`、`closing_inventory`、`net_revenue_per_unit`；可选默认：`{}`。`
（字节级检查 `contains net_revenue_per_unit: True`），母表 `model_cards.md` L2818 同样列出。
因此 `binding.json` 的 `card_text_required_list`（6 项）、`card_text_matches_registry: false`、
`divergence_note`、`oracle.md §12`、以及三卡 `handoff.json` 的 OQ-04 标题中
"does NOT list `net_revenue_per_unit`"的说法**均不成立**。
同一 attempt 的 `oq_rulings.json` 反而记了正确的 7 项，与 `binding.json` 自相矛盾。
**裁定**：处置（以注册表为准、按 7 驱动跑、缺失即 `missing drivers` 拒绝）**正确**，
但**不需要 owner 就"分歧"裁定**——该分歧不存在；需要的是勘误 `binding.json` / `oracle.md §12` /
`handoff.json` OQ-04 标题，并保留"注册表与卡片一致"的正确记录。
勘误为纯文字，不改变任何产品数值结论，故不阻断 formula；但**在勘误完成前不得关闭本卡**。

**保留的反例与缺陷（不改变本次 verdict）**：
- P2：`run_card.py` 不比较 `cases.json[*].expected`（把逐例 `expected` 改成 `"ValueError"`/`42`/
  全部 `"ImportError"` 后仍 **rc=0 pass**；对照反例均正确转红）。
- P2：`source_manifest.json` 同文件内 freshness 自相矛盾。
- P3：`evidence/M31/exit_code.json` 不存在；`evidence_hashes.json` 94/97；
  `oq_rulings.json` 的 `measured_probes[*].measured_matches` 为空字典（`extra_probes.json` 本身内容完整诚实）。

**待 owner / 提级项**：OQ-01（隔离绑定来源）；P2 的 `source_manifest.json` 文字更正；
若要把 `oracle.md` 当作事前冻结证据，则须按 OQ-05 最小范围重跑。

- 我**未**授予：D/E/F 任何资格；真实公司适配；准确性。
- 我**未能验证**：pass-1 是否调用过产品；`oracle.md` 运行前字节；仓库整体"零写入"。

## 独立 reviewer 追加确认（有界文本确认，独立 reviewer session，2026-09-20 04:2x）

- 抽验结论：①追加块与 reviewer 报告 §6 逐字节一致 → PASS；③ `source_manifest.json` 与 `oracle.md` E-1 已统一为
  "事后 stat 比较、不构成事前冻结"，未把 `oracle.md` 写成事前冻结证据 → PASS；④ `oracle.md` 冻结正文逐字节未动 →
  PASS（`recovery/pre_remediation/oracle.md` = `55a52c67…`/`aaa7faf7…`/`f89b1ad7…`，当前文件以其为前缀）；
  ⑤ F-01/P3 登记如实、无一处写成"已修" → PASS；② F-02 撤回**不完全** → 见残项 R-1/R-2。
- **维持判定：M29 / M30 / M31 = `accepted_scoped`（仅 `formula`）**；`disclosure_adaptation = unmapped`、
  `accuracy = unproven`；未授予任何其他资格。
- **关闭条件：M31 在 R-1 / R-2 清除前不得关闭**；M29/M30 的关闭不受影响（残项为共享文案）。
- 残项（纯文本，最小修法见 reviewer 确认报告）：
  R-1 `handoff.json` OQ-04 `title` 仍称存在 "the M31 card-text divergence on net_revenue_per_unit"；
  R-2 `scripts/write_binding.py`（三 attempt + `_m2931_build`）M31 常量仍为 6 项 / `False` / "does NOT list"；
  R-3 `handoff.json` OQ-05 `title` 仍称 "present mtime is later than the product stdout"（与同 attempt 的
      `source_manifest.oracle_md_provenance` 相反）；
  R-4 `scripts/pack_card.py` / `scripts/write_handoff.py` 仍会重新生成 R-3 的旧措辞。
- 只许追加：`oracle.md` / `review.md` 的进一步更正只能追加新节并附前缀 hash；
  `input.json` / `oracle.json` / `cases.json` 一律不得触碰；`handoff.json` / `binding.json` / `source_manifest.json`
  属活记录，可就地更正并记 `superseded_values`。
- 我零写入生产仓库。

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

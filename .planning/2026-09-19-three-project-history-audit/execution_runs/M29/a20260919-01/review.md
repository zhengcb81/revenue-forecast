# M29 · commercial_launch · supply-constrained commercial launch — review.md（实现者自述 + 待 reviewer 攻击点；**未自签**）

状态：`review_pending`。本文件由实现者撰写，**不含任何 accepted**；独立 reviewer 的结论应另写并覆盖/追加本节。生成时间 2026-09-20T03:00:29.561009+00:00。

## 1. 本 attempt 实际做了什么

1. 绑定：`binding.json` 在同一隔离副本上读回模型契约，并断言 `declared_drivers_match_registry_contract = true`；卡片引用的入口行 `model_registry.py:308` 与注册行 `model_extensions.py:211` 都在跑产品之前核对过。
2. 冻结期望：`oracle.md`（手算）与 `evidence/M29/{input,oracle,cases}.json`（由`scripts/oracle_M29.py` 生成，只用标准库、从不 import 产品）。
3. 唯一产品调用：`calculate_registered_model(**input)`，经 `--code-root iso/checkout_scripts`（与生产逐字节相同）。
4. 负例：11 个，每个都在**新的 deepcopy** 上执行；只有 `model_registry.ModelRegistryError` 记为通过。
5. 变异自证与重生成证明：`mutation_selfcheck.json`、`oracle_regen_proof.json`。
6. 枚举与边界探针：`registry_enumeration.json`（`oq_rulings.json` 的所有计数来源）、`extra_probes.json`（非门控）。

## 2. 关键测量（全部取自证据文件，未在此重述第二遍）

- 正例：期望 [300]，实测 [300.0]（手算：min(1000 x 0.2, 150) x 0.5 x 4 = 300）
- 连续性正例：期望 [300, 1000]，实测 [300.0, 1000.0]
- 结构/长度保真：`fidelity_ok = True`，`len(output) == len(years)` = True
- 负例：11/11 拒绝；runner 原始退出码 0（判定 `pass`）
- 变异自证（先红后绿）：见 evidence/M29/mutation_selfcheck.json
- oracle 逐字节可重生成：见 evidence/M29/oracle_regen_proof.json

## 3. 请求独立 reviewer 攻击的点

1. **手算复算**：从 `card_M29.md` 原文独立重算正例与两年连续性，不看本 attempt 的`oracle.json`；再看 `evidence/M29/oracle.json` 的 `hand_work` 是否与你的算式一致。
2. **负例语义**：确认 11 个负例的**期望错误原因**与卡片/共用规则一致，特别是卡片专属负例（adoption_rate = [1.1] (ratio domain [0,1])）与 CONT-BREAK（years = [2027, 2029] (must be consecutive and increasing)）——注意：this model has no stock-flow bridge, so its card-specific negative is a DOMAIN negative and its CONT-BREAK is a fiscal-year break。
3. **是否只测了目标异常**：`negative_results.json` 记录了 `is_target_type` 与`is_import_or_file_error`，请确认没有任何一条以 ImportError/FileNotFoundError 混过。
4. **变异证明是否真的先红后绿**：`mutation_selfcheck.json` 的 5 次运行分别是 rc 3 / 3 / 2 / 1 / 0；请尤其确认 B 例（把 CONT-BREAK 改成完全平衡的输入后 runner 必须报`FAIL_not_rejected`）不是同义反复，且 `B0_unpatched_continuity_break` 先证明了原负例确实被拒。
5. **oracle 是否真的独立**：`oracle_selfcheck.json` 只列 import 行；请自行确认生成器没有间接 import 产品，并确认 `oracle_regen_proof.json` 的逐字节一致是**重新生成**而非复制。
6. **mtime/新鲜度**：请检查 `source_manifest.json` 的 `mtime_ordering`、`oracle_document.freshness_claim` 与 `revision_r2.json`，特别是本 attempt 已自曝的OQ-05（`oracle.md` 事后按同内容恢复）。请裁定该自曝是否足以支撑“冻结先于运行”，或要求重跑一个新 attempt。
7. **卡片正文与注册表的一致性**：请独立核对 `card_M29.md` 的必填清单与注册表，并对任何分歧给出裁定。
8. **未被本卡证明的东西**：披露适配（`unmapped`）与准确性（`unproven`）**没有**因为本卡通过而获得任何证据；请确认 `qualification.json` 只动了 `formula`。
9. **隔离与生产零改动**：请核对 `integrity.json`、`before/`+`after/` 的 `git status --porcelain` 与 `source_hashes.txt`，并确认 `changes.diff` 为空是**真实**的。

## 4. 实现者已知的弱点（主动列出，便于攻击）

- 三个 attempt 的 `scripts/oracle_*.py` 是**同一份**生成器（都含 M29/M30/M31 三个 builder），因此 `oracle_selfcheck.json` 的 `script_sha256` 三卡相同；独立性来自“不 import 产品”，不来自“三份不同的脚本”。
- `defaults` 用例与 `positive` 用例逐字节相同（这三个模型确实没有可选驱动器），因此该用例不提供额外证据，只用于证明“无默认值”这一契约事实。
- `extra_probes.json` 是非门控的：它的期望值不进入 runner 退出码，reviewer 不应把它当作通过条件，但可以质疑其中任何一条 probe 的设计。
- `iso/oracle_card.md` 的名字有历史误导性（它不是 markdown，而是 `--emit-script` 写出的生成器副本）；`source_manifest.json` 的 `naming_note` 已声明。

## 独立验收结论（独立 reviewer session）

- card_id: M29 · model_id: commercial_launch · attempt: a20260919-01
- 结论：**accepted_scoped**
- 授予：**仅 `formula`**
- 未授予：`disclosure_adaptation`（保持 `unmapped`）、`accuracy`（保持 `unproven`）。
  本卡未产出 `disclosure_mapping.json` / `accounting_decision.md` / `historical_reconciliation.json` /
  `forecast_integration.json` / `accuracy_result.json` / `accuracy_independent_review.md`，
  按卡文这些不阻塞 A–C，也不得虚填。
- 未授予任何跨卡、跨模型或跨公司的推广：31 张公式卡通过不等于披露适配或准确性。

复核方式与结果：
1. 从 `card_M29.md` 原文**手算**正例 `min(1000×0.2,150)×0.5×4 = 300` 与两年连续性 `[300,1000]`，
   并用隔离解释器复跑，实测 `[300.0]` / `[300.0, 1000.0]`，均在冻结容差内。
2. 自造 5 个卡外正例（容量约束年、需求约束年、3 年含零产能年、`base_revenue` 被丢弃），
   全部与手算一致。
3. 自造 19 个卡外负例（字符串数字、`years=[2027.0]`、NaN/±Inf 落在**最后一个**驱动、
   负值越界、`reviewer_unknown`、重复年、三年跳跃、长度不符、负 `base_revenue`、
   `drivers` 非映射、bool 元素、`years=[0]/[10000]`、比例上下界）——**全部**以
   `model_registry.ModelRegistryError` 被拒，无"应拒而接受"。
4. 复现 11 个冻结负例与 6 子运行变异自证（rc 序列 3/0/3/2/1/0，B0 先证真被拒再钝化）。
5. 独立重跑生成器到自建 scratch 根：`input.json`/`oracle.json`/`cases.json`/`oracle_selfcheck.json`
   与冻结件 **逐字节相同**。
6. 重跑 `enumerate_registry.py`：models=31 / required=125 / optional=40 / ratio=41 /
   per-activity+unit=23 / optional 无声明默认=31，与冻结件逐字段相同；
   本模型 `optional=()`、`defaults={}`，`model_registry.py:335` 的静默补 0 **不可达**（已实测缺失必填即拒）。
7. 本模型**没有**存量桥，因此 STOP_BRIDGE 记 `not_applicable_with_reason`；
   其 `CONT-BREAK` 是财年断裂（`years=[2027,2029]`），已被拒。
8. 生产三锚点 hash 复算与任务书一致，`iso/checkout_scripts` 与生产逐字节相同，
   `<PLAN>\reviews` 未被写，company-wiki/filing-fetch 的 porcelain 前后一致。
9. 产品入口重放：真实 `run_card.py` 对真实 evidence 复跑 rc=0/verdict=pass，
   门控字段与冻结 `run_result.json` 逐字段相同。

**OQ-05 裁定（对 formula 不阻断）**：`oracle_document_freeze.json` 锚定的是**生成器代码**
（`iso/oracle_card.md` = `scripts/oracle_M29.py`，sha256 `3177247f…`），**不是** `oracle.md` 文本；
管线**从不读取或校验** `oracle.md`（`gen_oracle.py` 只要求 pointer + 脚本）。
`oracle.md` 的门控期望内容与 `oracle.json` 逐条对得上（正例/连续性/默认/11 个负例 id 与逐例拒绝原因，
全部输入驱动值均印在该文件），但"一致性"不等于"事前性"。
由于承载 A–C 门控期望的 `oracle.json` 可逐字节重生成、其生成器在运行前已被 hash 到盘上文件、
且 `oracle.json` mtime < `stdout.txt` mtime，**formula 资格不依赖 `oracle.md` 的 mtime**。
我**显式不采信** `oracle.md` 的字节（mtime 可被同内容改写后伪造，且该文件不在 git 跟踪内），
也不接受"oracle 文本事前冻结"这一主张。

**保留的反例与缺陷（不改变本次 verdict）**：
- P2：`run_card.py` **从不比较** `cases.json[*].expected`。我把 NEG-CARD 的 `expected` 改成
  `"ValueError"`、改成 `42`、把全部 11 条改成 `"ImportError"` 后重跑，三卡仍 **rc=0 pass**。
  负例判定只看 `isinstance(exc, ModelRegistryError)`。因此冻结的**逐例拒绝语义**在自动门里无约束
  （对照反例：把补丁改成 no-op → rc=3 `FAIL_not_rejected`；篡改 `oracle.json` 正例 → rc=3，
  说明循环本身对输入与 oracle 敏感，缺的只是"错误类型/原因"的绑定）。
- P2：`source_manifest.json` 自相矛盾——`mtime_ordering.oracle_md_precedes_product_stdout: true`
  与同一文件的 `oracle_md_mtime_note`/`freshness_claim.not_claimed`（称 mtime 晚于产品 stdout）相反；
  按记录数值（`oracle_md_mtime 1789872944.82` < `product_stdout_mtime 1789873148.36`）flag 是对的。
  请统一为"事后 stat 比较，不构成事前冻结"。
- P3：`run_card.py` docstring 指向的 `evidence/M29/exit_code.json` **不存在**；
  `evidence_hashes.json` 的 "written after everything else" 不成立（它在 03:59:10 写，
  H/H2/Z 在 04:00:25–31 才跑，97 项中 94 项通过）；
  `runs/A0-iso-venv-create/rc.json` 的 `creation_argv[0]` 是占位符 `<I-00-A template venv>\Scripts\python.exe`。

**待 owner / 提级项**：
1. OQ-01（隔离绑定来源：卡片要求 cwd 来自 I-00-B，本 attempt 自行 materialise `iso/checkout_scripts`）
   ——代码逐字节相同，但绑定来源语义需 owner 裁定。
2. 上列 P2 的 `source_manifest.json` 文字更正、以及共享缺陷 F-01（runner 不比较逐例 `expected`）
   ——属批次级 runner 议题，需 owner 决定是否作为后续卡的最小修复。
3. 若 owner 需要把 `oracle.md` 当作事前冻结证据，则本 attempt 不足以支撑，须按 OQ-05 最小范围重跑。

- 我**未**授予：D/E/F 的任何资格；任何真实公司适配结论；任何准确性结论。
- 我**未能验证**：pass-1 是否调用过产品；`oracle.md` 运行前的字节；仓库整体"零写入"
  （缺全仓 tracked 文件 hash 清单的前后对比）。

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

## 独立 reviewer session 点复审（裁决）

**结论：`accepted_scoped`（仅 formula 资格）。**
**授予范围：仅 `formula`，且仅限本 attempt（`execution_runs/M03/a20260919-01`）盘上版本、仅限 `iso/checkout_scripts` 副本。**

**未授予项（明示）**：
- `disclosure_adaptation` = **未授予**，保持 `unmapped`。§7 映射 1 的零残差**是构造性的**（`unit_revenue` 由同一行收入除以同一行销量反推），只证明量纲与乘法接线正确；映射 2 的 **14.3667% 分部缺口**（`88,697,566,000.69` 元，远超运行前冻结的 2% 容差）**未解决**，**严禁**把该 gap 填入 `other_revenue` 平账。
- `accuracy` = **未授予**，保持 `unproven`。`STOP_ACCURACY` 命中（无 I-12 冻结设计）。
- 未授予任何跨车型/跨公司/跨期间外推；未授予 D/E/F 完成；未授予"产销库存桥已完成"。
- `formula` 通过**不**提升 `disclosure_adaptation` 或 `accuracy`。

**独立复算（reviewer 自造输入）**：13 例全部通过。
- `units=[7,11], unit_revenue=[13.5,13.5], timing_factor=[1.0,0.5], other_revenue=[0,-4.25]` → `[94.5, 70.0]`
- defaults：只给 `units=[10]`、`unit_revenue=[3]` → `[30.0]`（`timing_factor`=1.0、`other_revenue`=0.0）
- 零量：`units=[0], other_revenue=[7]` → `[7.0]`（零量不得当"缺失"跳过）
- 连续性正例 `units=[100,110], unit_revenue=[2,2]` → `[200.0, 220.0]`；断裂 `years=[2027,2029]` → `unit_sales.years must be consecutive and increasing`
- 保真：全长 = `len(years)`，全部 `float` 且有限。
- 自造负例（均不在卡片清单内）全部以 `ModelRegistryError` 被拒：`timing_factor=[1.0000001]` / `unit_revenue=[-3.0]` / `units=[0]`+`other_revenue=[-1.0]`（净收入为负）/ `units=[True]`（bool 冒充数值）。
- 注册串读回：`revenue = units * unit_revenue * timing_factor + other_revenue`，与 `oracle.md` §1 冻结串逐字相同。

**冻结与追加（本卡有一处必须如实标注的例外）**：
- `oracle.json` 可由 `scripts/oracle_M03.py` **逐字节重生成**（`input.json` `9b319e8d3dae9435…`、`oracle.json` `cc78ce8384f66c6d…`、`cases.json` `41a3dd846399be54…` 三件 IDENTICAL；脚本自报 `BYD pv unit price 123751.503987`、`scope gap 88697566000.69 / 14.3667%`）。
- 预注册值未被改动：`card_M03.md` 的 `期望输出 [305]` = `oracle.json.expected_float [305.0]`；2% 冻结容差未被放宽；`oracle.json` mtime 01:20:42 早于 r2/r3 两轮修订。
- 段标题**无重复**。
- **例外（P1，已被实现者自曝，本裁决如实沿用、不得抹平）**：`NEW-1` 的修复**改动了 `oracle.md` 的冻结正文**（`## 7. 披露映射` 内第 122–123 行的派生单价由 `123,751.5203…` 改为 `123,751.503987(全精度)`），**破坏了"自 r2 起仅追加"的形态**。r3 段已自述此事并给出改前/改后 hash（`d0bed79bd868cda3…` → `45f10b58008f6020…`）与字节级重建法（9,889 B / `88635eb4`）。
  **判定**：改动对象是**派生单价的印刷笔误**，非公式预期/容差/披露数值；冻结判据值（`[305]`、13/13、2%、gap 14.37%）均未被改动；`oracle.json` 自首冻未动；实现者主动自曝。**故不推翻本卡的公式裁决，但"冻结正文未被改动"这一条对本卡必须写成"已被改动并自曝"。**

**P1（本卡必须处置）**：`handoff.json.evidence_paths` 含 `recovery/r2_exit_code_selfcheck/selfcheck_result.json`，**该文件在本卡 attempt 内不存在**（仅 M01 有）；本文件自检段却逐字引用它。处置：补落该文件，或删去该路径并改写自检段为"本卡未单独运行 selfcheck；`run_card.py` 与 M01 同一文件（`b5fcc685…`）"。（**缓解**：reviewer 已用同一 harness 独立复现 rc=0/1/2/3 四例全对。）

**九条复审项关闭情况**：`F-M01-01` = 仅 M01 有记录（本卡无 `first_run_forensics.json`）；`F-M01-02` CLOSED（独立复现四例全对）；`F-M01-03` CLOSED；`F-M02-01` CLOSED-AS-RESERVED（仍为 owner 裁定项，未自决，未改产品）；**`F-M03-01` CLOSED（但修复越界，见上"例外"）**；`F-M04-01` = not applicable to this card；**`NEW-1` CLOSED —— 但代价是改动冻结正文，已自曝**；`NEW-2` CLOSED；`NEW-3` not_applicable（M01 only）；`NEW-4` CLOSED。

**其余记账发现**：
- **P1**：`handoff.json.revision_history` 4 条真实轮次被记成 6 条（r2/r3 各逐字重复一次）。
- **P2**：`status="review_pending"` 与 `qualifications.formula="accepted_scoped …"` 自相矛盾；`evidence/M03/qualification.json.formula.status` 仍为 `review_pending`、`not_yet_independently_reviewed=true`。
- **P2**：`source_manifest.json.oracle_versions.oracle_md_versions[0].sha256`（`5597507c6a0e…`）为中间写入态，非当前盘上值（`b4881eeea7c1…`）。
- **P3**：`revision_r3.json` 自我 sha256 不可复现（其余 hash 声明全部相符）；`revision_r2.review_items` 扫入 `F-M03-01`/`F-M04-01`；`before/`+`after/` 三份文件与其他三卡同拷贝。

**订正要求（由实现者执行；见 §11）**：同上；另需把 `oracle.md` 的"仅追加"形态破坏与恢复方式在 `recovery/README.md` 或 `handoff.json.open_questions` 中登记为**永久性 provenance 事件**（不可回改为"从未改动"）。`disclosure_adaptation` 与 `accuracy` 两栏**不得**改动。

## 独立 reviewer session 点复审（裁决）

**结论：`accepted_scoped`（仅 formula 资格）。**
**授予范围：仅 `formula`，且仅限本 attempt（`execution_runs/M02/a20260919-01`）盘上版本、仅限 `iso/checkout_scripts` 副本。**

**未授予项（明示）**：
- `disclosure_adaptation` = **未授予**，保持 `unmapped`。§7 的对账**是构造性恒等式**（把已披露 FY2025 收入 `349,079,082,852` 元原值填回 `revenue` 必然零残差），只证明"复制"接线正确，**不能**证明来源/期间/总净额/口径，也**不是**准确性证据。
- `accuracy` = **未授予**，保持 `unproven`。`STOP_ACCURACY` 命中（无 I-12 冻结设计）；本模型无驱动，一期一值，无预测技能可评。
- 未授予任何跨公司/跨行业/跨期间外推；未授予 D/E/F 完成。
- `formula` 通过**不**提升 `disclosure_adaptation` 或 `accuracy`。

**独立复算（reviewer 自造输入）**：11 例全部通过。
- `revenue=[37.5, 0.0, 412.25, 1000000.0]`，4 年 → 逐值原样复制，diff 0；**含一个精确 0.0 的年份未被默认值替换**。
- base 无关性：同一 drivers 下 `base=0` 与 `base=999` 输出**逐值相同**。
- 保真：全长 = `len(years)`，全部 `float` 且有限。
- 自造负例（均不在卡片清单内）全部以 `ModelRegistryError` 被拒：`revenue=[-0.01]` / `revenue=["100"]` / `revenue=[None]` / `revenue=100.0`（标量而非序列）。
- 注册串读回：`revenue[t] = direct_revenue[t]`，与 `oracle.md` §1 冻结串逐字相同。

**冻结与追加**：
- `oracle.md` **无重复章节**；`oracle.json` 可由 `scripts/oracle_M02.py` **逐字节重生成**（`input.json` `8b7d9dc86578d1f6…`、`oracle.json` `258cd8e214e04fb7…`、`cases.json` `e10fb6c095bb16a8…` 三件 IDENTICAL）。
- 预注册值未被改动：`card_M02.md` 的 `期望输出 [80,0,120]` = `oracle.json.expected_float [80.0,0.0,120.0]`；容差规则未放宽；`oracle.json` mtime 01:19:52 早于 r2/r3 两轮修订。

**P1（本卡必须处置，否则"当前版本"的 oracle 层无凭据）**：**`oracle.md` 根本没有 r2 追加段，但本文件 `### Frozen expectations were NOT rewritten` 段逐字声称"`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body"。**
- 盘上事实：`oracle.md` = 7,838 B，sha256 `77dce63db21fe391f0dea0b8fb90ea71d37b2da7d3557bfa2c33fb9283031ad0`，mtime **01:19:25**（早于 r2 的 01:44 与 r3 的 02:04），`修订 r2` 出现次数 **0**。
- 全树检索 `修订 r2（独立复审后追加，非重写）`：仅命中 `scripts/revise_r2.py`（模板字符串），**未命中 `oracle.md`**。
- 根因：共享的 `scripts/apply_r2_patches.py:83` 把 oracle.md 追加写死在 `if card == "M03":` 分支内；M01 的 r2 段由仅存在于 M01 的 `scripts/finalize_r2.py` 写入。四卡 `apply_r2_patches.py`（`965c71fe3c9eb3e10bfa…`）与 `revise_r2.py`（`b0e6295c25069e027de2…`）逐字节相同。
- 影响：本卡的"五条必修已在 oracle 层登记"在盘上**无载体**；`source_manifest.json.oracle_versions.oracle_md_versions[0]` 只登记了一条 `v1_frozen_then_appended`（sha256 = 当前盘上 hash，`sha256_before_r2_append = "NOT CAPTURED"`），**没有任何"已追加"版本可索引**。
- 处置（见 §11.3，二选一，**不得维持现状**）：① 由实现者在 `oracle.md` 末尾**追加**一节 r2 索引（附追加前字节数与 sha256 `77dce63db21f…`/7,838 B，并如实注明"事后补记：r2 轮曾声称已追加但实际未落盘"）；或 ② 把上述 `review.md` 措辞改为"`oracle.md` **未被修订**，与运行前冻结件逐字节相同（`77dce63db21f…`/7,838 B）；本卡五条的 r2 处置由 `review.md` 与 `evidence/M02/revision_r2.json` 承载，不由 `oracle.md` 承载"，并把 `source_manifest.json` 的 `version`/`note` 改为 `v1_frozen_unamended` / `r2 did NOT append a section to this file`。

**P1（本卡必须处置）**：`handoff.json.evidence_paths` 含 `recovery/r2_exit_code_selfcheck/selfcheck_result.json`，**该文件在本卡 attempt 内不存在**（仅 M01 有）；而本文件自检段却逐字引用它作为 A/B/C/D 四例 rc 的出处。处置：补落该文件，或删去该路径并把自检段改写为"本卡未单独运行 selfcheck；`run_card.py` 与 M01 同一文件（`b5fcc685…`），该结论由 M01 的对应文件承载"。
（**缓解事实**：reviewer 已用同一 harness 独立复现该四例，`rc=0/1/2/3` 全对，故被指认的**主张为真**，缺的是本卡盘上载体。）

**九条复审项关闭情况**：`F-M01-01` = 仅 M01 有记录（本卡无 `first_run_forensics.json`，属 M01-specific）；`F-M01-02` CLOSED（reviewer 独立复现 rc 四例全对）；`F-M01-03` CLOSED；**`F-M02-01` CLOSED-AS-RESERVED —— 仍如实登记、仍为 owner 裁定项、未被自决、未改产品**（reviewer 实测：`base=999` 输出与正例逐值相同；`base=-5` → `ModelRegistryError: direct_revenue.base_revenue cannot be negative`）；`F-M03-01`/`F-M04-01` = not applicable to this card（但 `source_manifest.revision_r2.review_items` 误列，见 P3）；`NEW-1` not_applicable（M03 only）；`NEW-2` CLOSED；`NEW-3` not_applicable（M01 only）；`NEW-4` CLOSED。

**其余记账发现**：
- **P1**：`handoff.json.revision_history` 4 条真实轮次被记成 6 条（r2/r3 各逐字重复一次）。
- **P2**：`status="review_pending"` 与 `qualifications.formula="accepted_scoped …"` 自相矛盾；`evidence/M02/qualification.json.formula.status` 仍为 `review_pending`、`not_yet_independently_reviewed=true`。
- **P3**：`revision_r3.json` 自我 sha256 不可复现（其余 hash 声明全部相符）；`revision_r2.review_items` 扫入 `F-M03-01`/`F-M04-01`；`before/`+`after/` 三份文件与其他三卡同拷贝。

**订正要求（由实现者执行；见 §11）**：同上（`status`→`accepted_scoped`、`reviewer_status`→`point_review_returned`、`revision_history` 去重+追加 r4、`qualification.json.formula` 补独立复核块、补/删 selfcheck 证据路径、`review_items` 去非本卡条目）。`disclosure_adaptation` 与 `accuracy` 两栏**不得**改动。

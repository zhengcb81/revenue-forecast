## 独立 reviewer session 点复审（裁决）

**结论：`accepted_scoped`（仅 formula 资格）。**
**授予范围：仅 `formula`，且仅限本 attempt（`execution_runs/M01/a20260919-01`）盘上版本、仅限 `iso/checkout_scripts` 副本。**

**未授予项（明示）**：
- `disclosure_adaptation` = **未授予**，保持 `unmapped`。最小披露映射（紫金矿业 FY2024/FY2025）只构成 D 的素材，未获行业/会计签署。
- `accuracy` = **未授予**，保持 `unproven`。`STOP_ACCURACY` 命中（无 I-12 冻结设计）。§7 的 FY2024→FY2025 单率残差（CNY 14,588,108.91，0.0042%）是否证性证据，**不是**准确性证据。
- 未授予任何跨公司/跨行业/跨期间外推；未授予 D/E/F 完成；未授予 `calculate_model_path` 生产入口已核。
- `formula` 通过**不**提升 `disclosure_adaptation` 或 `accuracy`。

**独立复算（reviewer 自造输入，未照抄卡片）**：16 例（6 正例 + 6 自造负例 + 连续性正例 + 断裂 patch + 边界）全部通过。
- `base=175, g=[0.08,0.08,0.08]` → `[189.0, 204.12, 220.44960000000003]`（max_abs_diff 2.84e-14）
- `base=37.5, g=[0,0], years=[1999,2000]` → `[37.5, 37.5]`
- `base=500, g=[-1.0]`（域下界）→ `[0.0]`（精确 0，非负非 NaN）
- 保真：输出全长 = `len(years)`，全部 `float` 且有限。
- 自造负例（均不在卡片清单内）全部以 `ModelRegistryError` 被拒：`g=[-1.0000001]` / `years=[10000]` / `years=[0]` / `g` 长度超出 / `years=[2027.0]` / `g=[]`。
- 连续断裂 `years=[2027,2029]` → `direct_growth.years must be consecutive and increasing`。
- 注册串读回：`revenue[t] = revenue[t-1] * (1 + growth_rate[t])`，与 `oracle.md` §1 冻结串逐字相同。

**冻结与追加**：
- `oracle.md` **只追加、无重复章节**。追加边界**字节级复现**：总 12,310 B，前 9,889 B 的 sha256 = `88635eb46df3c3d13f6ac0bc9af884d1b8d92aac50c6f7703c2f29a7a227d99f`，与本卡自述一致。
- `oracle.json` 可由 `scripts/oracle_M01.py` **逐字节重生成**（reviewer 在 `%TEMP%` 复跑：`input.json` `22910b38da8558…`、`oracle.json` `cb60e60d07c75a05…`、`cases.json` `0e1f55af5d4b946a…` 三件 IDENTICAL）。
- 预注册值未被改动：`card_M01.md` 的 `期望输出 [220,110,0]` = `oracle.json.expected_float [220.0,110.0,0.0]`；容差规则未放宽；`oracle.json` mtime 01:18:24 早于 r2/r3 两轮修订。

**九条复审项关闭情况**：`F-M01-01` CLOSED（如实降级为永久缺口 + RECONSTRUCTED v1）；`F-M01-02` CLOSED（reviewer 自建 selfcheck 复现 rc=0/1/2/3 四例全对）；`F-M01-03` CLOSED；`F-M02-01` CLOSED-AS-RESERVED（仍为 owner 裁定项，见 `handoff.json.open_questions`，不阻塞 formula）；`F-M03-01`/`F-M04-01` = not applicable to this card；`NEW-1` not_applicable（M03 only）；`NEW-2` CLOSED（rc=2 可达，已复现）；`NEW-3` CLOSED；`NEW-4` CLOSED。

**未授予之外，本复审提出的记账/交付发现（不改变上述公式结论）**：
- **P1**：`handoff.json.revision_history` 把 4 条真实轮次记成 6 条（r2 与 r3 各逐字重复一次）——四卡同缺陷。
- **P2**：`handoff.json.status="review_pending"` 与 `qualifications.formula="accepted_scoped …"` 自相矛盾；`evidence/M01/qualification.json.formula.status` 仍为 `review_pending` 且 `not_yet_independently_reviewed=true`。
- **P2**：`source_manifest.json.oracle_versions.oracle_md_versions[0].sha256`（`73e1e587…`）为中间写入态，非当前盘上值（`90bce2fa…`）。
- **P3**：`revision_r3.json` 的自我 sha256 声明不可复现（其余 32 条 hash 声明四卡全部相符）。
- **P3**：`source_manifest.json.revision_r2.review_items` 把 `F-M03-01`/`F-M04-01` 列为本卡已处置项（模板扫入）。
- **P3**：`before/git_status_revenue-forecast.txt`、`before/pytest_version.txt`、`after/rerun_stderr.txt` 与其余三卡为同一份拷贝。

**订正要求（由实现者执行；见 §11）**：`status` → `accepted_scoped`；`reviewer_status` → `point_review_returned`；`revision_history` 去重为 4 条并追加第 5 条 r4 裁决记录；`qualification.json.formula` 补独立复核块；`source_manifest.json` 的 oracle 版本 hash 更新为当前盘上值；`review_items` 去掉非本卡条目。`disclosure_adaptation` 与 `accuracy` 两栏**不得**改动。

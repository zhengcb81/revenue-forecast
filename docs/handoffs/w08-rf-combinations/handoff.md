# W08-RF-COMBOS 交接记录（RF 原生模型剩余五组组合覆盖）

- 卡号：**W08-RF-COMBOS**
- 项目：`revenue-forecast`
- 工区：`C:\Users\郑曾波\Projects\_harness_worktrees\w08\rf-combinations`
- 分支：`codex/w08-rf-combinations`
- 固定基线：`8dc2671040f4330d3b54d1bea1d17246130f9c2a`
- 计划：`.planning/w08-rf-combinations/`
- JSON：同目录 `handoff.json`（schema `w08-lane-handoff/1`）
- 范围状态：**COMPLETE**（五组全部实跑闭环，非按数量推断）
- 外网 provider / LLM 调用：**0 / 0**，费用 **$0**
- `source_truth_verified=false`，`economic_reasonableness=not_evaluated`

## 1. 做了什么

原 W07 的 16 向量与 36 断言**原样保留**；W08 只做**加法**：新增独立 `COMBINATION_CASES`，与 W07 共用同一个引擎、同一个比较层、同一套 oracle 纪律，不另建引擎、不复制任何预测算术。

新增 `tools/model_generalization_matrix/combinations.py`，含 15 个 CaseSpec，覆盖施工卡确认的五组缺口：

| 组 | 合法向量 | 反例/未知向量 | 组状态 |
|---|---|---|---|
| C01 货币单位 | C01-USD-L、C01-CNY-L | C01-HKD-C、C01-CROSS-C | CLOSED |
| C02 并购/跨FY | C02-FY-L | C02-FYE-C、C02-QGAP-C、C02-DBL-C | CLOSED |
| C03 联合量价 | C03-JOINT-L | C03-ORDER-C | CLOSED |
| C04 目标/净额 | C04-CUM-L、C04-NET-L | C04-CUM-C | CLOSED |
| C05 actual/WAPE | C05-ACT-L | C05-COV-C | CLOSED |

全清单 **31** 条（原 16 + 新 15），**未删除任何原 case**。

## 2. 三节点证据

### A：先固定入口与独立期望

每条 case 先定 `native_entry`、真实调用参数、手算 `expected`、结果 JSON pointer。期望全部**运行前固定**，来自身份式与手算：

- C01：`scale = 输入单位scale / 引擎单位scale`；`7.25 rmb_100m(1e8) -> rmb_million(1e6) = 725`；`5.0 usd_million -> usd_thousand = 5000`。同时显式否定 ×100 / ×1000 的错误量级。
- C02：非 12-31 年结（`09-30`）+ 手排两季桥（Segment A FY2026 = Q1 36 + Q2 36，FY2027 = 90；Segment B 55/60.5）。合并口径 = Σsegments + adjustments，故手算年度 = **91.0 / 150.5**。
- C03：`unit_sales` 公式 `units × unit_revenue × timing_factor`；基础 FY2027 为 12 units × 5.0，量价同施 s=0.9 → 联合 **48.6**，只变一腿 54.0，重复施压 43.74，三者可区分。
- C04：累计 = FY2026 120.0 + FY2027 144.0 = **264.0**（目标 260，达成率 1.015384615…）；净额恒等式 165.0 + (−10.0) = **155.0**。
- C05：作用域恒等式 = {Segment A, Segment B} × {2026, 2027}；零样本 WAPE 必须为 null；Segment A 的校准不得外推到 Segment B。

### B：集中回归（一次）

```
python -B -m pytest -q tools/tests/test_w07_model_generalization.py tools/tests/test_w08_model_combinations.py
-> 71 passed, 6 skipped   (exit 0, 4.81s)
```

附带确认 ROOT 自有边界测试仍绿：`tools/tests/test_root_w07_model_boundaries.py` → **24 passed**。

新增 `tools/tests/test_w08_model_combinations.py`（59 passed / 6 skipped），关键行为测试：

- 每个新 case 的**错误实际结果必须被检出**（喂 ×1000 / 加后缀的错值 → 必须 FAIL）；
- 正确手算值必须通过（反向自检）；
- 合法向量若**产不出任何可检断言 → ERROR，绝不 PASS**；
- W07 原 16 case 与 8 类未被改动；W08 与 W07 case id 不重叠；
- `run.full_case_list()` 与 `report.required_case_ids()` 必须是**同一份**权威清单；
- 组闭环只能由**实跑**得到：缺 case / NOT_RUN / ERROR 一律让该组 **OPEN**；
- 同名币缩放不得变成汇率式 ×100/×1000；未登记单位名（hkd_*）是**未知单位拒绝**，不猜汇率；
- 缺 Q 不得零补、同一笔流不得重复计入；
- 联合量价一腿只承压一次；反例向量的冲击**确实不嵌套**；
- 未观测 actual 的 WAPE 为 null 非 0；跨 scope 校准不外推。

### C：真实原生 E2E（一次）

`--help` 确认已有 `--owned-root / --out-root / --e2e`，**未创造任何不存在的开关**。

```
python -B tools/model_generalization_matrix/run.py --owned-root ABS_NEW/owned --out-root ABS_NEW/out --e2e
-> exit 0, wall 2.15s
```

结果：`status=COMPLETE`，`counts: total=31 passed=22 reject_ok=9 failed=0 reject_mismatch=0 errored=0 not_run=0`，`combination_coverage.status=COMPLETE`，`open_groups=[]`，五组均 **CLOSED**。

真实 CLI 证据（单列，未 mock）：

| CLI | 返回码 | 说明 |
|---|---|---|
| `revenue_forecast.py <legal> --validate-only` | 0 | stdout `valid` |
| `revenue_forecast.py <bad fye> --validate-only` | 2 | stderr `error: fiscal_year_end is not a valid month-day` |
| `research_support_diagnostics.py --input ... --output ...` | 0 | 输出 schema `economic-support-diagnostics/1` |

恢复实测：

1. **absent**：运行前 owned-root 不存在 → 运行后仍不存在，报告正常写出；
2. **既有目录 + sentinel**：`keep_me.txt` 原样保留，`w07-*` 残留 **0**；
3. **失败路径**（out-root 已存在）：fail closed，exit 1，残留 **0**，owned-root 还原为 absent。

`cleanup`：`restored_absent=true`、`readonly_unchanged=true`、`owned_root_restored=true`，`residuals=[]`。

## 3. 只读输入与写集

- 297 个只读输入全部按 `INPUTS.json` 重新哈希：**297 复检 / 0 不符 / 0 缺失**。
- 实际改动仅落在唯一可写集内：`tools/model_generalization_matrix/**`、`tools/tests/test_w08_model_combinations.py`、`docs/handoffs/w08-rf-combinations/**`、`.planning/w08-rf-combinations/**`。
- `scripts/`、`tests/`、`config/`、`references/` 全程只读；主仓 `revenue-forecast` 未写；未改 W04 core；未安装、未改 CI/hooks、未推 main。`git status` 仅显示上述文件。

## 4. 交付物

- `docs/handoffs/w08-rf-combinations/native-payload.zip`（411,409 B，sha256 `3c67851a…f06c0`）——**唯一一份**原生 payload 压缩件（内含 5.0 MB JSON + Markdown）。
- `docs/handoffs/w08-rf-combinations/native-payload-summary.json`（2,995 B）——小摘要，含 31 个 required case id 与各组 CLOSED/OPEN；**未**在 PWF/handoff 再复制完整 JSON。
- `docs/handoffs/w08-rf-combinations/handoff.json` / `handoff.md`——本文件。

报告保持 `model-generalization-matrix/1` 兼容；新增字段仅为 additive：`required_case_ids` 与重构后的 `combination_coverage`（`groups` / `open_groups` / `evidence`）。原有 `counts` / `class_status` / `cases` 消费者不受影响。

## 5. 已知限制 / 剩余（如实）

1. `handoff_commit` 为 `null`：交接文件无法诚实自引用自身提交 hash，请 ROOT 从分支尖端取精确 SHA。
2. **PWF 受 sparse-checkout 限制未入 commit**：`core.sparseCheckout=true`，锥体内含 `docs/handoffs/w08-rf-combinations`，但**不含** `.planning/`。三个 PWF 文件（`task_plan.md` / `findings.md` / `progress.md`）已写好并落盘可读，但 git 拒绝暂存。本包**刻意未**执行 `git add --sparse`、也未改锥体，因为施工卡要求"不取消稀疏checkout"。ROOT 如需入库版本，可在并线时 `git add --sparse .planning/w08-rf-combinations`。
3. **C05 的 draft 作用域求值**：draft 结果不是正式发布快照（无 publication receipt / registry anchor），shipped `revenue_backtest.evaluate_snapshot` 按设计会拒绝它。本包改用 `bootstrap.evaluate_draft_scope`（schema `revenue-backtest-draft-scope/1`），它只复用 shipped 的 `revenue_backtest._error_record` 与 `_summarize_records`，**不重写 WAPE 或任何误差算术**。建议 ROOT 视需要把它升级为一等原生 draft-backtest 入口。
3. **C02 的日期窗口**：夹具把两季手算总额放在已声明的 FY2026 年度驱动上，日期语义通过引擎自身的 `fiscal_year_end` 与季度契约检验；本包未在 `combinations.py` 内重写 3.10 dated-composition 算术。若 ROOT 后续发布带季度消费契约的 W05 dated-contribution helper，可另加完全 dated 的变体。
4. 未发现 core 缺陷，因此没有最小复现/先红建议；未为求绿放宽任何期望。

## 6. 交给 ROOT

- 卡号：**W08-RF-COMBOS**
- 分支：`codex/w08-rf-combinations`
- HEAD：本 commit 落地后由 ROOT 从分支尖端读取（交接文件不猜自身 hash）
- handoff 绝对路径：
  - `C:\Users\郑曾波\Projects\_harness_worktrees\w08\rf-combinations\docs\handoffs\w08-rf-combinations\handoff.json`
  - `C:\Users\郑曾波\Projects\_harness_worktrees\w08\rf-combinations\docs\handoffs\w08-rf-combinations\handoff.md`
  - `C:\Users\郑曾波\Projects\_harness_worktrees\w08\rf-combinations\docs\handoffs\w08-rf-combinations\native-payload.zip`

工程通过不等同于公司来源真值或买方预测质量；请勿据此认证任何真实公司数字。

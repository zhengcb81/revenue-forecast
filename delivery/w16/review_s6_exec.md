# S6 独立执行型审查报告 — W16 revenue_basis（historical_revenue 口径元数据）

- 审查人：S6（未参与实现，仅运行、不修改产品代码/测试）
- 日期：2026-10-25
- 工区：`C:/Users/郑曾波/Projects/revenue-forecast-w16-basis`
- 分支：`codex/w16-rf-basis-20261025`
- 被审 commit：`cb60bd21`（前一版 `84e2152f`，基线 `094d55ad`）
- Owner 模块：`scripts/research/revenue_basis.py`；接线 `validate_document → run_forecast → CLI → render_markdown`
- 方法：独立运行关键链路（A1–A3）+ 构造作者测试未覆盖的反例（B1–B4）；所有命令记录原文、退出码与关键输出。判定取值：正确拒绝 / 正确放行 / 缺陷。

## 结论

**通过（无缺陷）。** 独立复跑关键链路全部成功：A1 W16 单测+CLI 测试 41 个全绿（退出码 0）；A2 在自建中文+空格系统 temp 目录用真实 CLI 子进程端到端运行成功（退出码 0），`out.json` 逐字保留 revenue_basis（operations/statement_status/period_kind/input_quantity 换算/components+claim 绑定），`out.md` 的"口径可比性"段对 as_reported vs restated 如实标注不可比、"基数采用"段正确指名 `总额/重述`、`与报告总额参数一致`、`附DU5换算记录`；A3 回归 41 个测试全绿。

六个作者未覆盖的反例全部按预期行为执行：B1 反向混合（上年 restated+基年 as_reported）正确放行且标不可比；B2 非基年 components（90+50=140）正确放行且组件保留；B3 篡改簇 4 个变体（改 components 数值/改 engine_value/删 input_document 锚/内外自洽伪造）在重算 `result_sha256` 后仍全部被输出校验拦截（等值检查→绑定存在性→哈希锚三层闭环）；B4a 复数 `engine_unit "USD billions"`、B4b 组件 claim 期间错配（FY2024 claim 挂 2025 记录）均被字段级错误正确拒绝。

**Findings：0 缺陷**（2 条非缺陷观察 N1/N2 备案）。

透明度备注：审查期间 HEAD 被外部推进（`cb60bd21` → `95c25c4b`，"w16: state the linter's basis scope honestly (S3-1)"）。经核对该 commit 仅改 `scripts/lint_input.py` 中 8 行注释文案（无运行时行为变化，且不在本次任何运行路径上），故本报告全部结果对被审 commit `cb60bd21` 仍然有效。S6 未执行任何 git 写操作。

## 环境记录

- Python 3.13.9（`C:\Miniconda\python.exe`），Git Bash on Windows 10.0.26300
- 工作目录：工区根（所有 pytest 与 CLI 在 `C:/Users/郑曾波/Projects/revenue-forecast-w16-basis` 下运行）
- 自建临时根：`C:\Users\郑曾波\AppData\Local\Temp\s6执行 审查w16\`（含中文+空格；报告收尾时核对在系统 temp 内后删除）
- CLI 命令模板：`REVENUE_PUBLICATION_REGISTRY=<临时目录> PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/revenue_forecast.py input.json --output out.json --markdown out.md`

## A. 独立运行

### A1. W16 单元测试与 CLI 测试

命令（工区根）：

```
python -m pytest -q tests/test_w16_revenue_basis.py tests/test_w16_revenue_basis_cli.py
```

- 退出码：0
- 输出：`41 passed in 11.46s`
- 覆盖：Owner 层 7 个（schema/parse/可比矩阵/YoY 守卫/Decimal 复算）、Contract 层 18 个、OutputValidation 1 个（篡改 basis 被拦）、Report 层 5 个、CLI 三个套件 10 个（含中文/空格目录的 ytd 错误用例）
- 判定：**通过**（与作者声明"41 W16 tests green"一致）

### A2. 自建中文+空格 temp 目录端到端 CLI 运行

步骤（全部独立完成，未复用作者测试的运行器）：

1. 建目录 `C:\Users\郑曾波\AppData\Local\Temp\s6执行 审查w16\A2 基期口径`（中文+空格）。
2. 写临时脚本 `gen_a2.py`：`sys.path` 加入工区 `scripts/` 与 `tests/`，`import` 共享构造器 `forecast_document` / `_basis` / `_add_component_claims` / `_record_for_year`，生成完整合法输入：
   - FY2024：`operations=total, statement_status=as_reported, period_kind=fiscal_year, source_ids=["filing"]`
   - FY2025：`operations=total, statement_status=restated`，`input_quantity`（0.15 USD billion → engine 150.0 USD million，conversion 表达式齐全），`components=[continuing 100, discontinued 50]`（附 exact_value claim，capture_receipt_sha256 取自 source）
   - 生成命令退出码 0。
3. CLI 运行（命令见环境记录，`REVENUE_PUBLICATION_REGISTRY` 指向该目录）：**退出码 0**，`out.json` 与 `out.md` 均生成，另见注册表副作用 `publications.jsonl` 落在指定注册目录（预期发布行为）。

`out.json` 的 `historical_revenue` 关键输出摘要（逐字段核对）：

| 年 | value | operations | statement_status | period_kind | input_quantity | components |
|---|---|---|---|---|---|---|
| 2024 | 140 | total | as_reported | fiscal_year | — | — |
| 2025 | 150 | total | restated | — | 0.15 USD billion → 150.0 USD million | continuing 100.0（claim_basis_component_2025_continuing）+ discontinued 50.0（claim_basis_component_2025_discontinued） |

`out.md` 关键段落摘录：

- 历史营收表：`| 2024 | 140.00 | 总额/原表 | — | filing |`、`| 2025 | 150.00 | 总额/重述 | 0.15 usd_billion x 1000 = 150 usd_million | filing |`
- `### 口径可比性`：`FY2024→FY2025：不可比（statement_status differs (as_reported vs restated); …）；观测值保留，不得当作可比增长；同比 7.1%仅按数值列示。`
- `### 基数采用`：`实际采用 FY2025 历史观测（150.00 USD million，口径 总额/重述，来源 filing）…与报告总额参数一致（参数 reported_total = 150.00，容差 1e-06，差值 0.00）；附DU5换算记录…`

判定：**通过** — 混合 statement_status 不是输入错误（成功运行），诊断如实标不可比；基数采用段正确指名重述口径与换算记录；中文+空格路径下 UTF-8 输入/输出无损。

### A3. 回归测试（data_contract + recognition_bridge）

命令（工区根）：

```
python -m pytest -q tests/test_data_contract.py tests/test_recognition_bridge.py
```

- 退出码：0
- 输出：`41 passed in 0.89s`
- 判定：**通过**（W16 未破坏既有 data contract 与 recognition bridge 行为；legacy 历史路径保持原样）

## B. 自建反例

所有反例均由共享构造器（`forecast_document` / `_basis` / `_add_component_claims` / `_record_for_year`）经临时脚本 `gen_b.py` 生成输入，再用真实 CLI 子进程运行（命令模板同 A2）。作者测试只覆盖"上一年 as_reported + 基年 restated"方向与"基年 components"，以下变体均未被作者测试覆盖。

### B1. 反向混合：上一年 restated + 基年 as_reported

- 输入：FY2024 `statement_status=restated`；FY2025（基年）`as_reported`；两者 `operations=total`。
- 命令：CLI（同 A2 模板），目录 `B1 反向混合`。
- 实际输出：退出码 **0**（成功运行）；`out.json` 保留两条观测值 `[140, 150]`。
- `out.md` 关键输出：
  - 口径可比性：`FY2024→FY2025：不可比（statement_status differs (restated vs as_reported); without an explicit restatement bridge the figures are not silently comparable）；观测值保留，不得当作可比增长；同比 7.1%仅按数值列示。`
  - 历史营收表：2024=`总额/重述`，2025=`总额/原表`。
  - 基数采用：`实际采用 FY2025 历史观测（150.00 USD million，口径 总额/原表…）`。
- 判定：**正确放行** — 反向混合与正向一样不是输入错误（B02/B05：观测保留、只降级可比性），诊断方向无关地如实标注；基年口径、reason 文案、表格标签全部正确。

### B2. 非基年 components（声明 total）+ 上一年也 total：正常路径复核

- 输入：FY2024（非基年，value=140）`components=[continuing 90, discontinued 50]`（附 FY2024 exact_value claim）；FY2025（基年）纯 `_basis()`（total/as_reported）。作者测试的 components 全部挂在基年 2025。
- 命令：CLI，目录 `B2 非基年构成`。
- 实际输出：退出码 **0**；`out.json` 中 FY2024 保留 `components=[('continuing', 90.0), ('discontinued', 50.0)]`，FY2025 无 components；Decimal 复算 90+50=140 通过。
- `out.md` 关键输出：口径可比性 `FY2024→FY2025：同口径可比；同比 7.1%。`；基数采用段仍锚 FY2025 观测。
- 判定：**正确放行** — components 桥不限基年，非基年 90+50 复算与 claim 对齐均按预期工作，输出逐字保留。

### B3. 篡改突变：改 components 数值后重算 result_sha256 再渲染

方法：取 A2 成功产物 `out.json`，篡改 `historical_revenue[2025].revenue_basis.components[discontinued].value` 50.0→90.0，按任务要求 `sys.path` 加 `scripts` 后 `from revenue_core import canonical_sha256` 对不含 `result_sha256` 的 dict 重算并回填，再 `from revenue_report import render_markdown` 渲染。

- B3 主例（components.discontinued 50→90）：
  - 对照组：未篡改产物渲染成功（长度 11544），证明测试链路本身有效。
  - 篡改后：`ForecastInputError: forecast output historical_revenue does not match the bound input (year, value, sources, claims or revenue_basis drifted)`。
  - 判定：**正确拒绝** — 重算哈希无法绕过 W16 输出校验（绑定输入等值检查）。
- B3 变体1（input_quantity.engine_value 150→999，同法重算）：同样被拒，消息同上。判定：**正确拒绝**（换算记录漂移也在等值检查覆盖内）。
- B3 变体2（更强攻击：篡改后整体删除 `input_document` 锚）：`ForecastInputError: current-schema artifact without a bound input cannot be validated`。判定：**正确拒绝** — 当前 schema 产物无绑定输入直接拒绝，不给降级到 legacy 校验的口子。
- B3 变体3（自洽伪造：同时改写嵌入 `input_document` 使两侧一致）：`ForecastInputError: input binding mismatch: embedded input_document does not hash to input_sha256`。判定：**正确拒绝** — `input_sha256` 锚使内外同改仍被识破。绑定链三层闭环（等值 → 存在性 → 哈希锚）。

### B4. 自选强错配反例（两个变体）

- B4a. 复数/非规范 engine_unit：手工构造 `input_quantity`，`input_unit="USD billion"`（合法）但 `engine_unit="USD billions"`（复数，注册表无此拼写；预探测 `money_unit_currency('USD billions') -> None`）。
  - 命令：CLI，目录 `B4 复数单位`。
  - 实际输出：退出码 **2**，`error: unknown engine_unit: USD billions`（字段级、点名非法拼写）。
  - 判定：**正确拒绝** — DU5 是单位拼写的唯一 owner，复数英文形式不在注册表即拒绝；错误消息来自 DU5 构造期校验而非 W16 层的 "not a money unit"，但均为明确字段级诊断，无静默放行（观察项 N1，见下）。
- B4b. components claim 期间错配：FY2025 记录的 discontinued 组件 claim `period="FY2024"`（其余完全合法）。
  - 命令：CLI，目录 `B4 期间错配`。
  - 实际输出：退出码 **2**，`error: historical revenue component discontinued claim period mismatch: 2025`（与记录级消息模板一致，label 带"component discontinued"）。
  - 判定：**正确拒绝** — 组件级 claim 的期间与记录年不一致被 component 路径的 `validate_historical_claim_alignment` 拦截。

## Findings 汇总

**缺陷数：0。** 六个反例（B1、B2、B3×4、B4a、B4b）全部按预期行为执行，无一处静默放行、无崩溃、无错误消息误导。

非缺陷观察（不要求改动，仅备案）：

- **N1（信息性）**：B4a 的拒绝消息是 `unknown engine_unit: USD billions`（DU5 `validate_input_quantity_record` 抛出），而非 `revenue_basis._validate_history_input_quantity` 的 "is not a money unit" 文案。行为正确（DU5 先于 W16 拒绝），但排查者按 W16 文档找 "not a money unit" 会找不到该消息。可选改进：在 W16 文档字符串注明货币单位拼写错误由 DU5 构造期先行拒绝。
- **N2（正面证据）**：B3 变体2/3 表明 W16 的输出绑定不是单点检查——`input_document` 存在性（schema 3.7 无绑定即拒绝）、`historical_revenue` 等值、`input_sha256` 哈希锚三层闭环，作者未在测试中覆盖变体2/3 但实现天然覆盖。

## PASS 证据汇总

| 编号 | 内容 | 证据 |
|---|---|---|
| A1 | 41 个 W16 单测+CLI 测试全绿 | `41 passed in 11.46s`，退出码 0 |
| A2 | 中文+空格目录端到端 CLI：混合 statement_status 成功且诊断如实 | 退出码 0；out.json 保留 basis/input_quantity/components；out.md 不可比+重述+DU5 换算记录 |
| A3 | 回归无破坏 | `41 passed in 0.89s`，退出码 0 |
| B1 | 反向混合（上年 restated+基年 as_reported）成功且标不可比 | 退出码 0 + `statement_status differs (restated vs as_reported)` |
| B2 | 非基年 components 正常路径 | 退出码 0 + components 保留 + `同口径可比` |
| B3 | 篡改 components/conversion/删锚/自洽伪造全被拦 | 4 次 ForecastInputError，消息见 B3 节 |
| B4a | 复数 engine_unit 拒绝 | 退出码 2 + `unknown engine_unit: USD billions` |
| B4b | 组件 claim 期间错配拒绝 | 退出码 2 + `claim period mismatch: 2025` |

## 复核约束遵守情况

- 未修改任何产品代码/测试（仅新增 `delivery/w16/review_s6_exec.md` 报告与系统 temp 下临时脚本/输入）。
- 未联网、未调用付费模型、未执行任何 git 写操作（工作树在收尾时仅含本报告未跟踪文件 `?? delivery/w16/`；审查期间 HEAD 被其他角色推进至 `95c25c4b`，非本审查所为，见结论节备注）。
- 临时目录 `C:\Users\郑曾波\AppData\Local\Temp\s6执行 审查w16\` 收尾时核对位于系统 temp（`C:\Users\郑曾波\AppData\Local\Temp`）内后整目录删除（`publications.jsonl` 为只读，以 chmod 后重删成功；删除后 `exists=False` 已验证）。

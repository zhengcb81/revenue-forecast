# W16-RF-BASIS Findings

ROOT已经按代码基线094d55ad884e4a886b1537c0e76f3a0bede16ca2准备隔离工区和施工卡，没有启动产品实现或测试。

本卡已知事实、来源和验收要求以construction_card.md为准。原主工区已有WIP由ROOT记录并保留，不属于本卡。禁止复用他人可变工作区、生产目录或收费调用充当合成测试。

## A 调查结论（2026-10-25 冻结）

### B01 真实缺口（用现有入口复现）

1. `grep -rni "continuing|discontinued|restat" scripts/` 仅命中 `research/target_comparison.py` docstring 一处无关词；全仓对历史观测无持续/终止/原表/重述概念。
2. `contracts/document.py::validate_historical_revenue`（L155-253）只校验 year/value/source_ids/claim 数值对齐：claim extracted_value≈value、period=FY{year}、unit="{currency} {unit}"；隐式假定所有观测同口径；base-year 观测与 reported_total 参数的数值匹配是口径盲的。
3. 历史值无原始单位/数量换算路径：DU5 `research/input_quantities.py` 的 `convert_input_quantity`/`validate_input_quantity_record` 只接 sensitivity/parameter/target 消费者；历史 claim 只有单位字符串比对。
4. `revenue_report.py::render_markdown` 历史表只渲染 年度/营收/来源ID；混合口径序列被静默呈现为可比。
5. `revenue_backtest.py::_benchmark_diagnostics`（L514+）从 history 值盲算 CAGR——该文件不在本卡可写清单，记 interface_request 交ROOT。
6. 结果装配在 `revenue_core.py::_build_forecast_draft` + `forecast/segments.py`（均不可写）；`historical_revenue` 记录原样透传进结果，因此记录级新字段天然到达 JSON 输出与 `input_document`。计算型加法诊断放在报告层（render_markdown + 输出校验重验），符合 COMMON"输出沿用现有forecast/report及加法诊断"。

### 冻结接口设计（B02/B03/B04）

可选 `revenue_basis` 对象（每个 historical_revenue 记录，`schema_version="rf-revenue-basis/1"`）：

- `operations`: `total|continuing|discontinued`（有 basis 时必填）
- `statement_status`: `as_reported|restated`（有 basis 时必填）
- `period_kind`: 可选 `fiscal_year|half_year|quarter|ytd|trailing_twelve_months`；非 fiscal_year 在年度历史位上给具体错误（同比/环比/年累计混淆的显式声明形式）
- `input_quantity`: 可选 DU5 记录，复用 `validate_input_quantity_record`；money 族、文档币种（DU5 `money_currency`，不复制货币表）、engine_value≈记录值
- `components`: 可选 `[{operations: continuing|discontinued, value, source_ids, claim_ids}]`，仅 `operations=total` 记录可带；必须同时含 continuing 与 discontinued；claim 复用 target `historical_revenue:{year}` exact_value 全套既有校验；Decimal 复算 总额=持续+终止，容差沿用 `reconciliation_tolerance`；无 components 不复算、不自造调整
- `source_ids`: 可选口径声明来源，须为已知 source

规则：base-year 记录声明 `operations!=total` → ForecastInputError（opening bridge 依赖合并总额口径，"持续经营替代总额"即依赖无效比较的模型）；跨年 statement/operations 混杂不报输入错误，观测保留、诊断标不可比+理由；缺元数据完全旧行为，诊断写 not_declared 不写 verified；yoy 比较基数为零/负 → None+理由，不产生 Inf。

单一共享 owner：新 `scripts/research/revenue_basis.py`（枚举、校验、可比性、Decimal 复算、base adoption 视图）；contracts/document.py、revenue_report.py、lint_input.py、generate_input_template.py 只调用不复制。

### B06 E2E 冻结矩阵（公开 CLI，两个独占临时目录其一含中文/空格）

同口径正常｜持续经营替代总额(错误)｜period_kind=quarter(错误)｜restated/as_reported无桥(成功+不可比诊断)｜双restated有桥(成功+可比)｜input_quantity 数值不匹配(错误)｜零比较基数(成功+yoy未定义理由)｜legacy 无元数据(成功，行为与基线一致)。

### B07 冻结来源（只读语义校对）

1. 药明康德 FY2025 年报（SSE 603259，A股，人民币元）：p7 三年营业收入原表 45,456,165,774.18/39,241,431,359.88/40,340,806,877.04；p235 终止经营表 收入列 WuXi ATU 338,274,914.78 + WuXi Testing 1,697,067,120.57 = 合计 2,035,342,035.35。收据 `company-wiki/docs/plans/du11-source-closure-2026-10-18/review/st-a02-table-source-20261025/source-route-receipt.json`，原件 SHA 7f1431d6…，本地原件存在；C 阶段用本地 PDF 只读复核 p235，不把收据当原件真值。
2. 安踏體育（HKEX 2020，港股市场）二零二五年年報：p.188 終止經營、pp.102/133-134 持續經營列报；C 阶段从本地 PDF 只读提取精确片段/单位/期间。

### B07 实测证据（2026-10-25 C 阶段，全部本地原件只读 pypdf，0下载0模型）

1. **药明康德《2025年年度报告》**（上交所603259，A股；原件 SHA=7f1431d66eae399d4b35639bb650e23287c7f52dacbb47b4b4a197fb5026d6a2，本地路径 company-wiki companies/药明康德/raw/financial_reports/）：
   - p.7 主要会计数据表：营业收入 FY2025=45,456,165,774.18、FY2024=39,241,431,359.88（本期比上年同期增减 15.84%）、FY2023=40,340,806,877.04——reported totals 三年序列。
   - p.235「5、终止经营」表头明示"单位：元 币种：人民币"；收入列：WuXi ATU 业务 338,274,914.78；WuXi Testing 部分业务 1,697,067,120.57；合计 2,035,342,035.35。表内 Decimal 桥 338,274,914.78+1,697,067,120.57=2,035,342,035.35 精确成立，与 components 复算设计一一对应。页内文字"依据企业会计准则……划分为终止经营业务，相应重述了可比期间数据"——重述与终止经营同页并存，对应 statement_status 与 operations 正交。
   - 校对结论：total≠continuing（终止经营收入非零）；"分项+合计"结构即 components 桥；单位/币种绑定在表头而非行内，支持 W16 要求换算/币种显式绑定而非从文字块猜测。
2. **安踏體育《二零二五年年報》**（港交所2020，港股市场，除另有註明者外以人民幣列賬，本地路径 companies/安踏體育/raw/financial_reports/annual/2026-04-09_hkexnews_12099632_二零二五年年報.pdf）：p.188"根據IFRS/HKFRS第18號，實體須在損益表中將所有收入和費用劃分為五類，即營運、投資、融資、終止經營及……（除另有註明者外，以人民幣列賬）"——不同市场（HK/IFRS）下 continuing/discontinued 是列报结构本身；枚举词汇市场中性成立。pp.102/133-134 的"持續經營"为审计 going-concern 语境，不作为收入口径证据（避免把going concern误当continuing operations，正例反例同时记录）。
3. **中芯国际《2025年年度报告》**（上交所科创板688981，A股，千元人民币；companies/中芯国际/raw/financial_reports/）：p.209 重要联营企业财务信息（单位：千元 币种：人民币）内含"终止经营的净利润 - -"零值行；pp.131-132"前期差错更正"行、p.189"由于企业会计准则及其相关新规定进行追溯调整，影响期初未分配利润0元""由于重大会计差错更正，影响期初未分配利润0元"。校对结论：零值/无影响的终止经营与重述行在真实报表中常态存在——设计允许不声明 components（不强制拆分）、restated 声明与零影响并存，不把零值误报为缺失。

以上均为公开原件小段只读校对（B07 输入语义校对），不宣称新公司 RF 全流程通过，不把片段当作 API 实收。

## 待调查

- revenue_backtest CAGR 口径接线（interface_request，不在本卡写范围）。

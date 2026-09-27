# ZR-603 工作单元卡（preflight）— F2：ownership/consolidation timeline 与地区层级

- 领取时间：2026-08-22T00:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-603`，ZR-602 accepted + closure→ZR-603（phase=F_revenue_mining，F2 第三卡）；锁 ZR-603（owner=zr603-implementer，ttl 86400s，nonce 4598cf5e…）。
- 依赖：ZR-601（✅ asset facts 数学契约）、ZR-602（✅ basis 契约——本卡消费其 ownership_basis 枚举）。Registry 依赖列=ZR-601。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F2 第三卡：**ownership/consolidation timeline 与地区层级**——资产所有权的时点契约（收购生效日前后不同、fraction ∈ (0,1]、链式有效权益一次性连乘不二次乘权益、period 内变更显式处理）+ 资产地区层级（country/region 声明与可检索）。Mandatory 证据：Kamoa/Porgera 不二次乘权益；收购生效日前后不同；country/region 可检索。
2. **production entrypoint 是什么？** `scripts/contracts/document.py::validate_segments`（segment 加性键校验）+ 新 `scripts/asset_ownership.py`（ownership/geography 契约纯函数层）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 ownership timeline 完全缺失（真实产品缺口）**：探针 P1/P2——scripts 全仓无 ownership/equity/stake/effective_date 计算词汇（`consolidated_forecast` 是场景合并、`segment_attribution` 是驱动归因、`equity_share` 仅是 ZR-602 枚举值——均为无关同名）。资产的 ownership fraction 无表达、无时点查询、无生效日语义。
   - **G2 二次乘权益无防护（真实产品缺口）**：无 apply-once 防护——若收入已按权益法折算（basis=equity_share）再乘链式权益即 Kamoa/Porgera 类双重折算，无 fail-closed 门。
   - **G3 地区层级缺失（真实产品缺口）**：探针 P3——country/region/geo 词汇零命中；segment 无 geography 键，无法按国家/地区检索资产。
4. **允许改哪些文件？** revenue：新 `scripts/asset_ownership.py`；`scripts/contracts/document.py`（validate_segments 加性调用：ownership/geography 键存在时校验——零 McCabe 增量模式）；新 `tests/test_zr603_ownership_timeline.py`；revenue receipts/ZR-603/**。禁止：改模型公式语义、改 golden 输出路径（行为锁定）、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-604（表格抽取/冲突）。本卡不做：内部交易/elimination（ZR-607）、asset→segment→group 对账（ZR-608）、会计 ADR 冻结（ZR-610）、pro-rata 之外的合并会计处理。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-602 accepted（closure.next=ZR-603；revenue closure commit 2139a2c）。
- [x] triplet 冻结：revenue 2139a2c、wiki 26a6b22…、filing 5a1c18f…。
- [x] 现状事实（RED 探针）：
  - P1：grep ownership|consolidat|equity_share|effective_date|country|region → `consolidated_forecast`（场景合并）/`segment_attribution`（驱动归因）/`constants.py:89 equity_share`（ZR-602 枚举值）均为无关同名；无 ownership 计算。
  - P2：grep equity|minority|ownership_pct|stake|holding|attribut → 零计算命中。
  - P3：grep country|region|geo → 零命中；segment 校验（document.py:802-）无 geography/ownership 键。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（ownership timeline/geography 契约层 + document 加性校验 + 探针驱动修复）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1/G2/G3 均为真实产品缺口。
- **Acceptance criteria**：
  - **C1 ownership timeline 契约（杀 G1）**：`validate_ownership_timeline(timeline)`——非空、effective_date ISO 唯一升序、ownership_fraction ∈ (0,1]，违者 ForecastInputError；`ownership_fraction_on(timeline, on_date)`——取 effective_date ≤ on_date 的最新条目，早于首条目 fail-closed（不隐式回溯）；`fraction_for_period(timeline, start, end)`——期初/期末 fraction 不一致（period 内收购）默认拒绝，显式 `allow_pro_rata=True` 才按日加权（不静默平均）。**收购生效日前后不同**由 lookup 语义钉死。
  - **C2 不二次乘权益（杀 G2）**：`effective_group_share(chain, on_date)`——多级链（如 集团 60%→中间体 70%→矿山 = 0.42）一次性连乘；`apply_ownership_share(annual_revenue, basis, chain, period_dates)`——basis=one_hundred_percent → 乘有效份额恰一次（group attributable）；basis=equity_share → 拒绝（"ownership share already applied"——Kamoa/Porgera 防线）；basis=consolidated → 拒绝（合并口径收入不再按权益折算）；与 ZR-602 basis 枚举逐字对齐。
  - **C3 地区层级（杀 G3）**：`validate_geography(geography)`——dict、country 非空 str、region 可选非空 str，缺省（None）兼容既有 segment；`geography_index(segments)`——{country: {region|None: [资产名]}} 可检索索引 + 空白/非 dict 拒绝；document 级：segment 携带 geography/ownership 键时校验（加性调用零 McCabe 增量——复用 ZR-602 None 早退模式）。
  - 质量门：revenue tests/ 全量无回归；ruff clean；ratchet 绿；skill-sync MATCH。
- **Stop conditions / handoff**：改模型公式语义、改输出路径（golden 行为锁）、真实 catalog 写、下载、LLM → 立即停止。

## Annex：ownership 判定矩阵

| 场景 | 期望 |
|---|---|
| timeline 空条目 / 日期重复 / fraction 0、>1、负 | ForecastInputError |
| on_date 早于首条 effective_date | ForecastInputError（不隐式回溯） |
| 生效日前 vs 后查询 | 返回不同 fraction（收购语义） |
| period 内 fraction 变更（默认） | ForecastInputError（不静默平均） |
| period 内变更 + allow_pro_rata=True | 日加权平均 |
| 链式 0.6×0.7 | 0.42（一次连乘） |
| basis=equity_share 再乘权益 | ForecastInputError（不二次乘） |
| basis=consolidated 乘权益 | ForecastInputError（合并口径） |
| basis=one_hundred_percent 乘权益 | 恰一次 ×0.42 |
| geography 空 country / 非 dict | ForecastInputError |
| geography 缺省（None） | 通过（加性兼容） |
| geography_index 检索 | country→region→资产名可查 |

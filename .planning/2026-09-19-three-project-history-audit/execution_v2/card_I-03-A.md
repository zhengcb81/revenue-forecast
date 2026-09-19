本卡由[filing_cards.md](filing_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[filing_cards.md共用规则](common_filing_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-03-A — 冻结期间、修订、最新性与授权绑定契约

父项：I-03。状态：planned；实施结果：未执行。角色：company-wiki 来源负责人（filing 为消费者 reviewer）。

依赖：I-00-A、I-00-B。

执行门：高级 reviewer 先定案；本卡不实施产品

### 现行源码锚点

- [src/company_wiki/source_catalog/gap_plan.py:95](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/gap_plan.py:95) — `build_gap_plan`；SHA-256 `d18391b7fa7adf06bf882d013cd9ccae48b9fad24429c3ac66d61b68d907c79f`。
- [src/company_wiki/source_catalog/gap_plan.py:214](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/gap_plan.py:214) — `_hash_gap`；SHA-256 `d18391b7fa7adf06bf882d013cd9ccae48b9fad24429c3ac66d61b68d907c79f`。
- [src/company_wiki/source_catalog/authorization.py:23](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/authorization.py:23) — `DownloadAuthorization`；SHA-256 `f858a369ed556d1b110be5ba7be7fa25ae3519fda94296cfe1c4f9e367d55f43`。
- [src/company_wiki/source_catalog/close_gap.py:55](C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/close_gap.py:55) — `CloseGapBinding`；SHA-256 `117c8166a6c26f3462574b787e0db79c419e00c8b18287f25738948032f475c3`。

### 允许改动

- 仅本次新 run 的决策文档、输入表和 oracle；不改产品 schema/代码/配置

### 输入与独立预期

- 原始反例：reviews/cross_history/current_recheck.json；阅读四个 current_gap_probes，不把候选集当已下载失败。
- 手工输入表使用抽象列 entity/market/kind/period_start/period_end/fiscal_year/provider/id/filed_at/accepted_at/amended/url；这些是待映射的语义列，不冒充现有 Python 参数。
- 固定 ACME/US、annual_report、FY2025、as_of=2026-07-31；本地 z-old/2026-03-01、远端 a-new/2026-04-01，均为受信同期间同文件族。独立预期 a-new 比 z-old 新；反向本地 a-new、远端 z-old 不得降级。

### 按序动作

1. 读取四个源锚点和 acquisition 的实际调用关系，列当前字段、来源与缺失值处理，不以 provider ID 字典序推断披露时间。
2. 高级 reviewer 决定：annual/interim/quarter 的期间键；非日历财政年；日期与精确时间及时区；filed/accepted/修订链冲突优先规则；已知更正版如何覆盖原件；缺期/缺可信日期/同日冲突的显式未知状态。
3. 决定 exact 与 latest_as_of 的输出契约、latest provider 故障时可否仅返回本地但必须声明最新性未知；明确 not_published、already_covered、no_gap 的区别，禁止同一布尔值代替三者。
4. 决定多期 gap 每次单候选还是有界批次；未完成候选如何保留，不能仅取第一个却宣称全 gap 关闭。
5. 决定哈希的规范序列化、schema 版本、候选排序、资格字段及 policy 绑定位置；确认 URL/date/period/revision/provider/entity/kind/market 变化的旧授权失效规则。不要自创第二策略源。
6. 写旧版本兼容和授权失效迁移表；高级 reviewer 为每个下面的输入给唯一输出/拒绝理由/消费行为，未决格必须阻断 I-03-B/C/D。

### 正反例与故障注入

| Case | 输入/注入点 | 独立预期 |
|---|---|---|
| G-D1 | 上述受信日期正向/反向，provider ID 与日期顺序相反 | 正向选择 a-new；反向不选择 z-old；不使用字符串 ID 排序 |
| G-D2 | annual FY2025 与 interim FY2025；非日历 FY2025 期间 2024-07-01 至 2025-06-30 | 不得因为 fiscal_year 相同合并不同期间/文种；具体 period key 由本卡签署 |
| G-D3 | 缺 period、无可信日期、同日不同文档且无修订关系、日期互相冲突 | 不得默选或把缺失 metadata 视为已覆盖；签署明确 ambiguous/unknown 类契约 |
| G-D4 | provider 空成功、provider 异常、本地完整覆盖、未来披露 2026-08-01 | 四类不得合并；未来文件不作截至日可用文件；空成功不等于证明公司尚未发布 |

### 本卡追加证据

- 逐字段映射与真实性来源；期/修订/最新性状态表；哈希字段表；兼容矩阵；高级 reviewer 签署的 oracle（值与理由，不能只写通过）

命令： 本卡无产品执行命令；仅设计与独立审查。

### 失败停止条件

- 任何状态或 schema 迁移仍有 TBD；日期可信性来源未明；想用新增 provider 网络请求填本卡输入时停止

### 恢复边界

- 仅修改本次决策文档；保留未决项；不得回写旧 PASS 或重算旧授权使之继续有效

### 关闭标准

- 决策表无未决项；独立 reviewer 复算 G-D1—D4；后继卡引用决策文件 hash

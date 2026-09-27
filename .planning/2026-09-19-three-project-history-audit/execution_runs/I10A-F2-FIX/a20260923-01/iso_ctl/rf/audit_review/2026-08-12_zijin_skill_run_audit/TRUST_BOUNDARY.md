# TRUST BOUNDARY — 紫金矿业 revenue-forecast 隔离运行

## 任务与输入边界

- 原生业务输入：紫金矿业，预测未来五年收入增速。
- 用户额外关注的 filing reuse、Dropbox、矿山、MD/切片/标签、网络保存仅用于旁路审计，没有注入原生业务任务。
- 信息截止日固定为 2026-08-12；整理跨到 2026-08-13 不引入截止日后的公司信息。

## 能被程序强证明的内容

- input 符合 schema 3.7，并通过 validate_document。
- draft 经过完整计算和 validate_published_forecast 的强输出重算后才返回。
- 同一 input 连续两次 draft 结果的 canonical SHA-256 相同。
- 四分部 base 对账、逐年分部汇总、情景排序、CAGR、概率和、growth-driver reconciliation 和 sensitivity 均可从 JSON 重算。
- publication registry 在本轮 builder 前后 size/hash 不变。
- source snapshot 与 claim/capture receipt 在 input 内按实际文件 hash 绑定。

## 依赖宿主/人工观察、不能由 JSON 自证的内容

- 浏览器是否真正搜索/打开了每个官方页面；由 trace/web_events.md 和宿主工具事件证明。
- filing-fetch 第三轮上游 handle 未由顶层 CLI 打印；reused_existing/0 download 是 envelope 实现、handle 到达路径、journal mtime/内容和请求无授权的联合结论。
- isolated prompt-injection review 是本次代理的只读模式扫描+人工抽查，没有外部签名 attestation provider。
- Dropbox 七份 PDF 的页码/内容结论来自只读文本抽取和代表性页面视觉抽查；未转成共享 artifact。
- 网络搜索不保证穷尽所有公开材料；未找到不等于不存在。

## 来源边界

| source_id | snapshot | SHA-256 | capture性质 |
|---|---|---|---|
| annual_2025 | company-wiki canonical PDF | 01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d | local_document；isolated self-reported review |
| annual_2024 | company-wiki canonical PDF | 004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89 | local_document；isolated self-reported review |
| results_2025 | audit目录 HTML | 08bbc18f4dcb2bce1cd0af21075ae10155fe69beeb178e73768a3fa410d648fe | isolated manual_open；未入共享 catalog |
| norton_2026 | audit目录 HTML | a9662471d15bf8ac287c179d3ae67cf3e35465b39425637119f25e1152f00b12 | isolated manual_open；未入共享 catalog |

Q1/H1/Allied Gold 只作为叙述性 sanity/counterevidence，不绑定参数；原因是没有获准冻结其本地 PDF/HTML snapshot。错误的 strategy HTML 被排除，不是 source。

## 模型边界

- 模型单元是四个外部收入报告分部，不是矿山、矿种或法律实体。
- FY2029–FY2030 growth 是无来源 analyst fade，不受 FY2028 管理层指引背书。
- 没有逐矿量价/权益/并表/抵销模型，没有商品价格/TC-RC/汇率曲线，没有历史回测。
- scenario probabilities 是分析师校准，不是管理层概率或承诺。
- direct_growth 使 revenue-weighted explicit model share 为 0；结果置信度为 low。

## 发布边界

- 结果是 draft；没有 formal publication，没有 registry entry，没有 host-signed attestation。
- 原生 render_markdown 无法处理合法 draft receipt，故 outputs/draft_report.md 是从已经强校验的 JSON 生成的透明 isolated summary，不冒充 official renderer output。
- outputs/draft_result.json 是数值真源；若 Markdown 与 JSON 冲突，以 JSON 为准并视为审计错误。

## 写入与未写入

本次写入：

- audit_review/2026-08-12_zijin_skill_run_audit/ 内的规划、trace、隔离 HTML、JSON、验证回执和报告。

本审计没有主动/显式写入：

- revenue/filing/company-wiki 产品代码或配置；
- company-wiki 的 ingest/index、文档 metadata、prompt-injection review、artifact、span/tag；
- worker 队列、优先级、状态。

不能作强零写声明的边界：

- reuse-only source-preparation 仍会构造具有目录创建、WAL、DDL、migration、fingerprint seed 和 commit 能力的 `CatalogStore`。一次受限运行因此报“attempt to write a readonly database”，一次 live 运行遇到 `database is locked`；第三次虽返回 exact reuse，仍经过同一初始化层。
- 后台 worker 在整个审计期持续改变约 49.6GB catalog；无法从 DB/WAL/SHM 的整体 mtime 或 hash 把字节变化归因给某个调用。
- 目标级 acquisition journal、canonical 文件 hash、artifact/producer-event 检查支持“本轮零下载、零新处理 artifact”；它们不等于全库 byte-for-byte 不变证明。
- 三个仓库的工作树和 HEAD 在运行中被其他 agent 并发修改。本审计未创作、覆盖或回滚这些产品变更；最终使用的运行时快照另见 `RUN_MANIFEST.md`。
- filing acquisition journal；
- publication registry；
- Dropbox 原文件或其旁路 MD。

# ZR-509 工作单元卡（preflight）— 官方公告/新闻 HTML capture：title/entity/period 身份门

- 领取时间：2026-08-19T20:40Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-509`，ZR-508 accepted + closure→ZR-509；锁 ZR-509（owner=zr509-implementer）。
- 依赖：ZR-501~508（✅，其中 ZR-503 entity 检测可复用）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第九卡：**官方 HTML capture 身份门**（authoritative_execution_plan："官方 HTML 的 title/entity/period 身份门和共享保存/索引"）。官方公告/新闻网页（交易所、公司官网）是上市公司信息的第一手来源——捕获前必须验证 title/entity/period 身份，防止把无关/空实体网页当官方公告入库。golden corpus 已注册 wrong strategy HTML（`audit sources/2026_strategy.html`，hash b2d215df…）为**空实体负例**（供 ZR-509/502 错归测试）。现有 announcement_collector 只处理 PDF 公告（URL 策略 + 下载 + receipt），无 HTML 身份门。
2. **production entrypoint 是什么？** 新 `src/company_wiki/source_catalog/html_capture.py` 纯函数：`parse_html_identity(html_text)`（title/entity 候选/period 提取）+ `validate_html_capture(identity, declared_entity)`（身份门：title 非空、entity 可验证、period 格式）——捕获前校验，不写盘不下载（本卡只做纯函数门 + 测试 fixture）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 无 HTML 身份门**：官方 HTML 捕获无 title/entity/period 校验机制（grep html_capture 0 命中）。
   - **G2 空实体网页不 fail-closed**：wrong strategy HTML（无公司名）无检测——若被捕获将作为无身份文档入库（错归/污染）。
   - **G3 无共享保存/索引契约**：HTML 捕获的规范化产物（identity 判定）无结构化输出。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/html_capture.py` + 新测试 `tests/contract/test_zr509_html_capture.py`；revenue receipts/ZR-509/**。禁止：真实下载/写盘、真实 catalog 写、LLM、改 admission/schema、实体名硬编码。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-510（阶段 E 收尾卡：完整 attribution/错归负例闭环）。本卡不做：真实下载执行、公告索引落库（后续卡）、PDF 公告路径（既有 announcement_collector）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-508 accepted（closure.next=ZR-509）。
- [x] triplet 冻结：revenue（ZR-508 closure 提交后）、wiki `8e2bf3f…`、filing `5a1c18f…`。
- [x] 现状事实：announcement_collector 仅 PDF（URL 策略/下载/receipt）；grep html_capture 0；golden corpus wrong strategy HTML 空实体负例已注册（hash b2d215df…，audit sources 路径）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（html_capture.py + 测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 HTML 身份解析（杀 G1）**：`parse_html_identity(html_text)` 纯函数（hermetic 零硬编码）提取 title（`<title>`/`<h1>`，去除标签与空白）、entity 候选（复用 ZR-503 公司名短语提取思路：后缀锚定模式）、period（`YYYY年M月D日`/`YYYY-MM-DD`/`YYYY年` 模式，多个取首个）→ {title, entities, period, schema_version}。
  - **C2 身份门（杀 G1 端）**：`validate_html_capture(identity, declared_entity)` → verdict ∈ {ok, missing_title, no_entity, entity_mismatch, invalid_period}；title 非空 + entity ≥1 + period 格式合法 → ok；declared_entity 提供时 entity 与声明匹配（含简称/全称 containment）否则 entity_mismatch；无 entity → no_entity（fail-closed）。
  - **C3 空实体负例（杀 G2）**：wrong strategy HTML 形状（无公司名短语的 HTML 文本）→ parse 后 entities=[] → validate 得 no_entity（fail-closed，不通过）。
  - **C4 结构化输出（杀 G3）**：identity 判定输出可 JSON 序列化（共享保存/索引的基础契约）；确定性（同输入同输出）。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超（新文件 max≤10）；独立 reviewer 复放。
- **Stop conditions / handoff**：真实下载/写盘、真实 catalog 写、LLM、改 admission/schema → 立即停止。

## Annex：HTML 身份门判定矩阵

| HTML 形状 | parse 结果 | validate(declared) |
|---|---|---|
| `<title>紫金矿业集团股份有限公司关于2026年年度报告的公告</title>` + 正文公司名 | title 非空、entities=[紫金…]、period=2026年 | ok |
| 正文无公司名（wrong strategy 形状） | entities=[] | no_entity（fail-closed） |
| 无 title/h1 | title=None | missing_title |
| entities=[陕西煤业…] vs declared=紫金 | entities 非空 | entity_mismatch |
| period="2026年13月45日" | period 提取或非法 | invalid_period（若提取到非法日期） |

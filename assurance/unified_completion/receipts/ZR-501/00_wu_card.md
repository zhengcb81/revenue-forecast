# ZR-501 工作单元卡（preflight）— broker_research 文档/准入/metadata contract

- 领取时间：2026-08-19T19:45Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-501`，ZR-409 accepted + closure→ZR-501（阶段 E 首卡）；锁 ZR-501（owner=zr501-implementer，nonce e84a375b…）。
- 依赖：ZR-301（readiness ✅）、ZR-401（RootPolicy 3.0 ✅）。Registry 依赖列=ZR-301,ZR-401。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 首卡：broker_research 文档的**准入与 metadata 契约**。证据= publisher/authors/date/entities/security IDs/page count；**filename 仅 proposal**。现状：broker_research 分类/准入已钉死（DBX-04/09/12、classification suite、sidecar generic kind、admission non_filing_kind）；但 metadata contract 未落库——sidecar normalized 不透传 publisher/authors/security_ids，normalized artifact frontmatter 无 page_count（pdf_page_aware 的 page_count 只在 parser 内部用于渲染）。
2. **production entrypoint 是什么？** sidecar adapter `_normalized_from_sidecar`（directory 根 broker_research 元数据源）→ documents.metadata_json；`normalizer._pdf_markdown`/`_frontmatter`（normalized artifact metadata 构造）；admission `evaluate_candidate`（non_filing_kind 门，已闭）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 filename 仅 proposal 未钉死**：无 sidecar 的 broker_research（真实 Dropbox 样本如 `20190311-阿里研究院-从连接到赋能…pdf`）文件名含日期/机构，但无测试钉死"文件名推断不作 metadata 事实"（publisher/date 不得从文件名冒充；published_date=None；metadata 缺字段可查）。
   - **G2 metadata contract 未落库**：sidecar 提供 publisher/authors/security_ids 时不透传进 normalized（加性缺口）；normalized artifact frontmatter 无 page_count（解析器已知但不落库）。
   - **G3 全字段准入闭环缺**：metadata 完整（publisher/authors/security_ids/page_count 全有）的 broker_research 仍必须 non_filing_kind 拒绝——无端到端断言。
4. **允许改哪些文件？** company-wiki sidecar.py（`_normalized_from_sidecar` 加性透传 publisher/authors/security_ids）+ normalizer.py（`_Normalized.page_count` 可选 + `_pdf_markdown` 传入 + `_frontmatter` 加 page_count 键）+ 新测试 `tests/contract/test_zr501_broker_metadata_contract.py`；revenue receipts/ZR-501/**。禁止：真实 catalog 写、下载、LLM/parser 调真实外部、改 admission 语义。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-502（sidecar 与原文角色分离、首页身份验证）。本卡不做：首页身份验证（ZR-502）、多实体 attribution（ZR-503）、页码保真 golden（ZR-504）、ProcessingDemand（ZR-507）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-409 accepted（closure.next=ZR-501）。
- [x] triplet 冻结：revenue `7f7acd3…`、wiki `726d63d…`、filing `5a1c18f…`。
- [x] 现状事实：scanner `_classification` directory 根→broker_research（文件名/路径）；admission generic profile non_filing_kind（DBX-09/12 已测）；sidecar `_normalized_from_sidecar` 现有键（schema/canonical_entity_id/display_name/market/security_id/document_kind/fiscal_year/period_end/provider/pdoc/source_url/published/filed/language/revision/content_sha/adapter）；pdf_page_aware.PageAwarePDFResult.page_count；normalizer `_frontmatter`（schema/role/document_id/source_id/source_sha/title/kind/published/status/parser/quality）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（sidecar/normalizer 加性 + 合同测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 filename 仅 proposal（杀 G1）**：无 sidecar 的 broker_research 文件名（含日期/机构模式）→ 分类 broker_research、published_date=None（文件名日期不冒充）、metadata 无 publisher（缺字段诚实）；sidecar 提供时字段来自 sidecar（文件名不覆盖）。
  - **C2 metadata contract 落库（杀 G2）**：sidecar 带 publisher/authors/security_ids → normalized 透传 → documents.metadata_json 含三键（加性）；broker_research PDF normalize 后 normalized artifact frontmatter 含 page_count（合成 2-3 页 PDF 验证；None 时不伪造）。
  - **C3 准入闭环（杀 G3）**：metadata 全字段的 broker_research（publisher/authors/security_ids/page_count 全有）→ evaluate_candidate 仍 non_filing_kind 拒绝；filing 请求（annual_report）不满足。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、改 admission/profile 语义 → 立即停止。

## Annex：broker_research metadata contract 矩阵

| 字段 | 来源 | 无来源时 |
|---|---|---|
| document_kind | sidecar/分类 | broker_research（分类） |
| publisher | sidecar（透传） | 缺（不冒充） |
| authors | sidecar（透传） | 缺 |
| security_ids | sidecar（透传） | 缺 |
| published_date | sidecar | None（文件名日期不作数） |
| page_count | parser（frontmatter） | None（不伪造） |
| filing 准入 | admission 门 | 永不 admitted（non_filing_kind） |

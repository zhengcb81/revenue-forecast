# ZR-502 工作单元卡（preflight）— sidecar 与原文角色分离、首页身份验证

- 领取时间：2026-08-19T20:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-502`，ZR-501 accepted + closure→ZR-502；锁 ZR-502（owner=zr502-implementer，nonce fefeaa1c…）。
- 依赖：ZR-501（accepted ✅）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第二卡：**sidecar 与原文角色分离 + 首页身份验证**。证据= `.source.json` 不成为年报/研报；错误文件名/首页矛盾 fail/review。现状：角色分离已钉死（test_n08 standalone sidecar 不作候选；sidecar 文件永不为 original；DBX-04 文件名"年报"实为研报已 fail closed）；**首页身份验证缺失**——PDF 首页文本与 sidecar 声称的 title/publisher 从未比对，错误文件名+矛盾首页无法在 normalize 阶段 fail/review。
2. **production entrypoint 是什么？** sidecar adapter（角色分离，已闭）→ normalizer `_pdf_markdown`（parser 产逐页文本，page 1 可得）→ `normalize_catalog`（normalized artifact frontmatter + quality_flags）。首页验证作为 normalizer 阶段纯函数质检接入（不改 schema/表）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 首页矛盾未检测**：sidecar title="中信证券-紫金矿业深度报告" 但 PDF 首页标题/机构指向其他公司或券商 → 当前无任何比对，照常 capture_ready（错误文件名/首页矛盾未 fail/review）。
   - **G2 首页验证无机制**：无 `assess_homepage_identity` 纯函数（首页文本×sidecar title/publisher → consistent/contradiction/unverifiable）；无 quality_flag 通道（矛盾进 frontmatter/quality_flags）。
   - **G3 角色分离端到端缺口**：无测试钉死"sidecar 文件自身绝不出现在 annual/broker 请求的 matches 中"（n08 只测 enumerate 不产候选；请求级需补）。
   - 既有已钉死（不重复）：standalone sidecar 不作候选（n08）、unknown schema/path escape/parse failure fail closed（n02/n03/n11/path_escape）、DBX-04 文件名误标、sidecar hash 错→indexed_only。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/homepage_identity.py`（纯函数）+ normalizer.py（page 1 文本提取 + 调用接入 + frontmatter `homepage_identity` 键 + 矛盾 quality_flag）+ 新测试 `tests/contract/test_zr502_homepage_identity.py`；revenue receipts/ZR-502/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-503（多实体 attribution）。本卡不做：多实体/局部归属（ZR-503）、页码保真 golden（ZR-504）、表格保真（ZR-505）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-501 accepted（closure.next=ZR-502）。
- [x] triplet 冻结：revenue（ZR-501 closure 提交后）、wiki `8c5f24f…`、filing `5a1c18f…`。
- [x] 现状事实：`_pdf_markdown` 逐页渲染（parser_results 含 coordinates.page_number）；`_Normalized.quality_flags` 进 frontmatter + artifacts；documents 有 title/publisher（ZR-501 加性）；sidecar adapter 角色分离已钉死（n08）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（homepage_identity 纯函数 + normalizer 接入 + 测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 角色分离闭环（杀 G3）**：sidecar 文件自身在任何 annual/broker 请求的 resolver matches 中永不出现在 matches[0]（enumerate 不产候选 + 请求级断言）；`.source.json` 不作年报/研报。
  - **C2 首页身份验证（杀 G1/G2）**：`assess_homepage_identity(first_page_text, title, publisher)` 纯函数 → consistent/contradiction/unverifiable（归一化文本匹配；title/publisher 强命中→consistent；明确矛盾信号→contradiction；无文本→unverifiable 不阻塞）；normalizer 接入：page 1 文本（coordinates.page_number==1 的 raw_text）→ 比对 documents.title/publisher → frontmatter 加 `homepage_identity` 键 + 矛盾时 quality_flag `homepage_identity_contradiction`。
  - **C3 矛盾 fail/review（杀 G2 端）**：构造 sidecar title/publisher 与首页明确矛盾的合成 PDF → normalize 后 frontmatter homepage_identity=contradiction + quality_flag 存在（review 信号）；一致 → consistent；首页无文本 → unverifiable 不伪造。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema → 立即停止。

## Annex：首页身份判定矩阵

| 首页信号 vs sidecar 声称 | 判定 |
|---|---|
| title 强匹配（归一化包含） | consistent |
| publisher 强匹配 | consistent |
| 首页明确含其他公司/券商名 + sidecar 声称不同 | contradiction |
| 首页无文本/提取失败 | unverifiable（不阻塞） |
| 文件名"年报"但首页研报特征（DBX-04 已有） | 既有分类已处理 |

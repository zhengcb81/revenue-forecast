# ZR-503 工作单元卡（preflight）— 多实体 attribution：不串实体（detection + fail-closed）

- 领取时间：2026-08-19T19:45Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-503`，ZR-502 accepted + closure→ZR-503；锁 ZR-503（owner=zr503-implementer）。
- 依赖：ZR-501（accepted ✅，sidecar security_ids 透传）、ZR-502（accepted ✅，首页身份验证）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第三卡：**多实体 attribution 不串实体**。证据= golden corpus `zijin_broker_20240304_changjiang`（长江证券「紫金矿业VS陕西煤业」比较报告，双实体负例，hash 273d4508…，dropbox anchor）；traceability BR-06/07：长江紫金/陕西煤业 section/table/row attribution 准确，**错归=0**。现状：多实体报告内容被隐式按单实体（sidecar canonical_entity_id）归属——长江报告全部归紫金，陕西煤业内容被污染/丢失（current_state_audit：长江比较报告绑定 Unresolved，单实体默认会污染或丢失多实体内容）。
2. **production entrypoint 是什么？** sidecar（canonical_entity_id/security_ids 声明，ZR-501 已透传）→ normalizer `_pdf_markdown`/`_first_page_text`（全文文本可得）→ `normalize_catalog`（frontmatter 加检测结果 + quality_flags）。多实体检测作为 normalizer 阶段纯函数质检接入（同 ZR-502 模式，不改 schema/表）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 多实体零检测**：正文出现多个公司名（如"紫金矿业…VS陕西煤业…"）→ normalize 产物无任何多实体信号（无 entities 键、无 quality_flag）→ 下游按单实体消费，错归无防护。
   - **G2 无检测机制**：无纯函数从全文文本提取公司名短语集合并与 sidecar 声明比对（multi_entity/single/unverifiable 判定）。
   - **G3 无防污染门**：无 fail-closed 标记——多实体文档不得静默按单实体 canonical 归属（ZR-510 做完整逐 section/table/row attribution；本卡先钉"检测 + 拒绝静默单实体污染"）。
   - 既有已钉死（不重复）：sidecar security_ids 透传（ZR-501）、首页身份验证（ZR-502）、sidecar 角色分离（ZR-502）。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/entity_detection.py`（纯函数：公司名短语提取 + 与声明比对）+ normalizer.py（全文文本接入 + frontmatter `detected_entities` 键 + 多实体 quality_flag）+ QualityFlag/observability 词汇注册（同 ZR-502 模式）+ 新测试 `tests/contract/test_zr503_multi_entity_attribution.py`；revenue receipts/ZR-503/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema、硬编码实体名（零产品硬编码：陕西煤业/紫金不得写死在产品代码）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-504（页码保真 golden）。本卡不做：逐 section/table/row 归属落库（ZR-510 错归负例闭环）、页码保真（ZR-504）、typed table（ZR-505）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-502 accepted（closure.next=ZR-503）。
- [x] triplet 冻结：revenue（ZR-502 closure 提交后）、wiki `19c3b73…`、filing `5a1c18f…`。
- [x] 现状事实：normalize frontmatter 无 entity 维度；sidecar security_ids 透传存在（ZR-501）；首页身份验证纯函数模式可复用（ZR-502）；golden corpus 长江双实体负例 hash 冻结。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（entity_detection 纯函数 + normalizer 接入 + 测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 多实体检测（杀 G1/G2）**：`detect_entities(text, *, declared_entity, declared_security_ids)` 纯函数（hermetic 无 LLM、零实体名硬编码）→ 从全文提取公司名短语（`…股份有限公司/…有限公司/…集团` 模式）→ 与声明比对 → verdict ∈ {single, multi_entity, unverifiable} + 提取集合；多实体报告（如长江紫金VS陕西煤业）必须 multi_entity，单实体报告 single，无公司名短语 unverifiable。
  - **C2 normalizer 接线（杀 G1 端）**：normalize 后 frontmatter 加 `detected_entities` 键（verdict + 提取集合）；multi_entity → quality_flag `multi_entity_attribution_needed`（fail-closed review 信号，单实体消费不得静默）；single/unverifiable 无该 flag。
  - **C3 零硬编码（杀 G3 伴生）**：产品代码 grep 无"紫金"“陕西煤业”等实体名硬编码；合成双实体 fixture（构造性文本）→ 检测 multi_entity 且提取集合含两个不同短语；golden corpus 长江条目 hash 锚定（只读引用，不拉原文）。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、实体名硬编码 → 立即停止。

## Annex：多实体判定矩阵

| 正文公司名短语 vs sidecar 声明 | 判定 |
|---|---|
| 只有声明实体相关短语 | single（正常单实体） |
| 声明实体 + 至少一个其他公司名短语 | multi_entity（attribution 需后续卡/人工 review） |
| 多个公司名短语且声明为空 | multi_entity（声明缺失但内容明确多实体） |
| 无公司名短语 | unverifiable（不伪造） |
| 声明实体在正文中缺失但无其他实体 | single（与 ZR-502 不同：此处不做矛盾 fail，归 ZR-502 首页验证管） |

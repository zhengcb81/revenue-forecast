本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-02-C — 注册已落盘的小米/微软原件且不再下载

parent：I-02；status：planned；owner：company-wiki 来源系统实施者。

依赖：I-02-A、I-02-B。设计前置：D-W02。证据目录：`execution_runs/I-02-C/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/canonical_writer.py:136](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/canonical_writer.py:136>) `CanonicalSourceWriter.import_staged`：目前入口只接受 validated staging receipt；不能假造新 receipt 把 canonical raw 冒充 staging。 SHA256 `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258`。
- [company-wiki/src/company_wiki/source_catalog/canonical_writer.py:225](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/canonical_writer.py:225>) `_validate_staged`：校验 staging containment/identity/hash/size。 SHA256 `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258`。
- [company-wiki/src/company_wiki/source_catalog/acquisition_service.py:76](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_service.py:76>) `SourceAcquisitionService.ensure`：先 resolve_or_stage；恢复入口须先查已知持久资产。 SHA256 `017ca75c1efec6986af058c068db86bbf9fed5edd2bd8ede94fd96a1a8e7f8c7`。
- [company-wiki/src/company_wiki/source_catalog/acquisition_journal.py:72](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_journal.py:72>) `AcquisitionJournal`：现有 append-only attempt，不等于完整恢复状态机。 SHA256 `104d73fdf68e7253d54258dd98fcc1e5bff09343b949e376ad1e199ccc9c6736`。

**必读原证据**

- [audit_review/2026-09-18_real_company_skill_audit/independent/acquisition_aftercheck.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/independent/acquisition_aftercheck.json>)： 两新 raw 的绝对路径、sidecar、candidate/request、字节 hash 与大小；必须逐字段取，不按公司名猜路径
- [audit_review/2026-09-18_real_company_skill_audit/runs/09_xiaomi_reuse_after_download/run.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/09_xiaomi_reuse_after_download/run.json>)： 落盘后仍 not_found
- [audit_review/2026-09-18_real_company_skill_audit/runs/10_msft_reuse_after_download/run.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/10_msft_reuse_after_download/run.json>)： MSFT 落盘后仍 not_found
- [audit_review/2026-09-18_real_company_skill_audit/independent/data_pipeline_review.md](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/independent/data_pipeline_review.md>)： 原件存在与 usable qualification 分开

**只允许修改**

- CW:src/company_wiki/source_catalog/canonical_writer.py
- CW:src/company_wiki/source_catalog/acquisition_service.py
- CW:src/company_wiki/source_catalog/acquisition_journal.py
- CW:src/company_wiki/source_catalog/cli.py（只接批准的现有 raw 恢复入口）
- 对应 isolated tests；不能改真实 PDF/HTM/sidecar/DB

**固定样本**

- HK 固定 hash ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c，4405561 bytes，hkexnews:12127452，FY2025。
- US 固定 hash e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff，8585615 bytes，sec:0001193125-26-323660，FY2026。
- I-00 复制上述 byte-identical raw/sidecar 到独立 root；保留 sidecar 的历史 staged_path 为 provenance，不能要求该历史临时路径仍存在；不得为迁路径改历史来源事实。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W02C-P1 / positive**：两真实 raw 副本存在、catalog 对应条目缺失、provider 全阻断。
  预期：各自完成 register→qualification→exact resolve；原 provider ID、期次、source hash 正确；discover=0/download=0/raw bytes changed=0。
- **W02C-P2 / positive**：P1 后通过原 exact 请求第二次复用。
  预期：同一版本/identity，无新原件/下载/重复有效记录；复用不等于审核或工件完成。
- **W02C-N1 / negative**：分别删除 sidecar 且无可验证持久 receipt、篡改 raw 1 byte、伪造 provider ID、缺 download receipt 来源链。
  预期：对应来源/身份/完整性缺口拒绝，不能自动从文件名补 provider/fiscal_year。
- **W02C-N2 / negative**：同 bytes 已 retired/quarantined 或所在 root 禁复用。
  预期：不调用 _reactivate_if_retired 偷换为授权重下载，不恢复 active，不返回合格 handle。

**按序执行**

1. I-00-A/B 提供只读来源定位和合法副本；先独立 sha/size 对照，拒绝原生产路径写入。
2. 在隔离 catalog 复现未注册；所有 provider adapter 改为测试 deny-on-call，记录计数。
3. 依 D-W02 接通批准的 register-existing 路径，只补已缺阶段；每阶段引用同 bytes/provenance。
4. 同一原请求重复验证，并测四个来源缺失/篡改负例及 retired/denied 边界。

**失败停止与恢复界限**

- 任一实际样本 hash 不符或 manifest 丢失就停该案例，不临时换公司或重新下载。
- 恢复仅 scratch catalog 和新增 journal；原件副本与诊断保留，不重写 sidecar 造事实。

入口：`CMD-W03`、`CMD-W05`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`sample-copy-manifest.json`、`zero-provider-events.json`、`registration-stages.json`、`exact-resolve.before-after.json`。

**退出判据**：两个原样本都通过零网络恢复注册；未审/工件不合格仍如实阻断，不称预测跑通。

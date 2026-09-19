本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-02-A — 扫描返回必须说明完成状态与目标注册结果

parent：I-02；status：planned；owner：company-wiki 来源系统实施者。

依赖：I-01-A。设计前置：D-W02。证据目录：`execution_runs/I-02-A/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/models.py:212](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/models.py:212>) `ScanReport`：目前有 errors/计数/strategy，无独立完成状态或目标文件结果字段。 SHA256 `65230572d355031d9634c9355939034d1dd8cb386bb98d1555e05184d4eb5087`。
- [company-wiki/src/company_wiki/source_catalog/scanner.py:1867](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/scanner.py:1867>) `scan_catalog`：异常会中断 scan_run；每根策略异常也可能累积进报告正常返回。 SHA256 `f039d5f8d1360bd0e87898c059b7cce68d7ec5d0fad31c9a0196a57a6425e45e`。
- [company-wiki/src/company_wiki/source_catalog/canonical_writer.py:136](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/canonical_writer.py:136>) `CanonicalSourceWriter.import_staged`：copy+sidecar 后调用 scan_catalog 丢弃结果，再 exact resolve。 SHA256 `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258`。

**必读原证据**

- [audit_review/2026-09-18_real_company_skill_audit/runs/07_xiaomi_source_download_authorized/run.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/07_xiaomi_source_download_authorized/run.json>)： 原真实失败命令、退出及日志定位
- [audit_review/2026-09-18_real_company_skill_audit/runs/08_msft_source_download_authorized/run.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/08_msft_source_download_authorized/run.json>)： 第二市场同阶段失败
- [../company-wiki/tests/contract/test_source_catalog_canonical_writer.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_source_catalog_canonical_writer.py>)： 现有导入及 post_import_rescan 测试范围

**只允许修改**

- CW:src/company_wiki/source_catalog/models.py（ScanReport）
- CW:src/company_wiki/source_catalog/scanner.py（报告/scan_run 状态）
- CW:src/company_wiki/source_catalog/canonical_writer.py（消费回执）
- CW:src/company_wiki/source_catalog/service.py（转发回执）
- 对应 isolated contract tests；枚举/schema 必须按 D-W02

**固定样本**

- 单 root、单有效 raw+sidecar 的小 catalog；另一个仅含不相关文件的健康 root；fake scanner 只允许测试故障注入，正例用真实 scanner。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W02A-P1 / positive**：目标文件经真实 scanner 与 resolver 成功。
  预期：完整 scan 状态+目标 hash/location 可核验，且 exact identity 一致才返回成功。
- **W02A-N1 / negative**：scanner 正常返回 ScanReport(errors=1, files_seen=0)。
  预期：writer 报 scan 阶段失败，不落成功 import/usable handle；raw/sidecar 保留。
- **W02A-N2 / negative**：errors=0 且 files_seen>0，但看到的只有另一个文件。
  预期：不得以总文件数充足推定目标注册；报告 target_not_registered 对应已冻结码。
- **W02A-N3 / negative**：DB scan_run interrupted/部分 root 成功/目标 identity 不符分别注入。
  预期：不报告 completed；各阶段区分；健康 root 的已提交结果不被误删。

**按序执行**

1. 先冻结 ScanReport/schema 和目标完成判据，正例独立核对 location/source/assertion/resolve，不只 assert report 字符串。
2. 复现函数正常返回但目标未注册的两种负例。
3. 在 scanner 生成受支持完成与目标信息，由 writer/service 消费；禁止仅 errors==0 或 files_seen>0。
4. 验证错误路径保存 raw 字节及 sidecar hash；记录 scan_run/target/最终 resolve 的关系。

**失败停止与恢复界限**

- scan 目标结果缺失不能再扫全库求绿；停在原目标，保留报告。
- 恢复隔离代码版本和 scratch DB 快照，不回滚真实 raw；不能把 interrupted 改 completed 关闭卡。

入口：`CMD-W02`、`CMD-W03`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`scan-return-contract.json`、`target-registration.sql-results.json`、`raw-before-after.json`。

**退出判据**：writer 不能忽略错误/中断/未注册目标；scan 成功与 exact resolve 成功分别有原始证据。

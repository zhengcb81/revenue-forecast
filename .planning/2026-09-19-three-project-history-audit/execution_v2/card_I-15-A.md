本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-15-A — prune 只删除已验证归档集合并证明可恢复

parent：I-15；status：planned；owner：存储维护实施者；独立恢复 reviewer。

依赖：I-00-A、I-00-B、I-00-C。设计前置：D-W15。证据目录：`execution_runs/I-15-A/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/prune_retired_evidence.py:28](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/prune_retired_evidence.py:28>) `_DELETE_BATCH`：当前选择全部 retired document 的 span，未绑定具体归档集合。 SHA256 `2358c73b82da65e5292998e3dba71c6132eebab1ab6c88a224a736c1e5a8ae46`。
- [company-wiki/src/company_wiki/source_catalog/prune_retired_evidence.py:59](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/prune_retired_evidence.py:59>) `prune_retired_evidence`：当前只以最老日期目录推 due。 SHA256 `2358c73b82da65e5292998e3dba71c6132eebab1ab6c88a224a736c1e5a8ae46`。
- [company-wiki/src/company_wiki/source_catalog/archive_retired_evidence.py:40](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/archive_retired_evidence.py:40>) `archive_retired_evidence`：按日期写同名 gzip；仅 count 对账，无精确集合 hash manifest。 SHA256 `143fef01fade43a5e6ae5c733d86e5ea6081482547c2560fc872990a9d8f53e0`。

**必读原证据**

- [../company-wiki/tests/contract/test_source_catalog_prune_retired.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_source_catalog_prune_retired.py>)： 当前 test_prune_apply_deletes_spans_when_due 仅建空旧目录却期望全删，必须改成拒绝反例；日期注释过时
- [../company-wiki/tests/contract/test_source_catalog_archive_retired.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_source_catalog_archive_retired.py>)： 现有真实归档测试，复用而不删除
- [../company-wiki/src/company_wiki/source_catalog/archive_retired_evidence.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/archive_retired_evidence.py>)： archive reader 的 snapshot/输出完成事实与同日覆盖风险
- [.planning/2026-09-19-three-project-history-audit/reviews/wiki/review.md](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/wiki/review.md>)： 维护边界；磁盘迁移已取消

**只允许修改**

- CW:src/company_wiki/source_catalog/prune_retired_evidence.py
- CW:src/company_wiki/source_catalog/archive_retired_evidence.py
- 对应 isolated contract tests；若需 manifest/CLI 新字段先由 D-W15 指明路径
- 仅 scratch archive/catalog 做 apply/restore；任何生产 DELETE/VACUUM/移动都禁止

**固定样本**

- 固定 now=2026-09-19T00:00:00Z，retention=90d；清单 verified_completed_at=2026-05-01T00:00:00Z。
- 归档包含 A:a1,a2 和 C:c1；apply 前 A 仍 retired、C 已 active；B:b1 为 retired 但从未归档；A:a3 为归档后新增。当前共 5 spans。
- 另有空旧目录、损坏 gzip、少一行/错误摘要清单、旧无 manifest、重复 span ID、归档与当前 bytes/identity 不符变异，分别测试。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W15-P1 / positive**：完整可验证 manifest，apply 前重新核对当前五行。
  预期：计划/实际只能删 a1,a2；删除=2，保留 b1,c1,a3 共3；根据独立预列 ID 集合判断，不调用 prune 生成 expected。
- **W15-P2 / positive**：P1 重复 apply；归档恢复到另一独立空 catalog。
  预期：第二次删除=0；restore a1,a2 字段/文本/hash 完全相同；不能恢复 active c1 覆盖较新状态。
- **W15-N1 / negative**：只有旧日期空目录，或 gzip/manifest 缺失/损坏/计数冲突。
  预期：dry-run 明确不具备删除资格；apply 删除=0，业务拒绝；旧测试绿不再当正确 oracle。
- **W15-N2 / negative**：90天未到/目录日期早但 verified 完成时间未到。
  预期：删除=0；以经验证完成时间计算，不能信任目录名。
- **W15-N3 / negative**：dry-run 后 a2 内容变更或文档转 active。
  预期：不得按旧计划删除 a2；本卡预期 apply 整体拒绝需重做计划，不容许静默缩集合当原计划成功。
- **W15-N4 / negative**：分批删除后进程中断/receipt 写失败。
  预期：以精确集合与事务事实恢复；剩余未删集合可重新计划，未获归档证明的行始终保留；不得因旧目录扩大到全部 retired。

**按序执行**

1. D-W15 冻结 manifest/计划 hash/锁与恢复协议；先写五行独立 oracle 与固定时钟。
2. 在新 scratch 创建真实归档，验证 gzip 内容/唯一 span ID/行摘要/清单完成状态；不伪造日期目录当归档。
3. dry-run 输出精确 ID 集合和证据摘要；apply 前重验归档及当前源状态，按同一集合在锁/事务下删。
4. 真实隔离 apply 对照固定2删3留，二次 apply、scratch restore、每个负例和中断恢复分别保留数据库快照/清单。
5. 确认 worker_control paused 未变、生产无写入；删除/restore 的真实资格由独立 reviewer 验。

**失败停止与恢复界限**

- 归档完整性、当前身份或计划 hash 任一不符立即不删；不临时把 retention 改0或关验证。
- 仅恢复当前 scratch snapshot/归档；生产清理仍未授权执行，本卡不涉及 D 盘迁移或启后台。

入口：`CMD-W10`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`archive-verified-manifest.json`、`exact-prune-plan.json`、`deleted-and-retained-ids.json`、`restore-proof.json`、`fault-recovery.json`。

**退出判据**：以行集合/实际可恢复性关闭缺口；scope 仅隔离维护，不能据此自动启动生产 prune。

## 范围限制

结构完整和文档干读只能说明计划可核查。12 张卡全部完成仍不自动证明真实 provider 可用、跨目录真实唯一样本存在、三家公司正式预测通过或准确性提高；这些仍由 I-07 与研究/评估/部署卡在其原范围验收。本轮没有运行弱模型实施试验。

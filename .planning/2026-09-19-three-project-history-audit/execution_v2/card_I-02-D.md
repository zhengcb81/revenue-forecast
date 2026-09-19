本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-02-D — 注册重入与同 bytes 去重不伪报成功

parent：I-02；status：planned；owner：company-wiki 来源系统实施者。

依赖：I-02-C。设计前置：D-W02。证据目录：`execution_runs/I-02-D/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/canonical_writer.py:155](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/canonical_writer.py:155>) `CanonicalSourceWriter.import_staged existing-original branch`：目前先删除 staging，再 resolve(request)，dedup 返回未明确检查 exact 成功。 SHA256 `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258`。
- [company-wiki/src/company_wiki/source_catalog/canonical_writer.py:276](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/canonical_writer.py:276>) `_existing_original`：只按 active company_raw 原件 dedup；不把外部 root 同 bytes 自动当 canonical 写目标。 SHA256 `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258`。
- [company-wiki/src/company_wiki/source_catalog/acquisition_journal.py:87](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_journal.py:87>) `AcquisitionJournal.record`：按完整 outcome 内容 hash 去重；不是所有相同 request 都压成一条。 SHA256 `104d73fdf68e7253d54258dd98fcc1e5bff09343b949e376ad1e199ccc9c6736`。

**必读原证据**

- [../company-wiki/tests/contract/test_source_catalog_canonical_writer.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_source_catalog_canonical_writer.py>)： deduplicates/ignores_dayu/reactivates 测试分别界定；不能扩大恢复授权
- [../company-wiki/src/company_wiki/source_catalog/acquisition_journal.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_journal.py>)： attempt_id 与 fsync/mutex 当前实现

**只允许修改**

- CW:src/company_wiki/source_catalog/canonical_writer.py（dedup/reentry）
- CW:src/company_wiki/source_catalog/acquisition_service.py
- CW:src/company_wiki/source_catalog/acquisition_journal.py（批准键与阶段）
- 对应隔离幂等测试；锁机制变更需 D-W02 及 I-04 owner 确认，不复制 worker scope 锁

**固定样本**

- 同 request/同 provider ID/同 hash 的登记重放三次；并发两个进程；同 bytes 不同 provider identity；同 request 新版本 hash。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W02D-P1 / positive**：同一已成功登记请求连续三次进入。
  预期：唯一有效 source version/location；零新下载/新 raw；每次有可对账调用结果，允许的审计 attempt 历史按冻结语义保留。
- **W02D-P2 / positive**：两个独立进程同时注册同一已存 raw。
  预期：最终只有一个有效登记，两个返回均指向同一已核验结果或明确可重试竞争；不丢 journal。
- **W02D-N1 / negative**：命中同 bytes 但 exact provider identity 未匹配。
  预期：不得返回 DEDUPLICATED 成功；保留恢复所需 staging/receipt 或持久等价证据。
- **W02D-N2 / negative**：相同 request 更换 hash/sidecar identity/policy。
  预期：不得命中旧完成状态；报告新版本/冲突/需重新资格审查，不覆盖旧 raw。
- **W02D-N3 / negative**：只有 dayu/external 同 bytes 或 retired 同 bytes。
  预期：遵循冻结 root/授权策略，不以 hash 相同绕过 canonical target、复用 deny 或退休资格。

**按序执行**

1. 先冻结逻辑完成键与审计 attempt 键的区别，用独立 SQL/文件清单作 oracle。
2. 从 I-02-C 成功状态开始串行三次；从 clean 副本开始两进程 barrier 并发。
3. 修正 dedup 返回的资格检查和清理时点；只有可恢复证据持久化后才移除临时 staging。
4. 运行 identity/hash/policy 三类变异，列有效记录数、raw 文件数、provider 调用数、各进程返回及审计历史。

**失败停止与恢复界限**

- 发现同 bytes 多身份设计未明确先交 senior，不按 first-row-wins 实现。
- 失败保留竞争日志和两进程退出信息；只停止本卡启动的 scratch 进程，不清全库锁或恢复后台 worker。

入口：`CMD-W03`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`idempotency-matrix.json`、`two-process-trace.json`、`logical-rows-vs-attempts.json`。

**退出判据**：幂等指业务资产与资格稳定，不以删除审计历史或跳过 exact resolve 换唯一数。

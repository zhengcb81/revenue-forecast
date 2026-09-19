本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-02-E — 在每个持久化边界中断后只恢复缺失阶段

parent：I-02；status：planned；owner：company-wiki 来源系统实施者。

依赖：I-02-D。设计前置：D-W02。证据目录：`execution_runs/I-02-E/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/canonical_writer.py:137](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/canonical_writer.py:137>) `import_staged / _atomic_copy / _write_provenance`：copy、sidecar、scan、resolve 跨文件和 DB 边界。 SHA256 `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258`。
- [company-wiki/src/company_wiki/source_catalog/scanner.py:1867](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/scanner.py:1867>) `scan_catalog`：持久 scan_run 中断处理应参与恢复判定。 SHA256 `f039d5f8d1360bd0e87898c059b7cce68d7ec5d0fad31c9a0196a57a6425e45e`。
- [company-wiki/src/company_wiki/source_catalog/acquisition_journal.py:87](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_journal.py:87>) `AcquisitionJournal.record`：append/fsync 已存在；仅现有 outcome 日志不足推定每阶段提交。 SHA256 `104d73fdf68e7253d54258dd98fcc1e5bff09343b949e376ad1e199ccc9c6736`。
- [company-wiki/src/company_wiki/source_catalog/acquisition_service.py:76](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_service.py:76>) `SourceAcquisitionService.ensure`：成功与失败 journal 的实际时点。 SHA256 `017ca75c1efec6986af058c068db86bbf9fed5edd2bd8ede94fd96a1a8e7f8c7`。

**必读原证据**

- [audit_review/2026-09-18_real_company_skill_audit/runs/07_xiaomi_source_download_authorized/run.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/07_xiaomi_source_download_authorized/run.json>)： raw 已保存但任务失败的真实切口
- [../company-wiki/src/company_wiki/source_catalog/canonical_writer.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/canonical_writer.py>)： 整段 import 与 copy/sidecar 原子写入实现
- [../company-wiki/src/company_wiki/source_catalog/acquisition_journal.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/acquisition_journal.py>)： 损坏/半行与互斥语义

**只允许修改**

- CW:src/company_wiki/source_catalog/canonical_writer.py
- CW:src/company_wiki/source_catalog/acquisition_service.py
- CW:src/company_wiki/source_catalog/acquisition_journal.py
- CW:src/company_wiki/source_catalog/scanner.py（仅恢复状态）
- D-W02 指定的既有 store/migration 精确文件；隔离故障注入测试

**固定样本**

- 固定同一 source/request；受控 kill 点：staging 校验后、raw rename 后/sidecar 前、sidecar 后/scan 前、scan 部分提交后、qualified 后/返回前。
- 模拟异常与真正子进程终止分别留证，不能仅 raise 代替 crash；上游没有完成可保留明确 pending。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W02E-P1 / positive**：每一 kill 点独立 scratch；重启同一请求。
  预期：由持久事实选择首个未完成阶段；已成功 raw/sidecar 不重写，已有合法资产不重新下载；最终 exact resolve 与无中断相同。
- **W02E-N1 / negative**：raw 存在但持久 provenance/receipt 不足。
  预期：明确 blocked，保留 raw，不猜 sidecar 内容或捕获时间；不为了自动恢复降低门。
- **W02E-N2 / negative**：DB lock、半写 journal 尾行、旧进程 lease、identity 冲突分别注入。
  预期：按 D-W02 各自恢复/拒绝规则执行；不得通用 catch 后 continue 或一律删除锁。
- **W02E-N3 / negative**：raw/sidecar 在中断后被修改或政策 epoch 改变。
  预期：重新核验失败/重新资格审查；不复用旧完成 receipt。

**按序执行**

1. senior 先给出每边界的持久证据、合法恢复动作与禁止动作表；没有表不写 crash 代码。
2. 创建每 case 独立 catalog/root/worker_control(paused)，固定子进程 PID 与 barrier。
3. 先进行可控异常，再进行绑定 kill 点子进程终止；每次保存磁盘/DB/journal 状态后启动新进程。
4. 对比无中断 oracle，并核 count/bytes/request identity；恢复最后验证 paused 未变。

**失败停止与恢复界限**

- kill 只作用于 runner 记录的 scratch 子进程；不能根据进程名批量终止。
- 恢复过程若出现未知中间状态，保留现场停卡，不自动删 journal 或重下 raw；DDL 恢复仅隔离快照。

入口：`CMD-W03`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`crash-boundary-matrix.json`、`before-restart/`、`after-restart/`、`recovery-and-paused-proof.json`。

**退出判据**：每个已冻结边界或成功恢复，或给出可执行且不丢资产的阻断；不把 blocked 计为自动恢复成功。

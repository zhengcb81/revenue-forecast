本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-01-A — doctor 与实际扫描共用配置能力判断

parent：I-01；status：planned；owner：company-wiki 来源系统实施者。

依赖：I-00-A、I-00-B、I-00-D。设计前置：D-W01。证据目录：`execution_runs/I-01-A/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/scripts/config_doctor.py:23](<C:/Users/郑曾波/Projects/company-wiki/scripts/config_doctor.py:23>) `diagnose`：当前不读 runtime policy；_cross_repo_checks 硬编码 directory root 名称。 SHA256 `7351cec4084af50c70049b006a0522c672c79e97b08fc20a943a3d09f3ce1459`。
- [company-wiki/src/company_wiki/source_catalog/adapter_dispatch.py:36](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/adapter_dispatch.py:36>) `adapter_for`：缺 adapter/未注册/无实现均拒绝。 SHA256 `6a72e7c552d791f23cec595fe885dd79cfbb1cc4efc082d1acebb04cd4ffbdbe`。
- [company-wiki/src/company_wiki/source_catalog/scanner.py:855](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/scanner.py:855>) `_scan_catalog_impl`：adapter 声明或 v2 flag 均走 adapter。 SHA256 `f039d5f8d1360bd0e87898c059b7cce68d7ec5d0fad31c9a0196a57a6425e45e`。
- [company-wiki/src/company_wiki/source_catalog/service.py:142](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/service.py:142>) `SourceCatalog.scan`：默认从 snapshot 取 flag；dry-run 默认不同。 SHA256 `32b76e6d7f9879a2c7280f20180a8584c61ec11d706dbd70e3d019fd8cb48fa5`。
- [company-wiki/src/company_wiki/source_catalog/adapters/registry.py:10](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/adapters/registry.py:10>) `ADMISSION_PROFILES / REGISTERED_ADAPTERS`：generic_document_v1 注册但不在 scanner factory；read_only 能力须分清。 SHA256 `33524affc460a65af9d7d500d8e90f58b0b9d6f54c0686ba7a4d1e7dc6d07a79`。
- [company-wiki/config/source_catalog.yaml:1](<C:/Users/郑曾波/Projects/company-wiki/config/source_catalog.yaml:1>) `source_catalog.yaml`：仅复制并保持真实配置形状；生产原件禁改。 SHA256 `f9eb72a6c37c2dfeacf18a10df9b983dac104276efaf55b0a55b2c5c15f655df`。

**必读原证据**

- [.planning/2026-09-19-three-project-history-audit/reviews/wiki/readonly_diagnostics.json](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/wiki/readonly_diagnostics.json>)： doctor healthy 与实际 policy/配置组合；git 失败段不作历史证明
- [.planning/2026-09-19-three-project-history-audit/reviews/wiki/historical_git_readonly.json](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/wiki/historical_git_readonly.json>)： GP002 fixture 与同提交 production config 不同的证据
- [../company-wiki/tests/contract/test_gp002_scan_v2_wiring.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_gp002_scan_v2_wiring.py>)： 当前 forwarding 已接通，不重复修旧参数转发
- [../company-wiki/tests/test_config_doctor.py](<C:/Users/郑曾波/Projects/company-wiki/tests/test_config_doctor.py>)： 旧第五 root 拒绝断言需要按已冻结能力契约改为分类，不删测试

**只允许修改**

- CW:scripts/config_doctor.py
- CW:src/company_wiki/source_catalog/config.py（现有 loader）
- CW:src/company_wiki/source_catalog/adapter_dispatch.py
- CW:src/company_wiki/source_catalog/models.py
- CW:src/company_wiki/source_catalog/scanner.py（仅策略选择接线）
- CW:src/company_wiki/source_catalog/service.py（仅 scan 配置解析）
- 对应隔离测试；新增共享解析模块须 D-W01 给出确切路径；生产 YAML/policy 禁改

**固定样本**

- CFG-REAL：复制生产 YAML 与 runtime policy，所有路径重定位到 scratch，保持 root 名/缺字段/flag 形状。
- CFG-GOOD：高级 reviewer 核对布局后按 D-W01 修正副本；每根一份可识别 fixture。
- CFG-FIFTH：此前未命名 archive_extra，directory + 已支持 sidecar adapter，同一布局，read_only=true，无写目标。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W01-P1 / positive**：CFG-GOOD 经 diagnose 与 SourceCatalog.scan 同一解析结果。
  预期：各 root 路由/adapter/profile/version/strategy 完全相同；每份可识别目标可按准确身份 resolve。
- **W01-P2 / positive**：CFG-FIFTH 加入 CFG-GOOD。
  预期：不因 root 名陌生被拒；只扫描适配器支持的 raw，不把 .source.json 当独立原件。
- **W01-N1 / negative**：CFG-REAL 保持三根 adapter_id 缺失与 true/true/true/false flags。
  预期：doctor 提前列出每个不兼容 root；正式 scan 不能静默退 legacy 或报告全部合格。
- **W01-N2 / negative**：逐个独立变异：unknown adapter、注册但无 scanner 实现、超版本、unknown profile。
  预期：分别稳定拒绝；不能为了用第五 root 把所有 directory 都放行。
- **W01-N3 / negative**：read_only root 设 canonical_write_target，及未批准半激活组合。
  预期：写能力/激活错误可解释；原件、配置、policy 没有副作用。

**按序执行**

1. 读取必读证据和绑定的当前源码，冻结 D-W01；把 CFG-REAL 与 CFG-GOOD 分开，不覆盖原样副本。
2. 先跑 doctor API 与真实 scan 的修改前对照，记录每根结果，不拿 dry_run 代替真实隔离写库。
3. 抽取/接入同一 effective 配置判断；不写第二份 allowlist，不硬编码新增 root 名。
4. 保持 GP002、F-BAR-10 已有行为；运行五组正反例，再从副本配置走 service 实际扫描和 resolver。
5. 将每 root 的配置指纹、解析结果、scan 回执和目标 resolve 做一一对应；由独立 reviewer 签范围。

**失败停止与恢复界限**

- 不能证明 Dropbox 当前布局适配哪一已实现 adapter 时停止该 root 映射，不凭文件后缀选 adapter。
- 发现生产路径、需要翻 production flag 或现存用户改动冲突则停止；恢复只撤本卡在隔离代码/config 的差异。

入口：`CMD-W01`、`CMD-W02`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`effective-config.before.json`、`effective-config.after.json`、`per-root-scan-and-resolve.json`、`config-copy-hashes.json`。

**退出判据**：配置负例被预检拦住，合法额外同构 root 被实扫/resolve 证明；不外推未知布局/真实部署。

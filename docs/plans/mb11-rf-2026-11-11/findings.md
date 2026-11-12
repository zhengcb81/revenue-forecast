# 发现

- B37 是分叉候选，不能整体 fast-forward 或 cherry-pick 其完整树；git diff main..candidate 涉及 628 文件、约 35k 行增加。
- 卡片指定的产品差额是 19 路径；其中 4 个完全相同，9 个需逐 hunk 适配，6 个主线缺失。
- 主要风险在 compare/scope/subject/publication DTO 的一致性；不能恢复直接读 CWP 私有 SQLite 的旧链路。
- 本工作树使用 RF 自有分支 codex/mb11-rf，与 RF 主线和既有 release 工区隔离。


## compare合同接收中的新发现

- 基线缺少 report_catalog_compare.py；加入该模块和固定 compare CLI 后，B37 新增合同测试51 passed/1 skip，证明主体实现可使用当前 ReportCatalog owner readers，而不需覆盖当前 catalog 模块。
- 原候选有 MAX_COMPARED_ROWS=512 与 MAX_OUTPUT_BYTES=1MiB 两个固定结果门槛，且无配置/owner工作预算依据。它们可能拒绝完整合法比较结果；已删除并补600期、长locator、>1MiB CLI完整JSON回归。
- MAX_METRICS=32对当前仅支持的revenue一项及重复项校验没有约束效用，已删除冗余计数上限。64KiB输入上限仍作为小型请求入口的资源保护；有效的四字段请求自身受字段和值形状约束。
- Decimal 4,096位/8,192精度限制用于限定精确算术资源消耗；尚未证明会触及有效报告输入，暂不在这次compare端口修改中动它。

## B37部署与来源测试调查（2026-11-11）

- 比较公开API已由 `e060a8607` 进入RF main；PWF记录提交为 `33d880826`。此前主线比较/job/recovery/source-port回归为102 passed、2 skipped，push smoke为12 passed；本轮新增的更完整组合回归为171 passed、1 skipped。
- 候选publication-source owner实现与当前main逐字节相同；保留它的合成回归即可，不复制生产实现。
- 初版部署测试错误要求 `catalog.jsonl.lock` 不存在；RF的 `OwnerFileLock` 会留下稳定锁载体并释放OS锁。修正后的测试验证owner文件集合不变且锁未持有，没有更改锁实现。
- Windows长 `--basetemp` 导致4个既有RF-job测试创建深层临时文件失败；相同测试换用短临时根后通过。这是测试临时路径过长，不是RF-job缺陷。
- scope/subject/verified-comparison候选不能原样并入：它导入或调用 `_clean_id`、`_json`、`_assert_pathless`、`_compare_pair`、`_identity_reasons` 等私有符号，直接访问catalog私有索引/读取器，并绕过ReportCatalog公开reader；还固定IFRS、12月31日财年和单分部结构，设置无预算依据的证据/台账/输出行数与字节上限；候选CLI差异会删除已发布的 `import-rf-job` 命令和root支持。后续需先定义增量公开合同，并覆盖多会计准则、财年、多分部，同时保留全部job能力。
- 首轮scope/publication候选测试为122 passed、1 skipped、5 failed：3项因scope命令或wire合同缺失，2项是锁载体断言错误。后两项已在保留的部署测试中修好；scope部分仍延期，不能记为通过。

## B2 公开 scope/subject/verified-compare 设计与发现（2026-11-12）

- 候选的 `scope_binding`/`subject_resolver` 直接导入 `_clean_id`、`_json`、`_index`、`_exact_report`、`_public_report`、`_read_json`、`_compare_pair`、`_identity_reasons` 等私有符号，并依赖 StockWiki 私有 CLI/DB。B2 不复制该实现：RF 侧只定义公开 DTO/reader，StockWiki 通过可注入的公开 subject port 消费；本地用冻结公开 fixture 推进，真实组合留给 ROOT。
- scope 绑定沿公开字段显式携带 `accounting_basis`、`fiscal_year_end`、`segment_ids`、`covered_coordinates`（含 period_start/period_end/scenario/basis）、`analysis_subject_id/revision`、`currency/unit/scale/basis`、来源见证。FY 坐标的 `period_end` 月日必须等于声明的财年结束日；不再默认 IFRS、12-31、单分部或 FY-only。
- 来源见证经 `ReportCatalog.get_source_snapshot` 公开 reader 逐条核对 source_id/content_sha256/字节 SHA/excerpt 包含关系；缺快照、缺必需角色、重复见证、摘录不在精确捕获源分别给出稳定错误码。
- verified-compare 不导入 compare 私有 helper，也不复制 Decimal 差值算法：先取公开 `compare_reports` 原始结果，再用仅公开 reader 的 effective-subject adapter 取一次生效视图；响应中的 left/right 仍是原始规范行，只有 delta/comparable/reasons 受当前 scope 影响。
- 输出不设行数/字节上限；CLI 只继承既有 compare CLI 的 64KiB 请求输入预算。长摘录 >1MiB 的完整响应和 600 期结果均有回归。
- 既有缺口（非本卡）：`tests/test_single_owner_guard.py` 的 subprocess allowlist 在 HEAD 基线就缺 `report_catalog_identity_resolver.py`、`report_catalog_rf_job_import.py`、`report_catalog_source_alias.py`、`rf_job_facade.py` 四项；新模块不含 subprocess。修复需要为这4个既有客户端补各自合同测试或调整该守卫的归属，交 ROOT 处理，不在 B2 里扩 allowlist 换绿。
- `tests/test_module_boundary_closure.py` 在本工区不存在（卡片证明库提到的文件名），已按“开工核对后记入 PWF”处理；不当作产品失败，也不新建同名占位测试。

## B2 独立审查后的修复（2026-11-12）

- 首轮审查（绑定 `940e05b4`）PASS，但指出 append 证据误用 64KiB compare 请求预算。owner 已有 `MAX_ARTIFACT_BYTES` 是管理产物的既有预算，append 路径改用该预算；`compare` 请求仍保持已发布的 64KiB 预算。两者都不是新造的任意截断。
- scope 状态从 `artifacts/report_catalog/` 移到 `artifacts/report_scope/`：即使部署把 owner 工作区作为 data root，也不写 catalog owner 保留目录。
- 补齐“省略 accounting_basis/fiscal_year_end/segment_ids/covered_coordinates/source_witnesses/verified_at 即拒绝”、财年日历不匹配、锚点不匹配、截断行、伪造行哈希、锁占用、resolver 身份不匹配等负例；新增 FY 空日期正例并明确其为显式 FY 粒度（与 compare 的 `period_kind=FY` 空日期语义一致）。新增 state 路径回归，锁定 `artifacts/report_scope/verified_scope_bindings.jsonl`，不再回到 catalog owner 目录。
- 仍未覆盖：`scope_comparison_shape_mismatch` 只在两次公开读返回不同形状时触发，现有假件不易稳定构造；真实 `ReportCatalog` 的 captured-markdown 快照未建模。均列为残余风险，不冒充已测。
- 证据范围：组合回归是**选定 311 个受影响用例**（B2 套件 + 卡片点名回归 + 两个守卫），不是整个 `tests/` 树；本工区 `pytest tests` 有既有收集失败（`test_zr1008` 导入缺失的 `test_zr709`，`test_ca204` 亦报错），属既有问题，交 ROOT，不用“全绿”措辞。
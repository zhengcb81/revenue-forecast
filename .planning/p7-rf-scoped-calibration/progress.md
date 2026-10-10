# Progress — P7-RF

2026-10-10T21:08:46.345975+00:00 MAIN仅初始化独立工作目录、PWF和施工卡同SHA副本；未实施源码、未运行责任RED/GREEN/E2E，未调用项目外部provider/model，新增费用0。

启动pin见IMPLEMENTATION_CARD.md。下一步由独立harness执行M1；交接写本PWF内HANDOFF.md/handoff.json，绝对路径回报给用户和MAIN。不要改中央汇总。

启动准备实查：Windows PowerShell 5.1 的解析器因缺 System.IO.Path.IsPathFullyQualified 返回空；已有PowerShell 7实际解析到本卡PWF。施工卡启动命令已明确使用该7运行时，未修改安装技能或项目源码。

2026-10-10 M1（独立harness）：基线 test_research_evidence_roles 11 passed。三反例复现+正控确认（attempts/m1/repro.py/.log）。新增 RED：tests/test_scoped_calibration_support.py（5 failed=责任反例, 2 passed=正控, exit 1, attempts/m1/red_test_scoped_calibration_support.log）；tests/test_research_support_diagnostics.py（5 failed=CLI缺失, 1 passed=负控fail-closed, exit 1, attempts/m1/red_test_research_support_diagnostics.log）。夹具 tests/fixtures/scoped_calibration_support/{valid_calibrated,unrelated_conversion_scope,unrelated_calibration_scope,no_research,partial_driver_calibration}.json 生成（partial 用 unit_sales 双driver, validate+compute OK, low2026=140=90+50）。CLI样例已冻结于 findings.md。零外部 provider/model 调用。

2026-10-10 M2（独立harness）：实现完成。evidence_roles._calibration 消费 binding_status + native scope 绑定（3类新reasons，独立端点不加DAG要求）；native_dependencies 抽 segment_roots；新CLI scripts/research_support_diagnostics.py（economic-support-diagnostics/1，只读）。SKILL_VERSION 4.2.0→4.2.1 + CHANGELOG 4.2.1 节；SKILL.md 3处定点文案；references/evidence-role-calibration.md 更新 + 新 references/economic-support-diagnostics.md。责任GREEN：test_scoped_calibration_support 8 passed（含 strong recompute 篡改拒绝、stress不变、跨年/跨segment不自动支持）、test_research_support_diagnostics 6 passed、既有 test_research_evidence_roles 11 passed。静态：ruff 6文件 clean，mypy 2文件 clean。
版本归因：本分支已知 baseline-diff = 5 version-pin 失败 + test_rf_coverage_report 4 个下游ERROR（其子进程要求 test_schema_compatibility exit 0）。MAIN_INTEGRATION_PATCH.patch（本PWF）trial 于本树 88 passed（5 pin 文件+registry+rf_coverage 全绿，回退后失败复现）；曾因 patch 文件混入 CR 字节失效，已重新生成（0 CR，roundtrip + base worktree --check 均过）。
全量差分结论：ca202 c1_samples 在干净 base 即失败（stash 双向验证）；zr806/zr1004/zr709/ca302/fc1307a 等 journey/canary/vendored 测试在 base 树不同时刻同样失败/通过翻转（同一绝对 sibling 路径随并行会话波动）——环境竞态非本卡改动；compatibility_manifest/p5/fc1101 等 "only in base" 为 base worktree git 状态依赖。零外部 provider/model 调用。
下一步 M3：TEMP 离线公共E2E（正负控、REVENUE_PUBLICATION_REGISTRY 指向 owned TEMP、诊断CLI一致性）、恢复、独立agent复核、commit/push + HANDOFF。

2026-10-10 M3 E2E（独立harness）：自有 TEMP（%TEMP%/p7-rf-scoped-calibration/m3，脚本 m3_e2e.py 在 TEMP 根）真实 CLI 正负控，ALL_PASS exit 0（attempts/m3_e2e.log，含 SHA 证据）。正控：build_auditable_case.py + run_target_measurement_e2e.py 真实 argv（同参考测试配方 build_revenue_source_record_from_verified_read），forecast.json referenced_range、reasons空、公式值100/110/120、engine 4.2.1、stable-fsum/1、snapshot 存在、markdown 渲染校准、magnitude=3输出、诊断CLI SegmentA FY2026 supported×3 / FY2027 unsupported、input_sha256 一致。负控（CE1 转换scope换无关业务）：同一管线 unverified + conversion_observation_unverified_scope:<pid>:<claim> 原因、magnitude 空、consolidated_forecast 与 confidence.score 与正控完全一致（诊断不改算术）、诊断CLI unsupported 且原因含参数/claim ID。publications.jsonl 落在 m3/{pos,neg}/native/ 内（owned 根内，无生产 registry 写；e2e 工具自身 override 亦在 owned 内）。正负 input.json SHA 相同 b515d368…，research.json 不同（突变仅 research）。外部 provider/model 调用 0、费用 0。等待独立 agent 复核两个不变量后提交。

2026-10-10 M3 完成（独立harness）：独立agent复核两不变量+API形状+3对抗探针全PASS（attempts/m3/independent_review.md）；TEMP全清理（m1/m2/m3、p7-rf-review、基线worktree），证据先固化attempts/；交付commit 05aa2661（hooks ruff/mypy/guard全过），HANDOFF.md+handoff.json（schema验证过）就绪并另行commit；分支push见HANDOFF §6。外部provider/model调用0、费用0。

2026-10-10 M3 push处置：normal git push 被本地 pre-push 门拦截（行为门 258 passed/2 failed，仅 test_data_contract.py:463 与 test_schema_compatibility.py:28 两个 MAIN-owned version-pin；ruff/mypy 门全绿）。本卡明文禁止 no-verify（不采用 M3-FLOW 先例的 --no-verify+披露推送），分支保留本地提交；门日志固化 attempts/m3/pre_push_gate_local.log（9721807a…），根因消除=MAIN patch（trial 88 passed 含两文件）。HANDOFF.md §2/§6 与 handoff.json ci.note 已如实更新。CI not_triggered，remote 无本分支。

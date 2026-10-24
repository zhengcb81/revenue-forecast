# W14-RF-CLEAN-CHAIN 交接报告

**范围声明**：本包是工程交付——"合成夹具的真实代码跨仓 E2E"。三仓生产代码从冻结 Git 对象部署后在自有 scratch 执行，链路真实（公共 CLI/SourceRef/真实子进程），但**不包含真实下载（S1 未跑）与真实公司分析**；真实来源/公司内容验收仍归 ROOT。

## 基本信息

| 项 | 值 |
|---|---|
| PLAN_ID | w14-rf-clean-chain-2026-10-24 |
| 工作目录 | C:/Users/郑曾波/Projects/revenue-forecast-w14-clean-chain（sparse，省略 .planning） |
| 分支 | codex/w14-rf-clean-chain-20261024 |
| 源码基线 (code_base_commit) | 599d17b89d8baee42ce203747496731ace2d0148 |
| start_head | 9196ef1c（bootstrap/PWF 就绪） |
| 实现提交（被审代码 reviewed_code_commit） | cc10f053 |
| 冻结输入 | CWP a31300a70215319e6bcf3a03d32b2882bdf1aeaa；FF 7f6a9268da90281c28b55d437860bc2d2b60106e；RF 599d17b89d8baee42ce203747496731ace2d0148 |

## 逐需求结论（E01–E08）

| ID | 结论 | 证据（路径/定位） |
|---|---|---|
| E01 默认离线、离线场景全执行 | PASS | `tests/test_w14_portable_chain_runner.py::test_e01_default_offline_full_suite_executes`（默认无 --live 即 never；S2/S3/S5/S6/S4 全 pass 无 skip）；`::test_e01_s1_intentional_skip_and_retired_auto`（S1 skip=live_gate_never；auto/env 退役公告且不联网） |
| E02 冻结对象部署+溯源+反控 | PASS | runner `--rf/-cwp/-ff-repo/commit`（e2e/run_cross_repo_chain_e2e.py main）；`replay_support/deploy.py`（git archive→scratch、provenance、DeployError=environment_unavailable→exit 3）；`::test_missing_commit_is_environment_unavailable`；import 探针 + 45 子进程全部 `deploy/cwp/src`（provenance.json/summary.child_processes）；decoy PYTHONPATH 反控（E01/E07 测试） |
| E03 真实三进程以上+公共链注册/读取 | PASS | 每回放 45 个子进程、S2 记录 6 个直接子进程 PID（summary.processes）；注册走公共 `company_wiki.source_catalog.cli scan` 子进程（fixtures.build_lake）；FF/RF/CWP 全为真实子进程，无 mock（runner/tests 无 monkeypatch） |
| E04 PDF+TXT 实际消费、错误保真 | PASS | `s2/pdf_record.json`、`s2/txt_record.json`（source_ref.content_sha256=夹具 SHA；TXT manifest fiscal_period=Q3 证明实际读取）；`wrong_period_refusal.json`（rc=3，no_local_match 原因保留，无审查门字样）；`empty_identity_refusal.json`（rc=2 request_error 原文）；S5/S6 结构化拒绝；夹具 1027B 真 PDF（pypdf/pymupdf 双解析）+797B 中文 TXT |
| E05 复用零计数、断网、key 清洗 | PASS | s3/counters.json（provider delta=0、catalog delta=0、lake tree hash 不变）；netguard socket 级阻断+记录（`test_netguard_blocks_and_records_a_real_attempt` 实测 BLOCKED+记录）；child_env.json 仅记 key 名（10 个被清洗），全证据文件无 key 值 |
| E06 不删用户目录、独占 attempt | PASS | replay_support/cleanup.py（attempt-<stamp>-<pid>-<seq>；owned_path 边界拒绝）；`test_w14_portable_chain_cleanup.py` 5/5；`test_e06_work_root_and_evidence_history_preserved`（sentinel/历史 evidence 保持）；失败路径清理见产品失败测试（S4 pass） |
| E07 双目录语义一致 | PASS | `test_e07_two_roots_same_semantics_one_with_unicode_and_spaces` + 交付双回放（replay-first 平凡根 / replay-second 中文空格根+外部 cwd+污染 PYTHONPATH），`summary_semantic.json` 完全相等（显式排除 PID/临时路径/时长） |
| E08 模块化、无特判、行为测试替代 pin | PASS | e2e/replay_support 五模块；grep 无公司名/个人目录/旧 pin SHA 特判（审查 agent 复核）；旧 CODE_PINS/preflight 删除，产品行为差异由 `test_real_product_failure_makes_suite_nonzero`（历史 commit 3b00b9384→exit 1）与夹具篡改测试覆盖；历史收据（delivery/w09 等）未触碰 |

## 实际测试命令与结果

| 命令 | 退出码 | 结果 | 时间 |
|---|---|---|---|
| `python -m pytest -q --tb=short -p no:cacheprovider tests/test_cross_repo_chain_e2e.py tests/test_w14_portable_chain_runner.py tests/test_w14_portable_chain_cleanup.py` | 0 | 17 passed | 426.67s（2026-10-24） |
| `python -m ruff check e2e/run_cross_repo_chain_e2e.py e2e/replay_support tests/test_cross_repo_chain_e2e.py tests/test_w14_portable_chain_runner.py tests/test_w14_portable_chain_cleanup.py` | 0 | All checks passed | <1s |
| `python tools/pre_push_gate.py` | 0 | 595 passed, 1 skipped, 36 subtests；pre-push/CI checks GREEN | 98.58s |

直接入口双目录回放（卡片示例命令，最终代码）：
- replay-first（平凡绝对根）：exit 0，S2/S3/S5/S6/S4 全 PASS，92.2s → `delivery/w14/replay-first/attempt-20261024-121507Z-76d0-001`
- replay-second（中文+空格绝对根，工区外部 cwd 启动）：exit 0，全 PASS，81.7s → `delivery/w14/replay-second/attempt-20261024-121658Z-76bc-001`
- 两回放 `summary_semantic.json` 完全相等；汇总见 `delivery/w14/replay-receipts.json`（每场景 status/PID/检查数、SourceRef/SHA/locator、git 版本、provider delta、清理证明）。

## RED 基线（改造前实测）

`tests/test_cross_repo_chain_e2e.py` 旧版在基线上 2 failed（runner 因 4 个源码 pin 全漂移直接 exit 2 "binding drift"），非 skip——本包改造的起点证据。

## 独立审查

<!-- REVIEW_SECTION_PENDING: 由独立审查 agent 的报告填充 -->

## 清理与恢复

- 开发期 scratch（`.test-scratch/`、外部回放目录）已删除；删除前各回放的 S4 已证明 attempt 目录移除、work-root 恢复初始、evidence 完整（各 attempt 的 s4/cleanup.json）。
- 三仓源工作区零写入（部署仅 `git archive` 读对象；S4 记录 HEAD 前后一致）。
- 生产湖/生产配置/密钥零访问；API key 仅在子进程 env 副本按名清洗，从未输出。

## 新增体量

- 新增源码+测试+夹具：约 110KB（fixture 3.8KB）；delivery/w14 收据约 380KB（<16MiB 目标；含开发期两次早期 attempt 历史与最终双回放）。

## 已知边界 / ROOT 下一步

1. S1 真实下载未跑（卡明确本卡不跑）；force 路径保留实现+环境缺失时 environment_unavailable。
2. E2E_DESIGN.md 旧文档未更新（不在本卡写范围）；建议 ROOT 在并线时补一句指向新 runner 文档串。
3. 历史产品失败测试依赖 RF 仓保留 `3b00b9384` 对象（浅克隆会缺——已在测试环境门中按 commit 存在性处理，缺则 skip 并注明）。
4. 真实公司/真实来源质量仍由 ROOT 验收；本包不主张任何业务结论。

# W14-RF-CLEAN-CHAIN 交接报告

**范围声明**：本包是工程交付——"**合成夹具的真实代码跨仓 E2E**"。三仓生产代码从冻结 Git 对象部署到自有 scratch 后执行，链路真实（公共 CLI/SourceRef/真实子进程），但**不包含真实下载（S1 未跑）与真实公司分析**；真实来源/公司内容验收仍归 ROOT。

## 基本信息

| 项 | 值 |
|---|---|
| PLAN_ID | w14-rf-clean-chain-2026-10-24 |
| 工作目录 | C:/Users/郑曾波/Projects/revenue-forecast-w14-clean-chain（sparse，省略 .planning） |
| 分支 | codex/w14-rf-clean-chain-20261024 |
| 源码基线 (code_base_commit) | 599d17b89d8baee42ce203747496731ace2d0148 |
| start_head | 9196ef1c（bootstrap/PWF 就绪） |
| reviewed_code_commit（被审代码） | 3bc0508e2a1ae97df2d0d67458fe288f677030a5 |
| 最终独立审查 | **APPROVE**（3 轮：3 并行初审→delta 补审→义务关闭确认，见 [review.md](review.md)/[review.json](review.json)） |
| 文件级绑定 | [reviewed_sha256.json](reviewed_sha256.json)（13 个被审产品/测试/夹具文件 SHA-256） |
| 冻结输入 | RF `599d17b89d8baee42ce203747496731ace2d0148`；CWP `a31300a70215319e6bcf3a03d32b2882bdf1aeaa`；FF `7f6a9268da90281c28b55d437860bc2d2b60106e` |

## 逐需求结论（E01–E08，全部 PASS；证据为实跑收据）

| ID | 结论 | 证据 |
|---|---|---|
| E01 默认离线、离线场景全执行 | PASS | `test_e01_default_offline_full_suite_executes`（默认无 --live 即 never；S2/S3/S5/S6/S4 全 pass 无 skip）；`test_e01_s1_intentional_skip_and_retired_auto`（S1 skip=live_gate_never；auto/env 退役且不联网）；`compute_exit_code` 单测（非 S1 场景 skip→exit 1） |
| E02 冻结部署+溯源+反控 | PASS | 六个新必填 repo/commit 参数；`replay_support/deploy.py` git-archive 部署+环境异常具名 environment_unavailable(exit 3)；`test_missing_commit_is_environment_unavailable`（statuses=={} 且早退清理）；import 探针 under_frozen_deployment；45 子进程全部 `company_wiki_file` 在 deploy/cwp/src 且全部 .py argv0 在三仓部署根内；decoy PYTHONPATH 反控 |
| E03 公共链+≥3 真实进程 | PASS | 公共 `source_catalog.cli scan` 注册（scan PID 落收据）；RF→FF→CWP `-m` 孙进程 needle 断言（source_preparation.py/fetch_filing.py/source_reader_cli/source_catalog）；S2 直接子进程 PID 6 个；无任何 mock/monkeypatch（审查 grep 零命中） |
| E04 夹具真实消费+错误保真 | PASS | `s2/pdf_record.json`（source_ref/capture SHA=夹具 SHA，locator=1，reuse 零下载）；`s2/txt_record.json`（source_manifest fiscal_period=Q3 证明实际读取）；wrong_period rc=3 `no_local_match` 原因保留、无审查门字样；empty_identity rc=2 `company_query must be non-empty`；S5 `not_found`、S6 `identity_error`（未知+歧义别名）；夹具 1027B 真 PDF（pypdf+pymupdf 双解析）+797B 中文 TXT+manifest 单一事实源，`.gitattributes * -text` |
| E05 复用零计数+断网+key 清洗 | PASS | s3/counters.json provider delta=0、catalog 行 delta={} 且内容级 `catalog_content_sha` 相等、lake 树 hash 不变；netguard socket 层 connect/connect_ex/getaddrinfo/sendto 非回环阻断+记录（正控测试实测 BLOCKED+1 记录，回环放行）；provider spy 正控（真实回环 HTTP 触发事件+安装标记接线）；10 个 key 只记名、全收据 .json/.txt 扫描 0 命中；路径重定向变量清洗字段断言 |
| E06 不删调用方目录+独占 attempt | PASS | attempt-<stamp>-<pid>-<seq> 独占子目录；work/evidence 重叠 exit 2（分配前）；sentinel+历史收据保持专测；全部终态路径清理（S4 或 _finish→early_cleanup.json，回归断言）；cleanup 报告携带全量前后 sha inventory+diff；`s4/restore.json` 夹具前后哈希 |
| E07 双目录语义一致 | PASS | `test_e07_two_roots_same_semantics_one_with_unicode_and_spaces`（中文空格根+外部 cwd+污染 PYTHONPATH）；交付双回放 summary_semantic.json 字节相等（replay-first 平凡根 / replay-second 中文空格根） |
| E08 模块化+无特判+行为测试替代 pin | PASS | e2e/replay_support 五模块（~1000 行，runner 净减 1469 行）；新代码 grep 无公司名/个人目录/旧 pin SHA；CODE_PINS/preflight 删除；行为替代=历史产品 `3b00b9384`→exit 1 且钉住预期失败名集、夹具篡改→exit 1+statuses=={}；历史收据（w09 等）零改动 |

## 实际测试命令与退出码（最终代码 3bc0508e）

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pytest -q --tb=short -p no:cacheprovider tests/test_cross_repo_chain_e2e.py tests/test_w14_portable_chain_runner.py tests/test_w14_portable_chain_cleanup.py` | 0 | **22 passed**（1381.00s，本机争用期；此前同套件最快 408s） |
| `python -m ruff check e2e/run_cross_repo_chain_e2e.py e2e/replay_support tests/test_cross_repo_chain_e2e.py tests/test_w14_portable_chain_runner.py tests/test_w14_portable_chain_cleanup.py` | 0 | All checks passed |
| `python tools/pre_push_gate.py` | 0 | **595 passed, 1 skipped, 36 subtests；GREEN**（98.04s，独立重跑） |

RED 基线（改造前实测）：旧 `tests/test_cross_repo_chain_e2e.py` 2 failed——runner 因 4 个源码 pin 全漂移直接 exit 2 "binding drift"。

## 双目录实际回放收据（最终代码）

- **replay-first**（平凡绝对根，工区内 cwd）：`delivery/w14/replay-first/attempt-20261024-160349Z-204c-001`，exit 0，S2/S3/S5/S6/S4 全 PASS，55.4s。
- **replay-second**（`C:/Users/郑曾波/Projects/回放目录 W14 第二次/...` 中文+空格根，工区外部 cwd 启动）：`delivery/w14/replay-second/attempt-20261024-161640Z-416c-001`，exit 0，全 PASS，82.3s。
- 两者 `summary_semantic.json` 完全相等；每场景 status/PID/检查数、SourceRef/SHA/locator、三仓 git 版本、45 子进程、guard 安装标记、`production_writes{measured,count:0,verbs:[archive,rev-parse,status]}`、0 网络尝试、清理证明汇总于 [replay-receipts.json](replay-receipts.json)。
- 两目录内更早的 attempt（replay-first 6 个中的 5 个、replay-second 2 个中的 1 个）为开发期/中间版本历史收据，按"不覆盖历史"规则原样保留；其中 `attempt-20261024-101245Z-4da0` 为中断残留（无 summary），`154833Z-1f20-001` 为 S4 归因修正前的失败实录。

## 生产写入与外部扰动（如实记录）

- 本运行**可归因写入=0**：`production_writes` 由本进程 git 动词日志实测（仅 archive/rev-parse/status，写动词 0），S4+收据测试双向断言；全仓代码审定无绕过该日志的源仓写路径。
- 三仓为**共享实时工作树**：窗口内观测到外部并行会话编辑跟踪文件与 CWP HEAD 前进（3bcfc202→4e593c71），以 `source_repos_observed`/`source_repo_heads.json` 观测收据披露，不归因于本运行（复审判定合法改判）。

## 清理与恢复

- 每次运行仅删自有 attempt 目录；调用方 work-root sentinel/历史 evidence/原始资料保持（集成+单元双覆盖）；成功/失败/timeout/启动异常统一清理路径均有回归断言；删除前绝对路径边界校验拒绝越界。
- 开发期 scratch（`.test-scratch/`、外部回放目录）已全部删除。
- 三仓源工作区零写入（动词日志+观测收据）；生产湖/生产配置/密钥零访问；API key 仅在子进程 env 副本按名清洗，从未输出；0 模型调用/0 下载。

## 新增体量

- delivery/w14 全部收据 963,523B；被审代码+测试+夹具约 110KB（夹具 3.8KB）；单次 scratch 峰值约 7MB（attempt 清理）。**< 16MiB 目标**；raw_copies=0。

## 已知边界 / ROOT 下一步

1. **S1 真实下载未跑**（卡明确本卡不跑）；force 路径保留实现，缺工具时 environment_unavailable。生产投资结论/付费摘要不属本包。
2. **离线阻断为 judged 子进程 socket 层**：connect/connect_ex/getaddrinfo/sendto 非回环被阻断+记录；绕过面：子进程再外挂二进制（curl 等）、`gethostbyname/gethostbyname_ex` 原生解析。本批链路实测 0 尝试。
3. **收据绑定语义**：回放收据 `runner_code_sha256`/`final_code_commit=83926eca` 记录"产生收据的代码"；其后 3bc0508e 仅改失败路径+guard 边角+测试（成功路径语义零变化），收据经补审确认仍有效。
4. **共享实时工作树**：外部并发编辑/提交会出现在观测收据中（本包如实披露）；如需绝对干净窗口，ROOT 并线时择静默时段重放。
5. sendto(flags,address) 修复无正向单测（NIT）；`run_cmd` 超时不杀进程树孙进程（NIT）；空 `--scenarios ""` 运行零场景 exit 0（先于本包行为）；语义投影当前按布尔 check 比较（注释已澄清）。
6. `e2e/E2E_DESIGN.md` 旧文档未更新（不在本卡写范围）——建议 ROOT 并线时补一句指向新 runner 文档串。
7. 历史产品失败测试依赖 RF 仓保留 `3b00b9384` 对象；浅克隆缺对象时按环境 skip（已实现守卫）。
8. 本机争用曾使 gate 内部 pytest 触发 300s 硬超时（环境问题单列）；独立重跑 GREEN 为最终记录。
9. 真实公司/真实来源质量仍由 ROOT 验收；本包不主张任何业务结论。

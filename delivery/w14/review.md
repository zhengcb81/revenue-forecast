# W14-RF-CLEAN-CHAIN 独立审查报告

**审查性质**：工程交付独立审查（非业务/预测内容审查）。全部审查由未参与实现的独立 agent 执行；实现者未自评。绑定代码：`reviewed_code_commit = 3bc0508e2a1ae97df2d0d67458fe288f677030a5`（文件级 SHA-256 见 [reviewed_sha256.json](reviewed_sha256.json)）。

## 轮次一：三并行独立审查（实现完成后，基于 b522c68d）

首个单体审查 agent 因 provider 网络失败两次后，按用户指示拆为三个并行小任务：

| 角色 | 范围 | 实际执行 | 结论 |
|---|---|---|---|
| A. 静态审查 | E01–E08 逐条映射、禁止特判 grep、参数兼容、模块化、收据字节抽查 | 读卡+接口+全 diff（9196ef1c..b522c68d）+全部被改文件；git/grep；收据 SHA 重算三方对账；ruff 复跑 | **REQUEST_CHANGES**（F1–F18，4 MAJOR） |
| B. 运行时重放核验 | 全新 scratch 独立重放 + 证据逐字段核验 + 清理落盘验证 | 独立命令重放（exit 0，S2/S3/S5/S6/S4 全 pass，45 子进程零越界）；S1-only（skip=live_gate_never，零网络）；语义投影与交付收据 sha256 字节级相等；10 个真实 key 值对 60 个收据文件扫描 0 命中 | **APPROVE** |
| C. 反掩盖审查 | 真实调用链（无 mock）、空转断言狩猎、退出码映射、清理安全、语义投影、EOL | 逐段追踪 RF→FF→CWP 调用链与 PYTHONPATH；mock/monkeypatch grep 零命中；EOL `git check-attr` 实证；发现 spy 无正控、work/evidence 重叠可删收据等 8 项 | **REQUEST_CHANGES**（2 MAJOR + 4 MINOR/NIT） |

### 轮次一发现（去重合并）与关闭证据

全部内部发现已修复，修复分布于 `62b62fa9`（修复批，12 文件 +683/−163）、`83926eca`（S4 归因）、`ea76a058`（收据按最终代码重生成）、`3bc0508e`（终审附带义务）。完整逐条映射见 `docs/plans/w14-rf-clean-chain-2026-10-24/findings.md` 的"C节点独立审查发现与修复"节。要点：

- **F1（收据夹具 SHA 手写错误）**→ 收据改为按 manifest 脚本派生 + `test_delivery_receipt_fixture_shas_match_manifest` 永久钉住；复审三方对账 True。
- **F2/F8（production_writes 硬编码）**→ 改为本进程 git 动词日志实测（`archive/rev-parse/status`，写动词数恒 0）+ 前后工作树观测收据；复审 grep 证明无绕过日志的写源仓路径，断言含正向 `archive` 存在性不可空。
- **F3（清理前后 hash 未落盘）**→ cleanup 报告携带全量 sha inventory + diff 字段；`s4/restore.json` 落夹具前后哈希。
- **A1（spy 无正控+docstring 谎称 read 计数）**→ sitecustomize 每子进程安装标记（真实接线返回值）；`test_provider_counter_spy_fires_on_real_loopback_request` 真实回环请求触发 provider 事件；docstring 更正。
- **A2（work/evidence 重叠可删收据）**→ 分配前 exit 2 拒绝 + 专测。
- 其余 F5–F18/C 项 3/4/5/6/7/8：均按 findings.md 逐条修复（异常包装、argv 断言、DNS/sendto 拦截、路径变量清洗、早退清理、探针测试重写、死代码删除、离线 skip 非零、runner SHA、scan PID、cwd、.txt key 扫描、内容级 catalog hash、失败名钉集），复审逐条 **CLOSED**。

### 关键改判（S4 HEAD 归因，复审判定"合法重归因，非削弱断言"）

三仓工作树为**共享实时仓**：审查期间实测外部并行会话在 CWP 编辑跟踪文件（`.tmp-m3-r6-focused/`、` M tests/unit/...`）并中途提交（HEAD 3bcfc202→4e593c71）。共享仓的 HEAD 相等性不可归因于本运行（外部原因假失败=flaky=无断言）。替代为可归因双向钳制：S4 断言本进程零写 git 动词 + 收据级测试断言最终动词全集⊆只读且含 archive + HEAD/porcelain 前后快照作为观测收据披露外部活动 + runner_code_sha256 绑定被审代码。

## 轮次二：delta 补审（b522c68d → ea76a058，独立复审 agent）

复核全部 19+2 项发现逐条状态 + delta 独立狩猎 + 独立全新重放（exit 0，208s，五场景 pass，production_writes count=0，45 安装标记全接线）+ 11 项快测 20.33s + ruff + 收据对账。

**结论：APPROVE_WITH_MINOR**，附带义务三项：
1. F12 回归断言（env-unavailable 退出无 attempt 残留 + early_cleanup.json）；
2. F10 回归断言（路径重定向变量清洗字段断言）；
3. 补齐 F4 交接件并在 handoff 披露新发现（探针异常、sendto 形态、gethostbyname 绕过）。

新发现无 BLOCKER/MAJOR；7 项中 3 MINOR + 4 NIT。

## 轮次三：义务关闭确认（3bc0508e，同一复审 agent）

对 `git show 3bc0508e` 的聚焦复审（探针异常包裹、sendto 解析、F12/F10 测试）：**四项义务全部 CLOSED、无新缺陷**。审查者独立验证（未采用实现者数据）：ruff clean；6 项聚焦快测 4.43s 全过；重型 `test_e01_default_offline_full_suite_executes` 53.99s passed。

**最终结论：APPROVE**

复审备忘（披露于 handoff 已知边界）：① 交付回放收据的 `runner_code_sha256`/`final_code_commit` 记录的是产生收据的代码（83926eca），3bc0508e 仅改动失败路径+guard 边角+测试，成功路径语义零变化，收据仍有效；② sendto(flags, address) 修复无正向单测（链路不触发，原发现即 NIT）。

## 最终验证（被审代码 3bc0508e 状态）

| 命令 | 退出码 | 结果 |
|---|---|---|
| `python -m pytest -q --tb=short -p no:cacheprovider tests/test_cross_repo_chain_e2e.py tests/test_w14_portable_chain_runner.py tests/test_w14_portable_chain_cleanup.py` | 0 | 22 passed（1381.00s，本机争用期） |
| `python -m ruff check e2e/run_cross_repo_chain_e2e.py e2e/replay_support tests/test_cross_repo_chain_e2e.py tests/test_w14_portable_chain_runner.py tests/test_w14_portable_chain_cleanup.py` | 0 | All checks passed |
| `python tools/pre_push_gate.py`（独立重跑） | 0 | 595 passed, 1 skipped, 36 subtests, 98.04s；pre-push/CI checks GREEN |

（环境事实：上一次三命令连跑中 gate 内部 pytest 因本机争用触发其 300s 硬超时——单列环境问题；独立重跑即 GREEN，最终以 GREEN 记录。）

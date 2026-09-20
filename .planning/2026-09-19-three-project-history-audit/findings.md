# Findings

## 最终判定（覆盖前期“待确认”状态）

审计正文范围已闭合：769候选路径中766全文语义审查，2份同源混合清单仅工程部分，1份误命中raw新闻排除。详见README及master_coverage；这些数字是覆盖，不是通过率。

1. 原规范多次写对了用户目标，但后继卡缩成helper、fixture、状态或收据形状。强规范hash仍在，语义没有被完成门保护。CA206/301/302、ZR409、197场景和READ10错映射构成直接证据链。
2. 真实生产配置缺adapter而v2扫描启用；测试fixture预置adapter，doctor未校组合。raw成功后scan失败没有正确透传，解释港美新文件落盘却无法再次复用。
3. raw/review/artifact/consumer四层不能合并成capture_ready。角色选择与DAG计划被命名成读取/调用，实际source-preparation提前阻断且需求只在内存登记。
4. 有效修复必须保留：已修发布验证顺序/嵌入输入、真实旧raw复用、规范化与队列部分修复、安装同步和安全拒绝。不能把后续断链倒推成所有旧修复无效。
5. 当前隔离反例仍包括普通文件host_signed、registry先登记后输出失败、deadline旧预算、refcount丢更新、SectionQuery旧版本/缺文件、GapPlan修订/期间/hash、验收器旧PASS遮新FAIL、日志字段名假脱敏。限定反例作用路径，不宣称生产事故已发生。
6. 数学/结构/置信分数都不能证明买方预测准确性。31模型的领域/公式边界已复审，真实信息冻结、经营约束、反证和未触碰样本外基准仍需实施。
7. wiki v5为冻结规划，不能叫已经实施又回归。已取消研究writer等保持退役；旧活动手册应消歧，不因旧框未勾而重建。
8. 此审计也经历独立纠错：判定原规范与后继兑现范围分开；修正证据路径、13命令口径、模拟clock表述和并发版本归属。第二波报告保存更正。

新计划为9阶段18项，见implementation_plan.md。全部属于未来产品/方法实施；本轮完成历史审计不等于修复已完成。

后续执行细化已完成：execution_v2将18项拆为86卡（含31模型公式卡和先行披露适配卡），具体路径、输入/oracle、专业决定、停止/恢复及接续均有明确记录。独立干读修正了新接口命令绑定、披露适配职责的隐式循环，以及发布故障前置与sidecar定位。结构检查不等于弱模型产品实测；全部产品卡planned，pilot尚未执行。

## 实施新证据（2026-09-19 实施段，全部限隔离副本资格）

- I-00-A：三仓HEAD可溯源；生产 catalog 单库 49,677,344,768 字节、WAL=0，全量快照因磁盘61G<2×47G 延后，backup API 已在188KB 小库 proven（integrity=ok）。worker_control desired_state=paused、PID15596已死但状态文件保留。全局 Miniconda python -I 仍加载 __editable___dayu_agent 钩子——后续所有卡级运行一律 per-attempt iso venv，全局解释器禁用。
- I-00-B：3/3 样本（紫金/小米/微软）raw+sidecar+request 精确hash匹配；source_preparation/fetch_filing 无 --config 参数，隔离依赖注入需在 I-01/I-04 验证——不得猜参数。
- I-00-C：当前 scenario_registry 197 项全 passed 且 fixture_hash/oracle 全 None 的形态在改前对照复现；iso 副本新增 scenario_gate（tier 显式 + evidence_path + fixture/oracle 绑定 + 空 commands/invariants 拒 + required_capability 覆盖检查 + narrowed successor 无 linkage 不清原义务），13/13 校验含 197 全拒与跨入口下层红→上层 incomplete。生产 uc 未触碰；步骤4“组合键/时间排序”专业冻结尚留 open question。
- I-00-D：company-wiki CLAUDE.md 与 README.md 各加时代边界/不擅自resume横幅（生产文档变更，diff 存档）；DEPLOYMENT/OPERATIONS/使用说明书于三均不存在，记录为 NA。
- I-01-A（D-W01）：选择在 config.py 内冻结 shared 判定 effective_root_profile + 六类错误码；doctor 与 scanner 同用，旧 root 名 allowlist 移除。CFG-REAL 三根 half_activated 逐根列出并 fail-closed（修改前 doctor healthy = 与审计认可的证据吻合）；N2 四类错误互异拦截；dropbox_stock 因无法证明属于某一已实现 adapter 布局而按停止规则不赋 adapter。
- I-02-A（D-W02）：ScanReport 契约 completion_status/per_root_results/target_files 冻结，registered 判据绑定 locations.last_seen_run=本run 的 active 行；writer 四道门（中断→scan阶段失败、completion 门、per-root 门、目标注册+exact-resolve 身份门）。N1/N2/N3a/b/c 全如预期拒绝；N3c（伪造 resolver reused_exact 命中无关 handle）曾在旧基线被原样接受——第二实例关闭。journal/事务边界、缺 sidecar receipt、ensure 入口留 I-02-B/C/D。
- 限定：两卡 D-W 的“专业冻结”由实施者起草 decision.md、独立reviewer确认，尚无人类专业 reviewer 复签；不构成生产部署资格。

- I-03 链新证据：provider ID 字典序缺陷实锤在 gap_plan.py L167-170（选择）与 L228-242（hash）；canonical P0 SHA（b9c18479…ba24）由独立序列化+reviewer 独立重算双向一致；G-C2 每次 14 类安全变异（URL/日期/实体/market/kind/period/provider/id/amended/policy epoch 等）hash 与授权双断言；close-gap remaining_gap=completed_partial 语义堵死"选第一个候选就报全 gap 关闭"。
- 资格边界持续成立：所有卡 accepted_scoped 均为隔离副本资格；生产合并、live provider、生产重试注册接线、弱模型 pilot、三公司正式预测与准确性均无资格或未完成。

## 审查起点
- 上轮真实场景仅正式来源链实跑，正式forecast结果0/3。新增港美raw有sidecar但catalog四表无记录，真实scan原因是生产v2策略开启而company_raw缺adapter_id。
- 紫金已有raw复用成功，但缺review阻止source_preparation。artifact旧绑定、错误包装、扫描新鲜度等另有证据。
- 当前工作区存在上一轮方法升级的未提交改动；审计不能把这些变动归为本轮修复。
- CodeGraph三项目可用，但只索引代码；历史Markdown清点需原生文件清单和文本阅读补充。
- 以上是待与历史承诺比对的起点，不是已完成的全面根因分析。

## 当前证据与待确认解释
- RF reviewer已发现原CA-302真实三公司全链要求与实际卡片缩小为prepare_forecast/缺失resolver之间存在差异；CA-206自然观察与测试内纯函数存在差异。独立复核和隔离反例执行中，不先定性所有accepted为虚假。
- filing reviewer发现部分bundle fidelity测试只验证自造dict的JSON往返、未调用生产转发；其支持范围需要降格。refcount并发和deadline的历史已知问题正在隔离复现。
- wiki reviewer指出v5已通过的是文档导入/冻结，明确不表示worker实施或恢复。必须把真实且限域的规划PASS与被过度解释的产品PASS区分，不能一概推翻。
- 新报告需同时指出完成治理的错误和读者对限定状态的误读，并识别旧总表/新补丁表共存带来的入口问题。

## 执行包细化缺口
- 总纲不是原子执行手册：源码锚点、确定性输入/预期、注入位置、部署组合绑定和逐模型oracle尚需显式化。部分事务/经济/统计设计必须由专业reviewer先冻结，不能靠弱模型自由补全。
- 文档干读和结构校验不等于弱模型已成功修改产品；本次不虚报该资格。


- 计划细化必须区分case资格：31模型公式验收不能依赖后继准确性，否则与正式预测/评估形成循环；实际采用模型的披露适配是公司case前置，未用模型不阻塞该case。
- 当前SLO脚本的catalog参数只检存在、实际入口依config；bundle是exact延迟副本。I14新增实际目标一致性与真实bundle测量要求，不把代理计时写作真实消费SLO。

## 隔离巡检（2026-09-20 父代理，逐条附证据）

- **越界写 1（我方，已处置）**：`revenue-forecast\prereg_expectations.json`（M05–M08 复核脚本以相对路径写、进程 cwd 恰为生产仓库根；sha256 `35fbc83ded27…a03a9f`，mtime `2026-09-20 02:59:55`）。先保全副本于 `execution_runs/_isolation_incidents/20260920-prereg-expectations-leak/`，再从生产树删除；删除后 porcelain 不再出现该条目。
- **越界写 2（我方，已处置）**：`filing-fetch\git_filing-fetch.txt`（I-00-A 采集命令的输出重定向落到生产仓库根，内容自指 `?? git_filing-fetch.txt`；sha256 `43b964e376e7…c160c`，mtime `2026-09-19 11:05:23`）。attempt 目录已有逐字节相同副本，直接从生产树删除；`filing-fetch` porcelain 现为**空**。这也解释了该仓 I-00-A `dirty_evidence` 的来历。
- **不可归因的生产树变化（未回退）**：`revenue-forecast\assurance\runs\daily_alert.jsonl` 新增一行（`run_id 20260919T210001Z`、`at_utc 2026-09-19T21:00:48Z`），格式与 run_id 口径即本仓每日告警作业自身；I-08-A 的 `after/git_status_after.txt`（mtime `2026-09-20 01:19:23`）中该条**已是 ` M`**，早于任何本计划卡触碰该路径。无卡被允许写 `assurance/`，故**不归因于本次审计**，且**不回退**（可能是用户自有自动化产物）。
- **provenance gap（登记不解释）**：`revenue-forecast` 既有脏文件 `CHANGELOG.md`/`SKILL.md`/`references/*`/`assurance/runs/daily_alert.jsonl` 的 mtime 在 `2026-09-20 02:24:00` 被批量刷新，恰在 `02:23:50 reset: moving to HEAD`、`02:23:58 commit 7d7ea1e` 前后。**内容未变的证据**：`SKILL.md` 磁盘 sha256 `45e4e343eba4…c47806`（26378 B）与 I-00-A 冻结基线登记值**完全相同**；其余文件无基线 hash，只能证明 porcelain 条目与基线逐条相同、`git diff` 仍只显示用户既有改动——**不声称字节未变**。已排除 `git stash`（list 为空）、`.git/hooks` 与 `.githooks` 内无 `stash` 调用，工作区未被回退。当前值已落盘于 INCIDENT.md 表格供今后比对。
- **生产不可变量测（同轮）**：`company-wiki` porcelain 仅 ` M CLAUDE.md`/` M README.md`；三模块磁盘 sha256 `e83179915333…`/`a73826aa10c9…`/`fad88c60294a…` 与 I-14-C 收尾实测一致（CRLF 工作区，故 HEAD blob 的 `git hash-object` 天然不同：`5d700302ca4b`/`d9ce30dfeb14`/`c5038a9db4ec`）；`.source_catalog\catalog.sqlite3` 49,677,344,768 B、mtime `2026-09-19T06:31:35Z`、`-wal` 0 B；`-shm` mtime `2026-09-20T02:25:33Z`（并发卡只读触达）。
- **I-04-C C1 父代理验收**：`verify_flk2.py` 独立复算 13/13；`decision.md`/`review.md`/`handoff.json`/`evidence/hashes.txt` 改后 hash 与实现者报告逐一相符；`verify_r4_appendonly.py` 证明"删去插入块后重建 sha256 与改前逐字相等"（原文未删）。真实 F-LK2 组 `[16,35,10,56,18] ⇒ lost [184,165,190,144,182]`；旧组 `[12,19,7,26,43]` 与 `expected=200` 自不相容（`200−finals=[188,181,193,174,157]`）。**C1 关闭由父代理验证，非 reviewer 复签**——如需 reviewer 级复签应在下次复核中补。


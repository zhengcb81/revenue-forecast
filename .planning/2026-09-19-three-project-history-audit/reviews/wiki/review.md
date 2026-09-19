# company-wiki：历史验收为何没有覆盖真实运行

审查日 2026-09-19。本轮只读产品；只在本审计目录写文件。没有扫描生产目录、下载、修复、改 flag、迁移数据库、删除 raw、启动或恢复 worker。

结论：存在有效的局部修复和合理契约，也存在生产配置没有迁移、验证对象不一致、默认调用未闭合、规划结构检查被扩大解释等问题。**不批准当前完整资料链或正式预测可交付，也不把尚未实施的 v5 计划说成产品回归。** 三家公司实战正式收入预测 0/3 仍是当前观察结果。

## 阅读与逐项审查边界

本分区共有 **1,263 条审查记录**，见 [逐项账本](item_ledger.jsonl) / [CSV](item_ledger.csv)。它不是 1,263 个独立运行测试；同一义务在不同历史状态出现时保留多条来源记录。

判定分布：supported_scoped **246**，contradicted **34**，insufficient_evidence **147**，not_deployed **490**，superseded **118**，historical_only **226**，not_applicable **2**。not_deployed 多数对应明确尚未实施的 v5 义务，不计作 490 个产品缺陷；contradicted 也包含规划或历史文档冲突，不能当作 34 个生产事故。

| 内容 | 已完成的阅读与判定 | 不代表什么 |
|---|---|---|
| v5 | 46 份 Markdown，11,728 行，完整正文 | 不代表未来 worker 已实现 |
| 旧 recovery | 15 份，6,616 行；共同正文映射到已完整读的基线，所有旧侧差异另读 | 不继承新版 PASS |
| 原调查副本 | 875 行，与 v5 investigation 规范化文本相同，保留双路径/hash | 不重复计作第二次性能实验 |
| 补充工程上下文 | 41 份完整正文，6,779 行，含 ADR、契约、操作文档及 4 份 web 工程页面 | 不重审业务文章财务事实 |
| 污染清单 | 仅工程头、组计数、来源链接和条目边界 | 31,958 行业务条目未逐事实验证，未批准删除 |
| raw/news | 一份工程关键词误命中的业务文档排除 | 不作全文审查声明 |

共 **103 份 Markdown 路径全文覆盖**，其中 87 份直接阅读、15 份按版本完整映射、1 份相同调查文本映射；另 1 份工程字段部分覆盖、1 份业务排除。机器计划另逐项核对 **315 个 test ID、115 个 DAG node、60 个 RQ、44 个 RK、105 个 PR finding**；173 条历史审查状态映射到 91 个不同关注点。这些数量只是规划与证据覆盖。

[阅读清单](read_coverage.json)、[旧版逐行映射](old_version_mapping.json)、[旧机器计划变化](old_machine_item_review.md)、[历史 closure 轨迹](freeze_issue_timeline.json) 保存具体边界。所有账本原路径和行号均存在，ID 无重复；[元数据验证](ledger_validation.json) 不替代语义审查。

初始冻结工程清单为 **373 选中 = 247 工程/历史 + 126 业务排除**。之前辅助分派表的 243 把 web/docs 四份工程导航也误排，已识别并完整审查。此处只证明本分区覆盖，不代替另外审查者的全文证明；并行期间新增文件须由主审单独登记，不能自动沿用此分母。

## 第一条失效链：生产组合不在绿色测试里

历史 GP002 确实修复了 flag 向扫描传递，并在测试、O1 独立检查后关闭。但它使用 `RootSpec(adapter_id="company_raw_v1")`，同一历史提交中的生产三根仍没有 adapter_id。进度日志已经知道生产 `v2_scan_shadow=true`，仍在“生产运行日志待 CI 后验证”的情况下正式关闭（revenue-forecast `assurance/runs/2026-09-02_remaining-gap-closure/progress.md:80–88`）。

当前三个真实根依然缺 adapter。扫描按 shadow policy 进入 adapter 路径；小米和微软日志显示 `completed_with_errors`、`files_seen=0`。`canonical_writer.py:181–193` 已写 raw/sidecar，调用 scan 却没有验证报告；随后 exact resolve 失败，在 `:209–211` 转成身份错误。根因不是原件下载失败，而是注册未完成且错误阶段丢失。

本轮真实只读 config doctor `exit=0/healthy`，因为它主要核文件、YAML/JSON/fixture/security master，不核 runtime policy 与 root 能力组合；它还对 root ID 有硬编码，不能支撑“任意已支持目录只添配置即可”。当预览固定 shadow=false、实际运行取 policy=true 时，预览成功也验证不了实际路径。

证据：[只读 doctor、冻结项与前后配置 hash](readonly_diagnostics.json)、[历史 Git 原文成功读取](historical_git_readonly.json)，账本 `WIKI-GP002-*`、`WIKI-DOCTOR-01`、`WIKI-ROOT-01`。前一个 JSON 中的历史 Git 查询实际 exit128，保留失败记录；后一个使用仅限单次进程的 `git -c safe.directory=…` 读取配置和测试，三条命令 exit0，没有更改 Git 配置。O1 的参数接线修复应承认，不能因注册链残缺反过来否认该小修复。不修改 flags 来让测试变绿。修复时应让 doctor、preview、actual scan 使用同一个有效能力解析结果，并对旧生产配置形状做反例。

## 第二条失效链：结构冻结不等于规划语义闭合

独立检查支持 **51 个规范文件 hash/size 一致、315 tests 和 115 nodes 结构完整**。最后一次 test/DAG closure 自己明确排除内容语义；应承认这个有限通过。旧 v1–v3 曾正式失败，v4 reviewer 中断而且后续字节漂移；v5 新基线不是“旧 v4 已验收产品”。115 nodes 大量为后续实施阶段，未跑不是新缺陷。

但冻结内容中仍有具体冲突：

| 账本 | 原文与独立判断 | 影响范围 |
|---|---|---|
| SEM-01 | test_acceptance_plan:609 将 WRITE-F01/02 绑定 G11J；registry:4352/4377 revalidate 未包含该门 | Gate×Test 关系未被 ID 存在检查覆盖 |
| SEM-02 | traceability:180 把 LLM 分支 D/G 数写成 1，DAG 与 agent_review_gates 是 2 | 文本计数与机器合同不一致 |
| SEM-04 | PR-089 已将产物改成 manifest.json/report.md；prompts:81、playbook:40/146 仍要求 manifest.md | “该意见已关闭”证据不足 |
| SEM-05 | G10R 文本 exact direct dependencies 缺机器 DAG 中条件必需的 G11M-L-ADR | 文本不精确；BP 仍传递依赖，不据此声称已发生运行绕过 |
| SEM-06 | playbook:922 旧摘要写 G11A 后可到 D11M/D11B-A1，后文和 DAG 要经过 D11J | 执行者读取不同段落会获得不同流程 |
| SEM-07 | runbook:277 给 ADR11 写 SCHEMA_DELTA，但其 enum 是 OFF/ENABLED，schema 分支属于 ADR13 | 规划中的决定值错误 |

SEM-03 专门保存最终 closure 的真实有限范围。相关 PR-055/061/070/077/092 已改判 `insufficient_evidence`：承认原具体改进，不用另一个残留问题否定整个改进。今后冻结 hash、结构完整、内容语义、产品实现、部署观察应各自给结论。

## 第三条失效链：小样本正确和生产规模正确是两个命题

worker 调查完整追溯了 locationless 功能修复后候选 SQL 在生产大量数据上的性能问题：小 fixture 能验证返回正确，不能揭示生产 query plan；实际 enqueue 阶段曾耗约 902 秒，parser 尚未开始。高 CPU 与低物理 IO 更支持 query bottleneck，而非笼统称解析慢。

历史强制索引/改 IN 子查询的 1.413、0.914、0.231 秒是有价值的局部实验，但只验证前 3 条相同，**未证明全候选集与排序完全等价**。LLM 一次 42 秒、批次 3:1 也不足测稳定吞吐。46.22 GiB DB、45.93 GiB 备份说明旧 20 GB 容量规划和固定 15/25 GB 阈值已经不能直接沿用。

历史测试和诊断并非无效；问题是从“小 fixture 功能正确”跳成“生产规模可恢复”，以及从“更快且前三条相同”跳成“全量语义等价”。修复要保存全候选集、排序、取消/暂停、并发时 snapshot 等价与真实规模性能；不启动当前 paused worker 去凑自然运行证据。

## 新补充工程文档揭示的范围漂移

1. **旧入口看起来仍是现行指南。** API、DEPLOYMENT、GATE_SYSTEM、使用说明书、TROUBLESHOOTING 含旧研究 pipeline、scheduler、估值、自动维护、重启、raw 移动及清理命令；ADR scope 和 legacy reachability 已将这些研究 writer 退役。文档应标注时代/owner并链接现行 source-only 入口，不能让代理从旧手册重启已退役能力。
2. **清理计数和来源链也需审。** ACTION_ITEMS 的 15,674−5,038 应为 10,636，与 10,642 差 6。污染清单分组与 heading 均为 3,886，但全部 4,175 相对来源链接从当前 docs 基址解析出 repo，且存在来源链接与下一日期拼接。只支持计数一致，不能证明误删为零或每条已审。没有据此宣称原件丢失。
3. **质量代理指标被当结果。** 两份手册的 Gate 五维权重不同；“提高阈值4.0→3.5”数值方向相反；semantic_copy“零误报”不能由规范文本相同保证；每天 LLM 次数、条目数、页面数、压缩比也不能证明买方准确性。旧计划“关键模块必须LLM禁止正则”全称不合理，身份/hash/单位/日期应有确定性规则。
4. **来源契约值得保留，但范围需精确。** 当前 SourceExportBundle.build:232–236 重验所有 merged manifests，兼容协商从合法三元组合里选最高支持项，EvidenceQueryService 使用 mode=ro/query_only 并拒绝不安全 WAL 条件。这些可支持静态有限结论；pure adapter、合同、只读查询不证明生产 worker 和下游真的读到工件。
5. **Pause 文档和显式下载 scope 应对齐。** filing 独立审查确认临时 scope 是明确授权下载的设计，结束恢复原 paused 状态；不报“未授权绕过”。source-catalog:128 的绝对拒绝描述与此不同。并发 RMW 丢引用是另一个有隔离证据的问题，见 filing reviewer 报告，不混为暂停权限缺陷。
6. **安全整改不能靠文本洁净宣布关闭。** SECURITY_REMEDIATION 的旧扫描数字仅为历史；外部凭据轮换需要相应回执。本轮没读取 .env、输出密钥或执行轮换。

上述所有条款按文件逐项保存在 `WIKI-CTX-001…379`，[工程复核证据](engineering_context_checks.json) 保存计数、链接基址和算术结果。污染清单业务内容与 raw/news 是显式排除，避免“全文审计”夸大。

## 对后续实施的建议

优先关闭生产 effective policy/root/adapter → scan receipt → 注册 → re-resolve，再用本次已下载原件验证恢复与第二次零下载。不要先增加更多计划卡，也不要用取消严格证据门换成功。

随后把 source preparation 的拒绝、补料、review writer、producer、真正工件读取、forecast 输入放在同一用户旅程里验；正例从没有手工预填绿色的新样本开始。真实外部唯一根样本缺失时明确留未验，不删除其他副本制造 only。

维护上区分每个待删除记录是否属于已验证归档集合；保持用户 paused 意图。部署证据同时记录源码 dirty hash、实际模块路径、安装副本、运行 flags、迁移与常驻 loaded version，不能用 git short 等于 HEAD 代替。

不把本审计中的 `supported_scoped` 计作产品 PASS：它可能支持一条合理设计、一个有限静态分支、一项算术或历史声明。正式验收仍需原义务、实际入口、独立 oracle、完整原始结果与剩余缺口。

## 自我更正与交叉复核

根审查者发现先前 worklog 错将历史 Git blob 成功记录定位到 `readonly_diagnostics.json`；该文件实际保留了三条 ownership 拒绝。现已新增成功原始记录并更正引用，保留原失败，不把再次读取说成旧命令原本成功。复核还把 `WIKI-GP002-03` 从 contradicted 改为 supported_scoped：O1 只要求 canonical writer 跟随 snapshot，这条已经成立；整体导入资格未闭合另由 GP002-01、真实失败链判断。

收尾时主审发现并行工作区的 `src/company_wiki/source_catalog/normalizer.py` 已变化；本 agent 只读复算当前 SHA256 为 `772075ed0d1c540aeb2a0feea17d7735a28c0aba981edfbdefa7297a57a06cff`。本分区没有编辑该文件，也没有新版本运行验收；历史 normalizer 观察不自动适用于新字节。本轮“未修改产品”是本 agent 的操作范围声明，不是整个共享工作区绝无其他写入的保证。不回滚其他并行修改。

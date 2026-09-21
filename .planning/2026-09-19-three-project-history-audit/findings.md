# Findings

## 【流程缺口·重复出现】reviewer 裁决未落盘为定字节报告（2026-09-21 登记）

**现象**：独立 reviewer 以 subagent 形式派发时，其裁决经**消息**返回父 agent，**不写盘**。载体落定执行器随后把该裁决转录为 `review.md`，并如实标注 `verdict_is_relayed = true` / `reviewer_report.exists = false`。**已确认至少两例**：
- **I-10-B**：执行器穷尽搜索 `%TEMP%`、`C:\*-rv*`、`execution_runs/_isolation_incidents`、`reviews/` 及整个 attempt 树，**未找到任何定字节 reviewer 报告**；`qualification.json.declarations.verdict_is_relayed = true`、`reviewer_report.exists = false`，`review.md §2` 自述为"relay transcript, not a reviewer-authored block"。对比**正常形态**：I-11-A 携 `e8b7d223…`、M09–M12 携 `5a44fd4e…`（定字节报告）。
- **I-05-C**：同一执行器把它登记为 **P3-3**（`review.md` 为转录、原始 reviewer 报告未归档）。

**影响**：①裁决的**原始字节**不可复核，只能复核转录（内容经父 agent 转述，链条多一跳）；②与 M09–M12/I-11-A 的"定字节报告 + 哈希"标准形态不一致，跨卡对账时形态参差。

**父 agent 处置**：**不伪造**报告路径或哈希（执行器正确地拒绝了这条路）；按"relayed"形态如实登记，并把**后续所有 reviewer 派单**改为要求其**先把报告写入 attempt 内固定文件**（建议 `<A>\reviewer_report.md`）再回报，使载体可携定字节哈希。**已发生的两例不回改**（attempt 已封盘），作为**已披露的历史形态限制**保留。

## 【已失效·核对记录】OQ-I10B-3（`model_extensions.py` untracked）已于 2026-09-20 解决

I-10-B 载体执行器正确地**标记而非静默关闭**该 OQ（"progress.md 称该文件已被纳管，该开放项可能已陈旧"）。父 agent 实测确认：`git ls-files --error-unmatch scripts/model_extensions.py` → **tracked**；`git cat-file -e HEAD:scripts/model_extensions.py` → **在 HEAD 中**；引入提交 **`5db4734a owner-authorized: bring the extension model registry under version control`**；工作树 blob `9a40b464099a64b7c1522ac32f6f1842954aa20d` **== HEAD blob**。⇒ **OQ-I10B-3 已失效**（不再构成残余风险），但**不改 I-10-B 的封盘载体**，只在本文件登记失效事实。

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

## 跨批复核发现的共享缺陷（2026-09-20，父代理登记）

- **【新，书签/收尾】“零写入 reviewer ⇒ 卡内无裁决载体”这一类缺口已批量补齐，并立为流程要求**：M09–M12 的 `review.md` **完全没有裁决区**（reviewer 零写入，唯一裁决只在 `%TEMP%\m09m12-review-20260920-035628\REPORT.md`，40679 B / `5a44fd4e…`，§1 结论汇总 L16–28）。父 agent 裁定：**允许落 `status=accepted_scoped`，但必须（a）把报告按字节固化进 attempt（四卡均已落 `evidence/<CARD>/reviewer_report_m09m12.md`，父代理复算 **4/4 hash 一致**）、（b）在载体里明写 `in_card_verdict_region: false` 与 `in_card_transcription_owed: true`**。同一类缺口在 I-15-A 也存在（裁决只在复核侧报告，卡内副本取自 I-04-C 的归档）。⇒ **流程要求**：今后凡 reviewer 采零写入模式，**其报告必须在任何载体落定之前先按字节落进 attempt 并登记哈希**（`%TEMP%` 会被清理）。**本轮批量载体落定 19 张**（M05–M07 r1、M09–M12 r1、M21–M28 r3/r2、I-04-C、I-11-A、I-14-B、I-15-A），**1 张按规则跳过**（I-07-A：最新一轮 r2 = `changes_required`（仅文档一致性）⇒ 保持 `review_pending`，**欠一次独立 r3 re-read**）；**32 份台账以“注记陈旧条目”方式登记、无一枚哈希被手改**（仅 I-11-A 有单一用途生成器 `tools/hash_attempt.py`，已归档前像后重跑 rc=0）。
- **【新，provenance gap】一次“引用哈希来源不明”的如实登记（含归属更正与只读反证）**：I-05-A 实现者最初把 `REPORT_R4_FULL.md = 23101 B / d64c8ce2…` 记为“父 agent 引用值”；**父 agent 复核自己的转达：只给过预注册文件的哈希 `0e884aff…`（实现者已核实完全吻合），未给过该报告的任何 sha256/字节数**。实现者随后**更正归属**：该值来自其**收到的“派工消息层”**（而非父 agent 的转达层）——**此归属在父 agent 当前上下文无法独立核实**（无该派工消息原文），故按“**来源未确定**”登记，并附其只读反证：**`%TEMP%\planrev4` 树下不存在任何 23101 字节的文件**，`rev\REPORT_R4_FULL.md` 即 15827 B/`d9567713…`（mtime 2026-09-20 04:31:11）。⇒ 结论：**被引用的那份字节在盘上不存在**（可能被覆盖或从未落盘），属**不可复现的引用值**。**父代理裁定**：接受实现者的处置（以**八要素内容签名**确认报告身份、按**盘上现字节**落定、把引用值原样保留并标 unverified），**不追另一版本**；其封盘证据里字段名 `cited_by_parent` 不准确这一点，**因 attempt 已封盘而不回改**（如需盘面准确须开新 attempt 或明确解封后仅追加只读注记）。


- **【新，严重·治理】“嵌合哈希”（chimera hash）—— 用字符串替换修哈希会造出从未存在过的值**：I-04-D 的 r2 返工在修陈旧哈希时用了**前后缀字符串替换**，结果产出 4 个**在任何时刻都不存在于磁盘且从未被任何真实文件产生过**的 sha256（例：`after_i04d_green_txt = f8220c7d29c8a35d…e56127` = r2 前缀 + r1 尾巴，真值 `f8220c7d29c82cde…a3115`；`changes_diff_sha256 = 7fdb0c27adb7cfb3…` **从未存在**，真值 `2197bce4…`；另有把台账 hash 当成 `hashes.txt` 的 hash 等）。这类值的危险性高于“陈旧”（陈旧可被复算发现；嵌合值看起来像真哈希却无法对应任何字节）。**父代理据此定为跨批纪律**：①**一切交付件里的哈希必须由 `hashlib` 从盘上字节现算写回**，写完立即断言 `recomputed == written` 并落盘原始输出；②**严禁**用字符串替换/前后缀拼接“修补”哈希；③台账类文件应整体由生成器产出，手改视为缺陷；④评审方遇到“哈希看似合理但复算不出”时，应按“不可复现值”登记而不是当作陈旧值。已转达 I-04-D 实现者按此重做，并建议同类修复在其它卡（含本文件下方各批）自查。
- **【新，环境】`.json` 命名与内容不符 / 超长路径两类的全量扫描结果**（父代理用隔离解释器对 `execution_runs` 全树扫描，排除 `iso/`、`venv/`、`__pycache__/`）：**`checked_ok = 6397`**；**50 个 `.json` 不是 JSON** —— 其中绝大多数是**故意**的（如 `I-07-A/after/cmd-V*/stdout.json`、`I-14-A/{after,before,harness/scratch}/**/stdout.json` 实为 **UTF-16LE 原始 stdout**（首字节 `0xff`），以及大量**空文件**占据 `.json` 名；`I-08-B/scratch/**/bad.json` 是**负例夹具**（故意畸形））；**51 个路径因 Windows MAX_PATH 无法打开**（`I-02-C/after/case_scratch_retained/**` 下含中文公司名与长文件名）。⇒ 结论：**除 I-04-D 那次（已修）外，未发现交付级 JSON 损坏**；但“把原始 stdout 存成 `.json`”这一命名习惯会让任何“全量 JSON 校验”产生假阳性，建议后续批在 `commands.json`/`handoff.json` 里显式声明 `non_json_files_named_json` 清单，或改名为 `*.stdout.txt`。


- **共享 harness 缺口（P2-1，影响 M05–M20、M25–M31 各 attempt 的同字节 runner）**：`scripts/run_card.py` **从不校验 `cases.json` 的 `expected` 字段** —— M21–M24 的复核者把 `NEG-CARD.expected` 由 `ModelRegistryError` 改为 `ValueError` 后重跑仍 **rc=0 / verdict=pass**（`run_card.py:233` 只把该字段抄进结果，`:246-252` 仅做 `isinstance(exc, ModelRegistryError)`）。后果：44 条负例的 `expected` 目前是**无约束文本**，"负例断言被篡改会变红"这一变异证明只在**输入**被篡改时成立。**处置口径**：只在**仍在返工**的批次内修（M21–M24 已派），并补"期望类型被篡改 → rc=3"的变异探针；**不**回改其它已冻结 attempt 的 runner（冻结件不动），本缺口按"已知共享 harness 限制"登记。
- **枚举口径差异（解释 40/3 与 41/4 之争，非错计）**：`direct_growth.growth_rate` 的 `dimensions` 是 `"ratio"`，但注册时**未声明 `ratio_drivers`**（`model_registry.py:221` 的 `_spec(...)` 未传该参数），其定义域 `(-1, inf)` 由 `driver_value_bounds` 的特例分支给出。按 `spec.dimensions[driver]=="ratio"` 归类 → **ratio=41、越界=4**（M05–M08 r3 更正后、M17–M24、M25–M28 的口径）；按 `spec.ratio_drivers` 归类 → **40/3**（M13–M16 的口径）。两者都是"脚本按自己读的字段如实产出"，**差异源于产品侧一处不一致**（31 个模型中唯一 ratio 维度未登记进 `ratio_drivers`，`MODEL_RATIO_DRIVERS` 兼容视图因而看不到 `growth_rate`）。→ 作为**产品侧待裁定项**上报，不按错计处理。
- **"optional 无显式默认"的计数单位差异**：M13–M16 与 M17–M24 报**槽位数**（31），M25–M28 报**模型数**（24/31）。两者单位不同、可并存；引用时必须写明单位（父 agent 已在各批复核中要求点名）。
- **`.pyc` 副作用来自仓库自带门而非卡**：`revenue-forecast\scripts\__pycache__\*.pyc`（mtime 2026-09-20 03:42:17 与 03:54:04）由 pre-push 门的 `compileall` 步骤与并发 session 的导入产生；`iso/` 与 `__pycache__/` 均被 `execution_runs/.gitignore` 忽略，**不污染提交**（`git ls-files` 下 `.pyc` = 0）。多批复核者主动删除自己产生的 `.pyc` 并披露。

- **F-01（runner 不比较逐例 `expected`）已在 M17–M20 修好，成为跨批复用候选**：该批把 `run_card.py` 改为**按异常精确类型名**比较 `cases.json[*].expected`（明确不用 `isinstance`，因 `ModelRegistryError` 是 `ValueError` 子类），新增计数 `declared_expectation_mismatch` 与第 6 变异臂 F（篡改声明 ⇒ rc=3）⇒ runner `9ea69c72…` → **`5307d2cc…`**（四卡仍字节相同）。同批另建批次级 `execution_runs/M17-M20/a20260919-01/`（`rc_namespace.json` + `batch_handoff.md`），明文**禁止未标注命名空间的跨卡 rc 聚合**。**未推广**到 M05–M16 / M21–M31（那些副本仍是 `fd3a11c9…`/`9ea69c72…`）；是否推广属 owner 决定。
- **F-01 在 M29–M31 第四次被独立命中**：把逐例 `expected` 改成 `"ValueError"`/`42`/全部 `"ImportError"` 后重跑仍 **rc=0 / verdict=pass、11/11 PASS_rejected**；对照反例（补丁改 no-op → rc=3；篡改 `oracle.json` 正例 → rc=3）说明循环对**输入**与**oracle 正例**敏感，缺的只是“逐例错误类型/原因”绑定 ⇒ **不是产品假绿**，是裁决门的点状缺口。
- **OQ-05 provenance 口径（可供 31 张公式卡复用）**：`evidence/<CARD>_oracle_document_freeze.json` 锚定的是**生成器代码** `scripts/oracle_<CARD>.py`（三卡同为 `3177247f…`，`pointer_equals_oracle_script: true`），**不是** `oracle.md` 文本；`gen_oracle.py` 只读 pointer + 脚本，**从不读取或校验 `oracle.md`**。承载 A–C 门控期望的 `oracle.json` 可被**逐字节重生成**（reviewer 独立重跑四件全 `BYTE_IDENTICAL`）、其生成器运行前已被 hash 到盘上文件、且 `oracle.json` mtime < `stdout.txt` mtime ⇒ **formula 资格不依赖 `oracle.md` 的 mtime**。反向结论同样要记住：**`oracle.md` 文本不得当作“事前冻结证据”**（mtime 非密码学承诺、该文件不在 git 跟踪内、无 NTFS 取证手段）；`source_manifest.mtime_ordering` 的 flag 是**事后 stat 比较**。
- **M31“卡片与注册表分歧”系误读（owner 提级撤回）**：`card_M31.md:9`（181 B）与母表 `model_cards.md:2818` **都列了 `net_revenue_per_unit`**（必填 7 项）；`binding.json` 的 6 项清单 + `card_text_matches_registry:false` + `divergence_note`、`oracle.md §12`、三卡 `handoff.json` OQ-04 标题**均不成立**，且与同 attempt `oq_rulings.json` 的正确 7 项自相矛盾。处置（以注册表为准、按 7 驱动跑）正确，但**不需要 owner 裁定**，需勘误。
- **I-14-B 的两个产品级缺陷（reviewer 自造、实测被 accept）**：①`natural_window.py:157-178` 对 `claim.basis` **无枚举校验（无 else 分支）** ⇒ `basis=''`/缺失/`None`/`'wall_clock'` 全部 `accept_claim` 且 `refusals=[]`，J1/J2/J3/J11 可被**一个字段名**绕过；②`union_of_windows`/`sum_of_windows`（`:137-147`）把 **quick_check 计入自然观察时长** ⇒ 接受“37 分钟当观察时长”（2220）而**诚实主张 1740 反被判 `R-CLAIM-EXCEEDS`**。**该漏洞已烧进冻结期望**（W1 `union_seconds=2220`）⇒ 修 P2 必须**同时以追加式 provenance 更正 oracle 期望**。另：**D-1 由 reviewer 落定** `frozen_tolerance_seconds = 5`（L1 实测 `0.9 拒 / 1.0 通过`、L2 实测 `≤86 拒 / 87 起通过` ⇒ 合法带 [1,86] s），**D-2 维持 blocked**（不授权建捕获路径）。
- **M24 用例重复（新类缺陷，不产生错误接受）**：`CONT-BREAK` 与 `CONT-BREAK-CROSSYEAR` 的 `id/kind/expected/base_input/value` **五项全同**（canonical `adcca438…`）⇒ `total=12` 实为 **11 个不同输入 + 1 重复**；且两条**互斥**消息要求压在同一输入上。另：消息要求闸门**只防“改坏”不防“删除”**（`message_requirement_met = None if requirement is None else …` ⇒ 删字段即 rc=0）⇒ 建议冻结 `required_message_ids`。

## 隔离巡检（2026-09-20 父代理，逐条附证据）

- **生产树被回滚事件（编排层自身造成，已恢复；完整记录见 `execution_runs/_isolation_incidents/20260920-precommit-stash-production-rollback/INCIDENT.md`）**：父 agent 的 `git commit/push` 作业触发仓库自带 pre-commit 门，该门 04:35:31 把未暂存改动导出为补丁 `…\.cache\pre-commit\patch1789875331-33652`（557,924 B），随后 `git checkout -- .` 因 3 个被并发占用的 scratch 文件 `unable to unlink … Invalid argument` **返回 255**，补丁**未被回放** ⇒ 生产工作树被重置到 HEAD（`scripts/model_registry.py` 由锚定 `9ec65295…`/26446 B 变为 HEAD 版 `1f2639e1…`/19703 B，本批四模型与 `driver_bounds` 机制整体消失；另有 `revenue_core.py`/`contracts/constants.py`/`revenue_report.py`/`tests/test_backtest.py`/`SKILL.md`/`CHANGELOG.md`/`assurance/runs/*`/`e2e/expected/*`/`references/backtesting.md` 同时“变干净”）。**恢复**：以同一补丁的 `--exclude=.planning/*` 子集 `git apply`（`--check` 与 `--apply` 均 exit 0），锚点全部复算一致（含 `SKILL.md = 45e4e343…` 与 I-00-A 基线相同）。**并发诱因同源**：`.planning` 下 3 个 attempt scratch 仓库内嵌 `.git`（`I-06-A/.../iso/ff`、`I-14-C/.../r5/diff-apply-check/tree`、`I-14-C/.../r5/diff-repo`）使父仓库递归报 `fatal: bad object HEAD`，已写入 `execution_runs/.gitignore` 兜底（**未删除任何文件**）。**裁定**：①M21–M24 / M25–M28 等卡的 `accepted_scoped` 依据 attempt 内 `iso/checkout_scripts` 逐字节快照，事件期间未变，且生产侧已恢复一致 ⇒ **失效条件解除、判定继续有效**；②窗口 `04:35:31–04:5x` 内的 `production_hashes_unchanged=false` 是**正确告警**，不得据此改期望或冻结件，各卡须保留漂移记录并追加恢复记录（时点限定）；③**凡以“生产文件 hash”为验收依据的卡，必须视其为可被外部 git 操作改变的量**；④编排层新纪律：有 attempt 在写 scratch 时不提交、提交前检查内嵌 `.git`、**每次 commit/push 后必须核对 hook 是否打印 `[INFO] Restored changes from <patch>`**（只见 stash 不见 restore 或出现 `Rolling back fixes` 即按红色告警处置：抽查生产锚点 → 用该次补丁 `--exclude=.planning/*` 子集回放 → 复算 → 记录时点）。

- **越界写 1（我方，已处置）**：`revenue-forecast\prereg_expectations.json`（M05–M08 复核脚本以相对路径写、进程 cwd 恰为生产仓库根；sha256 `35fbc83ded27…a03a9f`，mtime `2026-09-20 02:59:55`）。先保全副本于 `execution_runs/_isolation_incidents/20260920-prereg-expectations-leak/`，再从生产树删除；删除后 porcelain 不再出现该条目。
- **越界写 2（我方，已处置）**：`filing-fetch\git_filing-fetch.txt`（I-00-A 采集命令的输出重定向落到生产仓库根，内容自指 `?? git_filing-fetch.txt`；sha256 `43b964e376e7…c160c`，mtime `2026-09-19 11:05:23`）。attempt 目录已有逐字节相同副本，直接从生产树删除；`filing-fetch` porcelain 现为**空**。这也解释了该仓 I-00-A `dirty_evidence` 的来历。
- **不可归因的生产树变化（未回退）**：`revenue-forecast\assurance\runs\daily_alert.jsonl` 新增一行（`run_id 20260919T210001Z`、`at_utc 2026-09-19T21:00:48Z`），格式与 run_id 口径即本仓每日告警作业自身；I-08-A 的 `after/git_status_after.txt`（mtime `2026-09-20 01:19:23`）中该条**已是 ` M`**，早于任何本计划卡触碰该路径。无卡被允许写 `assurance/`，故**不归因于本次审计**，且**不回退**（可能是用户自有自动化产物）。
- **provenance gap（登记不解释）**：`revenue-forecast` 既有脏文件 `CHANGELOG.md`/`SKILL.md`/`references/*`/`assurance/runs/daily_alert.jsonl` 的 mtime 在 `2026-09-20 02:24:00` 被批量刷新，恰在 `02:23:50 reset: moving to HEAD`、`02:23:58 commit 7d7ea1e` 前后。**内容未变的证据**：`SKILL.md` 磁盘 sha256 `45e4e343eba4…c47806`（26378 B）与 I-00-A 冻结基线登记值**完全相同**；其余文件无基线 hash，只能证明 porcelain 条目与基线逐条相同、`git diff` 仍只显示用户既有改动——**不声称字节未变**。已排除 `git stash`（list 为空）、`.git/hooks` 与 `.githooks` 内无 `stash` 调用，工作区未被回退。当前值已落盘于 INCIDENT.md 表格供今后比对。
- **生产不可变量测（同轮）**：`company-wiki` porcelain 仅 ` M CLAUDE.md`/` M README.md`；三模块磁盘 sha256 `e83179915333…`/`a73826aa10c9…`/`fad88c60294a…` 与 I-14-C 收尾实测一致（CRLF 工作区，故 HEAD blob 的 `git hash-object` 天然不同：`5d700302ca4b`/`d9ce30dfeb14`/`c5038a9db4ec`）；`.source_catalog\catalog.sqlite3` 49,677,344,768 B、mtime `2026-09-19T06:31:35Z`、`-wal` 0 B；`-shm` mtime `2026-09-20T02:25:33Z`（并发卡只读触达）。
- **I-04-C C1 父代理验收**：`verify_flk2.py` 独立复算 13/13；`decision.md`/`review.md`/`handoff.json`/`evidence/hashes.txt` 改后 hash 与实现者报告逐一相符；`verify_r4_appendonly.py` 证明"删去插入块后重建 sha256 与改前逐字相等"（原文未删）。真实 F-LK2 组 `[16,35,10,56,18] ⇒ lost [184,165,190,144,182]`；旧组 `[12,19,7,26,43]` 与 `expected=200` 自不相容（`200−finals=[188,181,193,174,157]`）。**C1 关闭由父代理验证，非 reviewer 复签**——如需 reviewer 级复签应在下次复核中补。
## Round 35 补记账发现的缺口（2026-09-20 父代理登记，逐条附取证）

- **【记账·模式二结构性缺口，已立为计划级规则】零写入 reviewer ⇒ 卡内无裁决载体**：`M09–M12` 的 `review.md` **完全没有卡内裁决区**，其中唯一的 `accepted_scoped` 命中是**第 9 行的样板裁决词表**（不是裁决），裁决只存在于 `%TEMP%\m09m12-review-20260920-035628\REPORT.md`（40679 B / `5a44fd4e1e4dca5f8ad06d17fc759154741a6a22469145a837bcdf1615d21c4c`，§1 结论汇总 L16–28）。**风险本质**：`%TEMP%` 会被清理 ⇒ 若不在落定前固化，该批裁决将**永久失去唯一载体**，而 `handoff.status` 却已写 `accepted_scoped`，形成「有结论、无出处」的不可复核状态。
  - **处置**：报告按字节固化进四卡 `evidence/<CARD>/reviewer_report_m09m12.md`（父代理复算 **4/4 hash 一致**、read-back verified）；载体明写 `in_card_verdict_region = false` + `in_card_transcription_owed = true`。
  - **同位缺口**：`I-15-A` 同类（其 carrier 即 reviewer 自身报告块，已置 flag `review_md_has_no_verdict_region` + `carrier_is_the_reviewers_own_report_block`）。
  - **⇒ 计划级流程要求（强制）**：①凡 reviewer 采零写入模式，其报告**必须在任何载体落定之前**先按字节落进 attempt 并登记哈希；②**在 `review.md` 尚缺卡内裁决区时不得落任何载体**。
- **【载体·陈旧字段待对齐】6 张卡的 `reviewer_status` 与新 `status` 相互矛盾**：`M09–M12` 仍写 "no verdict received yet"、`I-14-B` 仍写 "a THIRD independent review round is required"、`I-15-A` 仍写 "PENDING independent review" —— 而三者现已 `accepted_scoped`。执行器按权限边界**未改该字段**（属实现者字段，改它等于实现者侧改写裁决周边语义），仅在 `status_authority.reviewer_status_note` 内注记 ⇒ **欠实现者一次对齐**（只改该字段，不动裁决字节）。
- **【读取纪律，父代理自身误判的更正】** `handoff.json` 的顶层 `status` 位于**文件末尾**，而 `"status"` 这个键在 JSON **内部子对象中大量重用**（I-04-C 内出现 5 次、I-04-D 内出现 5 次）。用 `grep -m1 '"status"'` 抽查会读到**子状态**（如 `"recorded, not re-run as an implementer command"`、`"done"`、`"closed"`），从而误判载体不合规。**实证**：`I-04-C` 顶层 `status` 在 L334 = `accepted_scoped`、`I-04-D` 在 L1157 = `accepted_scoped`，二者**均合规**。
  - **⇒ 读取纪律**：凡以载体字段作为记账依据，**必须 `json.load` 后取顶层键**（或取最后一个匹配）；**不得用首个匹配**。凡凭 `grep` 得出的字段结论，须经 JSON 解析复核后才可写入账本。本轮的「I-04-C/I-04-D status 异常」即为该纪律缺失导致的**假警报**，已在 `progress.md` round 35 段如实更正。
- **【记账滞后，机制性】账本追不上载体**：`progress.md` 最后写入停在 `c95f565e`（11:38），但其后 8 个提交（11:19–14:26）落地 5 张卡而无任何记录；`task_plan.md` 的计数口径同样滞后两代（「28/86」→「19+8+3」→ 实测 **61/3/1/21**）。**成因**：载体落定（`d4a42f5a` 落 19 张及后续批次）与 M08 三步转正**发生在记账动作之后**，而提交信息只写 `audit(planning): ...` 摘要、不回写计划文件。
  - **⇒ 流程要求**：多个卡在同一批落地时，**「落载体」与「写 `progress.md`」必须在同一次提交内完成**；提交信息若声称落地了 N 张卡，须同时给出归一后的 totals（`accepted_scoped` / `review_pending` / `blocked` / 未建），**禁止只写卡号不写总数**。
- **【口径归一，取代全部旧计数】当前唯一有效口径（2026-09-20 round 35）**：**已建 65/86；`accepted_scoped` 61 / `review_pending` 3（I-00-A、I-05-C、I-08-A）/ `blocked` 1（I-06-A）/ 未建 21**。旧口径「57/86」「19 张盘上可核 + 8 张条件性接受 + 3 张待补裁决」「28/86」**一律作废**。`disclosure_adaptation` 全卡 `unmapped`、`accuracy` 全卡 `unproven`，无一张外推；全部 iso-副本资格，不含生产部署。
- **【本次补记账的边界声明】** 本条为**事后补记**，**未新增任何裁决、未改写任何既有字节**：`progress.md` 以纯追加写入（前像 `104618 B / 04ddae77b2e551d261e5c230b3a6c7ea8735ad3eefa6a0914efe05fcfe6ffa1d` 经「移除新条目后重建」证明为精确前缀）；`task_plan.md` 仅改 `## Next Step` / `## Current Phase` 正文段与 Phase 7 checklist 的过期条目（前像 `11048 B / 5ee4d7f8207c7e600069968441f601eb732794d5e2d878cb0aa3b0b7d1f6d574`）。所有事实均取自盘上载体（`handoff.json` 顶层 `status`、`evidence/<CARD>/qualification.json`、`review.md` 裁决区、`_bookkeeping_20260920_carriers/summary.json`），未取自会话回传。
---

## Round 36 — 分支误切事故：确诊、恢复与取证（2026-09-20 父代理，逐条附证据）

> 本节取代本文件早前同一轮次的草稿表述。草稿把根因写成「`git checkout` 把工作树重置为 fcap 版本」，
> **那是错的**；实测根因是「后台 checkout 实际切到了 `main` 分支」。以下为订正后的记录。

### R36-1 事故：一次后台 `git checkout` 实际执行了 `checkout main`

**取证（`git reflog --date=iso`）**：

```
70dd9f6e HEAD@{2026-09-20 15:23:03 +0100}:
3ce9cc4d HEAD@{2026-09-20 15:05:08 +0100}: checkout: moving from fcap to main
70dd9f6e HEAD@{2026-09-20 15:04:13 +0100}: commit: [Checkout-checkpoint] from fcap to main (15:04:12)
8b7229c3 HEAD@{2026-09-20 14:26:05 +0100}: commit: audit(planning): I-04-E carrier landed, ...
```

**事实链**：
1. 15:04:13，仓库自带的分支切换保护机制先落一个**出站检查点提交** `70dd9f6e`（`[Checkout-checkpoint] from fcap to main`）。
2. `refs/heads/main` 指向 `3ce9cc4d`（`docs(audit): WU-1303 proposal — period_end as pure ISO + evidence notes`）。
3. **15:05:08，`checkout: moving from fcap to main`** —— 工作树与 index 被整体切换到了 `main`。
4. 15:23:03，HEAD 被改回 `refs/heads/fcap`（`git symbolic-ref`）。

**净结果**：`.git/HEAD → refs/heads/fcap` 且 `refs/heads/fcap = 70dd9f6e` **都正确**，
但 **index 与工作树的内容来自 `main`**。`git diff --stat main fcap` → **19500 files changed, 2453483 insertions(+)**，
故 fcap 独有的文件在工作树里表现为**已删除**。

### R36-2 为何被误判了一整个 round（本条是对我自己的记录，供后续 session 引以为戒）

round 35 里我把「`task_plan.md` 被回退到 fcap 原版」当作 checkout 行为的解释。
**`task_plan.md` 在 fcap 与 `main` 上内容相同**，因此「被重置为 fcap 版」与「工作树被切成 main」
在这一个文件上**表现完全重合**，我据前者得出了错误结论，事故被掩盖一整个 round。

> **纪律（新增）**：判定「文件为何变了」**不得只用「它变成了什么」**。
> 唯一可靠判据是 **`git reflog` 里的 `checkout: moving from … to …` 行**。
> 一个文件的回退在两种成因下都可能发生；只有当该文件两分支内容不同时，「它变成了哪个版本」才有判别力。

### R36-3 精确盘点（`build_restore_list.py` → `diagnosis.json`）

以 `HEAD`（= `fcap` = `70dd9f6e`）为基准：

| 量 | 值 |
|---|---|
| `fcap` tracked 条目 | 19633 |
| index 条目 | 19633（**条目数正确，仅内容陈旧**） |
| 工作树缺失 | **1758** |
| `status ' D'` | 1699 |
| `status ' M'` | 146 |
| `' M'` 中**真内容差异** | **67** |
| `' M'` 中 **index 陈旧伪差异** | **79**（占 `' M'` 的 **54%**） |
| 真差异总数 | 1766 |

**读取纪律（续 round 35，升级为强判据）**：`git status --porcelain` 的 `' M'` **不是**「内容有差异」的证据。
抽样三个伪差异文件，其 worktree blob 与 HEAD blob **逐字节相同**，且 `git diff HEAD` 输出 **0 行**：

| 文件 | 两侧共同 sha1 |
|---|---|
| `evidence/runtime_policy.json.baseline.txt` | `1ff80c5d82fc329ba1a2316ffcea4cd91dcaa53e` |
| `master_coverage.csv` | `0f129fd6066b6e5583b533837c7bae5a3a32fa48` |
| `reviews/aug09_plans/item_ledger.jsonl` | `26d860e56f1938f2f845ef9e7b41df0e0185b2e7` |

⇒ 分类必须以 `git diff HEAD --name-only`（或 `git hash-object` vs `git rev-parse HEAD:<p>`）为准，**不得读状态字母**。

### R36-4 恢复（三趟，全部经 blob 直读，绕开 index）

统一方法：`git ls-tree -r -z HEAD` 取 `path → blob sha`，`git cat-file --batch` 批量取内容写盘，
逐文件 `read-back == blob` 校验。清单落 `restore_manifest_fcap.json` / `_pass2.json` / `_pass3.json`。

| 趟 | 目标 | 结果 |
|---|---|---|
| 1 | 1758 个缺失文件 | `' D'` **1699 → 251**（进程被 SIGTERM 中断，非失败） |
| 2 | 补齐缺失 | `' D'` **251 → 0**；`skipped_already_present = 1448`（守卫生效） |
| 3 | **62 个仍持有 `main` 内容的文件** | 62/62 写入成功（校验见 R36-6） |

**第 3 趟为何必要**：前两趟带「已存在即跳过」守卫（见 R36-5），
因此**工作树里已存在、但内容来自 `main`** 的文件从未被修正。
由 `classify_diffs.py` 对剩余 67 条真差异逐一比对 `main:<p>` 与 `HEAD:<p>` 得出：

```
genuine differences: 67
  MAIN   : 62     <- worktree 内容 == main，!= fcap  ⇒ 必须恢复
  FCAP   : 0
  OTHER  : 5      <- 3 个本轮记账文件 + 2 个内嵌 .git scratch 目录
  ABSENT : 0
```

### R36-5 守卫与边界

**守卫（关键）**：恢复脚本对**任何已存在的工作树路径直接跳过**，绝不覆盖。
正是该守卫使本轮 3 个记账文件（内容 ≠ fcap blob）在前两趟中毫发无损。
第 3 趟为「必须覆盖」场景，故**反向**设置 `PROTECT` 白名单显式排除这 3 个文件，
并在执行前核验 62 个候选中**无一**落在 `.planning/` 计划根目录内（实测 `inplan = 0`）。

**正确性判据的修正（本轮第二个自我纠错）**：
第 3 趟初次报告 `failed = 62, reason = "sha1 mismatch after write"`，**那是我的校验错了，不是写入错了**。
本仓库 `core.autocrlf = true`，`.gitattributes` 另对 `*.py/*.md/*.json` 等声明 `text eol=lf`；
`git cat-file` 给出的是 **LF blob**，而写盘后 git 依 `eol` 规则转换，**on-disk 字节本就不等于 blob**。

验证（抽样）：

| 文件 | worktree sha | `fcap:<p>` | `main:<p>` | `git diff HEAD` |
|---|---|---|---|---|
| `SKILL.md` | `197bdc7c8cfbed6d36b997b8e73ff6310a5f85eb` | **同** | `0e6a16ef…`（不同） | **0 行** |
| `CHANGELOG.md` | `2810328f29017e12ba4a511efb7c8e5e6e55c48e` | **同** | `091f5bcb…`（不同） | **0 行** |

⇒ **纪律（新增）**：**不得用「on-disk 字节 == blob」作为本仓库的恢复判据**。
必须用 **`git diff <ref> -- <path>` 是否为空**，或 **`git status --porcelain` 是否仍报 `' M'`**，
因为这两者会自动套用 `core.autocrlf` 与 `.gitattributes`。裸字节比对会产生**大规模假失败**——
本次误报 62 例，若不纠正将导致对一个已经成功的恢复反复重做。

### R36-6 恢复后终态（已实测）

```
.git/HEAD          : ref: refs/heads/fcap
refs/heads/fcap    : 70dd9f6ee97a23506590e475e7cab1f64b5733f6
refs/heads/main    : 3ce9cc4d3ea91b15aad42eff1f55b72a44834dd7
' D' 缺失          : 0            (事故前 1699)
' M' 总数          : 84           (其中绝大多数为 index 陈旧伪差异)
git diff HEAD      : 5 条
' ??' 未跟踪       : 2            (.planning/_pwf_tmp/, .workbuddy-ai/)
```

**剩余 5 条差异全部为预期**：
- 3 条本轮记账写入：`progress.md` / `task_plan.md` / `findings.md`
- 2 条**既有已登记**的内嵌 `.git` scratch 仓库：
  `execution_runs/I-14-C/a20260919-01/r5/diff-apply-check/tree`、`…/r5/diff-repo`
  （见本文件隔离巡检节：这三处内嵌 `.git` 使父仓库递归报 `fatal: bad object HEAD`，
  已写入 `execution_runs/.gitignore` 兜底，**未删除任何文件**）

**记账文件哈希（三趟恢复前后完全不变）**：
```
progress.md   112641 B  6958954d3eafdc2dfe53b603152dd49ba35275a2b0873781a63b28028987bede
task_plan.md   19292 B  ff4d15e1626a9b1cc51ca641902ee13f868833f2c3da27aeb71474b05dcfca8c
findings.md    29979 B  8c207e346d63da9ff7d18050e7cce5b6f0be03c939a000519cfd68572a86bbae
```

**planning-with-files 自检**（恢复后）：
```
resolve-plan-dir.sh → C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit
check-complete.sh   → [planning-with-files] Task in progress (6/7 phases complete).
```

### R36-7 本轮踩到的四个技术坑（已全部沉淀入技能）

1. **`core.quotepath`**：`git ls-tree -r` 默认把非 ASCII 路径输出为 C 风格引号 + 八进制转义
   （`"a/\346\226\207....pdf"`），直接当路径用在 Windows 上抛 `OSError: [WinError 123]`。
   ⇒ 必须用 **`git ls-tree -r -z`** 取 NUL 分隔的原始路径。本次 310 个首轮失败中 **59 个**源于此。
2. **`ls-tree -r` 条目数会随 ref 变化**：首轮读到 19633，第 2/3 趟读到 19631。
   差异来自内嵌 scratch 仓库下的条目在 checkout 后被 git 重新解释。不构成风险，但计数时勿硬编码。
3. **`git symbolic-ref` 不回填 index 与工作树**：本轮即「HEAD 正确、内容错误」的直接成因，代价 1758 个文件。
4. **沙箱 safe-delete 是进程级钩子**：`rm` / `Remove-Item` / `os.remove` 对 stuck `.git/index.lock` 全部失败。
   本次全程未用 index 写，锁未构成阻碍。（本轮另测得该 hook 亦拦截部分 `open(...,'wb')` 场景的清理路径，
   故恢复脚本一律采用「先 `os.makedirs` 再 `open` 直写」的最小写盘面。）

### R36-8 边界声明（本轮未做的事）

- **未提交任何 commit**。
- **未写任何裁决字节**（`review.md` / `oracle.md` 均未触碰）：`verdicts_authored = 0`。
- **未改任何载体字段**：`carrier_fields_changed = 0`。
- **未动生产仓库**：`production_repos_written = 0`。
- **未修 index**（`git read-tree` / `git update-index` 均未调用），恢复全部经文件系统写入完成。
- **未删除任何文件**。
---

## Round 36 附注 — `reviewer_report_m09m12.md` 路径订正（父代理实测）

**订正对象**：本文件 round 35 节与 `task_plan.md` 中把该报告的落点写作 `evidence/<CARD>/reviewer_report_m09m12.md`。
该写法**有歧义**——计划根下并不存在一个统辖 M09–M12 的 `evidence/` 目录，按该路径去读会落空。
**实际路径**（本 round 逐卡实测确认）：

```
execution_runs/<CARD>/a20260919-01/evidence/<CARD>/reviewer_report_m09m12.md
```

即 `evidence/` 位于**各自 attempt 内部**，且其下再嵌一层同名 `<CARD>/`。

**四卡核验（本 round 复算）**：

| 卡 | 路径 | bytes | sha256 |
|---|---|---|---|
| `M09` | `execution_runs/M09/a20260919-01/evidence/M09/reviewer_report_m09m12.md` | 40679 | `5a44fd4e1e4dca5f8ad06d17fc759154741a6a22469145a837bcdf1615d21c4c` |
| `M10` | `execution_runs/M10/a20260919-01/evidence/M10/reviewer_report_m09m12.md` | 40679 | 同上 |
| `M11` | `execution_runs/M11/a20260919-01/evidence/M11/reviewer_report_m09m12.md` | 40679 | 同上 |
| `M12` | `execution_runs/M12/a20260919-01/evidence/M12/reviewer_report_m09m12.md` | 40679 | 同上 |

**结论**：①四卡**均存在**；②字节数与 sha256 **与 round 35 登记值完全一致**（40679 B / `5a44fd4e…`），
故 round 35 的「4/4 hash 一致」结论**成立**，订正的只是**路径写法**，不是结论。
③这是**纯文档订正**：未触碰任何报告字节、未改变任何裁决。

> **读取纪律（补充第 5 条）**：`.planning` 下写路径引用时，
> **`evidence/` 有两个层级** —— 计划根的 `evidence/`（8 项，放 `runtime_policy.json.baseline.txt` 等基线快照）
> 与 attempt 内的 `execution_runs/<CARD>/<attempt>/evidence/<CARD>/`（放该卡的裁决/资格文件）。
> 引用后者时**必须写全 `execution_runs/<CARD>/<attempt>/` 前缀**，否则会与前者混淆。
---

## Round 37 — D-W05 已批准（2026-09-20 16:45，owner 原话「批准 D-W05」）

**范围**：I-05-C 的 `produce_for_demand` 可从 **mock-only** 转**真实实现**，接进 CW `service.py` 现有 producer
（`CatalogConfig`/`CatalogStore`）；**不新增重复 parser**；调用事件记录在**实际调用边界**（不从结果表倒推）。**解锁 GAP-1**。

**不覆盖的范围（如实保留）**：
- **GAP-2 仍阻塞**：`consumer_analysis` producer **不存在**、真实 LLM 能力未验证 ⇒ 须 **RF `consumer_analysis` owner 提供入口**；**不得造绿色样例补全**。
- **GAP-3 待 reviewer**：`InvocationTracker` 事件 schema 需 reviewer 批准后方可生产持久化。

> **纪律**：`D-W05` 批准 = **授权实现**，**不等于验收**。`status` 保持 `review_pending`，验收归独立 reviewer；实现者与 owner 均不得自签。

**登记**：载体 `execution_runs/I-05-C/a20260919-01/handoff.json` → `rulings_applied["D-W05_producer_entry"]`
（5689 B / `d79a0438…` → 6926 B / `46c620b3…`）；owner 裁定单新增「十二、【已裁定·第三批】」
（28845 B / `eed9e7b5…` → 30767 B / `a40d32c8…`，追加式证明 **True**，新增 1922 B）。
**变更边界**：只改 `rulings_applied` 与 `next_action` 两个字段；`status` 未变；未写裁决字节；未触碰证据文件。

### 我自己的校验失误（如实登记，供后续引以为戒）

追加脚本内联的「移除追加段重建前像」证明**算术写错了**（少减一个分隔换行），首跑报 `append_only_proof: False`。
**但写入本身正确** —— 独立复核改用「定位追加段起点、取 `bytes[0:idx]` 算 sha256」，
得 `head bytes = 28845`、`head sha256 = eed9e7b5…`，**与前像逐字节相同**。

> **纪律（新增第 6 条）**：追加式证明**必须用「定位追加段起点」法**（`content.find(marker)` 后取前缀算 sha256），
> **不得**用「总长度 − 追加段长度」的算术——后者对分隔符数量的假设极易出错。
> 本轮错在算术、不在数据。

---

## Round 38 — 6 张卡陈旧 `reviewer_status` 已对齐（2026-09-20）

**触发**：记账批次（`_bookkeeping_20260920_carriers`）在六张卡的
`status_authority.reviewer_status_note` 内留了施工说明，明写
"the implementer should bring it into line" / "resolve the contradiction"。
本轮即执行该对齐。

**已对齐**：`M09` / `M10` / `M11` / `M12` / `I-14-B` / `I-15-A` —— 六卡的
`reviewer_status` 由「裁决到达前」的旧文本改为「裁决已返回且已注明载体位置」。

**证据链（写前先验，不采信自述）**：
- `M09–M12` 载体 = 独立 reviewer 报告 `5a44fd4e…`（40679 B）的 `## 1. 结论汇总`
  表（区 755 B / `9746d014…`），四行分别为 `resource` / `reserve_depletion` /
  `infrastructure` / `bank_revenue`，verdict 均为 `accepted_scoped`、授予「仅 `formula`」。
- `I-14-B` 载体 = `review.md` §5-b（`ab93734d…`，41849 B；区 10790 B /
  `0d5028a9…`；L315 标题、L322 结论）。
- `I-15-A` 载体 = closeout 报告（`9dafd6cf…`，39479 B）L294。

**边界**：只改 `reviewer_status` 一键；`status` 未动（六卡仍 `accepted_scoped`）；
裁决字节零改动；键序保留。`reviewer_status_alignment_provenance.json` 记录 6 份
文件的 before/after 双向哈希。

**遗留（明确不在本轮范围）**：`M09`–`M12` 的 `in_card_transcription_owed = true`
仍成立 —— 四卡 `review.md` 内仍无卡内裁决区，须 reviewer 本人或经其明确授权的
转录补齐，且须附前缀哈希证明（追加不改既有字节）。

**教训**：`status_authority` 与 `reviewer_status` 这两个字段**职责不同** ——
前者是记账批次写的**机器可读出处**，后者是**实现者字段**。记账批次因权限边界
刻意留空后者，属正确处置；但若**无人接续执行**，卡上就会出现「`status` 说已接受、
`reviewer_status` 说还没收到裁决」的自相矛盾。⇒ **凡记账批次在字段内留下
"should be brought into line" 一类的施工说明，必须同时登记为一条显式待办**
（本轮之前它只存在于字段注释里，靠本轮扫描才发现）。


---

## Round 39 — Owner 一次性总授权「给你所有批准」（2026-09-20 17:0x）

**处置原则**：待裁项约 40 条，**并非全部属于 owner 权限**。按权限归属拆为
**TIER-1 可裁 28 项（已裁）** / **TIER-2 需他方 15 项（owner 仅授权联系与启动）** /
**TIER-3 知悉 5 项**。逐项见 `OWNER_DECISIONS.md` 第十三节。

**决定性裁定**：`D-W06` OPEN-2 选 **A —— 幂等键必须含请求身份**。否决 B 的理由是
B 仍把「不同请求」表达为「同键异载荷」，属把业务语义错误延迟到运行时；且
`W06A-P1` 本就要求需求「含**原请求绑定**」，键含请求身份是该卡**既有硬要求**、非新立。
支撑证据为 c8/c9/c10 三个真实 CLI 探针（同一 `demand_id` 携带**首个请求**的
`request_sha256`，而两个仅 `as_of_date` 不同的请求得到 `d8afcf31…dd62` 与
`4bddf9e6…0b84` 两个不同摘要）。

**归档闭合一项长期待办**：第九节第 16 项（原标「最高优先」）—— 扩展模型版纳管**已完成**，
提交 `5db4734a owner-authorized: bring the extension model registry under version control`，
`scripts/model_extensions.py` 已跟踪、`model_registry.py` 锚定版（`9ec65295…`）已入库，
工作树与 HEAD 一致。**31 张模型卡的验收基准现已获得版本控制层的锚**。

**新增纪律第 7 条**：「总的批准」不得膨胀为「所有的结论」。owner 的总授权解除的是
**启动与实施许可**；凡专业裁判属他方者（TIER-2），最终结论**必须由该方出具**。
把 TIER-2 记为「owner 已裁」等同**伪造签名**。


---

## 【收尾】2026-09-21 —— 推送被 E2E 超时阻塞的定位结论

**现象**：`git push` 连续失败，报 `PUSH BLOCKED by pre-push gate (CI root-fix protocol)`，内层为
`subprocess.TimeoutExpired: pytest -q --tb=short tests/test_zr803_chaos_recovery.py tests/test_zr1103_journey_reverify.py tests/test_ca203_weekly_t3.py tests/test_fc1101_ci_manifest.py tests/test_compatibility_manifest.py tests/test_fc1002_three_process_e2e.py tests/test_ca302_three_journeys.py timed out after 600 seconds`。

**已排除的假设**（逐条实测）：
1. ~~门红~~ —— `drift_patrol` 七项 **ALL_GREEN**（含 `installation`/`manifest`，均已修根因）
2. ~~本地与远端分叉~~ —— `ahead=8 behind=0`
3. ~~自身并发负载~~ —— 机器降到 **2 个 python 进程**后**仍然超时**；故负载只是加剧因素，**不是**根因
4. ~~规格漂移~~ —— `input_snapshot.md`/`PLAN_MANIFEST.md`/`plan_inputs.json` 已修并**已提交**

**结论（已精确定位）**：七个 E2E 文件**全部通过**（55 passed / 0 failed），但**总墙钟 ≈861.7 s > 门的 600 s 子进程上限** ⇒ 推送必被拦。罪魁是 `tests/test_ca203_weekly_t3.py`（**387.1 s**，占 45%）。故根因是**门的超时配置**，不是测试失败、不是分叉、也不（仅）是并发负载——机器降到 2 个 python 进程后**仍然超时**，负载只是加剧因素。逐文件耗时表见 `REMEDIATION_REGISTER.md §十`。需要 owner 决定：①在更快或空载机器上推送；②提高门的 E2E 超时上限（改门属产品变更，须独立卡 + 红绿）；③拆分该套件以支持增量运行。
**纪律遵守**：**未绕过门**。8 个本地提交完好，工作全部落盘。

**方法教训（已写入事件记录）**：推送失败时**必须先看完整原始输出**——我此前用 `Select-String` 过滤，把 `TimeoutExpired` 与 `PUSH BLOCKED ... do not bypass` 滤掉，据此误判为"门红/规格漂移"，白花三轮。

---

## Round 67 — 中断形态、未跟踪载体、读取纪律补充（2026-09-21 编排层记账）

- **【新，流程缺口】「会话收尾声明」与「盘上状态」是两种东西。** `task_plan.md` 的 `【收尾·最终状态】` 节把 `I-14-D(r3)` 与 `I-14-E-APPLY` 记为「已派、结果未回收」，措辞读起来像「正在别处运行」。**实测二者是中途被打断**：`I-14-E-APPLY/…/after/bench.log` 末行为 `EXIT=3221225786`（= `0xC000013A` `STATUS_CONTROL_C_EXIT`，**进程被终止，非业务失败**），其后 `ARM B4-nonvacuity-quiet START` 只留下 **0 字节日志**；此后 **8 分钟零写入、零存活 python 进程**。
  - **⇒ 一般式：「结果未回收」≠「结果正在产生」**，两者**外观完全相同**。凡收尾声明把某物写成「在途」，须核对**它是否真有产出路径**（存活进程 / 增长中的日志 / 已落盘的中间产物）。与「**授权去做某事**」≠「**某事尚未做**」同族 —— 都属于**用谓词的外观代替谓词的实质**。
- **【新，载体风险】整目录未跟踪 = 该目录内的裁决**连基座都没有**。** `execution_runs/B5-plan-level-remediation/` **整个目录**未跟踪，内含 **34,764 B** 的 `reviewer_report.md`（B5 复审的**唯一**裁决载体）。这是 **T1-27** 已登记失效模式（「追加的裁决块只存在于工作树」）的**整目录版本**，且**更彻底**：追加块至少有一个**已提交的基座**可供回放，**未跟踪目录连基座都没有**。
  - **⇒ 计划级判据（建议）**：`git status --porcelain` 中出现的 **`??` 目录级**条目，若其内含**裁决/资格类文件**（`reviewer_report*`、`review.md`、`handoff.json`、`qualification.json`），**即按 T1-27 的红线处理**，不等「下次提交」。
- **【读取纪律·补充第 6 条】统计「待推提交数」必须用 `git rev-list --left-right --count <upstream>...HEAD`，不得引用会话内的记忆值。** 收尾节记 **8**，实测 **10**；差额来自收尾节写就之后又落的两个提交（`6d62b046`、`1bddfc1e`）。⇒ **凡引用「N 个提交待推」，须当场复算** —— 该量与 `progress.md` 的最后写入时点**无关**，因此**不能用「账本已记到哪」来推断它**。
- **【口径，非缺陷】`STATUS_CONTROL_C_EXIT` 不是失败码。** `3221225786` 只说明**有人终止了它**；把它读成「测试失败」会诱发对**未执行完的臂**作失败归因。⇒ **凡遇该退出码，正确结论是「未完成」，不是「未通过」**（与冻结 rc 码表的 `rc=2 无裁决` 同源：**判不了 ≠ 判了没通过**）。

---

## Round 68 — I-14-D r3 状态核验的三项发现（2026-09-21/22 编排层）

- **【新，悬空引用】F-R68-01：一个指向从未写出的记录的引用。** `iso/product_narrow_r3/.../observability.py` 的 r3 注释块明写「measured across the whole design space, **see `r3_fix_record.md`**」，而该文件**在 attempt 内不存在**。
  - **后果**：r3 最要紧的那条**设计取舍**（为何 `two-token-then-wrap` 这个形态**保持 OPEN 而不是修掉**——注释说修它会在另一形态上删掉 `doc=17`）**目前没有任何书面载体**。下一位读者只能读到「见某文件」，而那个文件不在。
  - **⇒ 一般式**：**引用的存在性是可判定的，必须判。** 一个把关键论证外包给「见 X」的记录，其证据力**等于 X 是否存在** —— 而 `r3_fix_record.md` 不存在。
- **【新，流程】「复现」与「收口」是两件事，本轮只做到了前者。** r3 的 oracle（28 行）与 rule table（79 行）**逐行零差异复现**，说明测量是真的；但 **`handoff.json`/`review.md` 仍是 r2 世代**（早于 r3 产物 1 小时以上）⇒ **迭代未收口**。
  - **⇒ 判据**：**「结果可复现」不等于「卡已收口」**。前者由重跑证明，后者由**载体存在且其世代晚于产物**证明——两者可以同时一真一假，本轮正是如此。
- **【新，口径】`rc=2 cannot_adjudicate` 是 fail-closed 的正面样本。** 全局解释器缺 PyYAML 时，attempt 的 harness 返回 **`rc=2`** 并写明 `ModuleNotFoundError`，**而不是**给一个基于错误导入的答案。
  - **⇒ 与冻结 rc 码表一致**（`rc=2` = 无裁决 / 判不了），**且与 `rc=3`（判了没通过）严格区分**。凡看到「工具跑不起来」，正确归类是 **rc=2 家族**，不得读成失败。
- **【自伤登记】两项判据错误，均属「闸红不是数据错」。** ①**字符转置**（搜 `+)"` 而源码是 `)+"`）；②**未归一化空白**（`fix_record.md` 硬换行成 `All\n  three FAIL`，裸子串跨不过换行）——**后者正是本文件上文 Round 60 已记录、并已写进 skill 的陷阱 17，在本脚本首跑上原样复踩**。
  - **⇒ 一般式（再次）**：**「写进 skill」不等于「下次会用」**；教训必须落进**默认动作**（此处已把「先归一化空白」写成该判据内的固定步骤，而非注释里的一句提醒）。

---

## Round 69 — 悬空引用、化石脚本、以及「代价要分类」（2026-09-22 编排层）

- **【新，判断】悬空引用**不要**用替代品去填。** r3 注释块引用的 `r3_fix_record.md` 不存在（F-R68-01）。本轮**拒绝**由编排层代写该文件。
  - **理由**：**悬空引用是显式损坏的**——读者立刻知道「那份记录不在」，会去找或去问。**替换品看起来权威，却不是作者本要写的那份**，于是下游会把它当原始记录引用，**洞被永久掩盖**。
  - **⇒ 一般式：补一个缺失的载体，只有在该载体是「可由测量重建」时才安全。** 无法重建时，**留下洞 + 供应实质（测量）**优于**造一个像样的替身**。本轮即按此办：文件不写，**取舍的实质用独立测量供应**。
- **【新，工具】脚本是「当时那套接口」的化石，接口一变就集体失效，而且没人会收到通知。** attempt 自己的 10 个设计探索脚本全部以 6 元组解包 `oracle.CASES`；r3 把它加宽为 7 ⇒ **全部 `ValueError`**。
  - **⇒ 判据（建议）**：`scratch/` 下的脚本**不得**被当作「可复跑的证据」引用，除非它**在本次会话内被实际跑过**。「它当时跑过」与「它现在还能跑」是两件事。
- **【新，口径】失败的**条数**不是代价的度量。** token-run 关掉 C10 换来「2 oracle + 2 rule」失败；但其中 **2 项正是登记残留行本身**（它们断言的就是那个泄漏输出，关掉泄漏自然转红）⇒ **真实代价是 2 项过度脱敏回归 + 2 行登记需重签**。
  - **⇒ 一般式**：**先分类，再计数。** 与「闸红要先分类：数据错还是判据错」同族——**同一张红榜上可以同时躺着缺陷、和正在正常工作的登记。**
- **【自伤登记】重打一个「就在模块里」的常量，是无收益地犯错的一种方式。** 我第一版用**重打的字面量**构造 RFC-7235 token 类，得到的 pattern 与盘上差几个字符 ⇒ 那次复现测的**不是盘上那个 pattern**。
  - **修正**：改为**直接用 `ob._AUTH_SCHEME_SPLIT`**，并**单独断言构造器忠实性**（喂盘上的 split 必须逐字节重建盘上的 pattern）。
  - **⇒ 一般式**：**能引用就不要重打。** 重打常量把「复现」悄悄降级成「重述」——而两者**外观相同**，直到你去做逐字节比较。

---

## Round 70 — 世代边界、以及一个差点被写进文书的手抄哈希（2026-09-22 编排层）

- **【新，机制】新一代的哈希表**不能**靠重写上一代的哈希表来维护。** r3 落定后，`after/final_hashes.json`（r2 世代的哈希表）对四个载体**已过时**。本轮**不改它**。
  - **理由**：重写它会让「r2 世代」与「r3 世代」的边界**消失** —— 下一位读者将无法判断某个哈希属于哪一次修订，而**世代边界本身就是证据**（它回答「这次改动是什么时候、以什么形态进去的」）。
  - **⇒ 判据（建议）**：**新世代的哈希表 = 新世代的载体**（本轮的 `handoff_r3.json`），旧表**原样保留**并**由新表显式指认它已过时**。
- **【自伤登记，重要】文书里的哈希只能是**算出来的**，不能是**写出来的**。** `review.md` 段的初稿里我为 `reviewer_report_r2.md` **手写了一个 sha256** —— 一个**从未由任何字节产生过的值**。
  - **被抓到的时点**：**脚本运行之前**（我在落笔前回头核对了真值）。
  - **若没抓到会怎样**：那个值**看起来完全正常**（64 位十六进制），且它出现的位置是**判决历史表**——下游会据此去核对一份对不上的报告，然后开始怀疑**报告**而不是怀疑**哈希**。
  - **⇒ 一般式（与 F-04-D 同源，但这次是**预防**而非事后修）**：**凡写哈希，必须来自 `hashlib` 的当场输出，且写完立即复算断言。** 「我记得是……」是**生成哈希的最坏方式**。
- **【正面】把「悬空引用不代填」的判断贯彻到底，代价是可接受的。** Round 69 拒绝代写 `r3_fix_record.md`；本轮落定 r3 世代时**同样没有**顺手补它，而是把它的**实质**（设计取舍的复现）**另置**于 `_r3_design_reprobe_20260922/`，并在 `handoff_r3.json` 里写明「源注释欠一次更正」。
  - **⇒ 结果**：**读者拿得到实质，作者的名字没有被冒用，洞仍然可见。** 三者同时成立，代价只是**一条已知的、被登记过的悬空引用**。

---

## Round 71 — 独立复核回收后的三条教训（2026-09-22 编排层）

- **【新，重要】「当时为真」≠「现在可复现」。** `handoff_r3.json` 把 Round 68 的状态核验引用为「overall PASS, idempotent」；**Round 70 追加了三个它固定哈希的文件** ⇒ **重跑给出 `overall FAIL`**。reviewer 据此把「carrier 不得夸大」判为 **REFUTED**（`F-REV-R3-02`, MEDIUM）。
  - **⇒ 一般式：引用一个验证结果，必须同时给出它的「可复现前提」。** 一个被固定哈希钉住的核验器，**在它钉住的文件被合法追加的那一刻就自动失效** —— 而它**不会报错**，它只会**从此报红**，于是**「当时为真」与「现在为假」被同一次引用混为一谈**。
  - **做法**：凡在载体里引用既往核验，写清**它钉的是哪个世代的字节**，并注明**该引用是否仍然可复现**。本轮已在 `review.md` 与本轮记录中按此写。
- **【新，方法】「构造器忠实性」保证的是「我在测盘上那个 pattern」，**不**保证「盘上那个 pattern 是对的」。** Round 68/69 的复现器**用盘上的 `_AUTH_SCHEME_SPLIT` 构造 pattern** —— 因此它**结构上不可能**发现该常量内部的缺陷，而 `F-REV-R3-01` **恰好在常量内部**。
  - **⇒ 一般式（自指盲区）**：**用一个取自被测对象的常量去构造判据，判据就对该常量免疫。** 这类盲区**外观完全正常**（判据忠实、可复现、有负控），只有**独立的、不取自被测对象的**检查才能穿透。
  - **这正是独立复核不可被自检替代的原因**：本轮自检给了「8 命题 + 7 负控全绿」，而独立复核在**同一天**给出了一个 BLOCKER。
- **【新，正面】流程要求真的挡住了一次损失。** 本仓 Round 35 立的要求是「reviewer 采零写入模式时，其报告**必须在任何载体落定之前**先按字节落进 attempt 并登记哈希」。本轮派单时**明写**该要求，reviewer **照办**：`reviewer_report_r3.md` 44008 B 先落盘，随后才登记哈希并落定裁决节。
  - **⇒ 对照**：`I-10-B` 与 `I-05-C` 两例的裁决**只存在于消息里**，其中一例的原始报告**在 `%TEMP%` 被清理后不可复核**。本轮**没有**重演。

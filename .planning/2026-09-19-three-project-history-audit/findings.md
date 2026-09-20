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

## 跨批复核发现的共享缺陷（2026-09-20，父代理登记）

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


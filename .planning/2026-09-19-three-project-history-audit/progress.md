# Progress

## 2026-09-20 — 实施段：并行推进 I-08-A / M01–M04 / I-14-C / I-15-A / I-04-C（4 张接受、2 张返工）

- **接受（+7 卡，累计 22/86）**：
  - **I-08-A（设计，accepted_scoped）**：三层证明域 L1/L2/L3、`host_signed` 只能由 L3 验签产出、provider 协议（一次性子进程 + 精确字段集 + fail-closed 错误码表 **E01–E32 唯一来源**）、信任域三元组（fingerprint∈名单 ∧ issuer==声明 ∧ 时刻在窗口 ∧ active）、规范载荷（`canonical_sha256` 的 64 字符 ascii hex、排除自指字段）、重放/过期分离、旧版本 **G1/G2/G3a/G3b/G4 与 `classify()`**、**schema 3.8 → G3a 不得自动旁路 + R-LEGACY-1 + E29**、`public_keys` 键名冻结 + 非法名单**报错不静默**、参数 `W`/`T`/`L` 化并登记 OPEN-D7。三轮复审：r1 changes_required(6×P1) → r2 changes_required(R-BIND-1/2) → **r3 accepted_scoped**（复审独立写配对校验：32 码 0 mismatch；作者新 `check_r3_pairs.py` 对两类变异**均检出**）。**未授予**：provider 协议"无未决"（OPEN-D6/D7+三参数）、旧包兼容"已定案"、`tests/test_attestation.py` 可直接复用；**OPEN-D1…D7 已按裁定方入 handoff**（D1/D2/D3 建议同批）。
  - **M01–M04（**仅 formula 资格**，accepted_scoped）**：direct_growth `[220,110,0]`+11/11 负例、direct_revenue `[80,0,120]`+11/11、unit_sales `305`+13/13、capacity_utilization `730`+15/15，连续性/默认值/单位与容差全部独立复算；披露映射用真实年报（紫金 FY2025 P15、比亚迪 FY2024 P23、中芯 FY2024 P6/P8/P84）并**明确 disclosure=unmapped、accuracy=unproven**（M04 命中 STOP：期末产能年化 vs 披露差 +21.40%）。三轮：r1 accepted_scoped(5 项必修) → r2 修 → r3 修（含**破坏"仅追加"形态的更正已自曝**）。**F-M02-01（被忽略字段仍受域约束）待 owner 裁定**。
  - **I-15-A（**仅证据/诊断资格**，accepted_scoped；产品实施 blocked）**：冻结 W15-R1..R8 + 固定样本，反例证明现产品"空目录也删/同日覆写/时钟取目录名/TOCTOU/崩溃后不可恢复"；**D-W15 五项未签 ⇒ 不得实施、不得生产 prune**。
- **返工中**：
  - **I-04-C（设计）复审 changes_required**：**P1** ADR-10 未定义"最后退出者非 owner 且无义务"⇒ 实测留下**永久 paused**；**P1** 认领周期缺 owner 证据校验 ⇒ 实测对**第三方持有的 pause 执行 resume**；P2 generation 非单调、**证据/报告不符（实际 9/16 例失败、25 条失败检查，报告写"10 PASS/6 failing"，`parse_run.py` 误判）**、F-L4a 无结果（harness 缺陷）、ADR-11 未落实；授予 ADR-1/ADR-3 核心/ADR-4 lease_id 轴/fail-closed/预算组合。
  - **I-14-C（实施）**：r1 的 3×P1 已闭合（左锚改 `(?<![A-Za-z0-9])`、真实 CLI 出口 E5a 命中 0、前像更正、E4a 变 load-bearing、记账更正），但修复**新引入正则 O(n²) 回归**（`_` 密集串 k=40000 >20 s）⇒ r3。
- **本批的隔离事故（已处置）**：I-14-C 直接编辑了**生产工作树** 3 个文件（worker.py/observability.py/cli.py）；复审判定违反"生产零代码合并"，**父代理已 `git checkout HEAD --` 三者回退**（现 company-wiki porcelain 仅 ` M CLAUDE.md`/` M README.md`），修复内容只留 `changes.diff` + `iso/product_fixed`；并要求后续实施卡一律在 `iso/` 内做。

## 2026-09-19 — 实施段续：I-04-B（filing-fetch 预算修复**实施卡**，两轮复审后 accepted_scoped）

- **产出**（execution_runs/I-04-B/a20260919-01/）：iso 副本（scripts+tests）、binding.json、oracle.md、commands.json（8 条命令全绑定）、iso_patching.md、decision.md（NA→I-04-A）、recovery/README.md、changes.diff（48 hunks）、before/after 证据、review.md（两轮）、handoff.json（accepted_scoped）。**生产零改动**（`fetch_filing.py` sha256 `046cc7dc…088`、tests `3087daf0…`、HEAD `d35b6f5` 每轮复核）。
- **修的是什么**：① 退避改用**子调用返回后**重算的剩余预算（原来用调用前的过期值：9 s 调用 + 5 s 退避 = t=14 > deadline 10，即 `pure_probes.json` 记录的历史事故）；② 删除 `_remaining()` 的 `max(10.0,…)` 下限，请求阶段预算无下限、截止后**零请求调用**；③ 清理用**独立预算** `C=max(30, 2×resume_wait+graceful)` 并单列 `cleanup_calls/cleanup_elapsed_seconds/cleanup_status`；④ pid 存活探测（原硬编码 20 s、不计账）改为 `min(20, 相位预算)` 且现读、计 `liveness_calls`/`liveness_probe_failed`；⑤ 信封新增 `request_deadline/request_elapsed/pause_action` 等分账字段。
- **证据链**：修前 RED **5 failed / 2 passed**（失败原因是实测 `[call(5.0)] != [call(1.0)]`、截止后仍以 `timeout=10.0` 发 worker-status、`10.0 > 0.2`、真进程 3 s 桩未被杀）→ 修后 **10 passed**；T-FILING **116 passed（基线）→ 126 passed / 1 deselected / 41 subtests**，被触碰的两个既有用例**断言与生产逐字节相同**（只改时钟脚本）。ε 按 I-04-A 预承诺程序重测（两次独立进程调用、原始样本留档）：第一版 0.57、修订版池化 0.38，**签名取最大值 0.57**（避免协议改进被读成放宽）。
- **两轮独立复审**（同一只读子代理，零写入）：r1 **changes_required**（**1×P1** 探测未按签署 `min(20,·)` 封顶，实测误授 44.9998/85.0；+4×P2 取证/接续 +5×low）→ 全部处置 → r2 **accepted_scoped**；随签 2 项非阻断条件 **C1**（守卫与 `_register` 双重读取的微秒竞态 → 已改为"只读一次"，并加三值时钟边界子案）与 **C2**（命令记录陈旧 → commands.json 重写 + iso_patching 旧数字标注）**均已处置**；3 项 carry 记入 handoff（信封探测耗时/相位墙 → I-04-E；跨进程 lease → I-04-C/D；相位墙只报告不设上限为持续口径）。
- **资格**：accepted_scoped=隔离副本内的预算规则修复；**不授予**真实 provider/worker（I-07/I-16）与跨进程并发（I-04-C/D）。**16/86 卡完成**；下一卡 I-04-C（冻结跨进程 lease/所有权/恢复协议）。

## 2026-09-19 — 实施段续：I-04-A（deadline/清理预算/计时 oracle **设计卡**，两轮复审后 accepted_scoped）

- **产出**（execution_runs/I-04-A/a20260919-01/）：binding.json（锚点 sha256 `046cc7dc…` 复验一致）、decision.md **v2**、oracle.md **v2**、commands.json（仅 2 条设计测量，无产品命令）、两份设计测量、review.md（两轮全文）、handoff.json。生产零改动；FF 树未动。
- **设计要点**：D0 三缺陷=过期预算（`max(10,…)`，F-D2）、陈旧剩余（L304/L326 ⇒ wait=5、t=14，pure_probes 实证，F-D1）、清理与请求不分账（F-D3）；阶段预算表含**新增 R-P 行**（tasklist pid 探测 L418-432：请求段 `min(20,请求剩余)`/清理段 `min(20,C)`，计 `liveness_calls`）；`_cleanup_timeout()=C`、**C=max(30, 2×resume_wait+graceful)**（默认 30）；TimeoutExpired=**终态**（否决改重试集）；清理义务=最后参与者（joined 含在内）；ε=0.4 **临时签署**+范围限定+预先承诺重测程序；B=20 仅请求段；新 stats 字段含 `liveness_calls`/`liveness_probe_failed`。
- **两轮独立复审**（同一只读子代理，零写入）：r1 **changes_required**（1P1/2P2/5P3，核心是 D3 未落实父项"返回后重算剩余"——按 v1 字面实现会复现 t=14 历史事故）→ 全部处置 → r2 **accepted_scoped**；预注册变化案例（deadline=30 三连争用）被 v2 规则逐数值复现。**随签携带 1 条 P3 强制口径**给 I-04-B：清理验收按**子调用**（resume ≤ C+ε；每探测 ≤ min(20,·)），相位总墙钟单列；另 ε 重测程序是 I-04-B/E 真实进程验收的前置。
- **资格**：accepted_scoped=仅本 attempt 的设计文本；不授予产品实施权。**15/86 卡完成**；下一卡 I-04-B（开工前重验源码 hash 并携带上述两项强制条件）。
- **交付时的门偶发（登记，未归因到具体步骤）**：本卡提交后**第一次** `git push` 被 pre-push 门拦下（rc≠0），可见的 stderr 只有两行 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd4 in position 17`（子进程侧 traceback 尾部）与 "PUSH BLOCKED"；**我没有留存该次的完整子进程输出**（当时的输出被我自己 `Select-String` 过滤后丢弃），因此**不指认**是哪一步失败。事实：树在两次推送之间**未改动**；随后直接重跑 `tools/pre_push_gate.py` 与再次 `git push` **均绿**，提交已推送（`2028576`）。**未绕过任何门**（是重跑通过，不是跳过）。可核事实：本次提交的 12 个文件经字节级检查**均为干净 UTF-8、无 BOM**；门自身的子进程解码已是 `errors="replace"`（其注释记录了 2026-09-08 同类事故），故那次报错来自某个**子步骤的子进程**而非门本体；`0xd4` 是 GBK 首字节（"曾"），提示消息里带 `C:\Users\郑曾波\…` 路径。**建议**（未做）：下次复现时保留门的完整 stderr 并在 `_run` 里打印失败步骤标签，以定位那条仍会把中文路径写成 GBK 的子进程。

## 2026-09-19 — 实施段：I-00..I-02 六卡（产品实施开始）

- I-00-A a20260919-01：三仓 HEAD/dirty/锚点/baseline.json/paths.json 快照说明齐备；47G catalog WAL=0、全量快照延后、backup proven；iso venv fallback_free=true；全局 Miniconda python 判不安全（editable dayu-agent 钩子）；独立reviewer发现两份 git 证据误捕获，已重采并 errata 关闭。
- I-00-B：8 个源码锚点 sha 绑定；3/3 样本 raw+sidecar+request 精确hash一致；负绑定规则生效；accepted_scoped（P1-3 非阻断）。
- I-00-C a20260919-01：iso 副本 gate（scenario_gate）+closure 接线，13/13（N1..N6/P1/X1）；改前对照复现 197 bare-passed；生产 uc 0 改动；steps=6/9 saga 下一步=4 留组合键专业冻结 open。
- I-00-D：company-wiki CLAUDE.md+README.md 边界横幅落地（生产文档唯一产品侧变动）；四问干读由 reviewer 独立复验；DEPLOYMENT/OPERATIONS/使用说明书 NA。
- I-01-A：D-W01 在 config.py 内 shared effective_root_profile+六错误码；五组正反例全过（CFG-REAL half_activated 逐根、CFG-FIFTH 陌生 root 不拒、N2 四类分离、N3 两类）。
- I-02-A：D-W02 ScanReport completion_status/per_root_results/target_files+writer 四道门；P1/N1/N2/N3a/b/c 六用例独立 reviewer 重跑 rc=0；raw/staged 字节保留验证。
- 均限定：资格=各自 attempt review.md 的 accepted_scoped；无生产代码合并；worker 保持 paused；不构成弱模型 pilot 或生产部署。

## 2026-09-19 — 实施段续：I-02-B/C/D（错误传播与注册恢复链闭合）

- I-02-B a20260919-01：D-W02 补充冻结 cross-cli-error-envelope/1.0（bool retryable fail-closed、嵌套 cause 原样、side_effects 真实计数）；9 case 跨进程真实链路（根 CN403 重放→P1；800字符不截断 N1；未知码/字符串'true'/畸形JSON fail-closed N2；download_events=1 不伪报 N3；DB busy vs 身份错 retryable 区分 N4+exit_probe）。source_preparation 的 800字符 stderr 截断已删（完整存档+短摘要）。
- （笔记：上条原文 '500字符' 为笔误，正确为 prepare_source 的 800字符截断。）reviewer 重跑 9/9 rc=0；信封契约须 I-04 owner ratify 后释放 FF 侧。
- I-02-C a20260919-01：读 register_existing_raw R1-R7 门（root可复性→containment→sidecar→字段完整→字节重算→身份契约→retired拒+I-02-A四道门与exact-identity门）。P1 两原件（HK ffd733…/4405561、US e3de0053…/8585615）零 provider 调用注册成功并 exact resolve；P2 二次复用同 identity 零新增；N1×4 逐项拒；N2 retired/denied fail-early（_reactivate 计数0）。envelope 如实 not_reviewed/bundle_usable=false——复用≠审核工件资格；生产 catalog 零写入。
- I-02-D a20260919-01：逻辑完成键（content_sha256 唯一） vs 审计 attempt 键（outcome hash 去重）冻结；P1 四次重入=业务1行、审计2行；P2 两真实 subprocess exit0/exit2(明确可重试) 不丢 journal；N1 同bytes异身份不 dedup、staging 保留；N2 三变异不命中旧完成不覆盖旧 raw；N3a dayu 同bytes 落 company_raw 不落 dedup、N3b retired 拒+reactivate spy=0。主要 delta=dedup 资格 exact-resolve 门。跨进程锁 owner 留 I-04。
- 状态推进（10/86 卡）：I-00-A/B/C/D、I-01-A、I-02-A/B/C/D 全独立 accepted_scoped；资格均为 attempt 限域（无生产代码合并；生产文档仅 I-00-D 两处）。下一步 I-02-E（持久化边界中断后恢复）。
（注意：原文的"1000字符"为笔误修正——I-02-B 删除的是 prepare_source 的800字符 stderr 截断。）

## 2026-09-19 — 实施段续：I-02-D/E（幂等与崩溃恢复，I-02 链闭合）

- I-02-D a20260919-01：完成键(content_sha256 唯一业务行) vs 审计 attempt 键(outcome hash 去重) 冻结；P1 四次重入=1行+审计不压缩；P2 两真实子进程 exit0/exit2(可重试竞争)共享目录1行不丢journal；N1 同bytes异identity不伪报 dedup、staging保留；N2 三变异不命中旧完成；N3a dayu同bytes落company_raw、N3b retired reactivate spy=0。dedup 仅在 exact-resolve 资格门之后；锁域留 I-04。accepted_scoped（reviewer 独立重跑 8 case rc=0）。
- I-02-E a20260919-01：禁区-恢复表（5边界×证据/允许/禁止/blocked）senior冻结后改码；P1 五边界 resume 仅补缺失阶段（B1/B3/B4/B5 真实 Popen 硬终止留证：PID+returncode+scan_runs interrupted 行保留+部分提交不删）；B2 sidecar 由持久字节重建非猜测；N1a/b blocked+raw保留、N2a 不catch-continue不删锁、N2b 只block+人工剪尾(坏尾.corrupt-tail保留,自动修复被冻结拒绝)、N2c stale takeover 非删锁、N2d identity冲突、N3a drift不覆写、N3b epoch回退重新资格审查。reviewer 独立重跑含真实 kill 场景 rc=0；观察项 O1-O5 记录（B5 durable 跳过未命中、N1a blocked 布尔账目笔误等，均不阻断）。
- 至此 I-02 整链 A-E 全 accepted_scoped（资格均为隔离副本+attempt 限域，生产零代码合并；跨进程锁策略属主已移交 I-04）。11/86 卡完成。

## 2026-09-19 — 实施段续：I-03 全链（契约→选择→绑定→事务）

- I-03-A a20260919-01（设计卡）：15 格 oracle 全定案（C01–C15，无 TBD）；期间键=(kind,period_start,period_end) 三元组、fiscal_year 仅展示；filed_at 唯一新近性主键+accepted_at 校验+四态（ordered/ambiguous_same_day/conflicting/unknown_missing_date）；反向本地不降级+latest_status=unknown_if_remote_confirmed_newer；有界批次 max_batch_size=8+completed_partial+remaining_count；canonical JSON+hash_schema_version=1+全资格字段+policy epoch 唯一来源；compatible-matrix 八类字段变化全 fail-closed 失效。独立 reviewer 15/15 复算一致后复签。字典序缺陷真实行号=gap_plan.py L167-170（hash 侧 L228-242）。
- I-03-B：iso 副本删字典序接冻结规则；修前 RED→修后 21/21（G-B1..B5 + C01–C14 纯选择面全复现；C15 执行面声明移交 I-03-D 或后续）；逆序 gap_hash 等价；I-03-A 未定义组合保守落 unknown 桶并列为高级裁决 open，不私自定案。
- I-03-C：独立序列化器（不 import 被测 helper）冻结 P0 canonical 786B / SHA b9c1847975c8…_24（reviewer 独立重算逐字符一致）；G-C1 URL/date 变异 hash 必变+A0 拒+fetch=0（历史反例关闭）；G-C2 14 单字段变异全触发；G-C3 顺序重排同 hash；G-C4 额度/过期/缺provider/旧版收据 fail-closed。29/29；reviewer 保留案例 id=z-fresh-1 独立 PASS。
- I-03-D：四事件类型（fetch_attempt/bytes_received/raw_saved/registration_succeeded）替代单计数；G-D5 stale binding 锁内真出口拒+fetch=0；G-D6 两缺期 max_items=1 → completed_partial+pending_next_batch 不全绿；G-D7 60+60=120 如实、超额即停 commit=0；G-D8 run1 fetch=1/raw_saved=1/registered=0 → run2 只恢复注册 fetch=0（复用 I-02-C R 门）；G-D9 异常 vs 空成功 vs 本地复用不越权。36/36。父项 I-03 不因本卡标注全完成（I-02 生产重试注册接线未完成）。
- 完成 14/86 卡（I-00×4、I-01-A、I-02×5、I-03×4），全部 accepted_scoped、生产零代码合并。下一卡 I-04-A（deadline/预算契约设计，filing-fetch）已建 attempt。

## 当前交付状态

历史正文、逐项判定、交叉复核和最终交付已完成。implementation_plan 的18工作项已开始实施（见上方实施段；6/86 卡 accepted_scoped，全部隔离副本资格）。下列旧“进行中”段落保留为过程历史，不代表当前遗漏。最终文件完整性结果见delivery_validation.json及reviews/second_wave/final_review_checks.json。

用户后续要求的执行细化v2也已完成：86张卡及独立干读/结构验证，入口execution_v2/README.md。仅文档细化完成；较弱模型的实际隔离试执行和产品修复均未运行。

## 2026-09-19 — 新审计启动
- 用户明确要求三个项目所有planning-with-files历史文档（含子目录）、每条内容及已审计通过项重新独立审查，多代理、多步骤执行，交付新的计划和实施文档。
- 已阅读技能、创建并解析命名计划；未读取任何本地agent会话存储。
- 已检查CodeGraph结构及当前git diff统计；接下来保存递归清单并拆分独立审查。

## 2026-09-19 — 递归清点与第一波并行
- 宽召回扫描：RF1423份Markdown、filing11份、wiki8452份。初选工程相关1018份；补filing关联3份，保留全部未选路径供覆盖质疑。
- 排除252份web/docs公司/行业/主题投研正文（非工程planning）；范围manifest暂计历史计划/证据609份、工程背景160份，共769份。此计数不是已语义审查数。
- RF嵌套旧wiki快照109份：64同字节、44仅解码分行后相同、1文件1行内容差异；已确认非同文件、非目录junction。snapshots不继承生产PASS，仅共享相同文本审查映射。
- 第一波代理：history_revenue审RF主线402份；history_filing审filing11份；audit_independent审wiki247份中v5/worker主线，后续按handoff分簇。
- 明确工程背景和被审业务内容边界：污染条目清单可作历史修复证据，不据此声称重验所有投资事实。
- 审计脚本首次Projects路径多取parent导致WinError267，已仅修审计脚本；无产品变化。
# 2026-09-19 续审进展（独立逐项阶段）

- 范围v2共769份工程历史/规划上下文Markdown，另252份业务生成正文明确排除。历史wiki嵌套快照109份中108份解码分行相同，1份证据合同有真实差异；版本路径和字节hash均保留，文字相同不继承运行通过。
- filing初审覆盖11份Markdown的400语义条目、89结构块及另55条receipt/terminal字段。280 tests/78 subtests隔离通过；2 live deselected与1 symlink skipped均不算通过。独立clock/refcount/plan-verifier反例另存证据。
- revenue已列262个原义务（25 CA + 92 ZR + 71 FC + 74 WU），其中117 CA/ZR已逐ID初审；其余及776 checklist继续审查，不能把枚举计为完成。
- wiki只读复算v5当前冻结51/51文件hash匹配；config_doctor实际exit0但未校运行flag与root adapter兼容，生产config/policy/worker哈希前后不变。v5冻结通过只证明规划包一致性。
- root的45份painpoint/planning-sync文档提取3461内容块，提取器不自动赋审查结论。分批全文阅读/逐义务映射仍在进行。输出被截断的调用仅计实际可见范围，不标全文完成。
- 三个独立代理仍在工作；无源码、生产配置、catalog、raw、worker或计划指针修改。

## 2026-09-19 — 原始正文与后继修复交叉核对
- root已完整阅读45份跨项目painpoint/planning-sync文档，按60项人工语义判定保留3461原文块；又完整阅读6份早期revenue正文5758行，按49项人工语义判定保留4421非空行。发生次数不是缺陷数或通过测试数。
- 47个冻结输入绑定（46唯一文件）hash复算一致；117原ID/痛点/旧判定映射一致；104编号=88实施+16映射、36测试组与44主步骤独立复算。仅证明文档结构和字节，不证明产品已完成。
- 旧35代码/证据指纹24相同、11不同。当前GapPlan隔离反例复现：accession字典序误判新旧、无period分组歧义、URL/日期变化未改变动作授权hash；未改生产数据。
- revenue代理已完成262原义务、776checklist、31模型审查；117单元116份现存最终卡及77 RED全文读完。模型隔离97passed+216subtests；发布4套37passed，同时普通源文件可触发host_signed无签名及registry写后输出失败两个反例成立。
- 早期F01/F02已有后继实质修复；全绿但漏签名状态和整组事务必须分别描述，不把历史所有问题当当前仍在。
- wiki审查确认v1–v4曾FAIL/中止，v5只冻结交接并未声称产品实施通过；其条目不能写成“修好又回归”。WR后继真实139P/10生命周期/7背景测试予以有限承认，同时不代替原CW3–10严格验收。
- 根接手wiki archive17份的逐文语义审查，代理继续其它分区。全范围审查尚未完成，当前不发布全部完成结论。

## 2026-09-19 — 全文补齐、第二波交叉复核与新计划

- revenue主线最终397份：代理313、root56、另一独立代理28；不是早期分派稿误写的402。另114嵌套旧副本单独映射。自有313份5519段中5428语义发生、91导航/分隔，全部非空行和1276个判断引用通过连接完整性检查；连接检查不代表产品PASS。
- wiki主体245全文：独立wiki103、legacy46、root归档17/跨计划45/上下文5、revenue附加FC29；另外混合污染清单1及误命中raw新闻1分别处置。filing11全部审完。全局766全文、2混合清单工程部分、1raw排除，共769；master_coverage无pending。
- root补完8/9全部26份、8/12与9/18实跑24份、wiki归档17份及最终5份上下文。另一代理补8/13两计划28份，97人工判断保留2497语义行与462结构行；26规范+30快照hash匹配。
- 根独立复算8/12草案15个年度总额差0、结果文件hash匹配；13份实跑日志哈希匹配，30个历史location/artifact/新raw字节hash匹配。未运行新下载、正式预测或共享producer。
- 第二波：audit_independent复核root175个人工case与报告；history_filing复核revenue31模型/24深层项/探针/实施计划；root完整复核分区报告及高影响原证据。接受修改规范判定对象、selector有限通过、错误路径、pause/13命令口径和TC条件范围。
- 新实施文档明确先生产配置/注册、再审核/工件与真实旅程；签名/事务与模型研究可并行；最后冻结样本外和实际部署观察。复用既有工具，不新增第四套框架。加入原验收器反例、旧活动手册退役提示、deadline每次重算、角色按需、payability唯一归属、真vintage与历史重建分开、预注册留出集。

## 2026-09-19 — 完整性与审计自身错误

- 357个旧产品基线文件当前356相同，company-wiki normalizer旧hash等于f39bd5a父commit blob，新hash等于f39bd5a。提交记录为其它agent；本审查四作者均未写产品。R4三份MD并发新增正文已补读并同时保留旧inventory及新review hash。不回滚用户并行修改。
- 三个生产config/policy/worker-control文件与本轮副本字节相同；不宣称整个工作区/活跃DB静止。
- 几次命令输出截断均分段补读；默认stdout GBK或错误相对cwd只影响审计工具，未作为产品缺陷。一次多文件apply_patch因最后片段不匹配整批失败，确认未改后重新正确应用。
- 初始两仓Git HEAD读取因ownership失败为空；两次用空HEAD作diff均exit128，只保留失败。后以明确f39bd5a及其父blob的hash核实正常变更，未修改全局Git设置。
- 最终交付检查读取769来源hash、Markdown链接、JSONL格式；当前无缺漏/坏链。该检查只证明交付完整性，不重新认证所有历史运行。

## 2026-09-19 — 独立终审与封存

- audit_independent完整复核最终报告和实施计划，独立重算766全文+2工程部分+1排除、769唯一路径、890含重复审查引用及9阶段18工作项。FR-01/02措辞修订已复核关闭；history_revenue对最终计划无阻断意见。
- 本轮task_plan五阶段完成。新实施计划仍全部待实施，不以审查完成替代产品验收、三公司正式预测或准确性证明。
- 完成文档收尾后运行validate_delivery.py，再运行独立final_review_check.py刷新最终hash。结果保存在上述JSON，不沿用中途文件版本；检查范围仅为交付元数据和可追溯性。

## 2026-09-19 — 执行计划细化启动
- 用户追问弱模型可执行性后要求改进；原总纲保留，增加执行卡、固定案例、设计门与独立验收。沿用原多代理授权并复用三名审查者，主审维护唯一计划入口。仅文档和审计辅助材料，不修产品。
- 重新解析原PLAN_ID成功，读取三份PWF状态；git diff显示34个既有/并发修改文件，未清理或归属本轮。


- 主审新增固定九步协议、专业设计门、命令绑定模板、独立验收/接续、弱模型试点方案和基线/真实旅程/测量/部署卡；创建三市场固定矩阵。
- build_samples仅从旧已审证据提取原身份并只读重哈希3份raw，3/3匹配；5个live/泛化样本保持unbound，未运行provider或catalog。
- 两次按缩略路径读取旧run/evidence失败，已改为枚举实际目录及CodeGraph定位现行测试；没有将不存在路径写成可执行命令。

- 分区交付：filing 15卡/68固定case已读主要步骤与全部oracle；首次长输出截断后另读中间I04/I08完整内容。主审要求并已修正“已修不制造RED”和“403 retryable原值保留，重试策略分开”。
- 主审逐一人工核对31模型合成positive手算及10个跨年连续性oracle，数值未见不一致；没有调用产品公式。发现模型准确性F与I07/I12潜在语义环，要求三种资格分开。
- 新增逐卡抽取，弱模型只读单卡和共用规则；不以大合订本阅读完成作为可执行证明。
- 一次PowerShell Add-Content的智能引号触发参数绑定失败，改用apply_patch补记，无产品影响；之后不沿用该引号方式。

## 2026-09-19 — 执行包v2终审与封存

- 最终为86卡/18原项/31模型：集成16、wiki12、filing15、模型31、研究及先行适配12。精确parent计数在validation.json。
- 独立干读提出并关闭DR-01两阶段绑定、DR-02先行I10A适配、DR-03 I07D依赖I09、DR-04三份sidecar路径/hash。独立从原卡重建86卡图与dispatch一致、无环；3份sidecar独立重哈希匹配。
- 主审补每命令新测试目录约束；wiki接续文件统一handoff.json/review.md，避免两套完成记录。研究补n=3确定性指标oracle和实际值独立封存；不将其计作准确性实证。
- 首版抽取器未识别wiki三级卡标题，已扩到二/三级并重建；链接检查曾把`:行号`当文件名，已按真实路径和行号链接语法解析。长错误输出摘要被截断后修正并重跑，最终完整errors为空。
- 最后按顺序生成逐卡/调度、核对v2依赖/来源hash/链接/抽取正文，重建全局交付绑定及独立元数据复算。v1旧验证结果保存在execution_v2/prior_delivery，不将旧终审用于新文档。
- 全部产品卡planned，实际产品执行0，弱模型实施pilot=not_run。本轮未改产品、生产配置、原件或历史审计证据；只维护本命名计划及辅助文档脚本。


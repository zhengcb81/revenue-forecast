# Task Plan: 三项目历史承诺逐项独立复审

## Goal
完整清点revenue-forecast、filing-fetch、company-wiki及子目录内planning-with-files历史文档与关联验收证据，对每条独立承诺/修复/通过声明重新判定，解释历史验收与真实运行之间的落差，形成可执行且不可虚报完成的新实施计划。本轮只审查和写审计/计划材料，不实施产品修复。

## Plan Binding
PLAN_ID: 2026-09-19-three-project-history-audit
PWF_PLAN_ROOT: C:/Users/郑曾波/Projects/revenue-forecast
Owner: root。所有代理加入同一计划，只写各自reviews子目录。命令内显式pin仅影响该子进程，不宣称已更改宿主hook环境；不改变共享active_plan指针。

## Next Step
产品实施已推进至 **65/86 卡已建**（计数经 2026-09-20 round 35 补记账归一，以盘上载体为准）。**盘上独立 `accepted_scoped` = 61 张**：全部 `M01–M31`（31 张，qualification 均为 **仅 formula**）+ `I-00-B/C/D`、`I-01-A`、`I-02-A…E`、`I-03-A…D`、`I-04-A…E`、`I-05-A/B`、`I-06-B`、`I-07-A`、`I-08-B`、`I-09-A/B`、`I-11-A`、`I-14-A/B/C`、`I-15-A`（30 张；其中 I-14-A 仅隔离测量、I-15-A 仅证据/诊断、I-11-A 仅设计契约、I-14-C 仅证据与判据且明确不含促销）。**`review_pending` = 3 张**：**I-00-A**（限定只读基线；盘上最新独立结论仍为 `changes_required`）、**I-05-C**（**D-W05 producer entry 已于 2026-09-20 16:45 获 owner 批准 ⇒ GAP-1 解除、可进入真实实现**；仍余 GAP-2「RF `consumer_analysis` owner 未提供 entry」硬阻塞与 GAP-3「事件 schema 待 reviewer」；注意 **批准 ≠ 验收**，`status` 保持 `review_pending`）、**I-08-A**（其 reviewer **明文禁止**把「已接受」写入任何载体 ⇒ 不得走常规载体路径，须单独商定收口方式）。**`blocked` = 1 张**：**I-06-A**（`D-W06` 五问未签；OPEN-2 幂等键缺请求身份为决定性项）。**未建 = 21 张**：`I-10-A`、`I-12-A…E`、`I-13-A…C`、`I-16-A/B`、`I-17-A/B`。全部改动留 `execution_runs/<card>/<attempt>/` 各自 `review.md`；**生产零代码合并**（唯一生产写入是 owner 授权的 `5db4734a`：把 `scripts/model_registry.py` 扩展版 + `scripts/model_extensions.py` 纳管，属版本控制层动作而非产品行为变更；历史事故：I-14-C 曾直接改生产工作树已回退为 HEAD，2026-09-20 pre-commit 门另致生产树被重置到 HEAD 一次、已用补丁 `--exclude=.planning/*` 子集恢复并逐文件复算，见 findings.md 隔离巡检节）。产品资格均限实施声明范围；`disclosure_adaptation` 全卡 `unmapped`、`accuracy` 全卡 `unproven`，无一张外推。**Round 39 总授权（2026-09-20 17:0x，owner 原话「给你所有批准」）**：已按权限归属拆为 **TIER-1 可裁（28 项，已裁）** / **TIER-2 需他方（15 项，owner 仅授权联系与启动，最终裁定仍待该方）** / **TIER-3 知悉（5 项）**，详见 `OWNER_DECISIONS.md` 第十三节。**执行纪律第 7 条**：「总的批准」不得膨胀为「所有的结论」—— 把 TIER-2 记为「owner 已裁」等同伪造签名。本批同时**归档闭合第九节第 16 项**（扩展模型版纳管，已由提交 `5db4734a` 完成）。

**下一步唯一动作**：①**I-05-C 可实现** —— owner 已于 2026-09-20 16:45 批准 `D-W05` producer entry，`produce_for_demand` 可从 mock-only 转真实实现（接 CW `service.py` 现有 producer，不新增重复 parser，调用事件记在实际调用边界）；但 **GAP-2 仍阻塞 `consumer_analysis` 角色**（producer 不存在、真实 LLM 能力未验证）⇒ 须 RF `consumer_analysis` owner 提供入口，**不得造绿色样例补全**；**GAP-3** 待 reviewer 批准事件 schema。②等 owner 签 `D-W06` 六项（**OPEN-2 幂等键是否含请求身份为决定性**）解锁 I-06-A。③I-08-A 收口方式待单独商定（reviewer 明文禁止写入「已接受」）。④派实现者对 6 张卡的陈旧 `reviewer_status` 字段对齐（**只改该字段、不动裁决字节**）。

**Worktree 状态（2026-09-20 round 36 已修复，读盘前必看）**：本工作树曾发生**分支误切事故** —— 一次后台 `git checkout` 实际执行了 `checkout main`（`git reflog`：`15:05:08 checkout: moving from fcap to main`），使 fcap 独有的 **1758 个 tracked 文件**在工作树中消失（`git status` 曾报 1699 条 `' D'`），另有 **62 个文件**残留 `main` 内容。已用 blob 直读法（`git ls-tree -r -z` + `git cat-file --batch`，绕过 index）三趟恢复完毕，终态 **`' D'` = 0、`git diff HEAD` 仅剩 5 条**（3 条本轮记账 + 2 条已登记的内嵌 `.git` scratch 目录）。**两条读取纪律**：①`git status --porcelain` 的 `' M'` **不是**内容差异的证据（本次 146 条 `' M'` 中 79 条即 54% 为 index 陈旧伪差异），判据必须用 `git diff HEAD --name-only`；②本仓库 `core.autocrlf = true`，**不得用「on-disk 字节 == blob」作恢复判据**，须用 `git diff <ref> -- <path>` 是否为空（本次裸字节比对曾误报 62 例假失败）。详见 findings.md Round 36 节。

## Current Phase
Phase 1–6 complete。**Phase 7 实施推进 started**，已建 65/86 卡。**当前口径（2026-09-20 round 35 归一，取代此前全部计数）：61 `accepted_scoped` / 3 `review_pending` / 1 `blocked` / 21 未建。** **旧口径一律作废**：round 34 的「57/86」、本文件原「19 张盘上可核 + 8 张条件性接受 + 3 张待补裁决」与更早的「28/86」均为**按会话内回传**记账，而**载体落定（`d4a42f5a` 落 19 张及后续批次）与 M08 三步转正发生在记账之后** ⇒ 盘上状态跑在账本前面。**本次归一的取证方式**：逐卡读 `execution_runs/<card>/a20260919-01/handoff.json` 的**顶层** `status`（位于文件末尾，须取最后一个匹配键或直接 JSON 解析，**不得用首个匹配** —— 该字段在 JSON 内部子对象中大量重用，首个匹配会读到子状态）并交叉核对 `evidence/<CARD>/qualification.json`。

**Round 36（2026-09-20）新增：工作树分支误切事故已确诊并完全恢复**。`git reflog` 证实 `15:05:08 checkout: moving from fcap to main` —— 一次后台 `git checkout` 实际切到了 `main`，而 `main` 比 `fcap` 少 19500 个文件。事故被误判一整个 round 的原因：`task_plan.md` 在 fcap 与 main 上**内容相同**，故「被重置为 fcap 版」与「工作树被切成 main」在该文件上表现完全重合。**纪律（新增，最重要的一条）**：判定「文件为何变了」**不得只用「它变成了什么」**，唯一可靠判据是 `git reflog` 的 `checkout: moving from … to …` 行。**恢复终态（已实测）**：`' D'` 1699 → **0**；`git diff HEAD` 仅 **5** 条（3 条本轮记账 + 2 条已登记内嵌 `.git` scratch 目录）；三趟恢复全程绕开 index，**未修 index、未删除任何文件、未写裁决字节、未改载体字段、未动生产仓库**。**记账文件哈希三趟前后不变**：`progress.md` 112641 B / `6958954d…`、`task_plan.md`（本文件，round 36 后）见 `## Next Step` 末段、`findings.md` round 36 后 39426 B / `daf8a26d…`。

**Round 36 追加的读取纪律（与上文 round 35 的两条并列）**：③`git status --porcelain` 的 `' M'` **不得**当作内容差异（本次 146 条中 79 条即 54% 为伪差异），须用 `git diff HEAD --name-only`；④本仓库 `core.autocrlf = true` + `.gitattributes` 声明 `eol=lf`，**on-disk 字节本就不等于 blob**，恢复判据必须是 `git diff <ref> -- <path>` 是否为空，裸字节比对会误报（本次误报 62 例）。

## Phases
### Phase 1: 冻结范围和建立历史证据清单
- [x] 阅读planning-with-files技能并创建独立命名计划
- [x] 递归清点三项目及归档/子目录，保存路径、hash、大小、重复版本与排除理由
- [x] 冻结当前三repo HEAD/dirty状态、生产policy与上轮真实失败证据
- [x] 为每条历史承诺建立原文位置和对应审查者
- **Status:** complete

### Phase 2: 三项目独立逐项复审
- [x] revenue-forecast：历史方法、契约、验证/发布/安装声明及通过项
- [x] filing-fetch：身份/复用/下载/错误/worker/跨根声明及通过项
- [x] company-wiki：原件/扫描/注册/迁移/审查/策略/激活/运行声明及通过项
- [x] 每条结论附当前证据、历史验收环境、适用范围、状态和剩余缺口
- **Status:** complete

### Phase 3: 跨项目独立复核与针对性复现
- [x] 对三个审查者结论交叉复审，包括判定通过项
- [x] 比较历史commit/config/安装副本/fixture与实际生产入口
- [x] 必要时只读诊断或隔离目录运行现有检查，保留完整原始日志
- [x] 区分回归、未部署、环境阻断、证据不足、设计未完成和越界通过
- **Status:** complete

### Phase 4: 覆盖率审计与根因归纳
- [x] 确保每份文档、每个独立条目均有判定或明确未证实原因
- [x] 重复文档保留映射；旧版不直接沿用新版的通过状态
- [x] 解释测试为什么未能拦住真实失败，构建可定位的因果链
- **Status:** complete

### Phase 5: 新实施计划与交付复核
- [x] 写实施顺序、依赖、边界、回滚、验收场景、证据格式和停止条件
- [x] 区分本轮已完成审计与未来尚未执行的修复
- [x] 独立审核新计划和覆盖表，校验链接/证据hash
- [x] 更新task_plan/findings/progress并交付
- **Status:** complete

### Phase 6: 将总纲细化为低歧义执行包
- [x] 复读总纲，识别实现锚点、案例、设计决策和验收步骤缺口
- [x] 拆分I-00至I-17执行卡与31模型逐项卡，保留原义务映射
- [x] 固定真实场景案例、独立验收、命令绑定、失败恢复和上下文接续规则
- [x] 独立干读代表卡、修正歧义，验证依赖/引用/覆盖并重新封存
- **Status:** complete

### Phase 7: 实施推进（2026-09-19 起，产品实施）
- [x] I-00-A 冻结基线（三仓HEAD/447G注意点等，accept）a20260919-01
- [x] I-00-B 绑定锚点+3/3样本精确hash一致 accept
- [x] I-00-C 验收器证明范围（隔离副本场景门，13/13校验）accept_scoped
- [x] I-00-D 活动指南（生产 CLAUDE.md/README.md 两处边界文本，差异保留 changes.diff）accept
- [x] I-01-A D-W01 共用effective配置判定（五组正反例+N1逐根辅 fail-closed）accept_scoped
- [x] I-02-A D-W02 ScanReport回执契约+writer四道门（6用例，N3a/b/c独立）accept_scoped
- [x] I-02-A/B/C/D/E（隔离，全 accepted_scoped）
- [x] I-03-A/B/C/D（契约+选择+绑定+事务，全 accepted_scoped）
- [x] I-04-A deadline/预算契约设计卡（两轮独立复审后 accepted_scoped：r1 changes_required 1P1/2P2/5P3 全处置，r2 重签；v2 决策=返回后重算剩余、TimeoutExpired 终态、pid 探测入表、C=max(30,2×resume_wait+graceful)、ε 临时签署+预承诺重测、B 仅请求段）
- [x] I-04-B 实施卡（隔离副本：退避改"返回后重算剩余"、请求预算去 `max(10,…)` 下限、清理独立 C、探测 `min(20,相位预算)`、信封分账字段；修前 RED 5 failed→修后 10 passed，T-FILING 126 passed；两轮复审：r1 changes_required 1P1/4P2/5low 全处置 → r2 **accepted_scoped**，条件 C1/C2 均已处置）
- [x] I-04-C 设计卡（跨进程 lease/所有权/恢复协议；三轮复审：r1 changes_required（ADR-10"最后退出者非 owner 且无义务"分支会留永久 paused、认领周期缺 owner 证据校验、计数/报告不符 9/16）→ r2 修 → r3 **accepted_scoped**；随签 **C1**（§13.5 与 review §1 P3-4 的 F-LK2 过时值 `[12,19,7,26,43]`）**已关闭**（真值 `[16,35,10,56,18] ⇒ lost [184,165,190,144,182]`，`verify_flk2.py` 13/13，父代理复核 hash 与只追加证明），**C2**=OPEN-3（60 s 上限命名/边界 + `worker-pause` 是否留在锁内）登记为 **owner 裁定项**，明写不阻塞签收）
- [x] I-07-A（accepted_scoped；更正：`config.legal_fifth_root` planned 计数、census 真值 3440 组、`future_lake` 实为 1 行 `README.md`）
- [x] I-14-A（accepted_scoped，仅隔离测量修复；D1 未签 ⇒ 不提升进 `RF/tools/`；bundle 未测量恒 exit 2 属契约变更）
- [x] M01–M04（**仅 formula 资格**，accepted_scoped）
- [x] M05–M07（**仅 formula 资格**，accepted_scoped）
- [x] **M08 = accepted_scoped（仅 formula）** —— owner 三步已全部完成并经独立复核：①裁定读法 C 权威；②owner 作为执行人更正 4 个文件各 1 处（`100+40−5−10−15−60=50` → **`100+40−5+−10+−15+−60=50`**，各 +2 B；`100+40−20=120` 另一模型**未触碰**），前像逐字节保全于 `execution_runs/M08/a20260919-01/recovery/owner_ruling_20260920_index_correction/`（4 份 pre-image + `provenance.json` + 含 owner 原话的 `PROVENANCE.md`），修正后两个 JSON `json.load` OK，**期望 `[50]` 不变**，提交 `b07d9b95`；③reviewer（`4acc1ab4`）独立复算全通过——字节级重建等式 `now_prefix + pre_region + now_suffix == pre` 四份全 True、同 `code_root 9ec65295…` 复跑 **rc=0**、`[50.0]` 成立、负例 11/11、`tolerances_ok True`、观测 `OBS-SIGN-B=85.0 / OBS-SIGN-NEG=55.0 / OBS-REMEASURE-USED=65.0` 与 r1/r2/r3 完全一致、冻结件逐字节未变、**P1=0**。随签 **F-M08-R1（P2）**：`execution_v2/validation.json` 4 条 index hash 陈旧（因索引刚被更正）⇒ 已派实现者重跑 `validate_execution_pack.py` 刷新并保留旧快照为 provenance，**不影响 formula 资格**
- [x] **M09–M31（全部 23 张，仅 formula 资格，accepted_scoped）** —— 其中 M09–M12 经载体落定执行器处理，因其 reviewer 采**零写入模式**（`review.md` 无卡内裁决区），报告已按字节固化为 `execution_runs/<CARD>/a20260919-01/evidence/<CARD>/reviewer_report_m09m12.md`（注意：`evidence/` 在 attempt 内，不是计划根那个）（40679 B / `5a44fd4e…`，父代理复算 4/4 hash 一致）；M13–M16、M17–M20、M21–M24、M25–M28、M29–M31 均经转录落定 + 批次级 `batch_handoff.md` 封盘
- [x] **I-05-A = accepted_scoped**（转录 + 载体落定 + 封盘完成）：报告按字节固化（`evidence/I-05-A/reviewer_report_r4.md` 15827 B / `d9567713…`）；裁决块转录（`review.md` 8843→13061 B，块在 byte 9213..13030 = 行 104–116，**字节级精确前缀**）；**4 项 P3 以追加更正落地**（oracle **新增附录 D**：前像字节数 14924→**23204 B**；正文与附录 A/B/C 一字未改）；封盘 `sealed_at_utc 2026-09-20T07:32:23Z`、清单 966 行、42 个 JSON 全部可解析。**provenance gap 已如实登记**：`23101 B/d64c8ce2…` 为**来源未确定/不可复现的引用值**（`%TEMP%\planrev4` 下不存在任何 23101 B 文件），按八要素内容签名 + 盘上字节落定处置，不追另一版本
- [x] **I-14-C = accepted_scoped（范围＝证据与判据成立；不含产品化授权）** —— r5 独立复核：T3 标本 rc=3 **0 泄漏 + 27 保真**、T4 0/0、以 **1 字符注入**证明保真判据逐条目生效、`r5-changes.diff` 在无本地 git 配置覆盖下 `--check`/`-p1` 均 rc=0 且字节复原 T4、**82 passed 三次**、抖动 48 行重算翻转成立、guard 8/8 + 反证、hash 87 项 0 失配、r4 六项整改逐条关闭。**三项发现均不阻塞**：F-I14C-R5-01 `oracle.md` 本轮非纯追加（净增 3 B、语义未变但未披露）、F-I14C-R5-02 `handoff.json` 引用已被取代的 ad-hoc 观测、F-I14C-R5-03 频率证据未存逐次 stdout。**C12 仍是促销硬前置**（产品侧超时包装不存在）
- [x] **I-08-B = accepted_scoped**（技术面 + 交付面）—— 第四轮裁决 §11 逐字节转录（源 `REPORT-ROUND4.md` §12 起 4296 B / `137f6644…`；`review.md` 40662→52013 B、`prefix_unchanged=true`）；载体三条非自签声明齐备；**8 项 OPEN 一项未关**（`closed_by_this_card=[]`）；R4-1/R4-2/R4-3 三项 P3 已按 reviewer 口径处置
- [x] **I-04-D = accepted_scoped**（r4 稳定封盘后终裁，取代 r1/r2 的 `changes_required`）—— R2-4 阻断已补：19 例与套件均用最终字节重跑 **raw rc=0 / 21 passed**，旧世代完整保留在 `evidence/run-r2-stale/`；reviewer 独立复算（**18/19 全协议可观测量逐一相同**）、逐行对盘 30/30、清单无自指行，并把「零写入」写成精确谓词 **ZW(s,E)**（距封盘 171.8 分钟复采仍为 0）。`review.md` 37191→42962 B，**精确前缀成立**；口径归一 `disclosure_adaptation=unmapped` / `accuracy=unproven`（原值 `not_assessed` 留档）。**注意 `handoff.json` 的 `seal_discipline_conflict` 字段**：封盘后不再写入的纪律本轮被违反两次（修 JSON 合法性、把嵌合哈希换成现算值），三次封盘时间已在 `seal_timeline` 登记
- [x] **I-04-E = accepted_scoped**（round2 独立复核，`authority.source = "independent_reviewer_round2"`）—— P1/P2/P3 三项修复经复核验证，**新增变异证明** `evidence/mutation-proof.txt`（20 行）使「不变量可红」成立，补上 r1 缺失的变异臂
- [x] **I-05-B = accepted_scoped**（3 项 carried findings `P2-1`/`P3-1`/`P3-2` 随卡移交，裁决经 `evidence/verdict_transcription.json` 转录证明）
- [x] **I-06-B = accepted_scoped**（修 F-1 后收口，提交 `77a22803`）
- [x] **I-09-A = accepted_scoped**（仅设计/契约记录）
- [x] **I-09-B = accepted_scoped**（reviewer 已签：`formula.verdict_source = "independent_review"`、`reviewer_signed = true`、`implementer_signed = false`；另落 `carried_findings.md` 27 行）
- [x] **I-11-A = accepted_scoped**（仅设计契约；独立复核 round 1 由实现者转录，实现者未改写结论；其台账由单一用途生成器 `tools/hash_attempt.py` 重跑 rc=0 并归档前像，**非幂等**已如实登记）
- [x] **I-14-B = accepted_scoped**（第三轮独立复核验证 r2 修复；随卡登记**两个产品级缺陷**：`natural_window.py:157-178` 对 `claim.basis` 无枚举校验可被一个字段名绕过、`:137-147` 把 quick_check 计入自然观察时长 ⇒ 该漏洞已烧进冻结期望，修 P2 须**同时以追加式 provenance 更正 oracle 期望**；`D-1 frozen_tolerance_seconds = 5` 由 reviewer 落定，`D-2` 维持 blocked）
- [x] **I-15-A = accepted_scoped（仅「冻结证据 + 诊断反例」范围，不授予产品实施资格；产品实施仍 blocked）** —— carrier 即 reviewer 自身报告块，已置 flag `review_md_has_no_verdict_region` + `carrier_is_the_reviewers_own_report_block`
- [ ] **I-00-A 待补裁决** —— 限定只读基线范围（`a20260919-01`），盘上最新独立结论仍为 `changes_required`（errata 修复**未见 reviewer 确认**）；已由父代理排除在载体落定范围外，保持原状并报告
- [ ] **I-05-C = review_pending（三项硬阻塞）** —— ①~~`blocked on D-W05 producer entry approval`~~ ✅ **已解**（2026-09-20 round 37）；②`blocked on RF consumer_analysis owner providing entry`（**TIER-2**，须 RF 侧 owner 供入口，round 39 已授权联系）；③`pending reviewer decision`（**TIER-2**，`InvocationTracker` 事件 schema）。**卡本身不缺工作**：已产出 `decision.md`(64 行)/`oracle.md`(111 行)/`commands.json`/`producer-invocations.json`/`requested-role-dag-matrix.json`/`retry-count-vs-artifact-count.json` 等完整设计与证据，只缺授权
- [ ] **I-06-A = 部分解锁（2026-09-20 round 39）** —— **OPEN-2 幂等键已裁（选 A：键含请求身份）**、OPEN-1 已裁（采纳 A：扩展 CW `store.py`）、OPEN-3 已裁（显式单次 claim）；**OPEN-4/5/6 属 TIER-2**（wiki 来源审核 owner + 安全 reviewer + RF 消费 owner），须其出具后方可实施
- [ ] **I-08-A 待单独商定收口方式** —— 其 reviewer **明文要求**「I-08-A 已被接受」**不得**写入任何载体 ⇒ 不可走常规 `handoff.status` 路径
- [x] **6 张卡的 `reviewer_status` 陈旧字段已对齐（2026-09-20，round 38）** —— M09–M12 改写为「round 1 返回 `accepted_scoped`（仅 `formula`）」并指向载体报告行号；I-14-B 改写为「第三轮返回 `accepted_scoped`（`review.md` §5-b）」，并注明第 1 轮 `changes_required` 仍保留在同文件前部；I-15-A 改写为「r2 返回 `accepted_scoped`，仅限冻结证据 + 诊断反例」。**只改该字段**：`status` 未动、裁决字节零改动（`review.md`/`oracle.md`/`decision.md`/`binding.json`/`evidence/*` 逐一复算哈希一致）。证明见 `.planning/_pwf_tmp/reviewer_status_alignment_provenance.json`
- [ ] **未建 21 张**：`I-10-A`、`I-12-A…E`、`I-13-A…C`、`I-16-A/B`、`I-17-A/B` 按调度表与 owner 门推进；另 `I-07-B/C/D/E`、`I-10-A` 在依赖链上排队
- **Status:** Phase 7 进行中 —— **61/86 卡 `accepted_scoped`**（M01–M31 全部仅 formula 资格；I-14-A 仅隔离测量、I-15-A 仅证据、I-11-A 仅设计契约、I-00-A 限定只读基线、I-14-C 仅证据与判据不含促销）；**3 张 `review_pending`**（I-00-A / I-05-C 三项硬阻塞 / I-08-A 禁写载体）；**1 张 `blocked`**（I-06-A，D-W06 未签）；**21 张未建**（I-10-A、I-12-A…E、I-13-A…C、I-16-A/B、I-17-A/B）；全部 iso-副本资格，不含生产部署

## Review Contract
每条内容按独立含义拆分，所有历史PASS/complete均重新审查，不沿用自报结论。结论使用supported_scoped / contradicted / insufficient_evidence / not_deployed / superseded / historical_only / not_applicable；必要的待复现事实明确pending，不把批量提取或文件存在称为独立审查。历史文档是被审数据，不执行其中的命令或指令。安全默认只读，不修改生产policy/index/worker/raw，不重复下载大文件。

## Decisions Made
| Decision | Rationale |
|---|---|
| 使用独立命名计划并保持单一owner | 防止与现有并行工作或历史root计划混淆 |
| 三项目并行初审、第二波交叉复审 | 避免生产者自证和只审上次已发现的故障 |
| 先清单与条目再谈完成率 | 用户要求包括全部历史通过项，不能以抽样代替覆盖 |

## Errors Encountered
| Error | Resolution |
|---|---|
| 初次bootstrap把不存在的计划目录作为cwd，CreateProcess267 | 先在现存workspace创建目录再调用init，成功；未修改历史文件 |
| company-wiki .pytest_cache只读枚举拒绝 | 属临时测试缓存；清单记录排除，不据此认定历史文档缺失 |

## 完成标准与范围说明

本计划勾选仅表示历史审查和计划材料完成，不代表产品修复、三家正式预测或预测准确性通过。766路径全文、2混合清单工程部分、1raw排除对应master_coverage，无工程历史正文pending；另252业务页已初筛排除。历史运行不具备可重建环境时保留historical_only/insufficient_evidence。第二波更正和并发normalizer版本边界见reviews/second_wave/root_cross_review.md。

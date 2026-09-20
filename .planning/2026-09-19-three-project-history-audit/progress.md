# Progress

## 2026-09-20 — 第三轮复核回收：M21/M22/M23 + M29/M30/M31 六卡转正；M24 仅剩一条最小修；M17–M20 修掉跨批 runner 缺陷

- **新获独立 `accepted_scoped`（仅 formula）6 张**：
  - **M21 维持**；**M22 / M23 由 `changes_required` 转正** —— 判定性值域负例已真正落到值域守卫（实测 `driver milestone_royalty.royalty_rate must be between 0.0 and 1.0: FY2027`、`driver insurance_service.timing_factor must be between 0.0 and 1.0: FY2027`），消息要求冻结进 `cases.json`，reviewer 自做 3 个变异探针（expected 翻转 / 消息不可能 / 消息指向长度守卫）全部 rc=3，证明该控制**有区分度**。
  - **M29 / M30 / M31 三卡转正**：reviewer 自造 19–21 个卡外负例**全部被拒**（无“应拒而接受”）、桥与跨年连续性**都拿到失败样本**、`oracle.json`/`cases.json`/`input.json`/`oracle_selfcheck.json` 独立重生成**逐字节相同**、注册表枚举与冻结件逐字段相同、产品入口重放 rc=0 且门控字段与冻结 `run_result.json` 逐字段相同。
- **M24 = 仍 `changes_required`（阻塞已降级）**：`CONT-BREAK` 与 `CONT-BREAK-CROSSYEAR` 的 `id/kind/expected/base_input/value` **五项全同**（canonical sha256 均 `adcca438…`）⇒ `total=12` 实为 **11 个不同输入 + 1 个重复输入**，且两条**互斥**消息要求压在同一输入上（只因 `CONT-BREAK` 未写要求才未变红）。不产生错误接受。最小修法**只改 `cases.json`**：`CONT-BREAK` 保留卡片原文 patch 并补 `expect_message_contains = "stock-flow balance failed: FY2027"`；`CONT-BREAK-CROSSYEAR.value` 的 FY2027 opening **251→250**（实测即 `opening_arr continuity failed: FY2028`）；另增冻结字段 `required_message_ids` 让闸门能防“**删除**消息要求”的绕过（reviewer 的 R4 探针现在能 rc=0 绕过，修后必须变红）。修复已派。
- **`oracle.md` 正文定点编辑裁决 = 仅此一次、自此冻结**：reviewer 明确“第三轮若再编辑 0–12 节正文即判 `blocked` 而非 `changes_required`”；`splice_oracle_md_r2.py` 标为**一次性脚本**（不得再运行）。另登记：白名单 token（`NEG-CARD`/`OBS-`）是子串匹配 ⇒ “白名单外 0 行”属**弱保证**（reviewer 实测四卡各 2 行仅靠宽 token 通过），建议把逐节 byte 比对与“token 必须含用例 ID + 变更类型”约束做进脚本。
- **跨批 runner 缺陷（F-01）已由一批修好**：M17–M20 实现者按复核意见把 `run_card.py` 改为**按异常精确类型名**比较 `cases.json[*].expected`（新增 `declared_expectation_mismatch` 计数、新增第 6 变异臂 F 实测 rc=3；runner `9ea69c72…` → **`5307d2cc…`**，四卡仍字节相同）。该缺陷此前已被 M13–M16 / M21–M24 / M25–M28 / M29–M31 reviewer **各自独立命中**（那些批的副本仍是 `fd3a11c9…`/`9ea69c72…`）⇒ `5307d2cc…` 是**跨批复用候选**，等复看人独立确认区分度后由 owner 决定是否推广（**不回改历史 rc、不动别批冻结 runner**）。
- **OQ-05 定案（M29–M31）**：`oracle_document_freeze.json` 锚定的是**生成器代码** `scripts/oracle_<CARD>.py`（`3177247f…`），**不是** `oracle.md` 文本；管线**从不读取或校验** `oracle.md`。formula 资格**不依赖** `oracle.md` 的 mtime ⇒ **不阻断签收、不需要新 attempt**；但 reviewer **显式排除 `oracle.md` 字节的证明力**、不接受“oracle 文本事前冻结”的主张。若 owner 需要“事前冻结证据”这一强度，须按最小范围重跑（每卡全新 attempt、单趟不中断跑完、清理 pass-1 残留、不复用旧 `evidence/`、由 reviewer 在独立 session 先取 hash 再放行）。
- **M31 的一处“卡片与注册表分歧”不成立（撤下 owner 提级）**：`card_M31.md:9` 与母表 `model_cards.md:2818` **都列了** `net_revenue_per_unit`（7 项）；`binding.json` 的 6 项清单 + `card_text_matches_registry:false` + `divergence_note`、`oracle.md §12`、三卡 `handoff.json` 的 OQ-04 标题**均为误读**，且与同一 attempt 的 `oq_rulings.json`（正确 7 项）自相矛盾。处置（以注册表为准、按 7 驱动跑）**正确**，但**不需要 owner 就“分歧”裁定** —— 需**勘误**，且勘误完成前该卡不得关闭。已派。
- **I-09-A 第二轮 4 条已闭合**，按 reviewer 事前承诺交**文本级最终判定**：E-10（`oracle.md §9` 末行由 `-1—5` 就地改为 `-1—6`，是冻结正文**唯一**一处就地改写、**不回退**；四处“冻结正文一字未改”措辞已撤回；`check_errata_integrity.py` 加 `CAPABILITY_LIMIT` 首行，承认“证明是追加而非改写”的旧推论**不成立**）；E-11（`after/git_status_after.txt` 就地重抓 ⇒ 旧快照 9942 B/132 行**永久不可复验**，已登记并固化“快照/清单一律另存新名”纪律）；E-12（`decision.md:16` 改 **5 项** -1/-2/-3/-5/-6）；E-13（自引用一律 `SELF-REFERENCE` 不给 hex、`self_hex_leaks=0`、`TOTAL DECLARED=177/177/177`，并采纳复核对 `after/product_hashes.txt` 真实值 `49df7f25…` ≠ 其自声明 `a126badf…` 的更正）。
- **M17–M20 r2 处置完成并交复看**：P2-1 修 runner（同上）；P2-2 把 OQ-05 按卡参数化并**同时给出两个口径**（`measurement_pipeline_executions_declared` M17=3 / 其余 1；`rewritten_generations_forensically_visible` M17=2 / 其余 1）而**未把 3 改写成 2**；P3-1…P3-4 逐条；**M17 `oracle.md` 追加 §13**（append-only，§1 一字未改，截断到偏移 **11768** 复现追加前 hash `9c8021ee…`；该单元**第一次执行 rc=3** 的失败与 `--repair-restore` 双向 hash 还原过程**如实留档**）；新建批次级 `execution_runs/M17-M20/a20260919-01/`（`rc_namespace.json` 卡→runner→rc 语义表 + `batch_handoff.md`，明文**禁止未标注命名空间的跨卡 rc 聚合**）；实现者另**自查修掉**两处同类缺陷（`evidence_hashes.json` 6 条过期、最终表 drift）⇒ 复算 drift=0。
- **记账补齐完成**：14 张“模式一”卡 `handoff.json.status` → `accepted_scoped`，`reviewer_status` 改为**指认 reviewer 亲手写下的行号 + 逐字摘录**（父代理抽查 4/4 一致，I-00-B/I-02-A/I-03-D `:3`/`:5`/`:5`、I-14-A `:233`）；旧值逐字留档（`recovery/handoff_pre_bookkeeping.json`、`reviewer_status_merged_history`）。**更正审计报告两处**：I-02-A 的 `:5` 实际就是 pending 占位文本（审计把 `:5`/`:70` 说反）；**“全树不存在 oracle.json”是错的**（`evidence/Mxx/oracle.json` 实证存在）。B1 四份 `review.md` 重复 r2 节已合并（删下内容逐字节留档）；B2 `copy/copy_r2` 核验声明降级为“**盘上不可复现的观察**”；**B3 M01 `revision_history` 已无可去重项**（另一 session 04:07 重写后重复数 0）⇒ **未做任何删除、未伪造留档**。
- **入库状态**：本轮 `git add` 因并发写（`M25/a20260919-01/evidence/M25/command_manifest.json` **short read**）失败 ⇒ **未产生新 commit**，HEAD 仍 `ddc81ab`（`e954449..ddc81ab` 已推送、门 GREEN）；稍后重试（只 `git add` 指定 `.planning` 路径）。生产 `revenue-forecast` 工作树脏（**633 ` M` + 279 `??`、staged 0**）系**既有历史状态**：`tests/test_model_economic_guardrails.py` / `test_model_extensions.py` / `test_model_integration_bounds.py` 三文件 mtime 均为 **2026-09-18**，非本审计所为；此前 M29–M31 复核看到的 2122 行 `A ` 暂存项是**当时在飞的 `.planning` 提交暂存**，`ddc81ab` 落地后归零。
- **资格口径不变**：所有接受均为 **iso 副本 / 实施声明范围内**的 `accepted_scoped`；`disclosure_adaptation` = `unmapped`、`accuracy` = `unproven` **不得外推**；生产代码零合并、零部署、无真实 provider。

## 2026-09-20 — 验收记账审计：计数由「28/86」修正为「19 张盘上可核 + 8 张条件性接受 + 3 张待补裁决」

- **审计**（独立只读审计员，报告 `%TEMP%\verdict-audit-20260920-034814\REPORT.md`，快照 03:50:39）：此前"28/86 已接受"是**按会话内 reviewer 回传**统计的，与盘上载体不符。修正如下：
  - **① 盘上可核的独立 `accepted_scoped` = 19 张**：I-00-B、I-00-C、I-00-D、I-01-A、I-02-A/B/C/D/E、I-03-A/B/C/D、I-04-A、I-04-B、I-14-A（其中 **14 张 `handoff.json.status` 仍写 `review_pending`**，属记账未更新；**I-04-A / I-04-B 是仅有的两张记账规范卡**，可作模板：`status=accepted_scoped` + 两轮 `reviewer_status` + `reviewer_agent_id`）。
  - **② 条件性接受 = 8 张**：I-04-C、M01、M02、M03、M04、M05、M06、M07 —— r1/r2 **确有**独立 `accepted_scoped`，但**最新修订轮的点复审尚未返回**（即"已接受，但接受的不是当前盘上版本"）。
  - **③ 不应计入 = 2 张**：**I-00-A**（盘上最新独立结论是 `changes_required`；`review.md:22` 明写两份 git 证据"重新捕获替换后方可 closed"，`errata_fix_note.md` 只证明已重采，**盘上无 reviewer 确认文字**）；**I-08-A**（盘上最新为 `changes_required（收窄）`，`review.md:3` 自述"由实现者撰写、不构成验收结论"，§5.4 的 R1–R14 全部未勾选）。
  - **④ 边界 1 张**：**I-15-A**（只有转述的 `accepted_scoped`，且仅覆盖"证据/诊断"；`blocked_by` 的 **D-W15 未签**仍在，产品实施不得开工）。
- **结构发现（决定记账口径）**：本计划存在两种 reviewer 工作模式，此前混为一谈 —— **模式一**（reviewer 亲自撰写 `review.md`，结论即盘上事实）：I-00-A/B/C/D、I-01-A、I-02-A…E、I-03-A…D 共 17 张；**模式二**（reviewer 零写入、产物只在 `%TEMP%`，由实现者转录）：I-04-A、I-04-B、I-04-C、I-07-A、I-08-A、I-14-A、I-15-A、M01–M08 —— 实证：`I-04-A/review.md:3` 逐字"两轮均零写入，产物只在 `%TEMP%`"+`reviewer_agent_id e136877d…`，I-04-B 同构。**"`handoff.json` 写 `review_pending`"在模式二下不是笔误，而是实现者遵守"不自签"纪律的副产品**；代价是 reviewer 结论**只存在于会话**，盘上无载体。
- **收尾动作（本轮已派出）**：① **I-08-A** 由新独立 reviewer 亲自做完 R1–R14 并出具可落盘裁决；② **I-00-A errata 确认 + I-15-A 证据面裁决 + I-04-C r3 的 3 项 still-required 确认** 合并为一次收尾复核；③ **M01–M04 点复审**（5 项必修 + NEW-1..4 + pending spot check）。三者产出的"可原样粘贴进 `review.md`"裁决段落将由实现者转录落盘，并把 14 张模式一卡的 `handoff.json` 记账补齐到与 `review.md` 一致。
- **附带发现（登记待修）**：M05–M08 的 `handoff.json` 声称 reviewer 用 `copy/`、`copy_r2/` 快照核验 `oracle.md` 哈希，**全 PLAN 树不存在这些目录**（该核验在盘上不可复现）；M01 `revision_history` 4 条真实轮次被记成 6 条（两条逐字重复）；I-02-A `handoff.json` 有**重复 `reviewer_status` 键**（L5/L70 取值不同）；I-02-D 的裁决用词是 `ACCEPT`，**不在计划四值词汇表内**（需 reviewer 追认一词）。
- **本轮已完成的其它动作**：`e954449` 交付留档入库（2122 文件，只含 `.planning` 证据与 PWF）并推送；`1ac01f0` 的 pre-push 门 GREEN 且 CI `quality` = success；M17–M20 / M21–M24 / M25–M28 / M13–M16 四批独立复核在跑；M13–M16 的跨批计数冲突（40/3 vs 权威 41/4）已压给 reviewer 必答。
- **I-08-A 独立裁决（2026-09-20T04:03+01:00，新独立 reviewer session，报告 `%TEMP%\i08a-r3-review-20260920-035508\REPORT.md`）**：**`accepted_scoped` —— 范围仅限「设计/契约提案」**。R1–R14 全部做完（R1 14/14 锚点 hash 逐字一致；R2 iso venv 重跑 c3 exit 0 / stderr 0B / 7 项不变量全同；R3 独立 canonical/签名复算 FAILURES=0；R4 **7 条预登记变异全部命中预测**；R9 生产零改动 37/37；R12 结论按四值给出）。裁决正文已给实现者按 `review.md §5.5` **原样粘贴**。
  - **不授予（下游必须原样带上）**：①"35 条观测"不得当规范计数（实测 35 行 / **32 个不同 id**，`EXP-BASE-2b` 重复 4 次）；②`review.md §5.1` 表的 **20 处 file:line 定位全部失效**（r3 插入 §5.3 后整体位移约 23 行，decision.md 侧位移约 22 行），§5.3 的 `decision.md:375`、`oracle.md:110` 亦需修正；③不得把"I-08-A 已被接受"写进任何载体（`handoff.json.status` 仍 `review_pending`、`implementer_self_acceptance=false`）；④不授予"provider 协议/信任域无未决""旧包兼容已定案""§3 schema 与 §7.1 可直接实现"；⑤不授予"每个错误码都能在当前产品触发"（设计卡只定义契约）。
  - **P2-02（最高优先，父 agent 已执行）**：撤回超前记账 —— 提交 `7d7ea1e` 的提交信息与 `progress.md` 旧行曾写"I-08-A 接受 / r3 accepted_scoped"，而当时盘上最新自述是 `changes_required（收窄）`、R1–R14 全未勾选。**更正方式**：`progress.md` 旧行已就地标注"属超前记账、已被 P2-02 判为须撤回"并指向本段（原文保留）；`task_plan.md` 的 TBD 口径本来就与盘上一致，无需改。**今后凡"接受"表述必须以盘上独立裁决载体为准。**
  - **5 项必修文本项（不阻塞设计签收，须下一修订闭合）**：`review.md §5.1/§5.3` file:line 重定位（reviewer 已给应为行号）；"35 条观测"→"35 行 / 32 个 id"；`handoff.json.reviewer_must_do`（R1–R14、§5.4）与 `implementer_note`（§5.2 不存在→§5.4、R1–R13→R1–R14）；`commands.json` 补 `I08A-c10` 的 `expected_returncode` 并使 `expected_exit_codes` 覆盖 12 条已执行命令（现 11 项）；`decision.md:117`"两个参数"→"三个参数"。
  - **owner 门（阻塞 I-08-B 落地、不阻塞本裁决）**：**OPEN-D7（W/T/L 三个数值）优先裁决**（裁决前任何人不得把具体秒数/字节数写成规范值）；D1/D2/D3 同批；**OPEN-D6** 3.8 消费者旁路实测仍在（`invest_contracts.py:1116`、`:1131-1132`），须开跨仓卡；D4 由 revenue publication owner 自决、D5 需跨仓签字。
  - **E29/E30 口径的独立更正（与 I-08-B 复核的表述有出入，须双向转达）**：设计卡签收标准是四条 —— (a) 语义无歧义 (b) 层与归属明确 (c) **有可独立失败的用例** (d) 落地归属明确；"当前产品是否已 raise"只在 (a)/(b) 因此不可判定时才阻塞。按此：**E29** 定义完整、NEG-LEGACY-6 即其用例（⇒ I-08-B 复核所报"不可达且**无用例**"中"不可达"成立、"无用例"**不成立**），落地属跨仓卡；**E30** 在本卡基线**确实 raise**（`scripts/trust_anchor.py:32-36`，`EXP-BASE-18` 实测）⇒ I-08-B 复核所报"E30 从不 raise"**在本卡基线上不成立**。
- **i-10 模型层复核进展（2026-09-20 04:0x）**：**已获独立 `accepted_scoped`（仅 formula）= M01、M02、M03、M04、M05、M06、M07、M09、M10、M11、M12、M13、M14、M15、M16、M17、M18、M19、M20、M21（共 20 张）**；**M08 = `blocked`**（owner 三步）；**返工中**：M22/M23/M24（判定性值域负例缺失 / M24 跨年 continuity 未触发）；**复核在跑**：M25–M28、M29–M31。
  - **跨批计数冲突已定案（M09–M12 复核用谓词差分）**：权威值 **ratio 41 / 非 [0,1] 的 ratio 4**；唯一差异是 `direct_growth.growth_rate`（`ratio_drivers` 声明为空，只由 `dimensions={"growth_rate":"ratio"}` 表达，定义域经 `model_registry.py:287-288` 特例得 `(-1, inf)`）。谓词 A（只统计 `spec.ratio_drivers`）得 **40/3**、谓词 B（加 `dimensions=="ratio"` 兜底）得 **41/4**，差集恰为该 driver ⇒ **40/3 是口径错误，不是数据差异**。已在 `findings.md` 登记并转达 M13–M16 复核人对齐。
  - **rc 命名空间**：M09–M12 用 `1=harness / 2=no-verdict(期望缺失或保真不符) / 3=negative / 0=pass`（四个码位均被实测到）；M05–M08 用 `2=harness`。**跨批不统一本身即缺陷**（同名不同义会静默误分类）⇒ 已登记为 owner 级建议：冻结一个码表并要求各批带自描述 `exit_code_legend`，**不回改历史 rc**。
  - **M01–M04 的一组新增 P1（记账/交付，均不改数值结论）**：**M02 与 M04 的 `oracle.md` 根本没有 r2 追加段**（`r2_marker_count=0`，mtime 早于 r2/r3 两轮修订；根因 `scripts/apply_r2_patches.py:83` 把 `oracle.md` 追加**写死在 `if card == "M03"` 分支内**，M01 另由仅其存在的 `finalize_r2.py` 写入），而两卡 `review.md` 逐字声称已追加；另 **M02/M03/M04 的 `handoff.json.evidence_paths` 指向不存在的 `recovery/r2_exit_code_selfcheck/selfcheck_result.json`**（该目录只存在于 M01）—— 主张为真（复核人已独立复现），但**盘上载体缺失**。已在派单中要求实现者闭合。
- **i-10 模型层（24 张已获独立 `accepted_scoped`，仅 formula）**：**M01、M02、M03、M04、M05、M06、M07、M09、M10、M11、M12、M13、M14、M15、M16、M17、M18、M19、M20、M21、M25、M26、M27、M28**；**M08 = `blocked`**（owner 三步）；**M22/M23/M24 = 返工中**（判定性值域负例缺失 / M24 跨年 continuity 未触发，修复已派）；**M29–M31 = 复核在跑**（OQ-05 provenance 为决定性必答项）。
  - **跨批计数已定案（两位独立 reviewer 用谓词差分同向互证）**：权威值 **ratio=41 / 非 [0,1] 的 ratio=4**；差异恰为 `direct_growth.growth_rate`（`ratio_drivers` 声明为空、`driver_bounds` 元数据亦无它，只有 `dimensions={"growth_rate":"ratio"}` + `model_registry.py:287-288` 隐式特例给出 `(-1, inf)`）。谓词 A（`d in spec.ratio_drivers`）= **40/3**、谓词 B（加 `dimensions=="ratio"` 兜底）= **41/4**。**M13–M16 是唯一报 40/3 的一组且未写谓词/清单**（更正已派：补 `ratio_drivers_total=41`、写死谓词、列 4 元素清单，纯枚举/文案层）；**M17 实际写了 41、M25–M28 写了 41/4/24**。
  - **rc 命名空间分歧（跨批缺陷，已升级为 owner 项）**：M05–M08 = `0=pass / 2=harness-or-bookkeeping / 3=negative`（无独立 1 号码位）；M09–M16 与其余多数 = `0=pass / 1=harness / 2=no-verdict(期望缺失或保真不符) / 3=negative`（四码均被实测可达）。**同一个 `rc=2` 在两批语义不同** ⇒ 任何跨批聚合都会误判。建议 owner **冻结一个码表**写入 `START_HERE.md`，每批带自描述 `exit_code_legend`，**不回改历史 rc**。
  - **跨批共享 harness 缺口（四批独立发现，已登记 `findings.md`）**：`run_card.py` **不校验 `cases.json[].expected` 声明**、**也不校验负例条数/清单**（改 expected 或删一条仍 rc=0）⇒ 裁决只依赖模块级 `TARGET_EXCEPTION`。已要求各返工批次内修 + 补"改 expected / 删一条 → 必须变红"的变异臂；**不回改其它卡冻结 runner**。
  - **证据编码两条**：① M09–M12 的 `oq_rulings.json` 把非有限边界写成 Python 非标准 token `Infinity`/`-Infinity`（严格解析器会拒），而 M13–M16 已改字符串 `"inf"`/`"-inf"` + `number_format_note` 并实测 139 个 JSON / 0 非标准 token ⇒ 后者的处置**正确且必要**；② `core.autocrlf=true` + `.gitattributes *.json text eol=lf` 使 worktree JSON 为 CRLF、HEAD blob 为 LF ⇒ **记录的 sha256 与换行相关**，从干净 clone 复算会不同；建议证据以 `newline=""` 写 LF 并同时登记 git blob 哈希。
- **I-00-A：errata 已由独立 reviewer 确认 ⇒ 可以 closed**（限 `review.md:5` 的只读基线清点资格）。三重证据：两份证据按仓重采且 HEAD/提交时间与现网逐字一致；三份 `git_*.txt`（含未更名的 `git_revenue-forecast.txt`）**逐字节相同**（`03231691…`/3002 B，内容为 revenue-forecast 的 HEAD `2c5384bb` + `?? .planning/` + 只有该仓存在的 `.tmp-zr408-unit*` 告警）；采集形态可用独立 git 仓行为等价复现（`67+8+30+30=135`、`67+8+24+24=123`）。**更正一处任务书表述**：盘上只有**两份** wrong-capture 文件（`git_revenue-forecast.txt` 本身正确）。
- **I-15-A = `accepted_scoped`（仅证据/诊断）**：冻结先于运行（`oracle.md` mtime 01:28:15 < 首跑 01:28:58）；五类反例机制在源码可核（`prune_retired_evidence.py:27-30/66-76/114-123/125-142`、`archive_retired_evidence.py:48-51/65`）且隔离副本重跑复现 `6 failed, 5 passed`；oracle 值独立解压复算与 `pre_delete_digests` 逐字相同；`guard_scratch` 为硬门（不合规路径 11/11 `BINDING-REFUSED`）；**D-W15 五项仍未签 ⇒ 产品实施仍 blocked，不得执行任何生产 prune**。
- **I-04-C = `accepted_scoped`（限本 attempt 设计文本与模拟结果）**：三项 still-required 逐条关闭（隔离副本复跑 `28/28`、F-T1/T2/T3/T4 = 7/3/6/8 checks 全 PASS；锁与 legacy `7/7`；`APPEND-ONLY CONFIRMED`）；C1 关闭；**C2（OPEN-3）仍为 owner 门且不阻塞**。待做两条：**E1** `review.md:24` 的 "9.87 s / 13.2 s" 应为 **9.78 s / 13.4 s**；**E2** `sim/cases_timeout.py:206-211` 的 `lease in successful_ids is False` 是**链式比较、恒为 False**（该子句永不失败），`:213-216` 断言传 `True`。另 CMD-I04C-08 无 raw log（声明已被复核者复现为真）。
- **I-08-A = `accepted_scoped`（范围仅限设计/契约提案）**：R1–R14 全做完（含 **7 条预登记变异全部命中预测**）；裁决正文已给实现者粘贴 `review.md §5.5`；5 项必修文本项（§5.1 表 20 处 file:line 全部失效、位移约 23 行；"35 条观测"→"35 行/32 个 id"；`handoff` 章节号与项数；`commands.json` 缺 `I08A-c10.expected_returncode`；`decision.md:117`"两个参数"→"三个参数"）已派。**E29/E30 口径双向更正**：E29"不可达"成立但"无用例"**不成立**（`NEG-LEGACY-6` 即其用例）；E30"从不 raise"在本卡基线上**不成立**（`trust_anchor.py:32-36` 确实 raise，`EXP-BASE-18` 实测）。
- **owner 待裁清单（更新版，均不阻塞当前并行）**：①**新增（reviewer 建议立卡，D 阶段前置）**：`model_registry.py:335` 对无声明默认值的 optional driver **静默补 0**（31 槽位/24 模型）——把"不存在"与"没找到"编码成同一输入；②**新增**：`_SIGNED_DRIVERS` 按**名字**而非语义角色决定符号（`other_revenue` signed 而 `usage_revenue` 非 signed；`franchise_system_sales`/`supply_revenue`/`recognized_performance_fees` 同属"可冲回已确认金额"却在 `[0,inf)`）⇒ 建议与①同卡改为基于角色的规则；③**rc 码表冻结**（见上）；④**I-00-B 绑定范围追认**（其 `binding.json` 只有隔离方案与两阶段规则、无 checkout 物化，而卡片 L49 明写"从 I-00-B 读取 isolated checkout"）——建议书面追认"物化由各 attempt 完成并记录来源 hash"；⑤原有：D-W05、D-W06、D-W15、I-04-C C2、M08 三步、M02-01、I-14-A D1/D2/D3、I-14-C C12、I-09-A OPEN-I09A-1…6（-1/-2/-3/-5/-6 阻塞 I-09-B）、**I-11-A OPEN-1…10（OPEN-2 铜当量系数、OPEN-3 微软分部口径、OPEN-5 港股原文、OPEN-6 四条专业阈值 阻塞 I-11-B/I-07-E；OPEN-1 是否允许 `pdftotext.exe` 作第二取文路径）**、I-14-B D-1（reviewer 填 `frozen_tolerance_seconds`，实现者提议 5 s）/D-2（是否用 PATH 上的 ffmpeg/playwright 建捕获路径）/D-3/D-6。
- **I-11-A 设计卡已交付待复核**：8 条冻结命题（**`approved_frozen` = 0**、pending_professional_decision 6、unquantified 2）、算术 oracle A1–A7 有理数精确 7/7、14 个先冻结反例 14/14 被拒、17 行日历映射**全部 pending**；**港股小米年报对象流 PDF 两条路径均不可读 ⇒ `STOP_EVIDENCE`，零条港股命题、未用二手稿补位**；自曝两处自查错误（`109,977,556,345÷885,141` 应为 **124,248.63**；FY2024 数据在 **328** 页而非 327）。
- **I-14-B 已交付待复核**：时间字段分列 + 重叠取并集（变异 MUT-1 把并集换回求和后 W4/W5 立即变红）；RED→GREEN 同一命令 rc **1/213 mismatch/12 个不合规主张被 accept** → **0/0/0**，pytest 30 failed→**32 passed**；合成用例实测观测 **1740 s（29 min）**而非 37 min；**30/60/120 容差未冻结 ⇒ blocked**（扫描实测 tol ≤86 s 一律拒绝、87 s 起通过；UI 捕获能力未建立：9/9 模块不可导入、4002 文件中 0 个预布置记录器，**但 PATH 上确有 ffmpeg/playwright 可执行文件 ⇒ 只能写"本 attempt 未建立"，不能写"物理上不可能"**）；17 行日历**全部 pending**；RED 侧外部锚点：只读导入**生产** `RF/tests/test_ca206_soak_window.py` 对"7 个不同 ID + 同一未来瞬时 + 空证据 hash"账本返回 `complete`（历史缺陷可复现）。
- **M01–M04 r4 记账整改完成（可入库）**：P1-1 取"补写"方案 —— 在 `M02/M04/oracle.md` 末尾**追加** `## 修订 r2 索引（独立复审后追加，非重写）`，首句即"**本节为事后补记：r2 轮曾声称已追加本节但实际未落盘**"，并写入追加前状态（M02 `7,838 B/77dce63d…`、M04 `10,495 B/1a69465b…`）、根因（`apply_r2_patches.py` 把追加**写死在 `if card == "M03":` 分支内**）与"MATCH 恰因从未追加、不得读成账目更规范"；**P1-2** 取"补落"方案（新写参数化 `selfcheck_card.py`，**四卡各自**产出 `recovery/r2_exit_code_selfcheck/selfcheck_result.json`，记录本卡 harness `b5fcc685…`，四卡 A/B/C/D = **3/1/0/2**）；**P1-3** `revision_history` 去重为 4 条 + 追加第 5 条 r4 裁决 → `[r1,r2,r2,r3,r4]`（两条 r2 是"待复核"与"五条已落地"两种不同结论）；**P2-1/P2-2** `status`→`accepted_scoped`、`reviewer_status`→`point_review_returned`、`qualification.json.formula.status`→`accepted_scoped`、`not_yet_independently_reviewed`→`false`（`implementer_claim` 保留、`disclosure_adaptation`/`accuracy` **两栏未动**）；**M03 provenance 永久登记**（`recovery/README.md` 新增 PERMANENT provenance event：`oracle.md` `## 7` 的派生单价 `123,751.5203…`→`123,751.503987`，`d0bed79b…`→`45f10b58…`，并写明"**对 M03 而言'冻结期望未被重写'不可用**，正确表述是'冻结正文被改动过一次、用于印刷笔误、且已自曝'，不回改"）；P2-3/P3-1/P3-2/P3-3 逐条（oracle 版本索引补成"追加前+当前"、自指 hash 改为显式 non-claim 并外置真值、`review_items` 按卡收敛、`shared_copy_registration` 登记三份四卡同拷贝文件）。裁决正文由 `extract_verdicts.py` **从报告 §12 逐字抽取**粘贴到各卡 `review.md`（非手工转写），并追加"未予验证事项"八条原样承接。`verify_r4.py` → **all checks pass, 4 cards**；`F-M02-01` 仍为 **owner 裁定项**（未自决、未改产品）。
- **入库**：`ddc81ab`（1732 文件，只含 `.planning` 证据与 PWF，零生产代码合并）已提交，推送 job 走 fcap pre-push 门中；此前 `e954449` 的门 GREEN 且 CI `quality` success。
- **记账补齐已落地并通过父代理抽查（2026-09-20 04:09–04:10）**：14 张"模式一"卡的 `handoff.json.status` 已由 `review_pending` 改为 **`accepted_scoped`**，`reviewer_status` 改为**指认 reviewer 亲手写下的那一行**的形式（例：I-00-B / I-02-A / I-03-D 均写 `accepted_scoped - verdict written by the independent reviewer in review.md:<行号>: "<逐字摘录>"`；I-14-A 指向 `review.md:233` 的 r3 复看段），**不是实现者自签**。父代理抽查 4/4 一致。连带处理：`next_action` 自相矛盾（I-00-D）、重复 `reviewer_status` 键（I-02-A）、`ACCEPT` 用词归一（I-02-D，注明待 reviewer 追认）等已按派单执行。
- **前沿已尽（重要结论）**：除在跑项外，**剩余 ≈24 张卡全部被"在跑卡"或"owner 门"卡住**，已无可新开工的卡 ——
  - 依赖在跑卡：I-04-E←I-04-D；I-08-C/I-09-B←I-08-B；I-09-C←I-09-B/I-08-C；I-17-A←I-14-B/I-16-B；I-10-A←I-07-B+全 M 卡。
  - 依赖 owner 门：**I-07-B（→I-07-C/E→I-12-A…E→I-13-A…C→I-16-A/B→I-17-A/B 整条链）依赖 D-W05（I-05-A OPEN-1/7）与 D-W06（I-06-A OPEN-2）签字**；I-05-B/C 依赖 D-W05；I-06-B 依赖 D-W06；I-15-A 产品实施依赖 D-W15。
  - 因此**下一轮起若无 owner 裁定，可推进的只剩"回收在跑复核结论 + 复评 + 入库"**。
- **接续清单（本段结束时的确切待办，按优先级）**：
 1. **回收并转发**在跑的复核结论 → 实现者处置 → 复看：M05–M08（四缺陷修复复看）、M09–M12、M13–M16、M17–M20、M21–M24、M25–M28、I-09-A、**I-08-A（R1–R14 全新裁决）**、**收尾三卡（I-00-A errata 确认 / I-15-A 证据面 / I-04-C r3 三项 still-required）**、**M01–M04 点复审**。
 2. **记账补齐**（已派）：14 张模式一卡的 `handoff.json` 补到与 `review.md` 一致；并修 M05–M08 `review.md` 重复 r2 节、`copy/copy_r2` 不可复现表述、M01 `revision_history` 重复、I-02-A 重复 `reviewer_status` 键、I-02-D `ACCEPT` 用词归一（待 reviewer 追认）。
 3. **三张返工待复评**：I-14-C（r4：F-I14C-R4-01…-07 + C12 硬前置）、I-08-B（P1-1 E29 不可达 / P2-1 E30 / P2-2 投影漏 4 键 / CONFLICT-1 两条 AST 断言）、I-05-A（A1 源字节切片绑定 / A2 C14 证据重跑 / A3 表述 + P3-1…4）。
 4. **在跑实施**：I-04-D（原子 lease + 9 项 carry）、I-11-A、I-14-B、M29–M31、M09–M12 的实现者报告。
 5. **owner 门（不得由实现者关闭）**：D-W05（I-05-A OPEN-1/7）、D-W06（I-06-A OPEN-2 幂等键）、D-W15（I-15-A 生产 prune）、I-04-C C2（OPEN-3）、M08 三步（更正目标串见 `task_plan.md` 实测值）、M02-01、I-08-B CONFLICT-1/2、I-14-A D1/D2/D3、I-14-C C12 产品前置、I-09-A OPEN-I09A-1/2/3/5。
 6. **入库**：新确认的接受卡按卡号 `git add` 指定路径 → 跑 fcap pre-push 门（必须 GREEN）→ push → 核 CI。**生产代码零合并**这一条从头到尾未破。

## 2026-09-20 — 实施段续二：接受 +6（**28/86**）、I-04-C C1 关闭 / C2 入 owner 门、隔离巡检

- **本段接受的卡（+6，累计 28/86）**：
  - **I-04-C（设计，accepted_scoped）**：三轮复审（r1 1P1×2+多 P2 → r2 → r3 签收）。随签 **C1 已关闭**：`decision.md` §13.5 与 `review.md` §1 P3-4 的 F-LK2 过时组 `[12,19,7,26,43] ⇒ lost [197,185,191,198,14]` 自身与 `expected=200` 不相容（`200−finals=[188,181,193,174,157]`）；真值 `[16,35,10,56,18] ⇒ lost [184,165,190,144,182]`、`range [144,190]`，由 `sim/verify_flk2.py` 从 `evidence/run/F-LK2-r{1..5}/` 逐轮复算 **13/13 PASS**；更正为**追加式**（`sim/verify_r4_appendonly.py` 证明删去插入块后重建 sha256 与改前逐字相等），原文与"261/200 撕裂写"历史叙述均保留。**父代理独立验收**：四个文件改后 hash 与实现者报告逐一相符（`decision.md f1a2396c…`、`review.md d416b73a…`、`handoff.json ac418ac6…`、`evidence/hashes.txt 698d6f71…`）。**C2**=OPEN-3（`lock_budget_for(x)=min(x,60)` 的命名/边界 + `worker-pause` 是否留在锁内）= **owner 裁定项**，`handoff.json.review_carry_conditions.C2_OPEN3_owner_gate` 明写不阻塞签收。
  - **I-07-A（accepted_scoped）**：更正 `config.legal_fifth_root` 为 planned（bound 9/planned 15/blocked 5/NA 0）、census LIMIT-20 低估 172×（真值 **3440** 组）、iso catalog 禁止事项、`future_lake` 实为 **1** 行 location（`README.md` 545 B）。
  - **I-14-A（accepted_scoped，仅隔离测量修复）**：D1 未签 ⇒ **不提升进 `RF/tools/`**；bundle 未被测量时恒 **exit 2**（对 D1/D3 的契约变更，须明示）；旧探针基线为父进程 `UnicodeDecodeError: 0xd4`（rc 不可观测）；tree-sum 高估约 11 MB；`calls.failed` 实为 6。
  - **M05 subscription / M06 usage_platform / M07 services（仅 formula 资格，accepted_scoped）**：冻结期望与 reviewer 预注册 `2a6398ed…` 逐一相等、负例 11/11、`oracle.json` 重生成逐字节相同、`run_card.py` 未漂移。
  - **M08 project_backlog = blocked**：`card_M08.md` L42 印出算式与上游"`+ 合同变更`"符号冲突；**父 agent 复核更正（2026-09-20）**：四个索引文件（`card_M08.md:42`、`model_cards.md:552`、`model_cards.json:1930`、`dispatch.json:5755`，各 1 处）印的都是**同一句读法 A 写法** `手算：100+40−5−10−15−60=50；−15重估必须剔除。`，此前流传的 `100+40−5−10+−15−60` **在四个文件里都不存在**；若裁定读法 C 权威，带符号呈现应为 `100+40−5+−10+−15−60`（**答案 50 不变，只改符号呈现**）；唯一出路 = owner 三步（裁定读法 C 权威 → owner 更正索引 → 同 `code_root 9ec65295…` 复跑留档）。复核另提出 **F-M08-06**（四份 `oracle.md` 各有两段重复 r2 节，第二段"追加前 hash"在任何行边界都复现不出）、**-07**（`oq_rulings.json` 计数错：ratio 驱动 41 非 40、不在 [0,1] 的 4 非 3，漏 `direct_growth.growth_rate=(-1,inf)`；且把 reviewer 署名为作者）、**-08**（重打包改了 `cases.json`/`run_result.json`/`negative_results.json` 的 hash，"冻结件未改"需限定说明）、**-09**（DEC-M08-1 仍 r1 措辞）。四项修复在办。
- **在跑（13 条）**：I-14-C r4 独立复核（r3 新 P1 **F-I14C-08** 重复 key 已修，`iso/product_fixed/observability.py 049f5d5b…`；**保真判据**已进 `run_rule_table.py`/`run_diagnostic_table.py`，任一不符 rc=2 —— r3 标本 T3 = `0 leaks` 且 **24** 条保真失败，修复树 T4 = 0/0；套件 76 passed；**C12 硬前置**：F-07 阻塞用例实测挂起 >90 s，产品测试必须加 `pytest-timeout` 或子进程硬超时；**C13** 裸值贪婪语义登记不改）；I-08-B 独立复核（CONFLICT-1 `subprocess` 豁免集、CONFLICT-2 `golden_behavior_hashes.json` 刷新待裁）；I-05-A r2 复评；I-07-A/I-14-A r2 证据复读；M05–M08 四缺陷修复；M09–M12 / M13–M16 / M17–M20 / M21–M24 / M25–M28 五批公式卡；I-09-A、I-11-A 设计卡。
- **隔离巡检（父代理，见 findings.md「隔离巡检」节与 `execution_runs/_isolation_incidents/20260920-prereg-expectations-leak/INCIDENT.md`）**：处置两处**我方越界写**（`revenue-forecast\prereg_expectations.json`、`filing-fetch\git_filing-fetch.txt`，均先保全再从生产树删除；filing-fetch porcelain 现为空）；登记一处**不可归因**生产变化（`assurance/runs/daily_alert.jsonl` 新增一行，格式与 run_id 口径为本仓每日告警作业自身，01:19 前已脏）**未回退**；一处 provenance gap（既有脏文件 mtime 于 02:24:00 批量刷新，`SKILL.md` sha256 与基线完全相同，其余如实声明无法证明）。生产不变量复测通过：company-wiki 三模块 `e8317991…/a73826aa…/fad88c60…`、catalog 49,677,344,768 B / `-wal` 0 B、porcelain 仅 2 条用户改动。
- **owner 待裁（累积，均不阻塞当前并行）**：D-W05（I-05-A OPEN-1/7）、D-W06（I-06-A OPEN-2 幂等键缺请求身份）、D-W15（I-15-A 生产 prune 五项）、I-04-C C2（OPEN-3）、M08 三步、M02-01（被忽略字段仍受域约束）、I-08-B CONFLICT-1/2、I-14-A D1/D2/D3、I-14-C C12 产品前置。
- **切片二（2026-09-20 03:5x）**：①**`1ac01f0` 已推送且 CI `quality` = completed/success**（pre-push 门 GREEN：mypy 契约集/元绑定/BOM/install-consistency/real-roots/real-data 全 ok；job 报 exit 1 是 PowerShell 把 git stderr 当错误记录的假阳性）。②**I-07-A 与 I-14-A 的 N1/N2 残留已关闭**：`I-07-A/oracle.md §8` 新增第三行，明确 "for any dimension/row-count question … never the word 'six' anywhere"（`a279bccb…`）；`I-14-A/after/summary.json` 的 `captured_at_utc` 改用 `datetime.now(timezone.utc)`（旧值以 `corrected_for_review_finding_N2` 保留未删，`1691abbb…`）。N2 另暴露一条环境事实：本机 `datetime.now()` 本地 03:49 而 UTC 02:49，但解释器 `time.timezone` 报 0 ⇒ **naive 本地时间贴 `+00:00` 在本机就已差 1 小时**。③两卡已把"HEAD 由编排层推进至 `1ac01f0`（仅 `.planning/` 49 文件、未触 `tools/`）"与"reviewer 对 company-wiki porcelain 的'完全为空'说法有误、实测为两条既有 ` M`"写入 `handoff.json`/`recovery/README.md`。④**M05–M08 修复已交回原 reviewer 定点复核**；实现者另更正了 reviewer 的两处前提（`afeefe43…` 类值**可复现 1 次**＝"v1 冻结体＋第一段 r2 正文"的中间写缓冲，reviewer 的行边界切法用 `rstrip()` 吃掉了 CRLF 的 `\r`；F-M08-08 点名的 5 个文件**只有 3 个真的变了**）。⑤**M17–M20 独立复核已派出**（自造输入复算 + 自造未披露负例 + 变异 + 重跑枚举）。
- **资格口径不变**：所有接受均为 **iso 副本 / 实施声明范围内**的 accepted_scoped；无生产代码合并、无生产部署、无真实 provider、无准确性资格。

## 2026-09-20 — 实施段：并行推进 I-08-A / M01–M04 / I-14-C / I-15-A / I-04-C（4 张接受、2 张返工）

- **接受（+7 卡，累计 22/86）**：
  - **I-08-A（设计，accepted_scoped；⚠️ 本行原写于 2026-09-20 实施段，当时的"r3 accepted_scoped"属超前记账，已被独立复核 P2-02 判为须撤回 —— 见本文件顶部最新段的更正：I-08-A 的盘上最新裁决在 04:03 才由新的独立 reviewer session 出具，为 `accepted_scoped` 但**范围仅限设计/契约提案**，且 `handoff.json.status` 至今仍为 `review_pending`）**：三层证明域 L1/L2/L3、`host_signed` 只能由 L3 验签产出、provider 协议（一次性子进程 + 精确字段集 + fail-closed 错误码表 **E01–E32 唯一来源**）、信任域三元组（fingerprint∈名单 ∧ issuer==声明 ∧ 时刻在窗口 ∧ active）、规范载荷（`canonical_sha256` 的 64 字符 ascii hex、排除自指字段）、重放/过期分离、旧版本 **G1/G2/G3a/G3b/G4 与 `classify()`**、**schema 3.8 → G3a 不得自动旁路 + R-LEGACY-1 + E29**、`public_keys` 键名冻结 + 非法名单**报错不静默**、参数 `W`/`T`/`L` 化并登记 OPEN-D7。三轮复审：r1 changes_required(6×P1) → r2 changes_required(R-BIND-1/2) → **r3 accepted_scoped**（复审独立写配对校验：32 码 0 mismatch；作者新 `check_r3_pairs.py` 对两类变异**均检出**）。**未授予**：provider 协议"无未决"（OPEN-D6/D7+三参数）、旧包兼容"已定案"、`tests/test_attestation.py` 可直接复用；**OPEN-D1…D7 已按裁定方入 handoff**（D1/D2/D3 建议同批）。
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


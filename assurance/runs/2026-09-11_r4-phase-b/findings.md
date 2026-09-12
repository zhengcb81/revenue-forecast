# R4 Phase B 发现（findings）

> 本文件在 B 设计阶段只记录**从阶段 A 继承的事实**与**设计期发现**；产品实测结果一律留待 B08/B.VR。

## F-B02-1：B02 段 3 的"同 hash 硬门"与 A 侧 4 条冻结断言冲突 → 实施让步（**S-10，待 owner 确认**）

- **事实**：`tests/contract/test_source_catalog_determinism.py` 的 fixture 写 `b"%PDF-fake"` 作字节，却把 `sha256(b"same-bytes")`/`sha256(b"other-bytes")` 当 `content_sha256`；`test_source_catalog_sql_pushdown.py` 同类。因此"字节必须等于声明 hash"若作为 **resolve 期硬门**，这 4 条既有断言必然失败（实测：硬门实现下 `determinism` 2 条 + `sql_pushdown` 2 条 FAILED）。
- **处置（已落盘）**：段 3 实现为**优先 + 逐候选诊断** —— 仍真读字节做**整文件**摘要比对、验证通过者优先、`verified_sha256` 仅验证通过时写入；若无任何候选通过验证但存在**本地可读**合格副本，则返回该副本并标注 `unverified_bytes`。**字节硬门归 B03 读路径**（设计 §B03 原文即"只返回验证版本字节或明确失败"）。
- **理由**：**S-1** 明令"仅新增测试、不得修改既有测试的任何断言"→ 让步只能在实现侧。若 owner 不认可，可选 (a) 另行批准修改那 4 条既有断言（与 S-1 互斥）或 (b) 把 B03 提前与 B02 合并交付。
- **证据**：[evidence/b02-implementation.md](evidence/b02-implementation.md) §3（复跑命令）；[evidence/b02-red-green-pre-b02.json](evidence/b02-red-green-pre-b02.json) / [post-b02.json](evidence/b02-red-green-post-b02.json)。
- **未做（勿当已完成）**：B03 落地前，**没有任何一层**对"读出来的字节"做返回前复验 —— 字节级硬门整体缺失。

## F-B02-2：重复计数口径随"合格"定义收敛（P2，副作用）

- **事实**：`_duplicate_summary` 原先按 `role/active/source_id` 统计副本，与新的"合格"定义（多一条 `.rejections` 排除）不一致。
- **处置**：改为只统计**合格**副本（`candidate_rank != 0`）。影响面仅 `.rejections` 泄漏场景：`exact_duplicate_location_count` / `exact_original_copy_count` 会变小。
- **证据**：`test_r4b02_l04_rejected_copy_with_best_priority_is_not_a_candidate` 断言新口径（`exact_duplicate_location_count == 0`、`exact_original_copy_count == len(healthy)`）。

## F-B02-3：首轮实现触发 FC-1201 根 token 门（P3，门按设计生效）

- **事实**：`_needs_hydration` 的 docstring 写了 `dropbox_stock` 与 `Dropbox` → `test_fc1201_root_hardcode_gate.py`（2 条）与 `test_future_root_config_only.py`（1 条）FAILED；同文件在干净 HEAD 上 10/10 passed（`git worktree` 对照）。
- **处置**：改写为与 root 无关的措辞（"a synced vendor root that materialises files on access"），三处门恢复通过。
- **意义**：这条门确实能挡住"把 root id 写进代码（含注释）"，是有效护栏而非误报。

## F-B01-5：`B.DR-rev5` = **rejected**（2×P1 / 4×P2 / 5×P3）→ v0.1.6，且**本次改用"新值在场 + 旧值不再作为断言"的双向自证**

审查记录 [reviews/B.DR-rev5.json](reviews/B.DR-rev5.json)（reviewer `52907a2f-…`；55 条输入哈希全部独立复算相符）。**本轮最重要的发现是过程性的，而非技术性的**：`B-DR5-01` 指出 **F-B01-4 的"处置"栏第二次把未做的改动写成已做** —— 与前一轮同一根因。作者据此把自证方法改为**双向**：

| 声明 | 检验（新值在场 **且** 旧值不再作为断言） | 结果 |
|---|---|---|
| N-1 从 B07 完成定义移除（v0.1.6） | 新值 `**不含 N-1**` @ `b-design.md:210`；旧值 `N-1 判定` 仅存于 findings 历史行 | ✅ |
| B07 可签列不含 N-1 | 新值 @ `b-design.md:205`；旧断言串 0 处 | ✅ |
| `metadata_json` 禁整列替换 | 新值 @ `b-design.md:149`（含 `:1073-1077`、`:1095-1099`） | ✅ |
| `legacy_observer.py:90` 入共享读取者 | 新值 @ `b-design.md:154` | ✅ |
| provenance 禁写原文片段 + `schema_version` | 新值 @ `b-design.md:159-160` | ✅ |
| 覆盖率棘轮 + `NEW_FILE_MAX` 登记 | 新值 @ `b-design.md:228` | ✅ |
| `B-payload-hash` 当前不可执行 | 新值 @ `test-acceptance-map.md` §1c | ✅ |
| VR-N21 移出 B | 新值（否定式）@ `b-design.md:193`；旧断言串 0 处 | ✅ |
| R-6 计数 = 11 锚点（v0.1.6） | 新值 @ `file-scope.md:51`；旧断言 `9 处同型排序` 0 处 | ✅ |
| F2 步骤列含 B06 / F11 移出 allowed | 新值 @ `file-scope.md:15`、§1b | ✅ |
| inputs 内层注记（逐文件版本） | 新值 @ `evidence/build_checkpoint.py:302`（外层字段会被 `main()` 覆盖，故写入 `inputs` **内层**） | ✅ |
| 版本/状态行（v0.1.6、F10 已获批、rev1–rev5） | 新值 @ `b-design.md:3`、`task_plan.md:80`、`file-scope.md:6` | ✅ |

**自证脚本自身的缺陷（一并登记，因为它同样属于"声明 vs 事实"）**：
1. v1 只查"新值在场" → 误报 22/22（**这正是 B-DR5-01 的根因**）；
2. v2 未把 `evidence/build_checkpoint.py` 纳入检索集 → 对 inputs 注记误报 FAIL；
3. v2 断言"恰好 4 轮复审" → 台账实为 5 轮，误报 FAIL；
4. v3 缺少"历史行豁免" → 对 `findings.md` 引用旧措辞误报 FAIL。
→ 现法：**双向 + 明确检索集 + 历史豁免（仅限带版本前缀的变更记录）**，结果 `16/16`，落盘 [evidence/claim-fact-audit.json](evidence/claim-fact-audit.json)。

**其余处置**：`B-DR5-03`（`metadata_json` 胜利路径整列替换）→ 已在 §B05 第 5 条禁止，并把 F3 锚点扩到 `scanner.py:1007-1099`；`B-DR5-04`（`B-payload-hash` 无基线且需待批 CLI）→ 标注为**当前不可执行**，须先在隔离副本冻结基线；`B-DR5-05` → 补 `legacy_observer.py:90` 并**禁止把原文片段写进 provenance**；`B-DR5-06` → 登记**覆盖率棘轮**（TIER1 `policy.py`/`service.py`=95、TIER2 `resolver.py`=86）与 `NEW_FILE_MAX=10`；`B-DR5-07…11` → VR-N21 移除、L06 口径统一、progress 状态行改真、F11 移出 allowed 表并写明调用目标、保留键加 `schema_version`。

- **新增待 owner 决定项 S-8**：把执行计划 `§B07` 的"先测 N-1 支持合同"整体移出 B，属**范围改判**，按本包自订标准（"不由本设计改判"）须 owner 确认——已登记在 [task_plan.md](task_plan.md) §5。
- **状态**：v0.1.6 已就地更正并双向自证；reviewer 明示架构无需推翻。

## F-B01-4：`B.DR-rev4` = **rejected**（11 条，均为文本/落点级；reviewer 明示"一次编辑可收敛、架构无需推翻"）→ v0.1.5

审查记录 [reviews/B.DR-rev4.json](reviews/B.DR-rev4.json)（reviewer `1f962189-…`，非作者会话；claim_checks 复现 5/15）。**该记录最有价值的部分是它抓到的"声称已修但实际未改"**——这正是本包连续被拒的根因。

| 发现 | 级别 | 事实 | v0.1.5 处置 |
|---|---|---|---|
| **B-DR4-01** | **P1** | B05 把 provenance/冲突塞进既有列 `documents.metadata_json` 的**顶层**，而该列是**多方共享的扁平命名空间**：`service.py:271-272`（`$.acquisition.fiscal_year` / `$.dayu_meta.fiscal_year` 过滤）、`llm_summarizer.py:388-392`（`$.prompt_injection_review.*` LLM 门，**该文件在禁止表内**）、`prompt_injection.py:101-128`、`scanner.py:1039-1045` 都按固定路径读它 → 照 v0.1.4 施工会**静默打断财政年度过滤与 LLM 门** | §B05 改为**只在保留键 `r4_provenance` 下新增**、**既有键原样保留**；L08 增加 **`json_extract` 回归断言**（证明 fiscal_year 过滤与 prompt_injection_review 门仍读到原值）；读取侧只读 `r4_provenance` |
| **B-DR4-02** | **P1** | **S-2 只在一处生效**：`b-design.md:36` 仍写"按 owner R-4：补门"、`:47` 仍令"两处默认值必须同改"、`:43/:45` 仍带 R-1 处置、`file-scope.md` F6 改动性质栏仍写 R-4、F10 与 test-map 仍把"合成 `privacy_class` 配置"列为 B 的断言 → **照 file-scope 施工即越界** | 全部就地改判：外向策略行标"**不属于 B**"、`privacy_class` 行改"**B 不改**"、`read_only`/`symlink_policy` 行改"**B 不改其处置**"、F6 改动性质去掉 R-4、F10 断言清单删"合成配置"、test-map 的 R-4 绑定行划掉 |
| B-DR4-03 | P2 | S-4 把**尚未定义**的"N-1 判定"写进 B07 的完成定义；两侧代码都只接受 `"1.0"`（`resolver.py:163-166`、`filing_contracts.py:273-277`），唯一"真实 N-1"是 `filing-audit.md:61` 要求**废除**的字段缺失降级 | B07 完成定义**移除 N-1**；N-1 登记为**跨仓协议待定义项**；B 只承诺"未知版本显式拒绝" |
| B-DR4-04 | P2 | checkpoint LEDGER 在受审修订处仍失真（step=v0.1.3、S-1..S-6 写"待裁定"、pending_review 无 rev2/rev3、gate="submitted"、next_step 是 rev1 时代、两条 failed_or_unknown 已被推翻、副作用现在时无时刻） | LEDGER **整体重写**：step=v0.1.5、S-1..S-6 记"已定"、**四轮复审全部登记**、`gate_status` 含 S-1..S-6 与 S-7、副作用改"**已发生**"并带时间戳与推送号 |
| B-DR4-05 | P2 | 生成器**写路径从不检查 `all_match`**；completeness 是同进程自比较（rc=3 不可达）；排除集未披露致 `files_on_disk` 对"目录内真实文件数"为假 | 写路径新增 **all_match 断言（rc=4）**；completeness 记录 `excluded_by_design` 与说明（"自比较，不能发现生成后新增的文件；`--verify-only` 才是发现点"） |
| B-DR4-06 | P2 | **未登记的默认门**：`test_fc1204_complexity_ratchet.py` 默认运行，且 **`config.py` 46/46、`scanner.py` 140/140、`policy.py` 5/5 恰好顶格** → 加一个判定点即失败；其自述补救是**改既有测试文件**，与 F10"仅新增"互斥 | 新增 **[b-design §B0x](b-design.md) 复杂度棘轮约束**（要求改动**复杂度中性**、每步真跑棘轮测试、做不到就停）；并把"是否允许更新棘轮表"登记为**新边界问题 S-7（待 owner）** |
| B-DR4-07 | P2 | findings.md 把**四处未做的改动**记为已做（LEDGER 前进/inputs 注记、R-6 表头 11 处、F9 引用清理、"§B03 给 max_bytes"） | 逐条**先做再写**：inputs 注记与 R-6 计数已在 v0.1.5 落地；F9 引用清理与 `max_bytes` 表述在 §B03/§B02 明确；本表即更正记录 |
| B-DR4-08 | P2 | B05 冲突结果写 `ambiguous`，而执行计划原文是"真冲突仍 **blocked**/待选择"；且响应级/字段级粒度与 `capture_ready` 不变式未定 | 冲突状态改回 **`blocked`**（`ambiguous` 只用于 L07 的"版本关系未知"）；明确**响应级状态 + 字段级冲突明细**；新增 `capture_ready` **不变式**（合格副本存在且身份/期间可判时不得变 false）并在 L09 断言 |
| B-DR4-09/10/11 | P3 | ① v0.1.4 编辑遗留（file-scope H1 版本、task_plan"F10 尚未获批"、changelog 止于 v0.1.3、F2 步骤列缺 B06、VR-N21 仍挂 B、progress 仍 v0.1.1）；② F11 哈希占位且"允许修改/不修改"自相矛盾；③ 继承的 `owner-rulings:25` 仍写 R-2"两处…收敛为一处"，与 root-contract v0.4.2 相反 | 三处就地更正（本批 diff）：版本标签统一 v0.1.5、F10 记"已批准"、changelog 补 v0.1.5、F2 步骤列补 B06、VR-N21 从 B 移除、F11 填实测哈希 `0ee11644da75e24d`（2792 B）并明确"只读调用≠可修改"；**A 侧 `owner-rulings` 的 R-2 措辞同步更正为"三处、对齐语义"** |

- **过程教训（v0.1.5 写入 risk-and-stop-rules §4）**：本轮被抓的实质是 **"我声称改了、文件里没改"**。→ 规则：**每条"已修"声明必须当场用 grep 自证**；提交前跑一遍"声明 vs 事实"清单（见 §5 的验证方法）。
- **状态**：v0.1.5 已就地更正；reviewer 明示**架构无需推翻**，故按其建议送 `B.DR-rev5`（须全新会话）。**S-7 是唯一未定的边界问题**。

## F-B01-3：`B.DR-rev3` = **rejected**（round-1 14/20、round-2 6/15 闭环；新增 11 条）→ v0.1.3 更正

审查记录 [reviews/B.DR-rev3.json](reviews/B.DR-rev3.json)（reviewer `ba59c7cd-…`，非作者会话；14 条 claim 中 6 条未复现）。**实际读到的修订**：phase-b 除 `checkpoint.json` 外的 11 个 blob = `9d21963`（逐字节相符），`checkpoint.json` = `472bd206`；**A 侧并非整体 v0.4.2**（只有 `root-contract.md` 是，`operation-contract.md`/`identity-contract.md`/`owner-rulings` 仍是 26fb780）——该观察正确，本 run 未声称过 A 侧整体 v0.4.2，但**台账里确实容易误读**，v0.1.3 在 checkpoint 的 `inputs` 注记里写清"逐文件版本"。

| 发现 | 严重度 | 事实 | v0.1.3 处置 |
|---|---|---|---|
| **B-DR3-01** | **P1** | owner **R-4**（外发门 + 无门出口）与 **R-1**（假保证字段处置）被写成 B01 的"处置/验收"，但承载文件**全在禁区** → 设计要素不可实施 | 新增 **[b-design §B01.3](b-design.md)**：两项**移出 B 的处置与验收**，只作引用；纳入 B 的条件 = owner 扩大 allowed_files 并重签工作包 |
| **B-DR3-02** | **P1** | B05 取消整行覆盖却**未给逐列合并规则**；"冲突按 priority 择一"与执行计划 §B05「真冲突仍 blocked/待选择」及 L08 相反；`scanner.py:1046-1058` 的 `capture_ready` 死锁恢复路径有回归风险 | §B05 新增**逐列合并表**（单值仅用于 `primary_source_id`；真冲突 → `ambiguous`）；显式保留"后到来源补空值、但不覆盖已确认单值"的恢复路径，并把"先缺后补"加入 L08 用例 |
| **B-DR3-04** | **P1** | allowed 全是产品源码/冻结 YAML，**无测试落笔处**，新断言无处实现 | file-scope 新增 **F10**（`tests/contract/**` **仅新增**文件）与 **F11**（只读金丝雀）；test-map 加注"若 F10 未获批，则本包不能声称可实施" |
| B-DR3-03 | P2 | 抽样预算无法证明整文件 `content_sha256`（L03 不可判定）；且引入五值之外的 `unknown` | §B02 预算**重写**：合格必须**全量 hash**（≤256 MiB/候选，超限即 `unavailable`），抽样**只用于排除**；**撤销 `unknown`**，未判定表达为 `blocked`/`unavailable` + `pending_candidates` |
| B-DR3-05 | P2 | 生成器"断言完整性"实为记录：写路径无条件 rc=0、生成时刻自比较、`--reviewed-commit` 不校验存在性、比对锚点从不取被审修订 | 生成器改为**真断言**：`--reviewed-commit` 必须解析为存在的 commit（否则 rc=2）、清单不完整时**拒绝写出**（rc=3）、`--verify-only` **按 `reviewed_commit` 比对**并同时报告完整性 |
| B-DR3-06 | P2 | 版本/台账标注失真（step=B v0.1.1、current_gate=rev2 pending 等） | checkpoint LEDGER 随 v0.1.3 前进；§inputs 注记说明"逐文件版本"（A 侧并非整体 v0.4.2） |
| B-DR3-07 | P2 | 计数与交叉引用不 reconcile（12 行/16 名 vs 14；R-6 表头 9 处 vs 11 锚点；F2 引用已删除的 F9；`evidence_query.py` 未入禁止表） | 计数统一为 **12 行 / 16 名 + `kind`**；R-6 表头改 **11 处锚点**；F9 引用清理；`evidence_query.py` 移入禁止表 |
| B-DR3-08 | P2 | 同一文件 L06 自相矛盾（§1 = B、§2 = B/C），矩阵原文 = **B** | test-map 两处统一为 **B**，并注明更正来源 |
| B-DR3-09 | P2 | B07 可签列含无规则的"N-1 支持"，并把执行计划归 B 的"最小协议适配"**单方面改判给 C** | §B07 改为**明确不签**消费者侧（含最小协议适配），并登记"是否扩范围"为 **owner 决定**，不由本设计改判 |
| B-DR3-10 | P2 | B06/L09–L10 未切分；file-scope 无 B06 落点行 | file-scope 新增 **§3b 各步骤落点行**（B06 → F2 `ResolutionEnvelope`）；test-map 的 B06 行标注"仅 wiki 侧" |
| B-DR3-11 | P3 | 推送**已发生**但 checkpoint 仍用将来时、未登记为实际副作用 | progress.md 新增 **§2b 实际副作用（已发生）**；checkpoint 的 `actual_side_effects` 同步 |

- **三轮的共同教训（v0.1.3 写入 risk-and-stop-rules §4）**：① **"写了却做不了"**（设计要素无 allowed 落点）是本包最容易被拒的形态；② **同一事实多处维护必漂移**（"两处/三处"、"4 个/0 个"、L06 = B/B/C）；③ **护栏必须是断言而不是记录**。
- **状态**：v0.1.3 已就地更正；**剩余 P1 已全部转为 scope 决定**（见 [task_plan.md](task_plan.md) §6），需 owner 定夺后才能进入下一轮复审或实施。

## F-B01-2：`B.DR-rev2` = **rejected**（7/20 闭环；新增 1×? 计的 15 条）→ v0.1.2 逐条更正

审查记录 [reviews/B.DR-rev2.json](reviews/B.DR-rev2.json)（reviewer `92aeb4c7-…`，非作者会话；**18 条 claim 中 10 条未复现**）。**round-1 的 20 条中 7 条真闭环**（B-DR-01 P0、06、07、08、09、10、13），其余 13 条仍未闭环；**新增 15 条**（P1×3 / P2×9 / P3×3）。

| 发现 | 严重度 | 事实（作者复核） | v0.1.2 处置 |
|---|---|---|---|
| **B-DR2-01** | **P1** | gate ②"收敛现存两处"按字面**不可满足**：活实现是**三处**——`policy.py:67-72`、**`policy_2x.py:308-312 _effective_reusable_2x`**（经 `:292` 在 `export_policy_2x` 内 → `cli.py:849-851` 在产）、`resolver.py:782-786/:933-940`；而第三处正位于 v0.1.1 自己冻结的导出路径内 | [b-design §B01.1/§B01.2](b-design.md) 改为"**对齐①的语义到②③**，不删③（在冻结导出路径内）"；A 侧 root-contract 同步更正为 **v0.4.2**（三处） |
| **B-DR2-02** | **P1** | `b-design.md:44` 写"缺省值变更影响所有未显式声明的 root（现为 4 个）"与冻结配置相反：`config/source_catalog.yaml` 的**四个 root 全部显式声明 `privacy_class: public`**（`:19/:24/:29/:40`）→ **受影响集合 = 0**，R-4 在现网**惰性** | 该行改为"受影响集合 = 0；验收只能靠**合成配置**；不得声称现网行为会变"；A 侧 root-contract §5 同步 |
| **B-DR2-03** | **P1** | B07 的"边界 adapter / 无 companies fallback"在 allowed 内**无落点**（`adapters/*`、`filing-fetch/**` 全在禁区），而验收映射把整条 L11 挂给 B07 | [b-design §B07](b-design.md) 新增**可签/不可签对照表**（B 只签 wiki 侧四件：版本化合同、N-1 判定、不新增 fallback、payload hash 不变）；[test-acceptance-map](test-acceptance-map.md) 的 B07 行同步标注"消费者侧未验" |
| **B-DR2-05** | P2 | B05 在"不落库"下**无法满足 L08**：落选值已被 `scanner.py:1078-1081` 覆盖销毁，读取层拿不到；`metadata_priority`/`:1038` 未处置 | §B05 改为：**写入侧停止销毁**（provenance/冲突写进**既有列 `metadata_json`**，**不新增列、无需 store.py**）；`metadata_priority` 保留但**不再决定覆盖**；若要求一等列（可索引）则**升级为独立工作包** |
| **B-DR2-06** | P2 | `resolver.py:1166` 是 `return None`——"首选不可用→切换"**今天不存在**，v0.1.1 的"保留该行为"是错的 | §B02 给出 `_handle` 的三条具体要求（合格清单入参、清单耗尽才 `unavailable`、返回实际选中项与理由） |
| **B-DR2-07** | P2 | B06 的 preview **无承载接口**、allowed 内无文件承载 | §B06 定案：载体 = **`ResolutionEnvelope`（`resolver.py:359-417`/`:418-552`）新增 `qualification` 字段**；消费者既有门与之对齐；若需新命令则属新增能力（待批） |
| **B-DR2-04** | P2 | L06 阶段写错（矩阵是 **L06 B**），反覆盖表仍归并 | [test-acceptance-map](test-acceptance-map.md) §1/§2 改为**逐行照抄矩阵**（L05 B/C、L06 B、L10 A/B/C、L12 A/B/C…） |
| **B-DR2-08** | P2 | `llm_summarizer.py` 同时出现在 allowed（F9）与 forbidden；F9 的哈希格为空 | [file-scope](file-scope.md) 从 allowed 表移除 F9（只留禁止清单）并给出哈希 `13ff33b76547d39d` / 24 572 B |
| **B-DR2-09** | P2 | checkpoint 机制未按 round-1 要求落地：无 commit 锚点、无完整性断言、`reviewed_commit` 非必填；被审修订自身 `reviewed_commit` 仍是 `"PENDING…"` | **生成器改造**：`--reviewed-commit` 变为**必填**；新增 `commit_anchor`（生成时 HEAD + tree）与 `completeness`（遍历运行目录断言"无未登记文件"）；`--verify-only` 报告对比修订与"不能证明什么" |
| **B-DR2-10** | P2 | B01.2 计数不自洽（写"14 字段"，实际 16 名 / 12 行），`admission_profile_id` 未映射 | §B01.2 更正为**12 行 / 16 名 + `kind`**，并补 `admission_profile_id` 行与"计数口径"说明 |
| **B-DR2-11** | P2 | B02 资格判定与 B03 交付**无预算/取消/尺寸上限**（L06/L12 要"有限资源/可取消"） | §B02 新增预算段（每候选 ≤1 MiB 采样、单请求 ≤32 MiB / ≤64 候选、超限标 `unknown`、可取消）；§B03 要求调用方给 `max_bytes` |
| **B-DR2-12** | P2 | A 合同明文"resolve payload 字节契约 = B02/B04 必测"，B 的验收映射**缺失** | [test-acceptance-map](test-acceptance-map.md) §1c 新增 **`B-payload-hash`** 必测项（不新造矩阵 ID，登记在本包） |
| **B-DR2-13/14/15** | P3 | ① "handbook §2.5" 仍残留在 `progress.md` 与生成器 LEDGER；`findings.md:40` 仍引 a06 §1；② `progress.md` 仍是"23:3x"与未来时（推送**已发生**）；③ loader"无调用者"漏了 `policy_3x.py:95` 这个真实调用点，"先停用"无 allowed 文件 | 三处就地更正（本批 diff）：引用改 §1 第 5 项 + §3；时间改实测值、推送改过去时；file-scope 的 loader 行补 `policy_3x.py:95` 并说明"停用=不引入，无需改文件" |

- **教训（v0.1.2 新增）**：**同一事实在两个 run 目录各写一遍就会漂移**——本轮"两处/三处"与"4 个/0 个"都源于重复维护。→ 规则：事实的**权威处唯一**（此处 = A 侧 root-contract v0.4.2），B 侧只引用不重述。
- **v0.1.2 声称的三处 P3**（实际未全部落地，见 F-B01-4）：handbook 引用改为 §1 第 5 项 + §3（`progress.md`、生成器 LEDGER）；变更记录时间改为实测值、推送改为过去时（`progress.md`/`task_plan.md`）；`file-scope` 的 loader 行补 `policy_3x.py:95` 并说明"停用=不引入，无需改文件"。

## F-B01-1：`B.DR` 独立设计审查 = **rejected**（1×P0 + 7×P1 + 9×P2 + 3×P3）→ v0.1.1 逐条更正

审查记录 [reviews/B.DR.json](reviews/B.DR.json)（reviewer session `7ad6f0f0-…`，非作者会话；17 条 claim_checks 中 **8 条未复现**）。**未复现的声明是最有价值的部分**——它证明"文档写了"≠"事实成立"。

| 发现 | 严重度 | 事实（已由作者复核） | v0.1.1 处置 |
|---|---|---|---|
| **B-DR-01** | **P0** | `policy_2x.py` **并非整体无生产调用者**：`cli.py:835` `_policy_export_payload` → `:849-851 export_policy_2x(config)`，由 `:811`（ensure）/`:831`（policy-export）/`:1182`（**resolve**）调用；其 payload 是 filing-fetch **FC-501 containment / ZR-405 policy_hash 唯一来源**（`filing_contracts.py:450/461-497`）。v0.1 据此把它列为"可停用/禁改"是错的。**同一 P0 亦被 A.AR-05 与 A.VR-05 独立命中** | [b-design](b-design.md) P-4 与 §B07 范围表、[file-scope](file-scope.md) §2 首行改为"**在产、字节/hash 契约冻结、不得按 R-3 停用**"；A 侧 root-contract 更正为 v0.4.1 并把 R-3 范围收窄为**仅准入 loader** |
| B-DR-02 | P1 | B01 的"旧字段版本映射"**交付物缺失**，而 task_plan/test-map 已声明完成 → gate 第一项无审查对象 | [b-design §B01.2](b-design.md) 补齐 **14 字段映射表**（含迁移条件），并要求产出 `field-owner-map.json` |
| B-DR-03 | P1 | B05 只盯 `metadata_json` 不够：`scanner.py:1078-1081` 的 UPDATE 还由 priority 胜出者写 `title/source_type/document_kind/published_date/source_status/primary_source_id`，开关在 `:1038` | §B05 改为**覆盖整条 UPDATE 的全部列**；并删除"完全移除 priority"的过强表述 |
| B-DR-04 | P1 | B02/B04 漏了 **`resolver._handle`（`:1142-1224`）**：`:1153-1165` 二次 canonical 过滤 + `:1166 is_file()` 才是"撤首选→自动切换"的落点 | §B02 明确**两处同改**（`service._annotate_locations` + `resolver._handle`）；file-scope F2 补锚点 |
| B-DR-05 | P1 | B07 的"无 companies fallback"实现在**禁止仓**（`filing_contracts.py:485-486`），且 `adapters/*`、`adapter_dispatch.py`、`cli.py` 未分类 | §B07 新增**范围重划表**：B 只保证"不新增 fallback + 合同显式声明"；消费者侧实现**归 C**；`cli.py:835-857` 冻结、adapters 列 forbidden |
| B-DR-06 | P1 | `.rejections`"只标记不屏蔽"与风险文件"拒绝在排序之前"**自相矛盾**，且无测试 ID 承接 | §B02 第 2 段改为**保持排除语义**（`.rejections` 属资格段）；风险文件同步更正；验收挂 L04 |
| B-DR-07 | P1 | B03 只在打开时校验 → **TOCTOU 未闭合**（Windows 共享模式只在打开时裁决） | §B03 改为"**读后对实际返回字节复验**"，并把"仅打开时校验"列为禁止 |
| B-DR-08 | P1 | B02 第 3 段"查询期真读字节"可能触发**云占位 hydration**（`dropbox_stock`），违反 A03 R3/P-5 与 L01"零网络" | §B02 第 3 段加硬约束：**资格判定不得联网**；需 hydration 的候选一律 `unavailable` |
| B-DR-09~17 | P2 ×9 | ① F1–F8"逐一等于 A01 §0"不成立（`reader.py` 非 A01 冻结项）；② F8 的"行号 `:1-3384`"实为字节数；③ **已存在两处活 `_effective_reusable`**，只禁"新增"不够；④ B05 的 provenance 落点/持久化未定（需 `store.py`）；⑤ owner R-6 的 5 个同型排序文件未分类；⑥ preview/verified_input **无承载接口**；⑦ R-1/R-2/R-4 未绑定测试 ID；⑧ `--verify-only` 只锚定运行时 HEAD、`reviewed_commit` 不校验、`reviews/**` 不在账内；⑨ "未执行任何 CLI"纯自述 | ① file-scope §5 逐行标注；② F8 改为符号锚点 + "共 86 行"；③ §B01 改为"收敛现存两处、不得出现第三处"；④ §B05 决定**B 只在读取合同输出 provenance、不落库**（持久化升级为独立工作包）；⑤ file-scope §3 给出 9 处的 allowed/forbidden 分类；⑥ §B06 明确 preview 合同归 B06 并须给出承载字段/命令；⑦ test-map §1b 新增**裁定↔测试绑定表**；⑧ checkpoint 生成器改为报告 `source_revision`/`head_revision` 并显式列出 `does_not_prove`，且 `reviews/**` 纳入清单；⑨ checkpoint 的副作用字段改为**如实披露**（`-shm` 由本次推送的 gate 触碰） |
| B-DR-18~20 | P3 ×3 | ① handbook 无"§2.5"（正确为 §1 第 5 项 + §3）；② 变更记录时间"23:3x"与实际（07:43–07:46）不符；③ 反覆盖表把 O03 标"不属 B"却承认交叉，L06/L11 阶段列与矩阵不符 | 风险文件 §5 + test-map §2 就地更正；变更记录改真实时间 |

- **教训（已写入 risk-and-stop-rules §4）**：把"某个符号无调用者"提升为"某个模块/路径无调用者"必须**重追 caller**——本轮 P0 正是这样产生的。
- **状态**：v0.1.1 已就地更正；按 B.DR 的要求，**需由另一名独立 reviewer 出 `B.DR-rev2`**，且 rev2 必须基于**新的冻结提交与新的输入哈希集**。

## F-B00-1：B 的三个改动热点全部落在阶段 A 已实测的"残留"上，不是凭空设计

- 证据（阶段 A 实测，含行号与哈希）：
  - **候选选择"先 canonical 后筛"**：`resolver.py:912-921` 在 `is_canonical` 上过滤，而 `is_canonical` 由 `service.py:643-653` 的 `(root_priority, root_id, relative_path, location_id)` 排序取 `ordered[0]` 决定 → 未被选中的同版本副本在查询早期即被屏蔽。
  - **metadata 真伪由 priority 决定**（F-B00-1，v0.1.0 记录；锚点范围后经 v0.1.6 更正为 `scanner.py:1007-1099`）：关键比较 `:1038`。
  - **复用判定不读显式声明**：`resolver.py:782-786`/`:933-940` 只看 `root.kind`（owner 裁定 R-2 要求 `false` 生效）。
- 影响：B02/B05 是**同一根因**（"位置/优先级被当成业务判据"）在两个层面的表现；B 的整改应**一次收敛**，避免打补丁式两处各改一半。

## F-B00-2：owner 裁定把"改不改"与"怎么改"分开了，B 因此可以在不碰代码的前提下完成设计

- 证据：[owner-rulings-2026-09-11.md](../2026-09-11_r4-phase-a/owner-rulings-2026-09-11.md) 六条全部是"方向 + 登记"，且明示"不授权现在修改产品代码"。
- 影响：B 的实施入口是 **owner 批准 [file-scope.md](file-scope.md)**（DEV 工作包 + 文件范围），而不是本次对话里的"接着做"。设计可以连续推进，代码不能。

## F-B00-3：B08/B09 的硬前置是**隔离副本**，而隔离副本不必是 49.7 GB 的拷贝

- 证据：矩阵 L01–L12 的机制层可用"新建小 catalog + 既有测试的 tmp-catalog 机制"覆盖（wiki 既有测试即如此运行，见 [a06-baseline-plan.md](../2026-09-11_r4-phase-a/a06-baseline-plan.md) §2/§4（v0.1.2 更正引用，B-DR2-13））；只有"真实四 root 端到端读取"（B09/L02/L09/L12 的 R1 层）需要真实字节。
- 影响：**G8 可分两级**——① 机制层隔离目录（成本低，可立即建，只需 owner 同意"允许在非生产路径创建目录"）；② 真实字节读取（需要在隔离根下引用真实文件，**只读**）。把 G8 当成"复制 50 GB"会无谓阻塞 B08。

## F-B00-4：B 的"零副作用"证明不能靠作者声明（阶段 A 的教训）

- 证据：阶段 A 的 [boundary-audit.md](../2026-09-11_r4-phase-a/boundary-audit.md) —— `-shm` mtime 不是可靠的"未开库"判据（本机至少三类合法开库动作），且作者自证不构成独立证据。
- 影响：B08 的"独立文件/OS 观察"必须由**独立 reviewer**执行并记录**方法**（观察什么、怎么观察、看到什么），作者只提供被观察对象。

## F-B00-5：设计期就能排除的一个错误方向——"用 priority 排序就不会有问题"

- 证据：矩阵 L08 明确要求"swap priority/scan order 不改变业务元数据"；执行计划 §B05 明确"不以 priority 决定真伪"。
- 影响：B02 第 4 段保留 `priority` **只作排序**，B05 把 priority 从 metadata 真伪判定中**完全移除**；任何"给 priority 更高的权重让它更权威"的方案都直接违反验收。

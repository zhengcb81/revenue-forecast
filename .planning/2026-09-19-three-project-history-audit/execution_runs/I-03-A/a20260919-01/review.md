# I-03-A review.md — 独立高级 reviewer 复核（a20260919-01）

- Reviewer：独立高级 reviewer（本卡"高级 reviewer 先定案"角色由本复核承担）。
- 日期：2026-09-19。性质：纯设计卡复核；只读三仓 + 仅写本 review.md。
- **结论：accepted_scoped**（复签，无未定格需要否决；见 §8 保留意见与 §9 限定）。

## 0. 输入指纹复验（先于内容）

| 文件 | 复算 sha256 | 与 handoff/卡内冻结值 |
|---|---|---|
| card_I-03-A.md | `7178fc51…2528179` | 一致 |
| current_recheck.json | `183352a2…e8aec4` | 一致 |
| gap_plan.py（95/214） | `d18391b7…907c79f` | 一致 |
| authorization.py（23） | `f858a369…d55f43` | 一致 |
| close_gap.py（55） | `117c8166…475c3` | 一致 |
| acquisition.py（74，实际调用方） | `c68a1c14…24067` | 一致 |

本次产物 hash（供下游引用，关闭标准要求"后继卡引用决策文件 hash"）：

| decision.md | compat-matrix.md | oracle-inputs.csv | oracle.md |
|---|---|---|---|
| `963229846b06ed3b4f48d0d3192b444101b5e16e5a4989d53abdbd1a983e910d` | `09040e469efd870bee12c436228536db9bb523af03a907bd4932c093a2161d2a` | `6b070c8eb979390bf455094713d2a59815c29dcbe01fa50cdfa31a832822bc18` | `dd5a57692a74f8bb664ef4b83b5a97dafad94cb519698037c4578a3cf8ec6358` |

## 1. 独立复算方法声明

我先不看 oracle.md，从 oracle-inputs.csv 的 16 列 31 行 + 我自己的会计/最新性常识（独立于 D1—D6 契约文本）推出每格预期草稿，再逐格对比 oracle.md。我的草稿判定与 oracle 的逐格对照见 §2；差异格见 §3。锚点语义以我直接阅读源码为准（关键行：gap_plan.py L136-141 eligible/future、L143-157 fiscal_year 分组与静默丢弃、L167-170 `max(key=(provider_document_id 字典序, amended))`、L188 `not_published = not missing and not newer_revision`、L214-246 `_hash_gap` 不含 entity/market/kind/period/url/date；authorization.py L111-125 仅绑 plan_hash+provider+accession+caps+expiry；close_gap.py L263 `actionable[0]`、L452-495 `_finalize` 重解析单 request、L486-490 `gap_closed_downloaded` 措辞；acquisition.py L84-85 filing_date 强制/fiscal_year int 1900-2200、L371 kind 校验、L469-476 as_of 年-1 兜底、无 period_start/period_end/accepted_at/revision 字段）。

## 2. C01—C15 逐格独立判定 vs oracle（15/15 格）

| 格 | 我的独立预期草稿 | oracle.md | 判定 |
|---|---|---|---|
| C01 | a-new filed 2026-04-01 > z-old 2026-03-01，新近性只认日期、ID 序（a<z）无发言权 → a-new 进 actionable、z-old 留 provenance、not_published=false、新 hash≠旧 | 一致（newer_remote_available, newer_revision=[a-new], reuse=[z-old]） | **一致** |
| C02 | 本地 a-new 已是新文件，远端仅 z-old（更旧）：本地资格不降级；远端响应不能证明不存在更晚修订 → latest 未知；z-old 是旧文档绝不构成 newer_revision | 一致（不降级、reuse=[a-new]、unknown_if_remote_confirmed_newer、not_published=false） | **一致**。oracle 语义比"纯 covered"更准：它拒绝把"remote 疑似 newer"挫成资格降级，同时用 latest_status=unknown 承认最新性不可确证——正是卡第 32/33 步要求 |
| C03 | 同日且有修订链（恰一 amended=true 配 amended=false 基准）→ 子文档为新，仅子文档进 gap | 一致（ordered, missing=[a-2026-04-01-amend]） | **一致** |
| C04 | 同日无修订链 → 禁默选、禁按 ID 选、禁 covered | 一致（ambiguous_same_day，missing=[]，歧义清单） | **一致** |
| C05 | 三文种同 FY2025 是三个独立期键，互不吸收 | 一致（三个独立 period_key，各自 missing） | **一致** |
| C06 | period 齐即成键，fiscal_year 缺失只能派生标签（period_end 年=2025），不得静默丢弃 | 一致（missing，FY2025 派生） | **一致** |
| C07 | 缺 period → 显式 unknown，不入桶、不 actionable、不 covered | 一致（annual_report\|unknown\|unknown, explicit_unknown） | **一致** |
| C08 | 双日期缺失 → 无法定披露时间，显式 unknown，不当 eligible（现源码 L139 `not _candidate_filed(c)` 把缺失当 eligible 是反向错误） | 一致（unknown_missing_date，不进 missing/newer_revision） | **一致** |
| C09 | accepted_at < filed_at 元数据矛盾 → conflicting，禁默选 | 一致（conflicting，不 actionable） | **一致** |
| C10 | discover 成功但候选集空且无证据表明穷尽 → 空成功≠未发布证明 | 一致（unknown_empty_success，not_published=false） | **一致**。oracle 明确区分了 G-D4 空 success 与 not published：not_published=true 需要 adapter 穷尽知识声明（目前不存在→保守 false），且 no_gap 只是计划级处置、不得反向当 not_published 证明——这正是卡第 33 步的"禁止同一布尔值代替三者" |
| C11 | provider 异常 → 可保留本地但必须声明最新性未知，禁止 up-to-date | 一致（unknown_provider_failed, reuse=[z-old], already_covered=true） | **一致**。already_covered 独立于 provider 状态，与 not_published/no_gap 不混淆 |
| C12 | 远端返回同 accession z-old → 唯一能确证 local_is_latest 的路径 | 一致（local_is_latest_confirmed, already_covered=true, no_gap 成立） | **一致** |
| C13 | filed 2026-08-01 > as_of 2026-07-31 → future，不算截至日可用文件、不进 gap、不下载；not_published 判定不被未来候选阻断 | 一致（future=[a-future], missing=[]，保守侧 latest_status=unknown_empty_success 同级） | **一致**。oracle 的保守处理（无穷尽声明时 not_published 维持 false）符合"更保守"总则 |
| C14 | 3 缺口 ≤ 批界 → 全批授权，全部完成后才可宣称关闭 | 一致（missing=[P1,P2,P3] period_start DESC，completed，remaining=0） | **一致** |
| C15 | 9 缺口 > 批界 8 → 前 8（新期间优先）授权，status=completed_partial，剩余 1 显式保留、下一事务重建计划，禁宣称全关 | 一致（processed=8, remaining=1, 禁 completed） | **一致** |

复算结论：**15/15 格与我的独立推导一致，无语义冲突格**；oracle 每格有值+理由+消费行为，无"只写通过"，无 TBD。

## 3. 与初稿不一致的格（发现清单）

无输出语义不一致格。记录三处**形式缺陷**（均不改变预期值，不构成否决）：

1. oracle-inputs.csv L8-9（C04）：remote_context 描述写"b-rev(amended=false)"，而 CSV 的 amended 列对 b-rev 为空串（缺省）。语义上空串=未声明，oracle 按"均 amended=false/无修订链→ambiguous"处理结果不变；但严格读 CSV 时 b-rev 的 amended 是**缺失**而非 false。D2 契约下"均 false"与"缺失"在无修订链判定上同归 ambiguous（无 amended=true 子文档可配对），故预期值不受影响。裁定：可接受，I-03-B 实施时应把"amended 缺失"与"amended=false"在输入验证上区分（缺失按显式 unknown 候选属性处理，不改变 C04 判定）。
2. decision.md L192 与 oracle.md L117 对格数的表述："14 个 oracle 输入格（decision L192）"vs"15 格（oracle）"。CSV 实际 31 行=15 case（C01—C15）。**decision.md L192 的"14"是笔误**，正确数是 15（oracle.md L117、handoff completed_steps、blocked_downstream 均按 C01—C15=15 格）。裁定：不阻断（oracle.md 是权威格表且数对），但记录为 editorial erratum；后继卡引用格数以 15 为准。
3. G-D2 的卡面归组：卡中 C03/C04（同日修订链/同日无链）按卡表属 G-D3 类同日冲突场景、C05—C06 属 G-D2；oracle 把 C03 标 G-D2、C04 标 G-D3。对照卡 G-D2"同 FY 合并"与 G-D3"同日不同文档且无修订关系"定义：C03（有修订链）更贴近 D2 修订语义而非 G-D2 字面的"annual/interim/quarter 合并"，C04 归 G-D3 正确。probe `missing_same_period_two_revisions` 同时被 C03/C04 覆盖（oracle L119 复核要求），归组偏差不产生覆盖缺口。裁定：可接受；三格（C03/C04/C05）合计覆盖了 G-D2+G-D3 的全部子情形。

## 4. 决策表五条契约（D1—D6）内部一致性

- **period key 双入口**：exact 模式输入含 period_key（D4 L129 身份四元组含 period_key）、latest_as_of 按 D1 三元组分桶——两入口的 period key 定义同源（D1），一致。
- **哈希资格字段与 oracle 消费行为**：D6 资格字段 13 项（entity/market/kind/period_start/period_end/fiscal_year/provider/id/filed_at/accepted_at/revision/amended/url）与 oracle-inputs.csv 16 列中除 case 元数据列外的全部语义列一一对应；C01/C02 的"新 gap_hash ≠ 旧实现 hash"断言与 D6 排序键+资格字段可推导，一致。
- **批次连贯性**：D5 max_batch_size=8 ↔ oracle C14（3≤8 全批）/C15（9>8 截断 processed=8/remaining=1）；`remaining_count==0 且 _finalize 重解析确认`才 completed，与 C14 的"逐个下载提交后 remaining=0 才宣称"一致；`allowed_accessions` 逐一列出本批 accession ↔ authorization validate 的成员检查（authorization.py L119）在 I-03-C 范围内闭环。
- **fail-closed 链**：D6 失效规则（任一资格字段变化→stale_gap_hash, fetch=0）↔ compat-matrix §2 全表 fail-closed ↔ close_gap.py L255-256 现行 stale_gap_hash 拒绝点复用，一致。
- **单一策略源**：D6 policy epoch 绑 RuntimePolicySnapshot，未自创第二策略源（卡第 35 步要求）；compat-matrix M10/§2"旧 RuntimePolicySnapshot 保留"与之呼应，一致。
- **四态/五值枚举**：D2 四态（ordered/ambiguous_same_day/conflicting/unknown_missing_date）与 C03/C04/C09/C08 一一对应；D4 latest_status 五值与 C01/C02/C10/C11/C12 一一对应（C13 复用 unknown_empty_success 同级保守，未发明第六值），一致。

## 5. compat-matrix.md 授权失效覆盖面

- 卡点字段变化全集：**url / date（filed_at、accepted_at）/ period（start、end）/ revision / provider / entity / kind / market** 全部出现在 D6 失效规则清单（decision L175）与资格字段表（L173）中；compat-matrix M7/M9 把绑定面从"仅 accession"扩到全资格字段。**覆盖完整**。
- **"旧授权继续有效的迁移"已列出**：compat-matrix §2 六行——旧 gap_hash、旧 DownloadAuthorization、旧 CloseGapBinding 一律判"否，重建"；仅已入库文档内容（DL-09 幂等）与 RuntimePolicySnapshot 保留。没有"无迁移=默认重建"的空白：每一类旧产物都有显式判定与消费行为，且与 I-03-C 依赖（M7/M8/M9 指向 I-03-C）一致。§3 底线（fail-closed、不回写旧 PASS、不重算续期）符合卡"恢复边界"。

## 6. 锚点现状对照（decision.md 第一部分 vs 实际代码）

- `_hash_gap`（L214-246）入 hash 仅 request_id/as_of/fiscal_year+provider_document_id（reuse 与 missing+newer_revision）/provider_unavailable/reader_reason——decision 1.2 描述**如实**；entity/market/kind/period/url/filed/amended 确实不在 hash（我逐行核对 digest.update 调用），probe `url_and_date_changed_same_gap_hash` 的 841bbe66==841bbe66 结论成立。
- **字典序缺陷真实行号**：gap_plan.py **L167-170**（`max(remotes_here, key=lambda c: (_candidate_accession(c), _candidate_amended(c)))`），`_candidate_accession` 即 provider_document_id（L81-82）；hash 侧同源排序在 **L228-242**（sorted key=(fiscal_year, provider_document_id)）。decision 1.5 点名的行号准确，"字典序压过日期"由 probe newer_date_lower_id（a-new ID 序在前却落 reuse）证实。
- L136-141 eligible（缺失 filed 视为 eligible，L139 `not _candidate_filed(c)`）、L143-157 fiscal_year 分组+None 静默跳过/丢弃、L188 单布尔 not_published、authorization.py L111-125 校验面、close_gap.py L263 `actionable[0]` 单候选与 L486-490 `gap_closed_downloaded` 措辞——decision 1.1/1.3/1.4 的描述与我读到的代码**全部一致**；acquisition.py DownloadCandidate 字段清单（无 period_start/period_end/accepted_at/revision）核对 L74-94 属实，L469-476 as_of 年-1 兜底属实。
- 四个 probe 均为纯函数合成探针（current_recheck.json scope 声明），decision 把"候选集错误对齐"与"已下载失败"区分——符合卡"不把候选集当已下载失败"。

## 7. 15 格完整性与 blocked_downstream 引用

- 15 格（C01—C15）每格有唯一输出+理由+消费行为；零 TBD；未决依赖（穷尽知识声明字段）单列为"非 oracle 格的下游依赖"，不违反"未决格必须阻断"（它不是格，是保守推论）。
- blocked_downstream（handoff.json）引用 **D1—D6**：decision.md 第二部分 D1/D2/D3/D4/D5/D6 全部存在；引用 **C01—C15**：oracle.md 15 节全部存在。**无悬空引用**。

## 8. 高级 reviewer 定案裁定

无未定格 → 无 changes_required。对 §3 三项形式缺陷的定案：(1) C04 amended 空串语义不改变判定，交 I-03-B 在输入验证层区分；(2) decision L192 "14" 为笔误，格数以 15 为准（oracle.md/CSV 为权威）；(3) C03/C04 的 G-D2/G-D3 标签归组偏差不产生覆盖缺口。三项均不触动任何"唯一输出/理由/消费行为"。**复签为 accepted_scoped，本 attempt 的 D1—D6 与 oracle C01—C15 即为下游 I-03-B/C/D 的契约基线。**

## 9. 限定（scope of this acceptance）

- 本卡授予的仅是**下游 I-03-B/C/D 的契约基线资格**：period 键三元组、日期四态、新近性规则、三态输出+latest_status 五值、有界批次、哈希/授权失效面。
- 本卡为**纯设计卡，产品未实施**：契约在 I-03-B/C/D 落地后，还必须被 **G-D1—D4 的真实执行复验**（届时按 review_and_handoff 固定操作第 4-7 条：独立预期不得由被测函数生成、跨仓入口走真实旅程）。本复签不构成任何运行时行为已正确的证据。
- `not_published=true` 在 adapter 穷尽知识声明字段落地前保持保守 false（D4 推论）；I-03-D 消费端不得把该保守值读作"已确证未发布"。

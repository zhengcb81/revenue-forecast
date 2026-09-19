# I-03-A Oracle — 冻结预期（高级 reviewer 签署前初稿）

- 固定参数：entity=ACME、market=US、kind=annual_report（除 C05 多文种行）、fiscal_year=FY2025（period 2024-07-01→2025-06-30）、as_of=2026-07-31。
- 输入：同目录 `oracle-inputs.csv`（抽象语义列，待映射，不冒充现有 Python 参数）。
- 本 oracle 只冻结**行为预期**，不绑定产品函数签名；实施时由 I-03-B/C 以本表为准验收。每格给值+理由+消费行为，不写"通过"。
- 预期全部由独立推导（契约 D1—D6 + probe 事实）得出，未调用被测代码生成。

## C01 — G-D1 正向：远端更新、provider ID 字典序与日期顺序相反

- 输入：本地 z-old（filed 2026-03-01）；远端 a-new（filed 2026-04-01，ID 字典序 < z-old）与 z-old。
- **唯一输出**：`latest_status=newer_remote_available`；`newer_revision=[a-new]`；`reuse=[z-old]`（provenance 保留）；`missing=[]`；`not_published=false`；新 gap_hash ≠ 旧实现 hash（资格字段/排序键已入 hash）。
- 理由：D3 新近性只看 filed_at（2026-04-01 > 2026-03-01），ID 序无发言权；probe `newer_date_lower_id` 旧实现输出 reuse=[z-old]+not_published=true 即本格要封死的错误。
- 消费行为：a-new 进入授权批次的 actionable 集，可下载；z-old 继续作为本地可用证据；不因 ID 序把 a-new 判旧。

## C02 — G-D1 反向：本地 a-new（新）、远端仅 z-old（旧）

- 输入：本地 a-new（filed 2026-04-01，capture_ready）；远端仅 z-old（filed 2026-03-01）。
- **唯一输出**：本地 a-new **不降级**，保持 exact/available；`reuse=[a-new]`；`newer_revision=[]`（z-old 不进 actionable）；`latest_status=unknown_if_remote_confirmed_newer`；`missing=[]`；`not_published=false`。
- 理由：D3 反向条款——远端未展示任何不早于本地的文档，最新性不可由本次响应确证；probe `older_only_remote` 把 z-old 标成 newer_revision 是本格封死的反向错误。z-old 的 filed 早于本地，不可能构成更新修订。
- 消费行为：不触发对本地覆盖的下载；不宣称 not_published；filing 消费端可继续用 a-new，但报告须标注 latest 未知（可比）。

## C03 — G-D2 同日、有修订链（amended 布尔可配对）

- 输入：远端 a-base（amended=false）与 a-2026-04-01-amend（amended=true），同 filed 2026-04-01；本地空。
- **唯一输出**：状态 `ordered`；`missing=[a-2026-04-01-amend]`（仅子文档进 gap）；a-base 不单独 actionable；`latest_status=newer_remote_available`。
- 理由：D2——同日存在恰一条 amended=true 文档对应 amended=false 基准，构成修订链，子文档为新；基文档不重复下载。
- 消费行为：授权只含子文档 accession；下载后 base+amend 都入 provenance。

## C04 — G-D3 同日、无修订关系（ambiguous）

- 输入：远端 a-base 与 b-rev（均 amended=false），同 filed 2026-04-01；本地空。
- **唯一输出**：状态 `ambiguous_same_day`；**不选择任何一方**；`missing=[]`（不产生 actionable 下载）；不宣称 covered；输出携带歧义候选清单（两 id + url + filed_at）。
- 理由：D2 显式契约——同日不同文档且无修订链 = ambiguous；禁默选、禁按 ID 选。probe `missing_same_period_two_revisions` 旧实现把两者都塞 missing 静默处理，即本格封死的错误。
- 消费行为：挂起待人工/元数据修复；filing 端不得声称该期已覆盖，也不得自动取任一文档下载。

## C05 — G-D2：annual/interim/quarter 同 FY2025 不合并

- 输入：annual（2024-07-01→2025-06-30）、interim（2024-07-01→2024-12-31）、quarter（2025-01-01→2025-03-31），均 fiscal_year=2025；本地空。
- **唯一输出**：三个独立 period_key（`annual_report|2024-07-01|2025-06-30`、`interim_report|2024-07-01|2024-12-31`、`quarterly_report|2025-01-01|2025-03-31`），各期各自 missing，互不吸收；fiscal_year 仅作展示标签 FY2025。
- 理由：D1 三元组键；同 FY 不同期间/文种永不合并。
- 消费行为：三份文档各自入授权批次（若 ≤max_batch_size 则同一批，排序 period_start DESC：annual 先于 interim 先于 quarter）；任何一期的处置不影响另两期状态。

## C06 — G-D2 非日历 FY2025 键形态（period 齐、fiscal_year 缺）

- 输入：唯一候选，period 2024-07-01→2025-06-30，filed 2026-04-01，fiscal_year 空；本地空。
- **唯一输出**：period_key=`annual_report|2024-07-01|2025-06-30`；派生 fiscal_year=2025（period_end 年）；`missing=[该候选]`；`latest_status=newer_remote_available`。
- 理由：D1——键是三元组，不依赖 fiscal_year 输入；period_end 所在年派生 FY 标签。
- 消费行为：正常进 gap 并可下载；展示为 FY2025；不得因 fiscal_year 缺失而静默丢弃（旧实现 L154-156 行为封死）。

## C07 — G-D3 缺 period_start/period_end

- 输入：唯一候选 filed 2026-04-01，period 双缺。
- **唯一输出**：period_key=`annual_report|unknown|unknown`；`period_confidence=explicit_unknown`；**不入任何 FY 桶**、不进 missing、不产生 actionable；输出单独 unknown 候选清单（id+url+filed_at）。
- 理由：D1——缺 period 显式 unknown，禁止静默丢弃也禁止当作已覆盖或常规缺口。
- 消费行为：挂起补元数据；filing 端该期不得声称 covered，也不得自动下载。

## C08 — G-D3 缺 filed_at 与 accepted_at

- 输入：唯一候选双日期缺失，period 齐。
- **唯一输出**：`date_state=unknown_missing_date`；不参与新近排序；不进 missing/newer_revision；不宣称 covered；输出 unknown 日期候选清单。
- 理由：D2——无可信日期无法判定披露时间，缺 metadata 不得视为已覆盖。
- 消费行为：挂起；不得作为 latest 候选、不得下载、不得阻断其它期正常处理。

## C09 — G-D3 日期冲突（accepted_at < filed_at）

- 输入：唯一候选 filed 2026-04-01、accepted 2026-03-01。
- **唯一输出**：`date_state=conflicting`；不 actionable、不下载；输出冲突详情（两日期）。
- 理由：D2——accepted_at 早于 filed_at 为矛盾元数据，禁默选。
- 消费行为：挂起人工/元数据修复；filing 端不声称 covered。

## C10 — G-D4 provider 空成功

- 输入：discover 成功、候选集为空、无穷尽性声明；本地空。
- **唯一输出**：`latest_status=unknown_empty_success`；`missing=[]`；**not_published=false**；no_gap 仅作为计划级处置成立（无 actionable），但**不得**表述为"公司未发布"；本地无可复用句柄。
- 理由：D4——空成功≠证明未发布；not_published=true 需 provider 穷尽知识声明（当前 adapter 契约无此字段，保守侧恒 false）。
- 消费行为：filing 端报告"provider 响应为空、最新性未知"，缺口保持未关闭状态待重试；不得写 not_published 到任何持久结论。

## C11 — G-D4 provider 异常

- 输入：discover 抛错；本地 z-old capture_ready。
- **唯一输出**：`latest_status=unknown_provider_failed`；`reuse=[z-old]`（already_covered=true）；not_published=false；不宣称 up-to-date；携带 provider_reason。
- 理由：D4——provider 故障可仅返回本地但必须声明最新性未知；already_covered 与 provider 状态无关。
- 消费行为：z-old 继续可用；filing 端标注"本地可用、远端最新性未知"；可按重试策略重试，不视为 gap 关闭。

## C12 — G-D4 本地完整覆盖（远端 accession 命中）

- 输入：本地 z-old（provider_document_id=z-old，capture_ready）；远端仅返回同 accession z-old。
- **唯一输出**：`reuse=[z-old]`；`latest_status=local_is_latest_confirmed`；`missing=[]`；`newer_revision=[]`；not_published=false；already_covered=true；no_gap（计划级）成立。
- 理由：D4——accession 命中即本地最新被 provider 确证；这是唯一能确证 local_is_latest 的路径（远端展示不早于本地的同文档）。
- 消费行为：fetch=0，无下载；filing 端可声称该期已覆盖且本地为最新（确证级）。

## C13 — G-D4 未来披露（filed 2026-08-01 > as_of 2026-07-31）

- 输入：唯一候选 a-future filed 2026-08-01；本地空。
- **唯一输出**：`future=[a-future]`；`missing=[]`；不产生 actionable；not_published 判定**不被未来候选阻断**——若 provider 知识穷尽则"截至 as_of 未发布"可为 true，否则维持 false + `latest_status=unknown_empty_success` 同级保守（本输入无候选且未来候选存在，按 D4 未来文件不算截至日可用文件）。
- 理由：D4——date > as_of 不算可用文件；旧实现 L136-141 的剔除语义保留并升格。
- 消费行为：future 候选仅记录待观察，不下载、不触发授权；filing 端 as_of 口径下该期不声称 covered。

## C14 — G-D4 3 缺口全批完成

- 输入：远端 3 个不同期候选（P1/P2/P3），本地空。
- **唯一输出**：`missing=[P1,P2,P3]`（排序 period_start DESC：新期间优先）；单批（3 ≤ max_batch_size=8）全部授权；逐个下载提交后 `remaining_count=0`；status=`completed`；宣称 gap 关闭仅在此之后成立。
- 理由：D5——有界批次、批内新期间优先、全批完成才可宣称关闭。
- 消费行为：三份文档各自入库（content_sha256 幂等）；filing 端三期均 covered。

## C15 — G-D4 9 缺口截断（max_batch_size=8）

- 输入：远端 9 个不同期候选，本地空。
- **唯一输出**：本批授权 8 个（period_start DESC 前 8）；status=`completed_partial`；`processed_count=8`；`remaining_count=1`；剩余 1 个候选必须显式保留（下一事务重建 GapPlan 后进入 missing）；**禁止** status=`completed`、禁止宣称全 gap 关闭。
- 理由：D5——批界截断必须保留未完成候选；单候选/静默丢弃均违规。
- 消费行为：filing 端 8 期 covered、1 期标注"待下一批次"；不产生"已全部关闭"的持久结论。

---

## 未决格与 blocked

- **C01—C15 共 15 格全部已定案，无 blocked 输入格。**
- 下游 blocked 依赖（非本卡 oracle 格）：`not_published=true` 需 adapter"穷尽知识声明"字段（I-03-B/C 落地前保持保守 false）；I-03-B（实施）、I-03-C（哈希/授权/批次重建）、I-03-D（消费端）未按 D1—D6 与本 oracle 实施即 blocked。
- 复核要求：独立 reviewer 须复算 C01—C15 与 probe 四项的对应关系（C01↔newer_date_lower_id、C02↔older_only_remote、C03/C04↔missing_same_period_two_revisions、C01/C12↔url_and_date_changed_same_gap_hash 的 hash 断言），两次起草冲突以更保守方为准。

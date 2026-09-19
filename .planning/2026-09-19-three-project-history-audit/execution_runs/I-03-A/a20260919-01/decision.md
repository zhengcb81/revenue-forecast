# I-03-A 决策文档 — 冻结期间、修订、最新性与授权绑定契约

- 卡片：I-03-A（父 I-03）；attempt：a20260919-01；角色：company-wiki 来源负责人（起草）；独立 reviewer 复算 G-D1—D4 并承担高级 reviewer 定案复核。
- 性质：纯设计卡。不实施产品、不改产品 schema/代码/配置、不调网络。
- 源锚点（已逐一重算 sha256，与卡内冻结值一致）：
  - `company-wiki/src/company_wiki/source_catalog/gap_plan.py`（95 `build_gap_plan`；214 `_hash_gap`）= `d18391b7fa7adf06bf882d013cd9ccae48b9fad24429c3ac66d61b68d907c79f`
  - `company-wiki/src/company_wiki/source_catalog/authorization.py`（23 `DownloadAuthorization`）= `f858a369ed556d1b110be5ba7be7fa25ae3519fda94296cfe1c4f9e367d55f43`
  - `company-wiki/src/company_wiki/source_catalog/close_gap.py`（55 `CloseGapBinding`）= `117c8166a6c26f3462574b787e0db79c419e00c8b18287f25738948032f475c3`
  - `company-wiki/src/company_wiki/source_catalog/acquisition.py`（74 `DownloadCandidate`，实际调用方）= `c68a1c14b8bc2117fb89c6a46283116d6792c26a8278fbde9c3b141dccb24067`
- 原始反例：`reviews/cross_history/current_recheck.json`（sha256 `183352a226ee8c903258ebc78b314cf5e33c59f4dbd9d24f6f43de028ae8aec4`）四个 `current_gap_probes`。四个 probe 都是**纯函数合成探针**：它们证明的是 gap 计划对"候选集"的错误对齐，不是"已下载失败"的证据，本卡不把候选集当已下载失败。
- 起草冲突规则：若独立 reviewer 复算时与本稿冲突，以**更保守的一方**为准记录（更保守 = 更少自动断言、更多显式 unknown、更严的授权失效面）。
- 本卡无产品执行命令；本文档无需先于 oracle 计算 hash（card 明示），直接产出文档。

---

## 第一部分：现状字段表（逐字段映射与真实性来源）

### 1.1 `gap_plan.py:95 build_gap_plan` — 当前字段、来源与缺失值处理

| 字段/输入 | 当前语义 | 来源 | 缺失值处理 | 本卡判定 |
|---|---|---|---|---|
| `request_id` | 透传进 GapPlan 与 gap_hash | 调用方 | 无校验空值 | 保留，入新 hash |
| `as_of_date` | 未来资格边界（`filing_date <= as_of_date` 才 eligible，L136-140） | 调用方 | 无 | 保留为 latest_as_of 边界 |
| `document_kind` | 请求级文种；候选侧在 acquisition.py:371 校验一致后**隐含同质** | 调用方 | 候选侧不匹配→拒绝候选 | 升格为期间键三元组的第一元 |
| `entity` / `market` | 透传标识，**不入 gap_hash** | 调用方 | 无 | 入新 hash 资格字段 |
| `local_handles` | 本地句柄；仅按 `capture_ready != False` 过滤（ZR-406，L89-92） | catalog | 无 fiscal_year 的句柄**被静默跳过**（L145-147：year is None 不入 local_by_year） | 缺期间键必须显式 unknown，禁止静默跳过 |
| `remote_candidates` | provider 元数据（metadata-only，不取字节） | adapter.discover | `_candidate_year` 为 None 的候选**静默丢弃**（L154-156 `continue`）——既不算 missing 也不算 unknown | 禁止静默丢弃，必须显式 unknown 桶 |
| `fiscal_year`（int） | **唯一分组键**：`local_by_year` / `remote_by_year`（L143-157） | DownloadCandidate.fiscal_year | None→丢弃 | 降级为派生展示标签；分组键改为 (kind, period_start, period_end) |
| `filing_date`（str，canonical YYYY-MM-DD） | 仅用于 eligible 过滤（缺 filed → 视为 eligible，L139 `not _candidate_filed(c)`） | DownloadCandidate.filing_date | 缺失→当 eligible，**无日期可信性状态** | 升格为主排序日期；缺失=unknown_missing_date，不当 eligible |
| `amended`（bool） | 仅作 max() 的次级 tie-break 键（L169） | DownloadCandidate.amended | 默认 False | 升格为同日修订链判定依据 |
| 新近性判定 | `max(remotes, key=(provider_document_id 字典序, amended))`（L167-170） | — | — | **persisting defect（见 1.5）** |
| `not_published`（bool） | `not missing and not newer_revision`（L188） | — | — | 与 already_covered / no_gap 合并为单布尔的 persisting defect（见 D4） |
| `provider_error` | 有值→provider_unavailable=True，保留本地，不声称 up-to-date（L113-133） | 调用方 | — | 保留语义，改名入 latest_status 三态 |

### 1.2 `gap_plan.py:214 _hash_gap` — 当前 hash 输入

| 入 hash | 不入 hash（defect） |
|---|---|
| request_id、as_of_date、reuse 的 (fiscal_year, provider_document_id)、missing+newer_revision 的 (fiscal_year, accession)、provider_unavailable 布尔、provider_reason | **entity、market、document_kind、period（period_start/period_end 不存在于 schema）、filing_date、amended、source_url、revision 身份** |

直接后果 = probe `url_and_date_changed_same_gap_hash`：URL 与日期都改了，gap_hash 不变（`841bbe66…` == `841bbe66…`），旧授权据此继续放行 → 授权绑定被架空。

### 1.3 `authorization.py:23 DownloadAuthorization` — 当前绑定面

| 字段 | 绑定内容 | 缺口 |
|---|---|---|
| `gap_plan_hash` | 间接绑定（经 1.2 的弱 hash） | hash 不含 url/period/date/entity/kind/market → 上游弱则此处全弱 |
| `policy_hash` | FC-801/DL-03 策略快照绑定（validate 时 plan_hash+expiry+provider+accession+caps 检查，L99-126） | 唯一策略源是 RuntimePolicySnapshot，本卡确认不增设第二策略源 |
| `allowed_accessions` | 仅 accession 字符串成员检查 | 不绑定 url / period / revision / 日期 |

### 1.4 `close_gap.py:55 CloseGapBinding` + acquisition 实际调用

- `CloseGapBinding` 字段 = request_id、gap_plan_hash、policy_hash、provider、allowed_accessions、max_items、max_bytes、expires_at——与授权同构，绑定面继承 1.3 全部缺口。
- `_actionable_candidates`（L144-152）= `missing + newer_revision` 全集，但 Step 3 实际只取 `actionable[0]`（L263）逐个精确请求——**每事务单候选**；`_finalize` 重解析原 request（非全部 actionable），多候选场景下 `reason="gap_closed_downloaded"` 会以单文档下载措辞覆盖整个 gap（夸大表述风险，见 D5 批次定案）。
- `acquisition.py:74 DownloadCandidate` 实际字段：candidate_id, provider, provider_document_id, market, entity, title, source_url（强制 https）, document_kind, filing_date（强制 canonical）, fiscal_year（int 1900–2200）, form_type?, fiscal_period?, language?, amended, etag?, last_modified?, remote_size?, adapter_payload_json?。**没有 period_start / period_end / accepted_at / revision 父子链**；fiscal_period 为可选自由文本。发现阶段 fiscal_year 为空时用 as_of 年-1 兜底猜测（acquisition.py:469-476）。
- 本卡新增的 period_start/period_end/accepted_at/revision 是**待映射语义列**（oracle-inputs.csv 抽象列），不是现有 Python 参数；映射到产品 schema 属 I-03-B/C 实施卡范围。

### 1.5 persisting defect 的正式陈述（当前以 provider ID 字典序推断披露时间）

`gap_plan.py:167-170` 以 `max(key=(provider_document_id 字典序, amended))` 决定"同期间最新修订"，`_hash_gap` 排序键同源（L228-242）。accession 字符串顺序与披露时间**无任何因果或约定关系**。四个 probe 逐一证实：

| probe | 现象 | 结论 |
|---|---|---|
| `newer_date_lower_id` | a-new filed 2026-04-01（ID 序在前）对 z-old 2026-03-01：actual reuse=[z-old]、not_published=true | 字典序压过日期 → 更新文件被无视，gap 被虚假关闭 |
| `older_only_remote` | 本地 a-new（新），远端仅 z-old（旧）：actual newer_revision=[z-old] | 反向把**更旧**的远端标成待更新修订 |
| `missing_same_period_two_revisions` | 同期两修订均入 missing，未选已知最新也未报歧义 | 无修订/最新性契约 |
| `url_and_date_changed_same_gap_hash` | URL+日期变更后 gap_hash 相等 | 授权绑定被架空（1.2） |

状态：**persisting defect，本卡不修代码**，以 D1—D6 契约冻结目标行为，由 I-03-B/C 实施。

---

## 第二部分：冻结契约（每条含理由/反例/状态表）

### D1 期/文种键（period key）

**定案：期间键是三元组 `(kind, period_start, period_end)`，不是单值 fiscal_year。**

- 规范 period_key 字符串：`"{kind}|{period_start}|{period_end}"`，日期一律 ISO `YYYY-MM-DD`。例：非日历财政年 2024-07-01→2025-06-30 的年报键为 `annual_report|2024-07-01|2025-06-30`。
- `fiscal_year` 降级为**派生展示标签** = period_end 所在年份：2024-07-01→2025-06-30 → **FY2025**。仅用于检索/展示，永不参与合并判定。
- 同一 fiscal_year 下不同期间或不同文种（annual/interim/quarter）**永不合并**：annual FY2025（2024-07-01→2025-06-30）、interim FY2025（2024-07-01→2024-12-31）、quarter FY2025（2025-01-01→2025-03-31）是三个独立键、三份独立 gap 状态。
- period_start 或 period_end 缺失 → period_key = `"{kind}|unknown|unknown"`，`period_confidence=explicit_unknown`；该候选不得计入任何 FY 桶、不得声称 covered、不得作为常规 actionable 缺口下载（先补元数据）。
- 理由：单值 fiscal_year 把中报/季报/年报压成同一桶（probe `missing_same_period_two_revisions` 的结构性成因之一），且无法表达非日历财政年（FY2025 跨 2024/2025 两个日历年，按 fiscal_year 整数分组会把 FY2025 与日历 2025 混淆）。
- 反例覆盖：oracle C05（三文种同 FY2025 不合并）、C06（非日历 FY2025 键形态）、C07（缺 period 显式 unknown）。

| 项 | 状态 |
|---|---|
| 键=三元组 (kind, period_start, period_end) | **已定案（冻结）** |
| fiscal_year=period_end 年派生标签 | **已定案（冻结）** |
| 缺 period → explicit_unknown，不合并不覆盖 | **已定案（冻结）** |

### D2 日期语义（filed_at vs accepted_at；三态不合并成布尔）

**定案：披露时间主键 = `filed_at`；`accepted_at` 仅作一致性校验与缺失回退；可信性是显式多态枚举，不是布尔。**

- 优先关系：`filed_at` 为新近性唯一排序主键。`accepted_at` 存在时只做校验：`accepted_at >= filed_at` 合法；`accepted_at < filed_at` → **conflicting**。`filed_at` 缺失且 `accepted_at` 存在 → 允许以 accepted_at 代替，但必须标记 `date_basis=accepted_at` 且该候选的新近结论带降级标注；两者都缺 → **unknown_missing_date**。
- 同日不同文档：同 period_key、同 filed_at、出现多个不同 id —— 存在修订链（恰一个 amended=true 的子文档对应 amended=false 基准）→ **ordered**，子文档为新；无修订链（均 false，或均 true 无基准）→ **ambiguous**（显式契约：禁默选、禁按 ID 选、禁宣布 covered）。
- 日期互相冲突（同 period_key 内两文档的日期关系既非可排序修订链又互相矛盾，或 accepted_at 早于 filed_at）→ **conflicting**：不 actionable、不下载，挂起待人工/元数据修复。
- 状态枚举（四态，禁合并布尔）：`ordered` / `ambiguous_same_day` / `conflicting` / `unknown_missing_date`。
- 时区与精度：所有日期为 canonical `YYYY-MM-DD`（继承 acquisition `_date` 校验），**不带时刻、不带时区**；同日判定按纯日期比较。
- 理由：布尔会把"无法判定"伪装成"已判定"；probe `missing_same_period_two_revisions` 正是缺失该枚举导致静默双选。
- 反例覆盖：oracle C03（同日有修订链→ordered）、C04（同日无链→ambiguous）、C08（缺双日期）、C09（accepted<filed→conflicting）。

| 项 | 状态 |
|---|---|
| filed_at 主 / accepted_at 校验+回退 | **已定案（冻结）** |
| 四态枚举禁布尔合并 | **已定案（冻结）** |
| 同日无修订链=ambiguous 显式契约 | **已定案（冻结）** |

### D3 修订/最新性（正向/反向）

**定案：新近性只由 (filed_at[, 修订链]) 决定，禁止用 provider_document_id 字典序。**

- 正向（远端比本地新）：同 period_key 文件族内，本地 z-old（filed 2026-03-01）、远端 a-new（filed 2026-04-01，ID 字典序反而靠前）→ a-new 判为 `newer_revision`（actionable 修订替换），z-old 保留为 provenance reuse，不删除。
- 反向（本地比远端返回的最新还新）：本地 a-new（filed 2026-04-01）、远端仅 z-old（filed 2026-03-01）→ **本地不降级**：仍为 exact/available 可用句柄；但 provider 未展示任何不早于本地的文档，最新性不可由本次响应确证 → 报告 `latest_status=unknown_if_remote_confirmed_newer`（本地位列可比、若远端此后确证存在更新修订则以远端为准；当前不得据此降级本地、不得触发对本地覆盖的下载、不得据此宣称 not_published）。
- 同日无修订链 → 按 D2 ambiguous，不参与新近选择。
- 理由：probe `newer_date_lower_id`（正向误判 gap 虚假关闭）与 `older_only_remote`（反向误标旧文档为更新）双向证明字典序不可用。
- 反例覆盖：oracle C01（正向）、C02（反向）。

| 项 | 状态 |
|---|---|
| 日期(修订链)定新近，禁 ID 字典序 | **已定案（冻结）** |
| 反向不降级 + latest_status=unknown_if_remote_confirmed_newer | **已定案（冻结）** |

### D4 exact 与 latest_as_of 输出契约分离；三态禁布尔；future；空成功

**定案：两种模式独立输出；not_published / already_covered / no_gap 是三个独立字段，严禁单布尔。**

- **exact 模式**：输入为精确身份 `(entity, market, kind, period_key, provider_document_id/revision)`，只回答"该具体文档是否存在且 capture_ready 可用"（命中→available / 不命中→精确拒绝理由）；**不做新近判断、不触 provider 最新性**。
- **latest_as_of 模式**：在 as_of 边界内做最新性选择，必须携带 `latest_status ∈ { local_is_latest_confirmed, newer_remote_available, unknown_if_remote_confirmed_newer, unknown_provider_failed, unknown_empty_success }`，缺该字段即为契约违规。
- **provider 故障**：可以仅返回本地（reuse 照常），但必须 `latest_status=unknown_provider_failed`，禁止 not_published=true，禁止"up-to-date"表述（现源码 L113-133 语义保留并升格）。
- **not_published**：仅当 provider **成功响应**且该响应对 `(entity, market, kind, period_key)` 构成**穷尽知识**（adapter 契约显式声明全列）且无 eligible 候选且无修订歧义时才可为 true。`as_of` 时点语义：判断"截至 as_of 是否未发布"。
- **already_covered**：本地存在 capture_ready 的 exact/equivalent 句柄即成立，与 provider 状态无关（provider_offline 时依然成立）。
- **no_gap**：**计划级处置** = GapPlan 无 actionable 候选（missing 空 + newer_revision 空），是 already_covered / not_published / 幂等已闭（close_gap 的 gap_already_closed）的汇总出口；它不是逐期发布声明，**不得反向当作 not_published 证明**。
- **future 披露**：filed_at > as_of 的候选一律进 `future`，**不算截至日可用文件**、不进 gap、不阻断"as_of 时点 not_published"的判定（当 provider 知识穷尽时：远端只有未来文件 → 截至 as_of 确实未发布）。
- **provider 空成功**：成功响应但候选集为空 **≠ 证明未发布** → `latest_status=unknown_empty_success`，not_published 保持 false；仅当响应带穷尽性声明（未来 adapter 契约字段，见 open_questions）时才可判 not_published=true。
- 理由：当前源码把三者压进 `not_published` 单布尔（L188），probe 双向误判皆源于此。
- 反例覆盖：oracle C10（空成功无本地）、C11（provider 异常）、C12（本地完整覆盖=accession 命中确证）、C13（未来披露）。

| 项 | 状态 |
|---|---|
| exact / latest_as_of 分离 | **已定案（冻结）** |
| latest_status 五值枚举必填 | **已定案（冻结）** |
| 三态独立字段禁单布尔 | **已定案（冻结）** |
| future 不算可用文件 | **已定案（冻结）** |
| 空成功≠not_published | **已定案（冻结）** |

### D5 多期 gap：有界批次

**定案：采用有界批次，`max_batch_size=8`（每次授权 ≤8 个 actionable 候选），不采用"每事务单候选"。**

- 批内候选排序：`(kind, period_start DESC, filed_at DESC, provider_document_id)` —— **新期间优先**（最新财期最先处理），period_start 缺失者不进批次（D1 explicit_unknown）。
- 授权 `allowed_accessions` 必须逐一列出本批全部 accession；下载器逐候选校验。
- **未完成候选的保留**：批次截断时，事务结果 status=`completed_partial`，必须携带 `processed_count`、`remaining_count` 与未处理 accession 列表；剩余候选在下一事务重新 revalidate（重建 GapPlan）后保留于 `missing`/`newer_revision`，不得丢弃、不得静默。恢复边界：不回写旧 PASS、不重算旧授权续期。
- **关闭宣称**：仅当 `remaining_count==0` **且** `_finalize` 重解析确认文档可复用，才可 status=`completed`/宣称 gap 关闭；`remaining_count>0` 时禁止宣称全 gap 关闭（现源码取 `actionable[0]` 单个下载后以 `gap_closed_downloaded` 收尾的措辞按本条整改，属 I-03-C）。
- 理由：单候选（现源码 L263）在多期缺口下要么虚报关闭要么需外部循环无界重试；无界批次则放大单授权爆炸半径。8 为有界且可审计的保守上界。
- 反例覆盖：oracle C14（3 缺口全批完成）、C15（9 缺口截断，1 剩余保留）。

| 项 | 状态 |
|---|---|
| 有界批次 max_batch_size=8 | **已定案（冻结）** |
| 排序 period_start DESC 新期间优先 | **已定案（冻结）** |
| completed_partial + remaining 保留 | **已定案（冻结）** |
| 禁止单个宣称全 gap 关闭 | **已定案（冻结）** |

### D6 哈希规范序列化与授权绑定

**定案：canonical JSON + 全资格字段入 hash + policy epoch 绑定；任何资格字段变化即旧授权失效；不自创第二策略源。**

- **规范序列化**：`json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`，UTF-8 编码后 SHA-256。
- **hash_schema_version=1**（本契约的 hash 版本，独立记录；与 GAP_PLAN_SCHEMA_VERSION="1.0" 并存但语义分离）。
- **候选排序键**（仅保证哈希确定性，与新近性判定无关）：`(kind, period_start, period_end, filed_at, accepted_at, provider, provider_document_id, revision, url)`；缺 accepted_at/revision 以空串占位。
- **资格字段（全部入 hash，缺一即契约违规）**：`entity, market, kind, period_start, period_end, fiscal_year, provider, id(provider_document_id), filed_at, accepted_at, revision, amended, url`；计划级另入 `as_of_date, request_id, not_published, provider_unavailable, provider_reason, hash_schema_version, policy_hash(policy epoch)`。
- **policy epoch 绑定**：授权绑定 RuntimePolicySnapshot 的 `policy_hash`（唯一策略源）；本卡不新增、不内嵌任何第二策略来源。
- **失效规则（旧授权 fail-closed）**：`url`、`filed_at`、`accepted_at`、`period_start`、`period_end`、`revision`、`provider`、`entity`、`kind`、`market`、`fiscal_year`、`amended` **任一变化** → 新计划 hash 必然不同 → 旧授权在 validate 处判 `stale_gap_hash`，fetch=0，必须重建计划+新授权。禁止重算/续期旧授权使其"继续有效"（恢复边界）。
- 理由：probe `url_and_date_changed_same_gap_hash` 证明现 hash 面缺 url/date → 授权被架空；新契约让"任何实质变化 ⇒ hash 不同"成为恒等式。
- 反例覆盖：oracle C01/C02 的 hash 差异断言 + compat-matrix 全量失效迁移。

| 项 | 状态 |
|---|---|
| canonical JSON / schema_version=1 | **已定案（冻结）** |
| 候选排序键固定 | **已定案（冻结）** |
| 全资格字段入 hash | **已定案（冻结）** |
| policy epoch 绑定，单一策略源 | **已定案（冻结）** |
| 资格字段任一变化→旧授权失效 | **已定案（冻结）** |

---

## 未决项（blocked）

- 本卡 14 个 oracle 输入格（C01—C15，见 oracle.md）**全部已定案，无 blocked 格**。
- 遗留依赖（不阻断本卡 oracle，但阻断其下游实施语义）：`not_published=true` 所需的"provider 穷尽知识声明"目前 adapter 契约无对应字段；在 I-03-B/C 落地该字段之前，not_published 只能保持 false（保守侧），这是 D4 的直接推论而非 TBD。
- 上述依赖使 **I-03-B（实施）/I-03-C（哈希与授权重建）/I-03-D（消费端）** 在触及 not_published 判定与 period 字段映射时受本契约约束；未按 D1—D6 实施即 blocked。

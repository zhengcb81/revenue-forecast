# oracle.md — I-06-A / a20260922-02（冻结于任何运行之前，2026-09-22）

> **冻结纪律**：本文件在本 attempt 的**第一次任何运行（测试/探针/CLI）之前**写定。全部预期**只**来自
> RATIFIED 裁定契约文本与卡片原文（下列来源逐条标注），**不**调用被测函数生成 expected。
> 若实现与本 oracle 冲突 ⇒ 实现改，oracle 不改（勘误除外，追加式）。

## 0. 契约来源（全部为 owner 终确生效件）

| 来源 | 载体 | 取用条款 |
|---|---|---|
| OPEN-5 裁定（RF 消费 owner） | `execution_runs/T2-SIM-OPEN5-RF/a20260922-01/ruling.md` | §4.3 持久化介质（= OPEN-1 选项 A）；§4.5 修订后接口契约 1–6；条件 C1/C4/C5/C6/C8；§4.2 恢复规则（demand 保持 open）；边界补充记 5/6 |
| OPEN-6 裁定（安全 reviewer） | `execution_runs/T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` | 缺失语义三值 `missing/unsupported/not_applicable`、无静默态（§3/C2/C5 适用说明①：编码化 fail-closed 错误契约）；C6（TTL 上限由 policy 绑定、调用方 now/ttl 只可收紧）；P2-B/P3/P6-A/P6-B 缺陷类（裸 None / 裸抛 / 静默覆盖 / 永久搁浅）必须不复现 |
| OPEN-4 裁定（wiki 来源审核 owner） | `execution_runs/T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md` | §4.3 恢复规则：**回执失效不自动关闭对应 demand、demand 关闭也不改写回执**（两域独立）；C5 失效语义（读取时 fail-closed） |
| I-06-A 原卡 | `execution_v2/card_I-06-A.md` | 范围 = 先登记持久需求再阻断（登记可恢复）；W06A-P1/P2/N1/N2/N3 固定样本与预期；退出判据「阻断产生可见持久需求和下一动作；只证明登记可恢复」 |
| 原 attempt 裁定形态 | `execution_runs/I-06-A/a20260919-01/decision.md` + `handoff.json` | OPEN-2 选项 A（幂等键含请求身份）；OPEN-2b（c7 错误契约 + role_set 权威来源）；OPEN-3（claim(owner, lease_seconds) 显式单次授权、无自动 resume、无后台 scheduler、过期回收须显式） |
| owner 终确 | `OWNER_DECISIONS.md §十九` | 三裁定全部接受生效；**TTL = 选项 A：30 天（86400×30）policy 上限，调用方只可收紧**（OPEN-6 C6 机制落产品策略） |

## 1. 冻结契约要点（逐条 → 期望）

1. **持久化介质（OPEN-5 §4.3 = OPEN-1 选项 A）**：唯一持久 owner = CW
   `src/company_wiki/source_catalog/store.py` 扩展、`catalog.sqlite3` 增表、经**既有 `_apply_additive_migrations`**
   （store.py:1072 区域）。**不另立介质**（独立 SQLite / RF 库 / JSONL 均为被拒方案）。
   demand 行生命周期**必须**明确：**豁免于文档目录的 prune/archival**（OPEN-5 §4.3 兼容影响明文）。
2. **幂等键（OPEN-2 选项 A / OPEN-5 §4.5 条 1）**：
   `demand_key = sha256(canonical_json({source_sha256, review_policy, role_set, request_identity}))`，
   `request_identity` 覆盖 `as_of_date / target / payload digest`。同请求重提 = 同一 active demand ID、
   只有一项待办；**不同请求（哪怕仅 as_of_date 不同）= 两条 demand 行**（c8/c9/c10 反例必须翻绿）。
3. **原请求绑定列（§4.5 条 2）**：`request_sha256` **且** `request_json` 都保留；`request_sha256`
   是恢复校验锚，不得只存不验（登记行内值必须等于该请求实际字节哈希）。
4. **状态枚举（§4.5 条 3）**：闭集 `pending / running / completed / failed / terminal_failed`
   （既有 ZR-507/RF 合同）；`completed` = 原请求已成功重跑并产出 record；`terminal_failed` = 放弃且**必须**留
   reason；`failed` = 可显式重试。
5. **CLI 最小面（§4.5 条 4）**：`list` / `show --demand-id` / `claim(owner, lease_seconds)`（显式单次）/
   `resume --demand-id --request-file`（仅 lease owner）/ `complete`/`fail`（lease 内）。**无** `resume --all`、
   **无**自动推进。**本 attempt 边界**：`resume`/`complete|fail` 的**可失败测试面属 I-06-B**；本 attempt 只落
   **STORE 侧需求生命周期**（登记 + 阻断前登记 + list/show/claim + complete/fail/显式回收的存储 API）。
   CLI adapter **文件未被任何裁定冻结具体文件名**（卡：「未冻结具体文件禁止猜建」）⇒ 本 attempt **不**新建 CLI 文件，
   只保证 store API 面可被该 CLI 承载。
6. **错误契约 c7（OPEN-2b 已裁 / §4.5 条 5）**：登记与恢复两路径同用「安全判定 + `demand_store_error=`
   附加子句」；成功登记报 `demand_queued`（含 demand_id / gaps / next_action）；写失败**无** `demand_queued`、
   **无**内存兜底、行数不变。错误面全部**编码化**（`DemandNotFoundError / DemandStateError / DemandStoreUnavailable`
   语义族）：**无裸 `None`、无裸 `sqlite3.OperationalError`**（P1/P2-B/P6-B 缺陷类不得复现）。
7. **gaps 三值语义（函 C / OPEN-5 C6 / OPEN-6 无静默态）**：角色/项缺失记录用**可区分**三值
   `missing / unsupported / not_applicable`；非法值拒绝（不静默归类）；demand 行 gaps **不得**把
   `detected_and_ignored` 或任何非 clean 态记为「已清洁」；无任何静默态。
8. **权限（OPEN-3 / OPEN-5 §4.4 = 条件 C5）**：`claim(owner, lease_seconds)` 显式单次授权；恢复/推进 = lease
   有效期内动作；lease 过期后操作 ⇒ **拒绝**（fail-closed），须显式重 claim；**不得**自动 resume、**不得**后台
   scheduler、过期回收只能**显式**触发（store 侧提供显式回收入口，防 P3「running + lease 过期永久搁浅」）。
9. **回执失效独立性（OPEN-4 §4.3 恢复规则）**：**回执失效不自动关闭对应 demand；demand 关闭也不改写回执**。
   登记实现不得挂任何 receipt 回调/级联。
10. **TTL（OWNER_DECISIONS §十九 = 选项 A / OPEN-6 C6）**：`86400×30` 秒为 **policy 上限**（policy_hash 绑定策略
    固定）；调用方 `now`/`ttl` **只可收紧**（1d/1h 可以，放宽不可）。实现须为 store/receipt-policy 常量 + 收紧钳制语义。
11. **N-1 升级路径（FIX-W06-GAPS P1 缺陷类不得复现）**：迁移必须走生产 `_apply_additive_migrations` 形状
    （additive、幂等、对 N-1 库**补表补列**）；旧行保留；register/claim 在升级后的库上正常工作。

## 2. 可失败用例（冻结判据；RED=旧代码失败 / GREEN=iso 修复通过 / MUTATION=翻一个 guard 红一个用例）

| ID | 类 | 判据（frozen expectation） |
|---|---|---|
| **W06A2-P1** register-before-block | positive | 合格来源但 `not_reviewed`：**先**持久登记 demand 行（含 source_sha256 / review_policy / role_set / request_identity 绑定 `request_sha256`+`request_json` / gaps 三值 / next_action），**后**给出结构化阻断；阻断文案含安全判定 + `demand_queued demand_id=… gaps=… next_action=…`；**零伪造 review 行**；行可被第二进程读到（可恢复）。 |
| **W06A2-P2** cross-process idempotent resubmission | positive | 独立进程重提**完全相同**需求 ⇒ 同一 active demand ID、恰好 1 条待办（不是每进程 pd-0 伪同一）。 |
| **W06A2-P3** N-1 upgrade path | positive | 旧 schema 级别的 `catalog.sqlite3` 经 `CatalogStore._initialize()` / `_apply_additive_migrations` 打开 ⇒ demand 表/列补齐、旧行保留、register+claim 正常（P1 缺陷类不复现）。 |
| **W06A2-P4** claim/lease lifecycle | positive | `claim(owner, lease_seconds)` 显式单次；并发下**恰好一赢家**；lease 内 complete/fail（store 侧生命周期）成功并留痕（terminal_failed 必留 reason）。 |
| **W06A2-N1** request identity in key | negative | 同 source/policy/role_set、仅 `as_of_date`（或 target/payload digest）不同 ⇒ **两条** demand 行、两个不同 demand_id、行内 `request_sha256` == 各自实际请求哈希（c8/c9/c10 反例必须翻绿）；source hash 变 ⇒ 新 demand，旧 demand **不**被关闭。 |
| **W06A2-N2** store write failure | negative | DB 写失败/数据非法/权限不足 ⇒ **不**报 `demand_queued`；结构化失败 = 安全判定 + `demand_store_error=` 子句；**不**静默内存兜底；行数不变。 |
| **W06A2-N3** paused worker | negative | 登记/查询**不**自动 resume、不自动 claim/推进、不启动任何后台 scheduler/线程（进程内线程数前后不变）。 |
| **W06A2-N4** defined refusals | negative | 未知 demand_id ⇒ 编码化 `DemandNotFoundError`；claim 冲突/无有效 lease 操作/lease 过期操作 ⇒ 编码化 `DemandStateError`（**非裸 None、非裸 sqlite3 异常**）；锁超时 ⇒ 编码化 `DemandStoreUnavailable`（包装 `OperationalError`）；非法参数（lease_seconds<=0、空 owner、非法 gaps 值）⇒ 编码化拒绝。 |
| **W06A2-N5** concurrent-write conflict | negative | 同 demand_key 异载荷重登记 ⇒ **定义拒绝**（幂等冲突），绝不静默覆盖/合并（P6-A 类不复现）；并发 claim ⇒ 一赢家 + 输家**定义拒绝**（P2-B 类不复现）；零静默丢写。 |
| **W06A2-N6** receipt invalidation independence | negative | 回执失效/变更（evaluate 落 `not_reviewed`、或收据被覆盖改写）⇒ demand 行**原样存活**（不关闭、不改写、不删除）；demand 关闭 ⇒ 回执字节**不变**。 |
| **W06A2-N7** gaps 三值语义 | negative | gap `kind ∈ {missing, unsupported, not_applicable}` 可区分、round-trip 保留；非法值 ⇒ 编码化拒绝（不静默归类）；gaps 中**无**任何「已清洁/ok」静默态。 |
| **W06A2-N8** TTL policy cap | negative | `RECEIPT_TTL_POLICY_CAP_SECONDS = 86400×30`（owner 选项 A）；调用方 ttl **只可收紧**：ttl>cap ⇒ 有效值=cap；`ttl=∞`/超大值**不能复活**已过期回执（仍 fail-closed `not_reviewed`）。 |
| **W06A2-N9** prune/archival exemption | negative | 文档 prune/archival 后，非 terminal demand 行**仍在**（OPEN-5 §4.3 生命周期豁免）。 |
| **W06A2-C8** error-contract pinning | contract | `demand_queued` / `demand_store_error=` 子句**逐字**钉住（PIN 断言）；变异（改一个字符）⇒ 红。 |

**变异（mutation）计划**：翻转 `register` 的「同键异请求身份 ⇒ 拒绝」guard（改为静默返回旧 demand）⇒ **W06A2-N1 必红**；
（附加）翻转 claim CAS 赢家 guard ⇒ W06A2-P4/N5 红。一次只翻一个 guard，各跑全表留证。

## 2-补. 追加用例（仍在首次运行之前冻结；来源 = OPEN-5 边界补充记 6，经 owner §十九 终确）

| ID | 类 | 判据（frozen expectation） |
|---|---|---|
| **W06A2-N10** 同词异义消歧 | negative | 缓存失效态 `cache_state="ignored"`（= policy changed since review）与审核结论态 `detected_and_ignored`（= 命中且经授权忽略）**可区分**、互不冒充：显式 `state_domain` 断言字段（`cache`/`review`）落契约层；**缺 `state_domain` 或取值非法 ⇒ 拒收/最严解释**（fail-closed，不默认归入任一语义）。因 `CACHE_STATES` 词汇被 ZR-507/I-06-B 冻结测试与 OPEN-5 §6.3 裁定词汇（`tampered/ignored/expired/absent`）双双钉住 ⇒ **改名方案不可用**，按边界补充记 6 的断言字段退路落地（依据记录在 decision.md）。 |

## 2-再补. dated APPEND —— 复审 `changes_required` 修复门禁（2026-09-22 晚，**先于二轮任何运行冻结**）

> 来源：独立复审 `reviewer_report.md` findings **1（阻断）/6（低）** + 父修法指令（owner「发现的缺陷都要全部修复」）。
> 冻结纪律不变：本节在二轮任何运行（红/绿/变异/证据）之前写定；判据只来自裁定契约 + 复审判定文本，不调用被测函数生成。
> 一轮 15 例判据一字不改；本轮为**增量门禁**，两例新增。

| ID | 类 | 判据（frozen expectation） |
|---|---|---|
| **W06A2-N8b** 非有限 ttl/now 门禁 | negative | **F1 堵死（OPEN-6 C6 fail-open）**：`ttl=NaN` 曾使 `NaN<0` 过门、`min(NaN,cap)=NaN`、`age>NaN` 恒 False ⇒ 已过期回执**永生**=调用方**放宽**，违反 C6「只可收紧」。冻结判据（修法 **(a) 非有限=非法输入=编码化拒绝**，选择依据记 decision.md；**不预判** CLIP-vs-REJECT 归一）：①`evaluate_review(ttl=NaN)` 对**已过期**回执 ⇒ 编码化 `PromptInjectionGuardError`（含 "finite"），**绝不**得返回 `hit`/复活；②`effective_receipt_ttl(NaN)`、`effective_receipt_ttl(+inf)`、`effective_review_instant(NaN 数值)` ⇒ 同类定义拒；③**有限**超 cap 值维持 CLIP（`effective_receipt_ttl(10**30)==cap`——机制不变，归一仍留父裁）；④垃圾字符串 `now="nan"` ⇒ 维持 `tampered` fail-closed（不得 hit）。 |
| **W06A2-N11** 请求身份三件套 | negative | **F6 收紧（OPEN-2 选项 A 逐字「request identity 覆盖 as_of_date / target / payload digest」= 三者全覆盖）**：`request_identity` **缺任一**字段（缺席 / None / 空串）⇒ 编码化 `DemandRegistrationError`（含 "cover"）、**零行产出**；完整三字段 ⇒ 正常登记（正对照）。依据：any-of 会让省略字段的分歧在同一键处撞 `DemandIdempotencyViolation`（裁定语义本应两行）——收紧为三字段全必填，论证记 decision.md。 |

**变异计划（本轮新增两臂，各翻一个 guard；原键 guard 臂保留）**：
① 去 `effective_receipt_ttl` 的 `isfinite` 门 ⇒ **W06A2-N8b 必红**（NaN 复活再现）；
② 身份校验退化回 any-of（集合交集非空即过）⇒ **W06A2-N11 必红**；
③（保留）`compute_demand_key` 键子句丢 `request_identity` ⇒ W06A2-N1 红（+P4/N5 连带）。
一次只翻一个 guard，各跑全表留证。

## 3. 明确不在本 oracle 内（out of scope，留 I-06-B / 后续卡）

- `resume --demand-id --request-file` 与 `complete|fail` 的 **CLI 可失败测试面**（I-06-B；本 attempt 仅落 store 侧生命周期 API）。
- 真实审核执行（scan/record/授权元组铸造）——本 attempt **零 review 行**（W06A-P1「没有伪造 review」）。
- 任何生产写入（生产仓改动 = 0，落地待独立复审 + owner 提交）。
- 数值规范除 TTL（owner 已裁 30d）外一律不写（lease 秒数由调用方给定，不入规范）。

# I-08-B decision.md — implementation decisions (and what is NOT mine to decide)

- card: **I-08-B**（父项 I-08「发布可信性声明」）；attempt `a20260919-01`
- 上游已签署设计: `execution_runs/I-08-A/a20260919-01/decision.md` **r3**（accepted_scoped）
- 本卡角色: **实现者**。本文只登记两类内容：
  1. 卡片/设计**明确授予**本卡的范围内的落地选择（含理由、反例、兼容影响、恢复规则）；
  2. 本卡**无权决定**、必须由 owner 裁决的 OPEN 项（D1–D7）与两项新发现的架构冲突。
- 实现者**不**自签 accepted。

---

## 0. 一句话结论

provider 协议、信任域三元组、规范载荷/验签、重放-过期分离与 G1/G2/G3a/G3b/G4 分类已**在隔离副本内实现并验证**；
`host_signed` 现在**只能**由一次成功握手 + 受信 Ed25519 验签产出；`sys.executable` 之类的普通文件再也拿不到该标签
（§7.1 的 RED 已先取得，见 `oracle.md` §7 与 `before/`）。产品仓**零写入**。

---

## 1. 授予范围内我做的决定（每条含理由/反例/兼容/恢复）

### D-08B-01 `PUBLICATION_RECEIPT_SCHEMA_VERSION` 升为 `"2.0"`（OPEN-D4）

- **授权依据**：I-08-A §8 明确 OPEN-D4「可由 revenue publication owner 自决」，且设计**推荐**升版。
- **选择**：写入端一律 `2.0`；读出端同时接受 `1.0`（`LEGACY_RECEIPT_SCHEMA_VERSIONS`）。
- **理由**：`attestation_status` 仍是自报字符串；若不升版，「无 attestation 的 1.0 收据」与「有 attestation 的 1.0 收据」无法用版本区分，G3a/G3b/G4 判据会被削弱（设计 §8 OPEN-D4 原文）。
- **反例（必须成立）**：旧 `1.0` 收据仍可被 `validate_publication_receipt` 读出并通过结构校验 → 已由 `receipt_kind()` 与 `ACCEPTED_RECEIPT_SCHEMA_VERSIONS` 覆盖；**不重签、不重算**任何历史收据。
- **兼容影响**：**改变了 artifact 字节** → `tests/golden_behavior_hashes.json` 必须按仓库自带流程刷新（见 D-08B-04）。
- **恢复规则**：把常量改回 `"1.0"` 并把新字段设为可选即可回退；本卡未写产品仓，恢复面为 attempt 内文件。

### D-08B-02 `publication_attestation` 记录放在 **result 顶层**（不在 receipt 子对象内）

- **授权依据**：设计 §7 的最小修改范围写的是「receipt 增加 `publication_attestation` 子对象 + schema 版本」。
- **选择**：记录放 `result["publication_attestation"]`，并在 receipt 内新增 4 个**只读溯源字段**
  （`attestation_key_fingerprint` / `attestation_issuer` / `attestation_key_id` / `attestation_signed_at`）。
- **理由（为什么这不是缩水）**：
  - 设计**同时**要求 `receipt_sha256 = canonical_sha256(receipt 去掉 receipt_sha256)`。若把记录塞进 receipt，
    则记录的载荷里含 `receipt_sha256`、receipt 里又含记录 → **不可满足的互相引用**；
  - 放在顶层后，观察到的 L3 证据在顶层，receipt 内仍有「谁、何时、用哪把 key」的实体字段，
    消费者可两者交叉核对；
  - 设计冻结的 `payload_sha256 = canonical_sha256(result 去掉 result_sha256/publication_receipt)` 因此**逐字**可用，无需发明第三个哈希规则。
- **反例**：把记录从顶层搬到 receipt 内 → `record["receipt_sha256"]` 与实际 receipt 不再可能一致（互相引用），
  `E16`/`E15` 会在**每一次**发布上失败。本卡不采用。
- **兼容影响**：顶层新增键，旧消费者忽略即可；`receipt_schema_version` 已区分新旧。

### D-08B-03 自引用：`result_sha256` / `receipt_sha256` 在载荷内取**空承诺**

- **事实**：这两个字段覆盖**整份 artifact（含刚产生的记录）**，因此只可能在签名**之后**才确定。
  设计 §4.2 把它们列进载荷字段集，同时 §4.2 的排除清单又禁止自引用。
- **选择**：载荷里二者取 `""`（空承诺）；**真正的绑定由 `payload_sha256` 承担**：它是"result 去掉
  `result_sha256`/`publication_receipt`/`publication_attestation`/outcome 附录"的规范哈希，
  在签名前后**逐字节稳定**，因此 receipt 的 `validated_payload_sha256` 与记录的 `payload_sha256` 能够相等。
- **反例与为什么不伪造**：若把签名后的 `result_sha256` 写进记录，签名必然失效（字段在签名域内）；
  若不校验该字段又保留它，就等于对外宣称一个没人能复核的摘要 —— 比空承诺更差。
  空承诺**不会**放松任何既有门：`E16` 的其余判据（`input_sha256`、`forecast_schema_version`、artifact 自报 `payload_sha256`）仍在。
- **恢复规则**：一旦 owner 裁决出「结果哈希如何进入签名域」的规则（例如两阶段签收据），此处可替换而无需改动协议其余部分。

### D-08B-04 未签名附录：outcome 报告进 result、**测量值不进**

- **选择**：`result["publication_attestation_outcome"]` 记录**确定性**事实：`status`、`failure_code`、
  `detail`、`provider_invocations`、`handshake_ok`、`trust_domain_size`、`W_enforced`、`W_parameter`。
  它属于 `UNSIGNED_APPENDIX_KEYS`，不进签名投影（它记录"这次签名尝试发生了什么"，只能在尝试之后知道）。
- **关键修正（本卡实测发现）**：最初把**实测发布窗长**也放进 outcome，结果
  `tests/test_zr1008_new_chain_cutover.py::test_c1_snapshot_round_trip_replays` 立刻失败 ——
  同一输入两次运行产生不同 `result_sha256`，破坏快照重放契约。已把墙钟测量值移出 artifact。
  证据：该用例现为 PASS（见 `after/I08B-c8-full-suite` 与 `after/c8_failure_diff.txt`）。
- **`tests/golden_behavior_hashes.json` 刷新**：artifact 形状**故意**变化（新增附录键 + header 版本变化），
  按该文件自带的、有文档的流程刷新：
  `python tests/test_golden_behavior_lock.py --update-golden`。
  刷新前后哈希都留在 `before/golden_behavior_hashes.json` 与 attempt 内新文件，**不是**为了让失败消失而改断言；
  并且已证明该刷新是**确定性**的（连续两次刷新文件 sha256 相同）。
  这是**必需的产品仓改动**，实现者在此显式登记，交由 reviewer 判定是否接受。
- **独立复核已裁决 CONFLICT-2：接受**，并补充两条证据（已记入 `review.md` §7）：
  新旧 golden 在**各自树上** `test_golden_behavior_lock.py` 均 **1 passed**（刷新不是在掩盖失败）；
  差异只有 **5 个值**且键名未变，来源只能是 schema 1.0→2.0 + 4 个新 provenance 键 + 顶层 outcome 键的形状变化。

#### D-08B-04b 未签名附录的**硬禁令**（独立复核裁决）

复核接受 outcome 的"非证据性存在"，但要求附禁令；本卡据此冻结：

> **任何文档、消费者或下游流程 MUST NOT 依据 `result["publication_attestation_outcome"]` 下任何结论。**
> 它不在签名投影内，可被逐字改写而不触发任何验签失败。信任决策**只**由
> `result["publication_attestation"]`（受签记录）+ 信任域验证 + receipt 的 `attestation_status` 承载。

复核实测（记录在案）：把 `publication_attestation_outcome["status"]` 改成 `"host_signed"` 后，
`validate_publication_receipt` **通过**、`verify_publication_attestation` 返回 `[]`，且仓内**无**消费者读它
⇒ 现存风险是"潜在误导"而非"现行漏洞"，故以**禁令**而非代码强制收口（写成代码强制会需要新的"禁止读某字段"机制，
超出本卡 allowlist）。

### D-08B-04c 签名投影口径修正（独立复核 P2-2）

- **复核发现**：`payload_sha256` 曾只排除 `result_sha256`/`publication_receipt`（+ 附录），因此
  `sources` / `parameter_trace` / `data_gaps` / `disconfirming_indicators` **不在承诺覆盖内**；
  逐个改这 4 个键时 `verify_publication_attestation` 返回 `[]`（只有 `validate_publication_receipt` 报错拦下）。
- **处置**：投影改为**包含式**——除 `result_sha256`、`publication_receipt`、`publication_attestation`（记录内含该哈希）
  与 `UNSIGNED_APPENDIX_KEYS`（只在尝试后才可知）之外，**所有 result 键都进入承诺**。
  这 4 个键在签名**之前**就已存在于草稿上，因此纳入承诺不引入任何自指，也不改变签名时机。
- **一致性**：`revenue_publication._payload_sha256` 委派同一实现，receipt 的 `validated_payload_sha256`
  与记录的 `payload_sha256` 不可能漂移（`ProjectionCoverageTests` 断言二者相等）。
- **恢复规则**：若 owner 要求收窄投影，回退点是把这四个键显式加入排除集，但**必须同时**删除任何"该函数覆盖整个 artifact"的表述。

### D-08B-04d E29 / E30 从"已声明"变为"可达"（独立复核 P1-1 / P2-1）

- **E29**：设计把它定位在**消费者**侧（OPEN-D6，跨仓），但独立复核实测本仓**没有任何** `raise E29_*` 的路径，
  `classify({"schema_version":"3.8"})` 返回 `(G3a, E26)`。本卡新增**同仓入口点**
  `require_legacy_exemption(schema_version)`：G1 集合 → 放行；其它（3.7/3.8/未知/None）→ 抛 **E29**。
  跨仓接线**仍然**是 OPEN-D6，本卡**不声称该缺口已闭**，只声称"码可达、有失败用例、消费者有判据可调"。
- **E30**：既有门 `trust_anchor.verify_input_binding` 只抛裸 `ForecastInputError`（消息为规范历史文本，但无码）。
  现改为抛 `AttestationError(E30, <原消息逐字>)`；因为 `AttestationError` 继承 `ForecastInputError`，
  **所有既有 `except ForecastInputError` 调用方行为不变**，消息文本也逐字保留（设计明确要求保留原文）。
- 两条都补了失败用例（`T-L7b`、`E30InputBindingTests`），使"码存在"与"码可达"不再混淆。

### D-08B-05 `W` / `T` / `L` 一律参数化（OPEN-D7），不发明数值

| 参数 | 落地方式 | 未裁决时的行为 |
|---|---|---|
| `W` | `REVENUE_ATTESTATION_MAX_WINDOW_SECONDS` | 未设置 ⇒ **不施加上限**，`W_enforced=false` 记入 outcome；结构顺序 `issued ≤ signed ≤ expires` 仍强制 |
| `T` | `REVENUE_ATTESTATION_TIMEOUT_SECONDS` | 未设置 ⇒ **拒绝调用**（`provider_call_budget_unspecified`），绝不无界等待 |
| `L` | `REVENUE_ATTESTATION_STDOUT_LIMIT_BYTES` | 未设置 ⇒ **拒绝调用**（同上码），绝不无上限读取 |

- 规范文本内**没有**任何具体秒数/字节数被写成硬性值；测试里出现的 `20`/`65536`/`3600` 都在测试或绑定里显式标注为**测试注入值**。
- 拒绝码 `provider_call_budget_unspecified` **不是 E 码**（不写成 `E##`），以免污染 §2.5 的唯一来源。

### D-08B-06 provider 调用形态：`provider + 可选固定 argv 尾`（**测试/运维专用**）

- 新增可选 `REVENUE_ATTESTATION_PROVIDER_ARGV`（JSON 字符串数组），拼在 `argv[0]` 之后；仍**无 shell**。
- **用途范围（独立复核 P3-4 要求标注）**：这是**测试/运维专用**契约，用于"provider = 解释器 + 脚本"的部署形态；
  **不设时行为完全不变**，也**不**取代或放宽设计 §2.1 的"绝对路径可执行文件"主契约（`argv[0]` 仍是该路径）。
  任何生产调用方**不依赖**它。
- 理由：Windows 上裸 `.py` **不可执行**（`Popen` 直接 `OSError`），而"解释器 + 脚本"是真实部署形态之一；
  没有它，负例只能证明"无法启动"，无法证明"能启动但协议不合规"。
- 反例：把它当万能逃生口 → 只有 JSON 数组被接受，非法值一律拒绝调用。

### D-08B-07 `record_to_payload` 返回**副本**

- 实测发现：原先返回内部字典，调用方改写它会**污染原记录**（本卡调试期真实踩到，表现为看似无关的 E18）。
  已改为 `dict(payload)`；这条是纯粹的缺陷修复，不属于设计变更。

### D-08B-08 CONFLICT-1 的加固（独立复核裁决：接受豁免 + 追加两条 AST 断言）

- 复核接受独立命名的豁免集合 `NON_DOWNLOAD_SUBPROCESS_USERS`（按**文件名精确匹配**，
  `FORBIDDEN_SYMBOLS` 对全体非 canonical 文件继续生效），但要求守卫**追加两条断言**，已实现：
  1. 豁免文件**不得**定义 `FORBIDDEN_SYMBOLS`（`test_exempted_subprocess_user_defines_no_filing_owner_symbol`）；
  2. 豁免文件**不得** import 下载/网络模块（`FORBIDDEN_EXEMPT_IMPORTS`：`requests`/`urllib`/`http`/`socket`/
     `ftplib`/`smtplib`/`telnetlib`/`webbrowser`/`filing_fetch_client`/`fetch_filing`）
     （`test_exempted_subprocess_user_imports_no_download_or_network_module`）。
- 两条断言**同时**校验豁免文件存在（防止改名后豁免静默失效）。
- 若 owner 仍不接受该豁免，回退点是：把 provider spawn 移出 `scripts/` 顶层模块（语义错位），
  或取消 `subprocess` 守卫对签名用途的适用——两者都需要架构决定，本卡不单方面选择。

---

## 2. 两项**本卡无权决定**的架构冲突（请 reviewer/owner 裁决）

### CONFLICT-1 `test_single_owner_guard.py` 禁止新文件 import `subprocess`

- **事实**：该守卫要求 `scripts/` 下除 `filing_fetch_client.py` 与 `source_preparation.py` 外**任何模块**不得 import
  `subprocess`，注释写明「No new entries without review」。设计强制的一-shot provider 子进程必然需要一个 spawn 原语。
- **本卡处置（可回退）**：新增**独立命名**的豁免集合 `NON_DOWNLOAD_SUBPROCESS_USERS = {"attestation_protocol.py"}`，
  与 `ORCHESTRATORS` 分开，并写明「本模块不下载、不接触 filing-fetch、不 resolve 任何取件，只做一次签名握手」。
- **为什么不静默塞进 ORCHESTRATORS**：那会让"第二个下载 owner"的判别失去可见性。
- **独立复核裁决：接受豁免，但要求加固**——已在守卫里追加两条 AST 断言（见 D-08B-08）。
  **本卡仍不声称该守卫的原始意图已被无条件满足**：它只在"豁免分类可见 + 两条新断言成立"的意义上被满足。

### CONFLICT-2 `tests/golden_behavior_hashes.json` 必须刷新

- 见 D-08B-04。artifact 形状是**故意**改变的，但刷新冻结基线本身是一次**版本化变更**，按仓库文档需要"explained baseline review"。
  本卡提供了：变化原因、刷新前后哈希、确定性证明、以及"新旧 golden 在各自树上均 1 passed"的补充证据。
  **独立复核裁决：接受。**

---

## 3. OPEN 项：本卡一律**不决定**，如实登记

| OPEN | 本卡的做法 | 本卡**没有**做 |
|---|---|---|
| **D1** 权威信任根 | 只用隔离的 attempt 内文件；默认路径缺失仍是合法零受信 | 未选仓库内/机器级/keystore；未创建任何生产信任域文件 |
| **D2** 私钥归属/operator 身份 | 只用进程内临时测试密钥 | 未生成、未保管、未提交任何真实私钥；未定义 issuer 命名政策 |
| **D3** 撤销是否回溯 | 只实现"撤销阻止未来发布"（设计默认），历史复验不受影响 | 未裁决回溯语义 |
| **D4** receipt 升版 | **已按授权自决为 2.0**（D-08B-01），读出端兼容 1.0 | —— |
| **D5** `require_attestation=False` 降级开关 | 未触碰跨仓消费者 | 未改开关归属/授权/留痕规则 |
| **D6** 3.8 消费者门 | 同仓导出 `is_legacy_exempt()`，只认显式 G1 集合 | **未**接线到跨仓消费者；**不声称缺口已闭** |
| **D7** `W`/`T`/`L` | 全部参数化，见 D-08B-05 | 未发明任何数值，也未宣称"provider 协议无未决" |

另登记设计遗留项：registry attestation 锚的**确切字段名**仍属 UNRESOLVED-BY-DESIGN。
本卡追加 `publication_attestation_status` / `publication_attestation_sha256` 两键（纯追加，旧行可读），**不宣称已定案**。

---

## 4. 失败停止条件的自查

| 停止条件（卡片原文） | 本卡状态 |
|---|---|
| 信任名单来自同一响应且无外部锚 | **未触碰**：信任域只从 host 侧文件解析，provider 从不决定信任域 |
| 签名证明被扩大到历史 capture | **未触碰**：L1 `signature_present` 原值保留；`T-L10` 断言无任何"capture 已签"字段 |
| 为通过而删 F01/F02 | **未触碰**：`validate_published_forecast` 仍在 `build_publication_receipt` 之前；正/反例仍在跑 |
| 普通解释器成为无界 provider | **已消除**：`T`/`L` 未裁决即**拒绝调用**；`sys.executable` 拿不到 `host_signed` |

## 5. 未做 / 未验证

- 未运行真实 provider、未联网、未发布、未写生产 registry、未生成生产密钥。
- 未裁决 D1/D2/D3/D5/D6 与 registry 锚字段名。
- 未验证跨仓消费者（invest-core）影响面；3.8 旁路缺口**保持 OPEN**。
- `E31`（发布回滚）属 I-09-A，本卡只登记（`after/I08B-c7-tpub` 只覆盖既有单文件事务用例）。
- 隔离副本无法收集的 26 个测试模块（依赖不在产品树中的文件）在 before/after 两次普查中**同样**无法收集，
  因此不构成本卡回归；它们被逐名列出（`scratch/c8_ignore.txt`）而不是静默丢弃。

---

## 6. 第四轮复核保留项（P3）的登记

> 本轮（第四轮）独立复核的 verdict 为 `accepted_scoped`（技术面 + 交付面），保留 3 项 P3。
> **本节只做登记与口径收窄，不关闭任何 OPEN 项**（`closed_by_this_card = []`）。

### D-08B-09 artifact 顶层 `payload_sha256` 的**对外契约**（R4-1）

- **事实**：签名发布时 `run_forecast` 在 result 顶层导出 `payload_sha256`，而该键**被排除出承诺投影**——
  必须排除，否则承诺会依赖自身。它是 P2-2 得以在**真实产物**上被观测的条件（见 D-08B-04c）。
- **面向下游的契约（本条即 R4-1 要求的落地说明）**：
  - "对**整份 artifact** 做规范哈希"**不会**等于 `validated_payload_sha256`；
  - 要与 `validated_payload_sha256` 对齐，必须**恰好排除**：`result_sha256`、`publication_receipt`、
    `publication_attestation`、`payload_sha256`、`publication_attestation_outcome`；
  - 该键**不是**可信声明：可信性只由 `result['publication_attestation']` + 信任域校验 + receipt 的
    `attestation_status` 承载（与 D-08B-04 的附录禁令一致）。
- **本卡不动它**：不移动、不改名、不改语义；只登记契约。`handoff.json.artifact_top_level_payload_sha256_contract` 同款登记。

### R4-2 / R4-3 的口径登记（不改任何结论）

- **R4-2**：第三轮转录块存在三组**同源**字节读数——4300 B/`d6388028…`（marker **行**边界的真块，与源块逐字节相同）、
  4302 B/`cca2ae29…`（marker **文本**边界，多带首尾各一个边界换行）、4299 B/`421e73a8…`（再去掉块尾换行）。
  口径收窄为"**内容逐字节相同、边界换行计法不同**"。证据 `after/c45_r42_block_reconciliation.json`，
  独立复算 `after/c47_round4_verdict_reextract.json`。**§9 已登记字节一个字节未改**。
- **R4-3**：`c43.prefix_unchanged` 只覆盖"**该次追加之前**"的状态（此前 §5/§7 各有一处复核要求的编辑）。
  自本轮起**每次写入重取前缀哈希**：本轮证据为 `after/c46_round4_verdict_transcription.json` 的 `prefix_unchanged=true`。

### 未因本轮裁决而关闭

`E31`、`OPEN-D1`、`OPEN-D2`、`OPEN-D3`、`OPEN-D5`、`OPEN-D6`、`OPEN-D7` 与 registry attestation 锚字段名
**共 8 项仍 OPEN/UNRESOLVED**。`accepted_scoped` 的范围**照抄 reviewer**：技术面 + 交付面；
跨仓消费者、部署、预测公式与准确性**均未授予**。

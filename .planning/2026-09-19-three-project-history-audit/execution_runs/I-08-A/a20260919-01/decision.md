# I-08-A 决策书 — 签名信任域、attestation provider 协议、载荷/版本绑定、重放与旧版本边界

- card: I-08-A（父项 I-08「发布可信性声明」）；parent: revenue publication owner
- attempt: a20260919-01
- 状态: design_frozen（设计冻结，**未实现任何产品改动**；实现属 I-08-B/C）
- 本卡角色: 设计卡 = 高级 reviewer 先定案。执行者（本模型）只做**只读锚定 + 设计冻结 + 可证伪负例声明**，不得自签 accepted。
- 证据基线: `binding.json` 中记录的源文件 sha256（本次实测，与卡内 anchor 一致）。
- 反例来源（只读）: `reviews/revenue/logs/publication_probe.stdout.txt`、`reviews/revenue/probe_publication.py`、`reviews/revenue/review.md` 第 25/26 行、`audit_report.md` 第 58/59 行。

本文所有 "MUST / 必须" 都是对 **I-08-B/C 实现者** 的约束；所有 "NEG-xx" 都是**必须可证伪的负例**，逐条列在 `oracle.md`。

---

## 0. 事实锚定（现状，非推测）

| 事实 | 现状代码锚点 | 实测 sha256 |
|---|---|---|
| `attestation_capability()` 只做「provider 路径存在」判断 | `scripts/revenue_core.py:113-125` | `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae` |
| `run_forecast` 用该布尔量决定 `attestation_status = "host_signed"` | `scripts/revenue_core.py:165-171` | 同上 |
| publication receipt 只**记录** `attestation_status` 字符串，不含任何签名/issuer/key | `scripts/revenue_publication.py:120-160`、`185-261` | `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba` |
| 真正的 Ed25519 验签存在且有效（白名单内 key 通过、伪造/未受信/失效签名拒绝、无白名单一律拒绝） | `scripts/contracts/evidence.py:270-308`、`311-363` | `bc5e4c5305fad22f9c028fd989536d6529ef868698fb0adfcd9363b3e096208e` |
| 默认受信名单文件 `config/trusted_signer_public_keys.json` **不存在** → 默认零受信 signer | `scripts/contracts/evidence.py:242-267` | 文件不存在（实测 `Test-Path=False`） |
| `host_receipt` 的签名是**可选字段对**；缺失时仍是「普通自报 attestation」并通过 `validate_host_receipt` | `scripts/contracts/evidence.py:311-363`；`company_wiki_source.py:325-337` | 同上 |
| provider 从未被真正调用：`build_host_receipt` 全仓仅被 re-export，生产路径无调用者 | `scripts/revenue_core.py:21`（`# noqa: F401 re-export for consumers`） | 同上 |
| CLI 顺序：先 `prepare_forecast`（内部 `register_publication`）→ 之后才 `_atomic_write_text` 写 output/markdown | `scripts/revenue_forecast.py:22-35`、`55-123` | `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc` |
| registry 无「签名字段」列，注册行只存 hash；只能事后拿外部收据比对，不能自证签名历史 | `scripts/publication_registry.py:127-159`；生产 registry 行键实测 = 14 个键，无 `attestation*`/`signature*` | `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa` |
| 消费者门（invest-core `adapt_revenue`）只把 `attestation_status == "host_signed"` 当作通过，不校验签名实体 | `~/.claude/skills/invest-core/scripts/invest_contracts.py:1130-1142`（属**跨仓消费者**，禁改） | 本卡只读引用，不写入 |
| 上述消费者门对**非当前 schema** 完全旁路（`is_legacy` → registry 门与 attestation 门都不跑） | 同上 `:1116-1127` | 只读引用 |

**结论（与 audit_report 一致，不夸大）**：缺口是 (a) `host_signed` 标签与「签名实际存在」解耦、(b) provider 从未被调用/无协议、(c) 签名与 publication 载荷无绑定、(d) 旧 schema 全量旁路。**现有密码学验签功能不在否定范围**，本卡不得声称「验签不存在」。

---

## 1. 三层证明域（按卡片动作 1）

| 层 | 名称 | 签名对象 | 唯一能证明的事实 | 明确**不能**证明 |
|---|---|---|---|---|
| **L1** | raw capture event 签名（来源层） | 一次取件事件：`event_sha256` + tool/action/timestamp/environment | 「该 issuer 在此时点、此环境、用该工具**执行过**这个取件动作，且返回字节的规范哈希就是 `event_sha256`」 | 不能证明文档来源真实、内容未被上游伪造、公司事实为真 |
| **L2** | host receipt 签名（本机执行层） | L1 收据整体（不含签名域本身） | 「这台 host、这个 issuer 复核/转写了 L1 收据」 | 不能凭空替代 L1；L2 存在不使 L1 从 unsigned 变 signed |
| **L3** | forecast publication 签名（发布层） | 规范序列化的 publication 载荷（见 §4） | 「某个受信 issuer 在此发布时刻为**这一份** input/payload/result 组合背书」 | 不能回溯证明历史 raw 曾由可信工具取得；不能把 L1/L2 的缺失补上 |

**硬规则 R-LAYER-1（对应 A-D3）**：任何后加签名（含 L3）**不得**改变既有 L1/L2 收据的 `signed/unsigned` 事实。历史 archive 的 `attestation_status` 与 source receipt 的 `signature_present` 一律保持观测原值；**禁止重签伪造历史事件**。

**硬规则 R-LAYER-2**：`host_signed` 只能由 L3 判定产出。L1/L2 全部存在且已验签，**也不**足以让 publication 成为 `host_signed`。

---

## 2. Attestation provider 协议（按卡片动作 2、4）

### 2.1 传输（request/response）
- provider 由 `REVENUE_ATTESTATION_PROVIDER` 指定：**绝对路径可执行文件**（PATH 名允许，但必须解析为真实可执行文件）。
- 一次 provider 调用 = 一次**单次**进程：写入 request JSON 到 **stdin**，读取 response JSON 到 **stdout**，`stderr` 只作诊断。
- **MUST NOT** 长驻服务、**MUST NOT** 开放任何网络端口、**MUST NOT** 由 provider 自行决定信任域。

### 2.2 请求（`attestation_request` schema `1.0`，精确字段集，多/少一律拒绝）
```
{
  "attestation_request_schema_version": "1.0",
  "request_id":            "<64 hex>",   # 一次性 nonce，调用方生成，本次发布唯一
  "issued_at":             "<RFC3339 UTC 'Z'>",
  "expires_at":            "<RFC3339 UTC 'Z'>",
  "domain_separator":      "revenue-forecast/publication-attestation/v1",
  "payload_sha256":        "<64 hex>",   # §4 规范载荷哈希
  "input_sha256":          "<64 hex>",
  "result_sha256":         "<64 hex>",
  "receipt_sha256":        "<64 hex>",
  "engine_version":        "4.1.0",
  "forecast_schema_version":"3.7",
  "publication_receipt_schema_version": "1.0",
  "requested_issuer":      "<str>"
}
```
- 请求**不含**私钥材料，**不含**原始输入文档（只放 hash），**不含**自由文本备注。
- `issued_at`/`expires_at`：`expires_at > issued_at`，且 `expires_at - issued_at <= W`，其中 **`W` 是参数，不是凭据**。本设计**不自行确定 `W` 的数值**：初值 900 s 与任何其它数值一样缺少证据支撑（复审 F-I08A-03 已 grep 确认产品 scripts 中 `expires_at`/`issued_at`/`not_before`/`not_after`/`validity` **零命中**，`900` 只命中取件超时），因此 `W` 登记为 **OPEN-D7（参数待证据）**，见 §8。在 OPEN-D7 裁决前，实现者**不得**把某个具体秒数写成硬性上限，也不得据此宣称「发布窗无未决」。

### 2.5 规范错误码表（单一来源；`oracle.md` 与 I-08-B/C 一律引用本节）

**错误码唯一来源（唯一来源规则）**：本表是错误码的**唯一规范来源**。`oracle.md` 的 NEG-* 与 `review.md` 的 R* 只**引用**本表，不再各自发明或合并码值；任何新增码必须先加进本表。
**编号规则（r3，复审 N-R2-05）**：编码按**语义连续**而非按序号连续——E01…E31 覆盖 provider / 签名 / 信任域 / 重放 / 旧版本 / 事务；**E32** 是 r3 新增的 `provider_capability_unproven`，**追加在末尾**而不打乱既有编号，以免使已发出的引用失效。因此「E 码表」在 r3 后含 **32 个码（E01–E32）**。
**码值与现状消息的关系**：现状产品消息（`not trusted`、`signature verification failed`、`invalid capture host_receipt signature`、`signature fields must come together`、`input binding mismatch: …`）**继续原样保留**，新码用于新协议层，二者映射关系写在表的最后一列。

| # | 错误码（冻结字符串） | 触发点 | 层 | 后果 | 现状产品消息 / 备注 |
|---|---|---|---|---|---|
| E01 | `provider_absent` | `REVENUE_ATTESTATION_PROVIDER` 未设置 | L3 | 不 `host_signed`，落 G3a | — |
| E02 | `provider_path_unopenable` | 变量已设置，但路径**不存在**或**不可作为文件打开**（`stat`/`open` 失败）。**r3 收窄（复审 R-BIND-2）**：本码**不再**涵盖 `sys.executable` 或裸 `.py`/`.txt`——那些路径是存在且可打开的，归 **E32** | L3 | 不 `host_signed`；**不得**读取/执行/import 该文件 | 原措辞「不是可执行文件」不可判定（`sys.executable` 恰恰是可执行文件），已移除 |
| E32 | `provider_capability_unproven` | provider 路径**存在且可打开**，但**未被证明具备签名能力**：即没有完成一次成功握手。涵盖 `sys.executable`、裸 `.py`、`.txt`、以及任何存在却无协议响应的路径 | L3 | 不 `host_signed`；**不得**以「存在/可执行/是 .py」作为能力依据；**不得**读取/执行/import 该文件（`provider_file_read_bytes` 只能为 0 或 null，`provider_calls` 只能为 0） | **A-D1 的主判据**（r3 新增，回应 R-BIND-2：`sys.executable` 可执行，按旧定义永远落不到 E02） |
| E03 | `provider_protocol_violation` | 不读 stdin / 无 JSON 输出 / 输出非单个 JSON 对象 | L3 | 不 `host_signed` | 与 E04 区分：E03 是「有输出但不成协议」 |
| E04 | `provider_invalid_json` | stdout 无法作为 JSON 解析 | L3 | 不 `host_signed` | 复审 F-I08A-02 指出本码原仅在 decision.md §2.4 出现，现正式入表 |
| E05 | `provider_exit_nonzero` | 退出码 ≠ 0 | L3 | 不 `host_signed` | — |
| E06 | `provider_output_too_large` | stdout > `L` bytes（`L` 见 OPEN-D7） | L3 | 不 `host_signed`；**绝不**解析被截断前缀 | r3 参数化（复审 N-R2-04）：初稿 65536 已撤下 |
| E07 | `provider_timeout` | 超过 `T`（§2.4；`T` 取值见 OPEN-D7 同类参数说明） | L3 | 不 `host_signed`；子进程必须被终止 | — |
| E08 | `provider_schema_mismatch` | 响应字段集多/少/类型错 | L3 | 不 `host_signed` | — |
| E09 | `provider_binding_mismatch` | `request_id`/`payload_sha256`/`domain_separator` echo 与请求不逐字节相同 | L3 | 拒绝（跨载荷重放唯一防线） | — |
| E10 | `provider_signing_unavailable` | provider 明确报无法签名 / 缺私钥 | L3 | 不 `host_signed`，保留 `unattested` + 原因 | — |
| E11 | `provider_version_mismatch` | 载荷内 `engine_version`/`forecast_schema_version`/`publication_receipt_schema_version`/`validator_version` 与当刻运行时值不等 | L3 | 拒绝 | 现有 `validate_publication_receipt` 有等价比对，但**不在签名覆盖内**；本设计要求纳入签名载荷 |
| E12 | `attestation_missing_signature` | 声称为 attestation 记录但无签名域 | L3 | 拒绝 | — |
| E13 | `attestation_malformed_signature` | 签名长度/字符集非法（非 128 位小写 hex） | L3 | 拒绝 | 现状消息 `invalid capture host_receipt signature`（保留） |
| E14 | `attestation_signature_invalid` | 载荷被改后旧签名失效 | L3 | 拒绝 | 现状消息 `signature verification failed`（保留） |
| E15 | `attestation_payload_fields` | 载荷字段集不精确（含截断载荷按已有字段签） | L3 | 拒绝 | — |
| E16 | `attestation_payload_hash_mismatch` | `payload_sha256` ≠ 实际 result 重算值 | L3 | 拒绝 | — |
| E17 | `attestation_domain_mismatch` | `domain_separator` 与当刻服务不符（跨域重放） | L3 | 拒绝 | — |
| E18 | `attestation_expired_at_publish` | `issued_at > signed_at` 或 `signed_at > expires_at` 或 `signed_at - issued_at > W` | L3 | 拒绝 | `W` 见 OPEN-D7 |
| E19 | `request_id_reuse` | 同一 `request_id` 第二次用于**不同** `payload_sha256` | L3 | 拒绝新发布 | **不**参与历史复验（见 §5） |
| E20 | `provider_key_untrusted` | fingerprint 不在信任域 | L3 | 拒绝 | 现状消息 `… is not trusted`（保留） |
| E21 | `issuer_key_binding_mismatch` | `issuer` ≠ 该 key 声明的 issuer | L3 | 拒绝 | 现状**缺失**该判定（EXP-BASE-11 gap=true） |
| E22 | `key_outside_validity_window` | 当刻 ∉ [`not_before`,`not_after`] | L3 | 拒绝 | 现状**缺失**该判定（EXP-BASE-12） |
| E23 | `key_revoked` | 信任域 `status == "revoked"` 的 key 用于**新**发布 | L3 | 拒绝 | 现状**缺失**该判定（EXP-BASE-12）；历史复验另见 §5 |
| E24 | `test_key_in_production_trust_domain` | 信任域条目的 `environment` 含 `test` 却走正式发布路径 | L3 | 拒绝 | 现状**缺失**该判定（EXP-BASE-12） |
| E25 | `trust_domain_schema_error` | 信任域文件存在但不可解析 / 键名不符 / 条目缺必填字段 / 签名公钥长度非 32 B | L3 前置 | **必须报错**，**不得**静默返回空集（见 §3「加载语义」） | 现状 `except (OSError, ValueError, KeyError, TypeError): return {}` **静默吞掉**，与「确实零受信 key」不可区分（复审 F-I08A-05） |
| E26 | `attestation_absent` | 当前 schema 包**未作任何签名声明**（receipt 无 `attestation_status` 或为 `unattested`） | L3 | 落 **G3a**：保留研究结果，不得升级 | 消费者现状已用 `unattested_bypassed` 词表 |
| E27 | `attestation_missing_record` | receipt 声称 `host_signed` 却**没有** `publication_attestation` 记录 | L3 | 落 **G4**：**拒绝**，不得静默降级 | 对应 NEG-LEGACY-4；F-I08A-01 的唯一归属由 §6 冻结 |
| E28 | `legacy_read_only` | 旧版本包（G1）走消费者正式门 | 消费者 | 只读兼容，不得新建下游 artifact | 沿用 `invest_contracts.py:1120/1132` 既有词表 |
| E29 | `legacy_exemption_not_allowed_for_optin_schema` | 把 opt-in schema（3.8）当作 G1 自动旁路 | 消费者 | **拒绝**；必须按 §6.3 的分类判据走 | 新增，回应 F-I08A-04；规则 R-LEGACY-1 见 §6.3 |
| E30 | `input_binding_mismatch` | `input_document` 与 `input_sha256` 不符（A-D4 下半段） | L1 前置 | 拒绝；provider 调用 = 0，registry 新增 = 0 | 现状消息 `input binding mismatch: embedded input_document does not hash to input_sha256`（保留原文，本码为其规范名） |
| E31 | `publication_rollback_required` | output 写失败但 registry 已有行 | 事务 | 必须回滚注册，不得留可消费半发布 | 属 I-09-A；现状实测 `registry_entries_added=1, output_exists=false` |

**两个参数、一个未决**：`W`（发布窗长度）、`T`（provider 超时上限）、`L`（provider stdout 上限）取值同属 **OPEN-D7**；本表只冻结它们的**语义与失败码**（E18/E07/E06），不冻结数值。**本设计不自行确定 `L`**：初稿的 65536 bytes 与任何其它数值一样缺少证据支撑（复审 N-R2-04），在 OPEN-D7 裁决前**不得**把某个具体字节数写成硬性上限（r3 已从 §2.4 与 §4.2 撤下该数值）。

**一致性规则（码值唯一来源）**：`oracle.md` §2 的 NEG-* 表第 4 列**只引用**本节的码值；两份冻结文本之间**不得**存在同名不同义、或一处有另一处无的码。reviewer 的一致性判据：对任一 NEG 行取第 4 列的 `E` 编号，必须能在本节精确命中同一字符串（r2 已用 `check_r2_consistency.py` 机器校验：31 个码、0 未定义、0 未被引用）。

### 2.3 响应（`attestation_response` schema `1.0`，精确字段集）
```
{
  "attestation_response_schema_version": "1.0",
  "request_id":           "<echo，必须与请求逐字节相同>",
  "payload_sha256":       "<echo，必须与请求逐字节相同>",
  "domain_separator":     "<echo，必须与请求逐字节相同>",
  "issuer":               "<str，非空>",
  "key_id":               "<str，非空>",
  "key_fingerprint":      "<32 hex>",     # = sha256(raw public key) 前 32 hex（沿用现有格式）
  "signature_algorithm":  "ed25519",
  "signature":            "<128 hex>",
  "signed_at":            "<RFC3339 UTC 'Z'>"
}
```
- 签名对象 = `canonical_sha256(response 去掉 signature 域)` 的 ASCII 字节（与现有 `_validate_host_signature` 同构，见 §4.3）。
- 未实现/失败的 provider 用 **非 0 退出码** 或 **协议错误** 表达，**不得**返回「空签名成功」。

### 2.4 限额与失败语义（fail closed）

本节只写**限额**；每一行的失败码以 **§2.5 规范错误码表**为准（复审 F-I08A-02：两份文件不得各自发明码值）。

| 项 | 冻结值 | 违反后果（码值见 §2.5） |
|---|---|---|
| 超时 | `T`（参数，取值见 OPEN-D7；provider 不得自行放宽，且不得无限） | `attestation_status = "unattested"` + **E07** |
| provider stdout 上限 | `L` bytes（参数，取值见 OPEN-D7；初稿的 65536 已撤下，不再作为规范值） | 截断即失败 **E06**，**绝不**解析部分输出 |
| 进程退出码 | 必须为 0 | **E05** |
| 输出可解析性 | 必须是单个 JSON 对象、无尾随垃圾 | **E04**（不可解析）/ **E03**（可解析但不成协议） |
| 字段集 | 精确匹配，多/少/类型错均拒 | **E08** |
| `request_id` / `payload_sha256` / `domain_separator` echo | 必须逐字节相同 | **E09**（这是**跨载荷重放**的唯一防线） |
| 签名验签 | Ed25519 + 受信名单三元组（§3） | **E14** / **E20** / **E21** / **E22** / **E23** / **E24** |
| provider 未设置 | 变量缺失 | **E01** |
| provider 路径**不存在或不可作为文件打开** | 未设置之外的最基本失败：路径无法 `stat`/打开 | **E02** `provider_path_unopenable` |
| provider 存在但**未被证明具备签名能力** | 存在、甚至可执行（`sys.executable`）、或是裸 `.py`/`.txt`，但**没有完成一次成功握手** | **E32** `provider_capability_unproven` → **A-D1 的主判据** |

**硬规则 R-PROV-1（对应 A-D1）**：**禁止**以「文件存在」「可执行」「是 .py」「是 sys.executable」作为能力或签名依据。`attestation_capability()` 语义改为「**已完成一次成功握手**（含受信 key 验签）」。存在性探测**不再**是充分条件。选择路径本身**不得**调用、不得 `import`、不得执行该文件（失败码 **E02**）。

**硬规则 R-PROV-2（测试替身边界，对应失败停止条件「测试私钥被当生产信任」）**：
- 测试/bounded fake provider 只允许位于 **attempt 隔离目录**，其公钥只能写入**隔离的** `trusted_signer_public_keys.json`（经 `REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` 指向 attempt 内路径）。
- **MUST NOT** 把测试 key 写进仓库 `config/trusted_signer_public_keys.json`；**MUST NOT** 用测试 key 签发任何生产 registry 条目。
- 信任域清单必须带 `environment` 与生效窗口；`environment` 含 `test` 的 key **MUST** 在正式发布路径被拒绝（**E24**）。
- **MUST NOT** 由弱模型自造「自签自信任」，**MUST NOT** 引入网络 key service。

---

## 3. issuer / key 识别、轮换与撤销（按卡片动作 4）

信任域表（**必须是数据文件，不是代码常量**）精确形状。**键名冻结为 `public_keys`**：现有加载器 `contracts/evidence.py::_trusted_signer_public_keys` 读的就是 `data.get("public_keys", [])`，因此本设计**沿用**该键名并把新增字段加在**条目内部**，而不是发明一个顶层 `keys` 键（复审 F-I08A-05：初稿写的 `"keys"` 会让「按设计 schema 写的信任域」被现有加载器读成 0 个受信 key，与真正的零受信 key 无法区分）。

```json
{
  "trust_domain_schema_version": "1.0",
  "domain_separator": "revenue-forecast/publication-attestation/v1",
  "public_keys": [
    {
      "name": "host-a-2026a",
      "key_id": "rf-prod-2026a",
      "issuer": "revenue-forecast/host-a",
      "public_key": "<base64 raw 32B>",
      "fingerprint": "<32 hex>",
      "algorithm": "ed25519",
      "environment": "production",
      "not_before": "2026-01-01T00:00:00Z",
      "not_after":  "2027-01-01T00:00:00Z",
      "status": "active",
      "revoked_at": null
    }
  ]
}
```

- **键名与条目字段冻结**：顶层**只允许** `trust_domain_schema_version`、`domain_separator`、`public_keys`。
- **条目字段集 = 12 个字段，允许集合封闭**（复审 R-BIND-1：初稿把 `revoked_at` 用在 §3「撤销」条款里却没放进字段清单，导致「按撤销条款写必被 E25 拒」与「E23 要求 revoked 条目可加载」自相矛盾；r3 把它正式纳入）：
  - **无条件必填（10）**：`public_key`、`fingerprint`、`issuer`、`key_id`、`algorithm`、`environment`、`not_before`、`not_after`、`status`、`revoked_at`。
    - `revoked_at` **无条件必填**但**允许为 JSON `null`**：`status == "active"` 时**必须**是 `null`；`status == "revoked"` 时**必须**是 RFC3339 UTC `Z` 时间串。这样「字段存在性」与「状态」解耦，既不会出现「active 条目偷偷带撤销时间」，也不会出现「revoked 条目忘了写撤销时间」。
  - **可选（1）**：`name`。
  - 计数核对：10 + 1 = **11 个键名**出现在上面的示例条目中；加 `revoked_at` 新增键 = 12 个键名。**本条款以点名的字段集为准，不以计数为准**（避免再次出现「计数与清单不一致」）。
  - **条件约束**：`status == "revoked"` 时必须同时满足 `revoked_at` 非 null **且** `revoked_at >= not_before`；`status == "active"` 时 `revoked_at` 必须为 null 且 `not_after > not_before`。任一违反 → **E25**。
  - 多键、少键、类型错、`status` 不在 {`active`,`revoked`}、`public_key` 非 32 B、`fingerprint` 非 32 hex、时间不可解析 → **一律 E25**（`trust_domain_schema_error`）。**禁止**为兼容而静默忽略未知字段：忽略未知字段就等于允许「改了信任域却没生效」，这正是本卡要消除的失败模式。
- **加载语义（fail loud ≠ fail closed 的静默版）**：
  - 变量未设置且默认路径**不存在** → 合法地**零受信 key**（现状行为，保持 fail closed）；
  - 路径**存在但内容非法** → **必须报错 E25 并中止发布**，**MUST NOT** `return {}`。
  - 理由：现状 `except (OSError, ValueError, KeyError, TypeError): return {}` 把「配置坏了」和「本来就没有配置」压成同一个结果，使运维无法区分，也让 reviewer 无法判定一次 `not trusted` 是攻击还是配置事故。
  - 该行为差异**新增负例 NEG-TRUST-4**（见 `oracle.md`）。
- **绑定三元组**：受信 = (`fingerprint` ∈ 信任域) ∧ (`issuer` == 该 key 声明的 issuer) ∧ (当刻 ∈ [`not_before`,`not_after`]) ∧ `status == active`。失败码分别是 **E20 / E21 / E22 / E23**，不再合并成一个泛码。
  - 现状 `_validate_host_signature` 只查 fingerprint，**不查 issuer、不查时间窗、不查 status** → 属本卡确认的缺口，由 I-08-B 补齐（负例 NEG-SIG-7/8/9）。
  - `environment == "test"` 的条目在正式发布路径 → **E24**。
- **轮换**：新增 key 用**新 `key_id`** + 重叠有效期（新 key `not_before` ≤ 旧 key `not_after`）。重叠期内两者皆可验签；**历史签名在 `not_after` 之后仍可复验**（有效期约束作用于 `signed_at`，不作用于验证时刻）——否则历史证据会在轮换时集体失效。
- **撤销（r3 与字段集对齐）**：`status: "revoked"` **并且** `revoked_at` = 撤销生效的 RFC3339 UTC `Z` 时间串（两处必须同时满足，否则该条目根本无法通过 E25 加载）。撤销**不新增任何字段**——`revoked_at` 已纳入上面的 12 字段封闭集合，因此本条款与字段冻结条款不再冲突（复审 R-BIND-1）。
  - 撤销**只能**阻止**未来**发布；**不得**让既有已发布 artifact 无法复验（复验输出必须区分 `verified_at_publish_time` 与 `key_now_revoked`）。
  - 「撤销是否回溯作废历史发布」= **OPEN-D3（须人/owner 裁决）**。
- **私钥**：**MUST NOT** 存在于本仓、本 attempt 或任何被 schema 校验的文档内。provider 是唯一持钥方（外部）。
- **MUST NOT** 让 provider 决定自己的信任域；信任域解析**只**发生在 host 侧（`contracts/evidence.py` 风格加载：文件缺失 = 0 受信 key；文件非法 = **E25 报错**，二者必须可区分）。

---

## 4. 规范载荷序列化 + hash + 版本绑定（按卡片动作 2）

### 4.1 规范 JSON（冻结，与现有 `canonical_sha256` 完全一致）
- `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))`，UTF-8 编码，`sha256` 十六进制小写。
- 禁 NaN/Infinity、禁整数/浮点混用同一键、禁重复键；时间一律 RFC3339 UTC `Z` 秒级精度；字符串 NFC 归一（**新增要求**，避免同形异码绕过）。
- 哈希的**精确字节**是唯一签名对象；不得对「pretty JSON」「原始文件字节」签名。

### 4.2 L3 publication 载荷（精确字段集；任何增删字段即版本升级）
```
publication_attestation_payload = {
  "attestation_payload_schema_version": "1.0",
  "domain_separator":  "revenue-forecast/publication-attestation/v1",
  "issuer":            <str>,
  "key_id":            <str>,
  "key_fingerprint":   <32 hex>,
  "algorithm":         "ed25519",
  "request_id":        <64 hex>,        # 一次性
  "issued_at":         <RFC3339 Z>,
  "expires_at":        <RFC3339 Z>,
  "signed_at":         <RFC3339 Z>,
  "input_sha256":      <64 hex>,
  "payload_sha256":    <64 hex>,        # = canonical_sha256(result 去掉 result_sha256/publication_receipt)  ← 复用 revenue_publication._payload_sha256
  "result_sha256":     <64 hex>,        # 现约定仍覆盖整份 result（含 receipt），保持既有 tamper 契约不变
  "receipt_sha256":    <64 hex>,        # = canonical_sha256(receipt 去掉 receipt_sha256)
  "engine_version":    "4.1.0",
  "forecast_schema_version": "3.7",
  "publication_receipt_schema_version": "1.0",
  "validator_version": "4.1.0",
  "gate_ids":          [<str>...]       # 实际执行的 gate，不是固定声明
}
```
- **排除清单（防递归）**：签名域本身（`signature`）、`signature_algorithm`、`result_sha256`、`publication_receipt` 三者永不进入被签载荷。载荷与 receipt 互相引用会形成自指/不确定性 → 明确禁。
- **domain separator 必须同时出现在** request、response、payload 三处，且逐字节一致；跨域重放（同一签名换 schema 版本/换服务/换 issuer）由此拒绝。
- **版本绑定**：`engine_version` / `forecast_schema_version` / `publication_receipt_schema_version` / `validator_version` 全部进载荷；任一不匹配当刻运行时值 → 拒绝（**E11**）。沿用现有 `validate_publication_receipt` 的逐项相等比较，但**这些比较必须在签名覆盖之内**才有效——否则攻击者可改字段后重算 hash。

### 4.3 签名对象
`message = canonical_sha256(payload).encode("ascii")`，签名 = Ed25519(`message`) 的 64 字节 hex。
（**与现有 `_validate_host_signature` / `tests/test_attestation.py::_signed_host_receipt` 完全同构**，便于消费者零成本复用同一 helper。）

---

## 5. 重放 / 复用 / 过期语义（按卡片动作 3）

| 概念 | 冻结规则 | 理由 |
|---|---|---|
| **历史签名复验** | 对**同一 immutable artifact**（同 `payload_sha256`）在**任意时刻**重复验证**必须始终通过**；`expires_at` 之后亦然（仅标记 `expired_now`，不改变历史判定） | 「同一产物重复读取不应因签名曾使用过而失效」 |
| **`expires_at` 的真实含义** | 约束**发布时刻**：`issued_at <= signed_at <= expires_at` 且 `signed_at - issued_at <= W`。超窗 = 签名在**发布时**即无效（**E18**）。`W` **是参数不是定值**，取值登记为 **OPEN-D7**（复审 F-I08A-03 已确认产品 scripts 内 `expires_at`/`issued_at`/`not_before`/`not_after`/`validity` 零命中，任何具体秒数在裁决前都无依据） | 需要防的是「预签空白凭证」；但窗长本身要先有证据 |
| **跨载荷重放** | 同一签名换到不同 `input_sha256` / `payload_sha256` / `result_sha256` / `receipt_sha256` / schema 版本 / issuer / domain separator → **全部拒绝**（**E09/E11/E16/E17/E21**） | 签名只绑定一个精确 byte string |
| **同 payload 复用** | 允许当且仅当**所有已签字段完全相同**（同输入、同 result、同版本、同 gate 集）；此时等于「同一物件的第二次自证」，不产生新的历史事件 | 卡片动作 3 原文 |
| **`request_id`** | 一次性 nonce。**新发布请求 MUST 使用新 `request_id`**；同一 `request_id` 第二次用于**不同** `payload_sha256` → 拒绝（**E19**）。`request_id` **不得**进入历史复验门槛（否则重放即失效） | 区分「允许的历史复验」与「不允许的跨载荷重放」 |
| **幂等重跑** | 同输入重跑 → 产生**新的** `request_id`/`signed_at`/registry 行，且**旧行保留**（审计历史）。`registry.audit` 的冲突判据（同 anchor + 同 engine/schema + 同 artifact_type 出现多个 `result_sha256`）继续适用，不得因签名而放宽 | 与 I-09 的重复发布语义衔接 |

**硬规则 R-REPLAY-1**：签名字段**不得**成为「一次性令牌」。任何实现若让历史 artifact 在第二次验证时因 nonce 已用而失败，即为**回归缺陷**。

---

## 6. 旧版本边界：grandfather / invalidate（按卡片动作 5、7）

### 6.0 修订说明（复审 F-I08A-01 / F-I08A-04）
初稿把两类**完全不同**的输入塞进了同一个 G3：「**从不声称签名**的包」与「**声称签名却没有签名记录**的包」，而 `oracle.md` 的 NEG-LEGACY-4 又要求后者被拒绝——两份冻结文本对同一输入给出相反结论。本节按「**是否作出签名声明**」这一唯一判据把 G3 拆成 **G3a / G3b**，并给出**唯一归属**：G3b 归 **G4（拒绝）**，不再属于 G3。同时把 opt-in schema 3.8 的归属写死。

### 6.1 唯一分类判据（单一函数裁决，不得散落）
```
classify(artifact):
    if artifact.receipt.publication_attestation is present:
        return G4 if not verify(record) else G2      # 有记录：验得过才算历史签名，验不过是无效
    if artifact.receipt.claims_host_signed:          # 声称 host_signed 但无记录
        return G4                                    # ← F-I08A-01 的唯一归属（E27）
    if artifact.forecast_schema_version in G1_VERSIONS:   # 仅 {"3.0".."3.6"}
        return G1
    if artifact.forecast_schema_version in {"3.7","3.8"}:  # 当前 + opt-in
        return G3a
    return G4                                        # 未知版本：拒绝
```
`claims_host_signed` 的定义是**精确的**：receipt 存在且 `attestation_status == "host_signed"`。

### 6.2 分类表

| 类别 | 判据 | 允许 | 禁止 |
|---|---|---|---|
| **G1 — 可读不可发布（grandfathered read-only）** | `forecast_schema_version` ∈ **{"3.0","3.1","3.2","3.3","3.4","3.5","3.6"}**（`SUPPORTED_FORECAST_SCHEMA_VERSIONS` 中除当前 3.7 与 opt-in 3.8 之外的集合） | 保留原标签、可复验 hash 链、可作 lineage/标注引用（**E28** `legacy_read_only`） | **不得**升级为 `host_signed`；**不得**穿过要求签名的消费者门新建下游 artifact；**不得**重签 |
| **G2 — 可复验（legacy signed）** | 携带 `publication_attestation`（或旧 L1/L2 签名）**且当刻验签通过** | 按当刻信任域复验；key 被撤销时仍报 `verified_at_publish_time` + `key_now_revoked` | 不得因当时未记录 issuer 就宣称已验签 |
| **G3a — 无签名声明（unattested，保留）** | 当前 schema **3.7** 或 opt-in **3.8**，且 receipt **不含** `attestation_status` 或其为 `"unattested"`（**E26** `attestation_absent`） | 研究结果保留；可被显式降级消费者（`require_attestation=False`）读取，并在输出中记录 `unattested` | **不得**标 `host_signed`；**不得**作为正式可投资来源 |
| **G3b — 声明签名但无记录 → 归 G4** | receipt `attestation_status == "host_signed"` 却**没有** `publication_attestation` 记录（**E27** `attestation_missing_record`） | 无 | **拒绝**。**不得**静默降级为 `unattested`，**不得**进 G3a |
| **G4 — 无效（invalidate）** | G3b；或 `publication_attestation` 存在但签名缺失/伪造/未受信/超窗/绑定不符（E12–E24）；或 `payload_sha256` 与实际 result 不符（E16）；或 schema 版本未知 | 无 | 一律拒绝，且**必须报 §2.5 中的具体错误码**，不得静默降级 |

**关键结论（与卡片动作 5 原文一致）**：既有 unattested 档案**保留研究结果**（G3a），但**不得**升级为 `host_signed`，**不得**穿过要求签名的消费者门。**禁止**「重签伪造历史事件」。**G3b 不是「保留」类**：一个声称 `host_signed` 的包若拿不出签名记录，它唯一可信的读法是「声明为假」，因此必须拒绝。

### 6.3 opt-in schema 3.8 的归属（复审 F-I08A-04）
**冻结归属：3.8 属 G3a（可保留、只读、不得新建下游 artifact），并且 3.8 不获得任何自动旁路。** 需要的门是：3.8 与 3.7 一样必须**同时**通过 **registry 门**与 **attestation 门**（除非消费者显式降级，且降级必须留痕）。

理由（复审已给出、本节确认）：消费者 `invest_contracts.py:1116` 用 `schema_version != FORECAST_SCHEMA_VERSION` 判 `is_legacy`，`:1131-1132` 对该分支**同时跳过 registry 门与 attestation 门**。若把 3.8 判成 G1 式的「旧版本自动只读」，3.8 就继承了**全量旁路**，与「新 schema 不绕过强验证」（关闭标准之一）直接冲突。

**因此新增硬规则 R-LEGACY-1**：
- 消费者的「旧版本豁免」**只允许**由**显式 G1 版本集**（{"3.0"…"3.6"}）触发；**禁止**用 `schema_version != FORECAST_SCHEMA_VERSION` 这种「非当前即豁免」的派生判据。
- 3.8 被当作 G1 自动旁路时 → **E29** `legacy_exemption_not_allowed_for_optin_schema`。
- 3.8 归 G3a 意味着：**版本号本身不决定门**；门由「是否作出签名声明」（§6.1）加「是否在 G1 集合内」共同决定。

修复该消费者判据**属跨仓 scope**（见 §7 scope 外条目），本卡只冻结规则并登记；在跨仓卡完成前，**3.8 的消费者旁路缺口保持 OPEN-D6 状态**（见 §8），不得宣称已闭。

### 6.4 已实测的存量事实（写入 binding/oracle 证据）
- 生产 registry `artifacts/registry/publications.jsonl`：60 行、57 行有 `validation_status`、3 行（第 4/8/12 行，`artifact_type=snapshot`，`note=revenue_backtest create`）无该键 → 这些行**不是 artifact**，属 pre-ZR-701 的**注册行级**旧记录；按 §6.3 的 registry 门处理（保持可读，不得据此推断任何签名声明）。它们**没有 schema/receipt 可言**，因此 §6.1 的 artifact 分类函数不适用于它们。
- registry 行**不含**任何签名/attestation 字段 → **无法从 registry 判定历史发布是否曾签名**（这是设计缺口，I-08-B 必须在注册行加入 attestation 锚，字段名见 §8 UNRESOLVED 登记）。

---

## 7. F01/F02 冻结与最小修改范围（按卡片动作 6）

**现状（已实测，保护性冻结，不得回退）**
1. **验证先于签发**：`run_forecast` 中 `validate_published_forecast(result, data)` 在 `build_publication_receipt` 之前；`build_publication_receipt` 无 `VerificationContext` 直接 `TypeError`（禁止自签收据）。
2. **强验证优先**：`validate_forecast_output(result)` 在有 `input_document` 时走 `validate_published_forecast`（重跑输入门控 gate）；无输入时只能走 `validate_legacy_output` 且**当前 schema 无输入直接拒绝**。
3. **注册失败 fail closed**：`register_publication` 抛 `RegistryError` → `ForecastInputError`，整个发布失败。
4. **单文件原子写有效**：`_atomic_write_text` 用同目录 tmp + fsync + `os.replace`。

**本卡引入的新顺序要求（I-08-B/C 必须实现，I-09-A 消费）**
```
1 解析输入
2 validate_document / validate_published_forecast   (强验证，先)
3 构造 publication 载荷 + payload_sha256
4 调用 provider 取签名 → 验签 → 组装 publication_attestation
5 validate_publication_receipt（含 attestation 验证）
6 registry 追加一行（含 attestation 锚）
7 写 output / markdown
8 步骤 7 失败 ⇒ 必须回滚 6（补偿删除/标记 void），不得留「可消费但无输出」的半发布
```
- **A-D4 冻结要求**：输入无效或 `input_document` 被篡改 ⇒ **provider 调用次数 = 0**、**registry 新增行 = 0**、**无输出文件**。
- **当前 A-D4 的 output 失败分支**：现状实测 `registry_entries_added = 1` 且 `output_exists = false`（audit 反例）→ 属 I-09-A 的事务边界，本卡**只冻结顺序要求**，不实现。
- **最小修改范围（本卡冻结，不得扩大）**：
  - `scripts/contracts/evidence.py`：信任域加载（issuer/key_id/时间窗/status/environment）、`publication_attestation` 载荷与验签 helper。
  - `scripts/revenue_core.py`：`attestation_capability()` 语义（成功握手而非存在性）、`run_forecast` 中 L3 签名步骤与错误码。
  - `scripts/revenue_publication.py`：receipt 增加 `publication_attestation` 子对象 + schema 版本（**必须**升级 `PUBLICATION_RECEIPT_SCHEMA_VERSION`，见 OPEN-D4）、`validate_publication_receipt` 增加 G3b/G4 拒绝（E27 及 E12–E24）。
  - `scripts/publication_registry.py`：注册行增加 attestation 锚（**追加键，旧行保持可读**）。
  - `tests/test_attestation.py` + 新增 provider 协议测试：本卡负例的落地位置（含 §7.1 的假绿前置）。
- **scope 外（由 owner 另开卡，本卡只登记）**：
  - invest-core `adapt_revenue` 的 `is_legacy` 全量旁路（`:1116-1127`）与 issuer 实体校验 → 跨仓消费者卡。**这是 §6.3 规则 R-LEGACY-1 与 E29 的落地位置**；在该卡完成前，3.8 的消费者旁路缺口保持 **OPEN-D6**，不得宣称已闭。
  - registry 先写后写 output 的补偿/事务 → I-09-A。
  - `company_wiki_source.py` / `filing_fetch_client.py` 侧 L1/L2 收据的 issuer/环境绑定 → 对应仓 owner 卡。

### 7.1 I-08-B 的验收前置：先失败，再改（复审 F-I08A-06，须转给 I-08-B）

**已确认的假绿源**：`tests/test_attestation.py:71` 是**全仓唯一**设置 `REVENUE_ATTESTATION_PROVIDER` 的地方，它把 provider 设为 `sys.executable`，并断言 `result["publication_receipt"]["attestation_status"] == "host_signed"`（`test_configured_provider_means_host_signed_publication`；同一文件 `:68` 的 `assertTrue(attestation_capability())` 同理）。

**冻结的验收前置（I-08-B 必须逐条满足，否则视为假绿）**：
1. 在**新语义落地之前**，先用**同一断言、同一输入**证明该用例变 **RED**：provider 指向 `sys.executable` 时 `attestation_capability()` 必须为 `False`，`attestation_status` 必须为 `"unattested"`，且失败码为 **E32**（`provider_capability_unproven`）。该 RED 必须留原始 stdout/rc 作为证据。
   - **r3 修正（复审 R-BIND-2）**：初稿此处引用 **E02**，但 `sys.executable` 是一个**存在且可执行**的文件，按 E02 的旧定义（"不存在或不是可执行文件"）它**永远落不到 E02**，该前置条款因此不可达。r3 把「存在但未被证明具备签名能力」独立为 **E32**，本前置改为引用 **E32**，并使 E02 收窄为「路径不存在或不可作为文件打开」。两个码的分工见 §2.5 与 §2.4。
2. **不得**直接改写该断言来让它变绿；必须改写**测试意图**：把「配置了 providers」改为「bound provider 完成了一次成功握手」——即在隔离目录内起一个 bounded fake provider，用**隔离的**信任域（`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` 指向 attempt 内路径）签发，再断言 `host_signed`（遵循 R-PROV-2；**MUST NOT** 把测试 key 写进仓库 `config/`）。
3. 新增一条**反向**用例，并按下表**分别**断言可达的码（r3：三类不再并成一类）：

| 输入 | 可达失败码 |
|---|---|
| 变量未设置 | **E01** `provider_absent` |
| 路径不存在 / 不可作为文件打开 | **E02** `provider_path_unopenable` |
| `sys.executable`（存在且可执行，但无协议响应） | **E32** `provider_capability_unproven` |
| 裸 `.py` 源文件 | **E32** |
| 普通 `.txt` 文件 | **E32** |
| 可执行但协议不合规 | **E03** / **E04** / **E08**（视具体违规） |

   所有情形都必须满足「不得 `host_signed`」且「不得以读取/执行/import 该文件作为能力依据」（`provider_file_read_bytes` 只能为 0 或 null，`provider_calls` 只能为 0）。
4. 每条用例的 raw rc 与 stdout 都要进入 I-08-B 的证据目录；只报「全部通过」不算。

**本卡不修改该文件**（设计卡不实施产品），只把上述前置写成 I-08-B 的准入条件。

---

## 8. OPEN 决策（须 owner / 人裁决，弱模型不得自定）

- **OPEN-D1（权威信任根）**：production 信任域文件的权威位置与签署人。候选：(a) 仓库内 `config/trusted_signer_public_keys.json`（现默认路径，但**当前不存在**）；(b) 机器级只读路径（`%PROGRAMDATA%` 风格），避免仓库可写者改信任域；(c) OS keystore/TPM。
  - 后果：(a) 最简单，但「能改仓库即可换信任根」；(b) 隔离性更好，需运维落地；(c) 最强，需平台支持且不可移植。
  - **本卡不选**。在裁决前，默认行为必须是**零受信 signer = 全部拒绝**（现状已如此，继续保持）。
- **OPEN-D2（私钥归属与 operator 身份）**：谁能持有 L3 私钥、是否允许一人多 key、是否需要双人复核。影响 issuer 命名与轮换流程。
- **OPEN-D3（撤销是否回溯）**：key 被撤销时，撤销前已发布的 artifact 是「仍可复验（标注撤销）」还是「一律作废」。本卡**默认**取前者（不回溯），但需 owner 确认；若改取后者，必须同时提供历史重签之外的替代证明路径，否则等于批量作废历史证据。
- **OPEN-D4（receipt schema 版本）**：新增 `publication_attestation` 子对象是否升 `PUBLICATION_RECEIPT_SCHEMA_VERSION` 到 `"2.0"`（推荐）还是保持 `"1.0"` 加可选键。
  - 影响：升版 → 旧 receipt 明确落在 G1/G3；保持 1.0 → 消费者必须容忍缺字段，且「无 attestation 的 1.0 receipt」与「有 attestation 的 1.0 receipt」将无法用版本区分，削弱 G3/G4 判据。
- **OPEN-D5（是否允许 `require_attestation=False`）**：消费者降级开关是否保留、由谁授权、是否必须写入 artifact 痕迹。现状存在该开关（`invest_contracts.py:1070-1071`），本卡不改。
- **OPEN-D6（谁来实现 3.8 的消费者门；编号在本表内稳定，不受 §6.3 标题影响）**：§6.3（标题为「opt-in schema 3.8 的归属」）已**冻结规则**（3.8 属 G3a；旧版本豁免只允许由显式 G1 版本集触发；违反 = E29），但规则落地需要改**跨仓**消费者 `invest_contracts.py:1116-1127`，这超出本卡 scope。选项：
  - (a) 由 owner 新开一张跨仓消费者卡落地 R-LEGACY-1 与 E29（推荐）；
  - (b) 由 I-08-B 在同仓内提供一个「消费者应使用的判据函数/常量」，跨仓卡再接线；
  - (c) 在跨仓卡完成前，把 3.8 的消费者路径**视为已知旁路**并在交付说明中显式标注。
  - **不论选哪项，都不得声称该缺口已闭。** 本卡在 §6.3 与 §7 scope 外条目中登记它。
  - **建议归属（复审意见，r3 采纳）**：**计划 owner 裁定并开卡**。
- **OPEN-D7（三个数值参数待证据）**：r2 登记 `W`/`T`；**r3 把输出上限 `L` 并入同一决策**（复审 N-R2-04 指出 65536 仍硬编码在多处，与「数值已撤下」矛盾）。
  - `W` = 发布窗长度（`expires_at - issued_at` 的上限，E18 的判据）；
  - `T` = provider 调用超时上限（E07 的判据）；
  - `L` = provider stdout 上限（E06 的判据）。
  - 现状证据：复审 grep 产品 `scripts/` 确认 `expires_at`/`issued_at`/`not_before`/`not_after`/`validity` **零命中**，`900` 只命中取件超时；本卡也没有任何实测能支持某个具体秒数或字节数。**初稿的「900 s 上限」「10 s / 上限 60 s」「65536 bytes」都是执行者自选值，已从规范位置全部撤下**，只保留语义与失败码。
  - 候选依据（须由 owner 选一并留证）：(a) 以「一次发布流水线的实测 P99 时长 / provider 输出实测 P99 字节数」定 `W` 与 `L`，`T` 取同批实测上界；(b) 以攻击面论证（预签凭证可被挪用的最大时间窗；provider 响应的合法最大体积）定 `W`/`L`；(c) 先取**宽松**默认并在 I-08-B 的 provider 协议测试里实测后再收紧。
  - 在 OPEN-D7 裁决前：实现者**不得**把任何具体秒数或字节数写成硬性规范值，也**不得**宣称「provider 协议无未决」。
  - **建议归属（复审意见，r3 采纳）**：**owner 选依据口径 + 实现方供实测数据**。

### 8.0 OPEN 归属与批次建议（复审意见，r3 采纳并固化）

| OPEN | 建议裁决方 | 备注 |
|---|---|---|
| D1 权威信任根 | **项目 owner 决选** + 安全/运维出方案 | 与 D2/D3 **建议同批裁定**，以免 I-08-B 返工 |
| D2 私钥归属/operator 身份 | **项目 owner 政策裁定** | 同上，同批 |
| D3 撤销是否回溯 | **项目 owner 裁定** + 独立安全 reviewer 复核 | 同上，同批 |
| D4 receipt schema 是否升 2.0 | **可由 revenue publication owner 自决** | 不需上级裁定；决定须写入 decision 修订 |
| D5 降级开关 `require_attestation=False` | **invest-core 消费者 owner + revenue publication owner 联席** | 跨仓，须双方签字 |
| D6 3.8 消费者门由谁落地 | **计划 owner 裁定并开卡** | 在跨仓卡完成前该旁路缺口保持 OPEN |
| D7 `W`/`T`/`L` 三个数值参数 | **owner 选依据口径 + 实现方供实测数据** | 参数值与依据一并留证 |

**批次约束**：D1/D2/D3 **建议同批裁定**——三者共同决定 issuer 命名、轮换与撤销语义，分批裁定会使 I-08-B 的信任域实现返工。

---

## 8.1 修订记录（r2，回应独立复审 changes_required）

| 复审条目 | 处置位置（本文件） |
|---|---|
| F-I08A-01 G3/G4 相反 | §6.0 说明；§6.1 单一分类判据；§6.2 G3a/G3b/G4；E26/E27 |
| F-I08A-02 错误码不相交 | 新增 §2.5 规范错误码表（E01–E31，唯一来源）；§2.4 改为引用；§4.2/§5/§6.2 引用码值 |
| F-I08A-03 900 s 无依据 | §2.2 参数化 `W`；§2.4 参数化 `T`；§5 `expires_at` 行；§8 OPEN-D7 |
| F-I08A-04 schema 3.8 未归类 | §6.3（归属 G3a + 规则 R-LEGACY-1 + E29）；§7 scope 外条目；§8 OPEN-D6 |
| F-I08A-05 信任域键名冲突 | §3 键名冻结为 `public_keys` + 加载语义 fail loud + E25；负例 NEG-TRUST-4 |
| F-I08A-06 test_attestation 假绿 | §7.1（I-08-B 验收前置：先 RED 再改意图） |
| F-I08A-07 probe 依赖生产 tests fixture | §11「复现与依赖」 |
| F-I08A-08 c3 绑定 argv 与重定向方式不一 | §11「复现与依赖」 |
| F-I08A-09 oracle `read_bytes==0` 措辞 | 由 `oracle.md` 修订；本文件 §2.5 E02/E32 备注同措辞 |

---

## 8.2 修订记录（r3，回应独立复审定点复核 changes_required）

| 复审条目 | 处置位置（本文件） |
|---|---|
| **R-BIND-1** `revoked_at` 未在字段清单 ⇒ 按 §3 撤销条款写必被 E25 拒 | §3 示例条目加入 `revoked_at: null`；§3 字段集改为**点名式 12 字段**（10 无条件必填 + `name` 可选 + `revoked_at` 条件语义）+ 条件约束（active ⇒ null，revoked ⇒ RFC3339 且 ≥ `not_before`）；§3「撤销」条款改写为与字段集一致的两条件表述（不新增字段）。**计数以点名字段集为准，不再以数字计数为准** |
| **R-BIND-2** E02 不可达（`sys.executable` 可执行） | §2.5：**E02 收窄**为 `provider_path_unopenable`（路径不存在/不可作为文件打开）；**新增 E32** `provider_capability_unproven`（存在且可打开但未被证明具备签名能力，含 `sys.executable`/裸 `.py`/`.txt`）；§2.4 末两行改写；§7.1 前置 1 改为引用 **E32**，前置 3 换成分情形断言表 |
| **N-R2-04** 65536 仍硬编码 | §2.5 新增参数 **`L`**（E06 判据）并入 OPEN-D7；§2.4 行改为 `L`；§2.5 E06 行改为 `L`；§10 第 2 项改为 `L` |
| **N-R2-05/06/07** | OPEN-D6 命名借位：§2.5 E29 行改指「§6.3」而非「§6」；OPEN-D6 表内加编号稳定说明；新增 §8.0 OPEN 归属与批次表（含 D1/D2/D3 同批建议）。`oracle.md` §1 旧措辞由该文件修订；`review.md` 重复的「6.」列表项由该文件修订 |
| **限制声明（复审实测）** | `check_r2_consistency.py` 的能力边界写入 `review.md` §5.1/§5.3 与 `commands.json` I08A-c10 的 `capability_limit`；新增独立配对校验 `check_r3_pairs.py`（校验 §2.5 编号↔码值 与 NEG 行 编号↔§2.5 码值 的一致性），并以**变异自测**证明它能检出复审的两处变异 |

---

## 9. 拒绝的替代方案（为什么不是「按最佳实践」）

| 替代方案 | 拒绝理由 |
|---|---|
| 保留 `attestation_capability()` 的存在性判断，只在文档里写「provider 应当签名」 | A-D1 已证明它可被普通 `.py` 文件满足并产出 `host_signed`；文档约束不能证伪 |
| provider 作为常驻服务 / HTTP 端点 | 扩大攻击面、需新网络服务（本卡明确禁止），且弱模型无法验证其隔离性 |
| 把签名私钥放进仓库或测试 fixture 供 CI 使用 | 直接违反「测试私钥被当生产信任」失败停止条件；且使信任域等于仓库可写性 |
| 让 provider 自报信任域 / 自签自信任 | 信任域必须由 host 侧解析；否则 provider 换 key 即可自证 |
| 用「文件存在 + 内容 hash」代替签名 | 不能证明**谁**在**何时**为**哪份载荷**背书；对本地文件系统攻击者零成本 |
| 签名对象取「pretty JSON 文本」或整份文件字节 | 序列化不确定（键序/空白/换行），同一逻辑载荷产生多份有效签名，无法绑定 |
| 让 `expires_at` 作用于「验证时刻」 | 会让历史证据在过期日集体失效，直接违反「同一 immutable artifact 重复读取不应失效」 |
| 让 `request_id` 成为一次性令牌并参与复验 | 同上；且会把幂等重跑变成伪造失败 |
| 把旧 schema（≤3.6）整批拒绝 | 破坏 `SUPPORTED_FORECAST_SCHEMA_VERSIONS` 既有只读兼容与 lineage；卡片只要求「不得升级、不得穿过签名门」 |
| 给历史 unsigned 档案补签 | 伪造历史事件；且新签名无法证明旧 raw 的可信取得 |
| 让「声称 host_signed 但无签名记录」的包落进 G3a（保留） | 等于把一句无法兑现的声明当作「只是没签名」；G3a 的前提是**不作声明**。二者必须分开（F-I08A-01） |
| 沿用顶层 `"keys"` 键并同时兼容 `"public_keys"` | 双键并存使「改了信任域却没生效」仍可能发生；冻结唯一键名 + 非法即报错（E25）才能让失败可观测（F-I08A-05） |
| 信任域解析失败时静默返回空集 | 使「配置坏了」与「本来就没有配置」不可区分，运维与 reviewer 都无法判定一次 `not trusted` 的性质（F-I08A-05） |
| 用 `schema_version != FORECAST_SCHEMA_VERSION` 判旧版本豁免 | 会把 opt-in 3.8 一并放成全量旁路，与新 schema 不绕过强验证冲突（F-I08A-04）；豁免必须由显式 G1 版本集触发 |
| 把 `W`／`T` 的初稿数值继续写成硬性规范 | 复审已确认产品内零命中、本卡零实测；无依据的数值写成规范值会制造「已定案」的假象（F-I08A-03） |

---

## 10. 交付给 I-08-B/C 的实现清单（可验收）

1. 信任域加载器（键名冻结为 `public_keys`、精确 schema、文件非法 = **E25 报错**而非静默空集、test 环境 key 在正式路径 E24 拒绝）。
2. provider 客户端（stdin/stdout、超时 `T`、输出上限 `L`、非 0 退出、精确字段集、echo 逐字节比对），失败码一律取自 §2.5；`T`/`L` 取值待 OPEN-D7 裁决，实现方须提供实测数据。
3. `publication_attestation` 载荷构造 + Ed25519 验签（复用 §4.3 message 规则）。
4. `attestation_capability()` 改为「成功握手」语义；`run_forecast` 只在 L3 验签通过时写 `host_signed`。
5. `validate_publication_receipt` 增加 §6.1 的 G3b/G4 判据（E27）与其余码值。
6. registry 注册行追加 attestation 锚（追加键，旧行可读）。
7. 顺序：验证 → 签名 → 注册 → 写输出（+ I-09-A 的补偿）。
8. 负例测试：`oracle.md` 的 NEG-* 全部落地为独立可失败的测试；**先满足 §7.1 的 RED 前置**。
9. 消费者侧：落地 §6.3 规则 R-LEGACY-1 与 E29（跨仓，见 OPEN-D6）。
10. **不得**改动：生产 registry 文件、生产密钥/名单、历史 artifact、`PLAN/reviews/**`。

---

## 11. 本卡未做 / 未验证

- 未实现上述任何一条（设计卡）；`iso/` 内只有**只读行为探针**，不修改任何产品代码。
- 未运行真实 provider、未做网络调用、未发布任何 artifact、未写生产 registry。
- 未裁决 §8 的 OPEN-D1—D7。
- 未验证跨仓消费者（invest-core）修改的影响面；本卡只登记 scope 外入口。
- 本卡的独立验证结论在 `review.md` 的 **PENDING independent review** 段落之外，尚未由独立 reviewer 出具。
- **未授予的资格（复审明确）**：provider 协议与信任域**不是「无未决」**（OPEN-D6/D7 尚未裁决）；签名范围与旧包兼容**不是「已定案」**（3.8 消费者门待跨仓卡，E25/E29 未实现）。

### 11.1 复现与依赖（复审 F-I08A-07 / F-I08A-08）

**F-I08A-07 — 探针依赖未被绑定的生产 fixture。** `iso/probe_attestation.py` 通过 `sys.path.insert(0, <生产>/tests)` 导入 `test_recognition_bridge.forecast_document` 生成合成输入，而 `binding.json.input_hashes` **没有**登记该文件的哈希，因此「重跑得到同样结果」依赖一个未绑定路径。处置（本轮不重跑，只补绑定与声明）：
- 已在 `binding.json` 追加 `RF/tests/test_recognition_bridge.py` 的 sha256 与 `fixture_symbol=test_recognition_bridge.forecast_document`，并标注它是**合成 fixture**（非真实公司披露）。
- reviewer 复跑前必须先核对该哈希；若不一致，按 START_HERE 漂移分支停止复跑并记录差异，**不得**用新 fixture 结果替换旧证据。
- I-08-B 若继续使用该 fixture，必须把「fixture 文件 hash + 函数名 + 是否合成」写进自己的 binding；**MUST NOT** 让新卡继承本卡的未绑定依赖。

**F-I08A-08 — c3 的绑定 argv 与实际重定向方式不同一。** `commands.json` 的 `I08A-c3-probe` 把解释器路径写成 `<attempt>/iso/venv/Scripts/python.exe`、脚本写成相对名 `probe_attestation.py`，而实际记录到的 raw stdout 来自 `run_c3.py` 用**文件句柄**启动的子进程，其 argv 是**绝对路径**形式（`[…\iso\venv\Scripts\python.exe, -X, utf8, -B, …\iso\probe_attestation.py]`），因为 PowerShell 的文本管道重定向会用 UTF-16 破坏非 ASCII 路径（见 `review.md` 第 4 节第 2 条）。处置：`commands.json` 的该条已补 `argv_as_recorded`（实际绝对路径 argv）与 `argv_frozen_as`（初稿相对形式）两栏，并说明二者**语义等价、仅路径形式与重定向通道不同**；reviewer 用任一形式复跑都应得到相同不变量（§`review.md` 的 I08A-c9 已给出不变量清单）。**不重写** raw 证据，也不把不一致藏起来。

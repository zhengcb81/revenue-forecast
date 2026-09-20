# I-08-A oracle — 运行前冻结的独立预期

- attempt: `a20260919-01`
- 冻结时刻: 在任何 harness 运行**之前**写定（见 `commands.json` 的 `frozen_before_run: true`）。
- 目的: (a) 固定本卡必须交给 I-08-B/C 的负例语义；(b) 用**只读行为探针**取得现状基线，证明缺口真实存在而**不是**靠存在性断言。
- 读取顺序要求（reviewer）: 先看 `binding.json` 源 hash → 本 oracle → `commands.json` 的 raw rc → `after/` 原始输出 → 再看结论。
- **不得**为了让某项通过而放松任何断言；若现状与预期不符，保留 raw 输出并记为差异。

---

## 0. 探针范围声明（为什么这不是「跑产品」）

`iso/probe_attestation.py` 只做三件事：
1. 以只读方式 `import` **复制到 `iso/rf/scripts/` 的产品模块**（sha256 与生产一致，见 `binding.json`）；
2. 在 attempt 隔离目录内构造**合成**输入与**合成**测试密钥（绝不进入仓库 `config/`、绝不写生产 registry）；
3. 观测并打印现状函数的行为。

**允许的副作用白名单**：`iso/scratch/**`（含隔离 registry、隔离信任域 json、合成 provider 脚本）。
**禁止**：写 `revenue-forecast/scripts/**`、`config/**`、`artifacts/registry/**`、`.planning/reviews/**`、任何网络调用。

`cwd` 冻结为 `iso/`，argv 冻结为隔离 venv 解释器（见 `commands.json`）。`PYTHONDONTWRITEBYTECODE=1` 防止在复制树里产生 `__pycache__`。

---

## 1. 现状基线探针（EXP-BASE-*）

这些是**观测**而非「要求现状通过」的断言；目的是给独立 reviewer 一份不可辩驳的当前行为记录。

| id | 输入 | 冻结预期（现状） | 若不符 |
|---|---|---|---|
| EXP-BASE-1 | `REVENUE_ATTESTATION_PROVIDER` 未设置 | `attestation_capability()` 返回 `False` | 记录差异，暂停本卡结论 |
| EXP-BASE-2 | provider = `sys.executable`（一个真实存在、与签名毫无关系的**可执行**文件） | `attestation_capability()` 返回 `True`；**未发生任何 provider 调用**（`provider_calls == 0`、`spawn_witness_calls == []`）；`provider_file_read_bytes` 为 `null`（该路径不被读取） | 同上 |
| EXP-BASE-3 | provider = 本探针自身 `.py` 源文件路径 | `attestation_capability()` 返回 `True` | 同上 |
| EXP-BASE-4 | provider = 不存在的路径 | `False` | 同上 |
| EXP-BASE-5 | provider = 存在但不可信的普通文件（非可执行 `.txt`） | `attestation_capability()` 返回 `True`（**存在性即充分**）→ 这就是 A-D1 的机制 | 同上 |
| EXP-BASE-6 | 默认信任域文件 `config/trusted_signer_public_keys.json` | **不存在** → `_trusted_signer_public_keys() == {}` → 任何签名一律 `not trusted` | 同上 |
| EXP-BASE-7 | 未签名 host receipt（`build_host_receipt` 产物） | `validate_host_receipt` **通过**（`signature_present = False`） | 同上 |
| EXP-BASE-8 | 生产 registry `artifacts/registry/publications.jsonl` | 60 行；57 行含 `validation_status`；3 行（4/8/12）不含；**任一行都不含** `attestation`/`signature` 键 | 同上 |
| EXP-BASE-9 | 现有验签能力（白名单内 key 正确签名） | `validate_host_receipt` **通过** → **不得**声称「验签不存在」 | 同上 |
| EXP-BASE-10 | 伪造签名（攻击者 key 签名、受害者 key 在白名单） | `ForecastInputError`，消息含 `not trusted` | 同上 |

**A-D1 的现状判定（冻结）**：EXP-BASE-2/3/5 三者合起来 = 「普通文件存在 ⇒ `host_signed` 标签可得」。因此 **A-D1 现状为 RED（缺口成立）**。I-08-B 修好后的**目标判定**：A-D1 的三条输入全部不得产出 `host_signed`；必须失败（**E32** `provider_capability_unproven`）或明确 `unattested`，且**仍不得调用**该文件。

> **r3 修正（复审 R-BIND-2）**：本条原引用 **E02**。但 `sys.executable` 是**存在且可执行**的文件，而 E02 在 r3 已收窄为「路径不存在或不可作为文件打开」，因此 `sys.executable` 归 **E32**「存在但未被证明具备签名能力」。可判定分类见 `decision.md` §2.5（E01/E02/E32）与 §2.4 末两行。

---

## 2. 治理负例（NEG-*）— I-08-B/C 必须实现的独立可失败用例

每条格式：`注入 → 必须的拒绝/降级 → 精确错误码 → 持久化后果`。
「拒绝」= 抛 `ForecastInputError`（或 I-08-B 定义的同等 fail-closed 异常）且**不产生** `host_signed` 收据、**不新增** registry 行、**不写** output。

**错误码唯一来源（复审 F-I08A-02）**：下表第 4 列的码值**全部取自 `decision.md` §2.5「规范错误码表」**，本文件不另立、不合并码值。若某行需要的码不在 §2.5，先加进 §2.5 再回来引用。下表的 `E` 编号即 §2.5 的编号。

| id | 注入点 | 冻结预期 | 错误码（= decision.md §2.5） |
|---|---|---|---|
| NEG-PROV-1 | `REVENUE_ATTESTATION_PROVIDER` = 存在且可打开的路径，但未被证明具备签名能力：裸 `.py` 源文件、普通 `.txt`、或 `sys.executable` 这类存在且可执行却没有协议响应的路径 | 不 `host_signed`；不得执行/import/读取该文件（`provider_file_read_bytes` 只能为 0 或 null，`provider_calls` 必须为 0）；无签名 | **E32** `provider_capability_unproven` |
| NEG-PROV-1a | `REVENUE_ATTESTATION_PROVIDER` = **不存在**的路径 | 不 `host_signed`；不得尝试其它回退路径 | **E02** `provider_path_unopenable` |
| NEG-PROV-1b | `REVENUE_ATTESTATION_PROVIDER` = 存在但**不可作为文件打开**（如目录路径、权限拒绝） | 不 `host_signed` | **E02** `provider_path_unopenable` |
| NEG-PROV-2 | provider 可执行但无协议响应（不读 stdin / 输出非单个 JSON 对象） | 不 `host_signed` | **E03** `provider_protocol_violation` |
| NEG-PROV-2b | provider 有输出但不是合法 JSON | 不 `host_signed`；不得尝试「尽力解析」 | **E04** `provider_invalid_json` |
| NEG-PROV-3 | provider 退出码非 0 | 不 `host_signed` | **E05** `provider_exit_nonzero` |
| NEG-PROV-4 | provider 输出 > `L` bytes（`L` 见 OPEN-D7；r3 已参数化，初稿 65536 撤下） | 不 `host_signed`；**不得**解析被截断的前缀 | **E06** `provider_output_too_large` |
| NEG-PROV-5 | provider 超时（> `T`，`T` 见 OPEN-D7） | 不 `host_signed`；子进程必须被终止（无遗留进程） | **E07** `provider_timeout` |
| NEG-PROV-6 | provider 返回字段集多一个/少一个键（含类型错） | 不 `host_signed` | **E08** `provider_schema_mismatch` |
| NEG-PROV-7 | provider 缺私钥/无法签名（明确报错） | 不 `host_signed`；保留 `unattested` + 失败原因 | **E10** `provider_signing_unavailable` |
| NEG-PROV-8 | `REVENUE_ATTESTATION_PROVIDER` 未设置 | 不 `host_signed`；落 G3a | **E01** `provider_absent` |
| NEG-SIG-1 | 合法受信 key 签名正确载荷 | **通过**（正例，必须成功） | — |
| NEG-SIG-2 | 无签名字段 | 不 `host_signed` | **E12** `attestation_missing_signature` |
| NEG-SIG-3 | 签名长度/字符集非法（如 127 hex、大写 hex、非 hex） | 拒绝 | **E13** `attestation_malformed_signature` |
| NEG-SIG-4 | 攻击者 key 签名 + 攻击者自己的 fingerprint | 拒绝 | **E20** `provider_key_untrusted` |
| NEG-SIG-5 | 信任域**文件缺失**（含默认路径不存在） | 一律拒绝（合法零受信 key，现状已如此，**不得放松**） | **E20** `provider_key_untrusted` |
| NEG-SIG-6 | 正确签名但载荷被改（改 `event_sha256` 后重算自报 hash） | 拒绝 | **E14** `attestation_signature_invalid` |
| NEG-SIG-7 | 正确签名 + 只改 `issuer`（fingerprint 与 key 不变） | 拒绝（issuer 必须绑定 key 声明） | **E21** `issuer_key_binding_mismatch` |
| NEG-SIG-8 | 正确签名 + `signed_at` 超出 key 的 `not_before`/`not_after` | 拒绝 | **E22** `key_outside_validity_window` |
| NEG-SIG-9 | 信任域中 `status = "revoked"` 的 key 签名 | 拒绝（未来发布） | **E23** `key_revoked` |
| NEG-SIG-10 | 信任域中 `environment = "test"` 的 key 走正式发布路径 | 拒绝 | **E24** `test_key_in_production_trust_domain` |
| NEG-SIG-11 | 截断载荷（`payload_sha256` 只覆盖前缀 / 缺尾字段） | 拒绝（载荷字段集必须精确匹配，不得「按已有字段签」） | **E15** `attestation_payload_fields` |
| NEG-SIG-12 | 载荷 hash ≠ 实际 result 重算值 | 拒绝 | **E16** `attestation_payload_hash_mismatch` |
| NEG-SIG-13 | 载荷内版本字段（engine/schema/receipt/validator）与当刻运行时值不等 | 拒绝 | **E11** `provider_version_mismatch` |
| NEG-TRUST-1 | 信任域文件存在但 JSON 不可解析 | **报错并中止发布**（**不得**静默返回空集） | **E25** `trust_domain_schema_error` |
| NEG-TRUST-2 | 信任域顶层键名不符（例如用 `"keys"` 代替 `"public_keys"`） | **报错**（不得被当作 0 个受信 key） | **E25** |
| NEG-TRUST-3 | 条目缺 `issuer`/`key_id`/`not_before`/`not_after`/`status`/`environment`，或 `public_key` 非 32 B、`fingerprint` 非 32 hex | **报错** | **E25** |
| NEG-TRUST-4 | 文件缺失 vs 文件非法必须可区分 | 缺失 → 合法零受信（E20 路径）；非法 → **E25 报错**。二者**不得**输出同一个结果 | **E25** |
| NEG-REPLAY-1 | 同一签名整体复制到**不同 `input_sha256`** | 原件通过、变异拒绝 | **E09** `provider_binding_mismatch`（echo 不符）/ **E16** |
| NEG-REPLAY-2 | 同一签名换**不同 `result_sha256`** | 拒绝 | **E09** / **E16** |
| NEG-REPLAY-3 | 同一签名换**不同 schema 版本**（3.7 → 3.6） | 拒绝 | **E11** `provider_version_mismatch` |
| NEG-REPLAY-4 | 同一签名换**不同 issuer** | 拒绝 | **E21** `issuer_key_binding_mismatch` |
| NEG-REPLAY-5 | 同一签名换**不同 domain separator**（跨服务重放） | 拒绝 | **E17** `attestation_domain_mismatch` |
| NEG-REPLAY-6 | 同一 `request_id` 第二次用于**不同** `payload_sha256` | 拒绝新发布 | **E19** `request_id_reuse` |
| NEG-REPLAY-7 | **历史复验**：同一 `payload_sha256` 的 immutable artifact 反复验证（含 `expires_at` 之后） | **必须始终通过**；仅可附加 `expired_now` 标记 | —（**不得**失败） |
| NEG-REPLAY-8 | 发布时 `issued_at > signed_at`、`signed_at > expires_at`，或 `signed_at - issued_at > W` | 拒绝（预签空白凭证）。**`W` 是参数**，取值见 OPEN-D7；本卡不冻结具体秒数 | **E18** `attestation_expired_at_publish` |
| NEG-REPLAY-9 | 同 payload 且所有已签字段完全相同（同输入/同 result/同版本/同 gate 集） | **允许**复用，记为同一物件第二次自证，不产生新的历史事件 | —（正例） |
| NEG-LEGACY-1 | 历史 unsigned source receipt + 新 publication 签名 | 新发布可以 `host_signed`；**但** `source_receipts[*].signature_present` 必须仍为 `false`，**不得**写任何「原 capture 已受信签名」字段 | —（不得出现升级字段） |
| NEG-LEGACY-2 | schema ∈ {"3.0"…"3.6"} 旧包（**G1**）走消费者正式门 | 只读兼容（lineage/标注），**不得**新建下游 artifact、**不得**获得 `host_signed` | **E28** `legacy_read_only`（沿用 `invest_contracts.py:1120/1132` 既有词表） |
| NEG-LEGACY-3 | 当前 schema（3.7 或 opt-in 3.8）**不作签名声明**（`attestation_status` 缺失或为 `unattested`）→ **G3a** | 研究结果保留（只读、不得新建下游 artifact），**不得**升级为 `host_signed` | **E26** `attestation_absent` |
| NEG-LEGACY-4 | 声称 `host_signed` 但无 `publication_attestation` 对象 → **G3b，归 G4** | **拒绝**，不得静默降级为 unattested，**不得**落进 G3a | **E27** `attestation_missing_record` |
| NEG-LEGACY-5 | `publication_attestation` 存在但 `payload_sha256` ≠ 实际 result 重算 | 拒绝 | **E16** `attestation_payload_hash_mismatch` |
| NEG-LEGACY-6 | opt-in 3.8 被消费者当作 G1 自动豁免（用 `schema_version != FORECAST_SCHEMA_VERSION` 判旧版本） | **拒绝**；3.8 属 G3a 且必须过 registry + attestation 双门（规则 R-LEGACY-1） | **E29** `legacy_exemption_not_allowed_for_optin_schema` |
| NEG-TX-1 | 输入无效（缺必填字段） | 抛出输入错误；**provider 调用 = 0**；**registry 新增 = 0** | 输入契约错误（现有 `ForecastInputError`） |
| NEG-TX-2 | 篡改 `input_document`（与 `input_sha256` 不符） | 拒绝；**provider 调用 = 0**；**registry 新增 = 0** | **E30** `input_binding_mismatch`（现状消息 `input binding mismatch: …` 原样保留） |
| NEG-TX-3 | 输入与签名均合法，但 output 写失败 | **必须**不留下「registry 有行而 output 不存在」的可消费半发布（回滚步骤 6） | **E31** `publication_rollback_required` |


**注**：NEG-TX-3 的**实现**属 I-09-A（事务边界）。I-08-A 只冻结「顺序要求 + 不得留下半发布」这条契约，并在 `decision.md §7` 记录现状为 **RED**（实测 `registry_entries_added=1, output_exists=false`）。

---

## 3. 卡片反例 A-D1—A-D4 的固定消费者预期（关闭标准要求）

| case | 固定消费者预期（I-08-B/C 实现后必须成立，且必须可独立复算） |
|---|---|
| **A-D1** | provider 指向「任意存在 `.py`」或 `sys.executable` 且无协议响应 ⇒ **不得** `host_signed`，失败码 **E32**（`provider_capability_unproven`；路径不存在时才用 **E02**）。判定不得依赖存在性；不得读取/执行/import 该文件（`provider_file_read_bytes` 只能为 0 或 null、`provider_calls` 必须为 0、无子进程）。 |
| **A-D2** | 合法受信 key 签名正确载荷 ⇒ 原件 `verify` 通过；同一签名复制到不同 `input_sha256` / `result_sha256` / `schema_version` / `issuer` ⇒ **全部**拒绝（**E09/E11/E16/E21**）；**同一 immutable artifact 的历史重复验证必须通过**（不得因「签名已用过」失败）。 |
| **A-D3** | unsigned 旧 source receipt + 新 publication 签名 ⇒ 新发布可 `host_signed`，但**不得**声称原 capture 具备先前不存在的可信签名；`signature_present` 保持 `false`，信任范围在输出中显式受限。 |
| **A-D4** | 输入无效或 `input_document` 被篡改 ⇒ provider 调用 **0** 次、registry 新增 **0** 行（失败码 **E30**）；F01/F02 已修顺序（强验证先于签发/登记）保持。 |

---

## 4. 现状 RED/GREEN 冻结表（供 reviewer 对照 raw 输出）

> **r2 修订说明**：§1–§3 与本节中所有「必须/不得」的**码值**都指向 `decision.md` §2.5；本节不引入新码。F-I08A-01 的分类矛盾已在 `decision.md` §6 拆为 G3a/G3b 并在本文件 NEG-LEGACY-3/4 对齐。

| 命题 | 冻结判定 | 依据 |
|---|---|---|
| `host_signed` 不需要任何签名即可获得 | **RED（缺口成立）** | EXP-BASE-2/3/5 + A-D1 |
| provider 协议从未被调用（无调用点） | **RED（缺口成立）** | `build_host_receipt` 仅 re-export；EXP-BASE-2 观测 `provider_calls == 0` |
| publication receipt 与签名无绑定（无 issuer/key/签名域） | **RED（缺口成立）** | receipt 键集实测无签名域 |
| registry 无法证明历史发布是否曾签名 | **RED（缺口成立）** | EXP-BASE-8 |
| 信任域加载器把「文件非法」静默压成「零受信 key」 | **RED（缺口成立，F-I08A-05）** | `contracts/evidence.py` 的 `except (OSError, ValueError, KeyError, TypeError): return {}`；EXP-BASE-6c 观测 `trusted_key_count=0`（与缺文件不可区分） |
| opt-in schema 3.8 继承消费者全量旁路 | **RED（缺口成立，F-I08A-04）** | `invest_contracts.py:1116` + `:1131-1132`（跨仓，属 OPEN-D6） |
| 现有 Ed25519 验签本身有效（白名单内通过、伪造拒绝、无名单拒绝） | **GREEN（不得否定）** | EXP-BASE-9/10 |
| 验证先于签发（无 `VerificationContext` 即 `TypeError`） | **GREEN（保护性冻结）** | `revenue_publication.py:137-141` |
| 单文件原子写（tmp+fsync+replace） | **GREEN（保护性冻结）** | `revenue_forecast.py:22-35` |
| 整组发布事务无孤儿 | **RED（属 I-09-A）** | `audit_report.md:59` + 生产 probe 日志第 17-23 行 |

---

## 5. 独立复算要求（reviewer 不得只看本 oracle）

1. 用**本 attempt 的隔离 venv** 重跑 `commands.json` 中全部命令，比对 raw rc 与 stdout。c3 的 argv 有两种等价形式（`argv_frozen_as` / `argv_as_recorded`，见 `commands.json`），**不变量**必须一致、字节不必一致（探针每次生成新随机测试密钥）。
2. 至少自行构造 1 个本 oracle **未列出**的变异：建议 (a) 把同一签名换到**另一个 `artifact_type`**（forecast → snapshot）；或 (b) 把信任域 key 的 `issuer` 改成另一个字符串而 fingerprint 不变；或 (c) 让 `not_after` 早于 `signed_at` 1 秒；或 (d) 把信任域顶层键写成 `"keys"`，观察是否报 **E25** 而不是静默 0 受信 key。记录预期与 hash 后再运行。
3. 亲自复算至少一个 hash：`canonical_sha256(payload)` 与签名对象字节是否一致（不得由被测函数生成 expected）。
4. 核对生产三仓 `git status --porcelain` 条目集合与 `binding.json` 记录的基线一致（revenue-forecast 基线 52 项、filing-fetch 1 项、company-wiki 2 项；注意 `?? …/I-14-C/` 属并发卡，已在 `after/git_delta_analysis.md` 归因）。
5. 核对 `iso/rf/scripts/**` 的 sha256 与 `binding.json` 中生产源文件一致（证明探针跑的是同一份代码）。
6. 核对探针**未绑定依赖已补绑**：`RF/tests/test_recognition_bridge.py` = `187ea01e45d144031d34b11e3a76c551b2029556c4d26b0b34983f7d59bcc1a5`（合成 fixture `forecast_document`，见 `binding.json.unbound_dependency_closed_in_r2`）；不一致即停止复跑并记录漂移。

---

## 6. 措辞修订（F-I08A-09；r3 扩到 E02/E32）

`decision.md` §2.5 的 **E02**（`provider_path_unopenable`）与 **E32**（`provider_capability_unproven`）以及 §1 的 A-D1 判定使用**同一措辞**：**「不得以读取/执行/import 该文件作为能力或签名依据」**。本文件 §1 表中 EXP-BASE-2/3/5 的 `provider_file_read_bytes` 字段是**观测值**：EXP-BASE-3/5 因探针为展示「这是一个普通文件」而读取了字节数（30142 / 16），EXP-BASE-2（venv 的 `python.exe`）为 `null`。**冻结的要求不是「探针不许读」，而是「生产判定路径不得以读取/执行该文件作为能力或签名依据」**：目标实现下该字段只能是 0 或 null，且 `provider_calls == 0`、`spawn_witness_calls == []` 必须恒成立。初稿把「`read_bytes == 0`」写成对探针本身的要求（且 EXP-BASE-2 实测为 `null` 而非 0），措辞偏差已在此更正。

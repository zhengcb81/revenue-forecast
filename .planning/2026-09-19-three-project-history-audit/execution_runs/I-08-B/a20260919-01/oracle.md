# I-08-B oracle — 运行前冻结的独立预期

- card: **I-08-B**（父项 I-08「发布可信性声明」）
- attempt: `a20260919-01`
- 上游已签署设计: `execution_runs/I-08-A/a20260919-01/decision.md` **r3**（独立复审 accepted_scoped）
- 冻结时刻: **在任何实现代码写出之前**（见 `commands.json.frozen_before_implementation=true`）
- 本文件的作用: 固定 (a) 32 个错误码的**唯一字符串**、(b) 正例/负例/重放/过期/旧版本/故障注入的**逐条预期**、(c) reviewer 应独立复算的不变量。
- **不得**为了让某项通过而放松任何断言；现状与预期不符时保留 raw 输出并记差异。
- 实现者**不**自签 accepted；结论由独立 reviewer 出具。

## 0. 本卡的边界与“不决定”清单

本卡只实现 I-08-A §10 已授予的实现清单第 1–8 项中**属于 I-08-B 的部分**，以及 §7.1 的验收前置。
**OPEN-D1…D7 一律不由本卡裁决**（见 `decision.md` §1）。其中直接影响代码的三项按“**参数/拒绝**”落地：

| OPEN | 本卡的落地方式（不发明数值） |
|---|---|
| **D7-`W`** 发布窗上限 | 代码检查结构顺序（`issued_at ≤ signed_at ≤ expires_at`）并**报告实测窗长**；上限判定由 `REVENUE_ATTESTATION_MAX_WINDOW_SECONDS` 提供，**未设置 ⇒ 不施加上限**（不硬编码任何秒数），并把 `W_enforced=false` 记入 attestation 记录 |
| **D7-`T`** provider 超时 | 由 `REVENUE_ATTESTATION_TIMEOUT_SECONDS` 提供；**未设置 ⇒ 拒绝调用**（码 `provider_call_budget_unspecified`），**绝不**用无限等待替代 |
| **D7-`L`** provider stdout 上限 | 由 `REVENUE_ATTESTATION_STDOUT_LIMIT_BYTES` 提供；**未设置 ⇒ 拒绝调用**（同上码），**绝不**用无上限读取替代 |
| **D4** receipt schema 版本 | **升为 `"2.0"`**（设计推荐项；owner 可自决）。读出端同时接受 `1.0`（旧收据按 G1/G3 类判定），写入端一律 `2.0`。**旧收据保持可读、不重签** |
| **D6** 3.8 消费者门 | 跨仓，本卡**只**在同仓导出判据 `is_legacy_exempt()`（**只有**显式 G1 版本集触发豁免）并登记它尚未接线到消费者；**不得**宣称缺口已闭 |
| D1/D2/D3/D5 | 本卡完全不涉及（不写信任根位置、不生成/保管真实私钥、撤销不回溯、不改消费者降级开关） |

**registry attestation 锚**：设计 §6.4 登记“字段名 UNRESOLVED-BY-DESIGN”。本卡在注册行**追加**两个键
`publication_attestation_status` 与 `publication_attestation_sha256`（无记录时后者为 `null`），**旧行保持可读**（读取端只用 `.get()`）。
字段名选取理由：与 §9 拒绝的“provider 自报信任域”无关，纯追加键，不改任何既有键的语义；字段名的最终规范化仍留 OPEN，本卡不宣称已定案。

---

## 1. 规范错误码表（**唯一来源**；字符串逐字冻结）

码值与 `decision.md` §2.5 **逐字相同**。任何实现、测试、断言只能引用本表字符串；本卡不新增、不合并、不改写任何码值。
E01…E31 按语义连续，**E32 追加在末尾**（沿用 r3 决议，不打乱既有编号）。

| # | 冻结字符串 | 触发点 | 层 | 本卡的期望后果 |
|---|---|---|---|---|
| E01 | `provider_absent` | `REVENUE_ATTESTATION_PROVIDER` 未设置 | L3 | 不 `host_signed`；`attestation_status="unattested"`；落 G3a；**provider 调用 0** |
| E02 | `provider_path_unopenable` | 路径不存在 / 不可作为文件打开 | L3 | 不 `host_signed`；**不得**读取/执行/import 该文件；调用 0 |
| E03 | `provider_protocol_violation` | 有输出但不成协议（非单个 JSON 对象 / 尾随垃圾 / 不读 stdin） | L3 | 不 `host_signed`；调用 1；**不解析**输出 |
| E04 | `provider_invalid_json` | stdout 无法作为 JSON 解析 | L3 | 不 `host_signed`；调用 1；**不做**“尽力解析” |
| E05 | `provider_exit_nonzero` | 退出码 ≠ 0 | L3 | 不 `host_signed` |
| E06 | `provider_output_too_large` | stdout > `L` bytes | L3 | 不 `host_signed`；**绝不**解析被截断前缀；子进程被终止 |
| E07 | `provider_timeout` | 超过 `T` | L3 | 不 `host_signed`；子进程**必须**被终止（无遗留） |
| E08 | `provider_schema_mismatch` | 响应字段集多/少/类型错 | L3 | 不 `host_signed` |
| E09 | `provider_binding_mismatch` | `request_id`/`payload_sha256`/`domain_separator` echo 与请求不逐字节相同 | L3 | 拒绝（跨载荷重放唯一防线） |
| E10 | `provider_signing_unavailable` | provider 明确报无法签名 | L3 | 不 `host_signed`；保留 `unattested` + 原因 |
| E11 | `provider_version_mismatch` | 载荷内 4 个版本字段与当刻运行时值不等 | L3 | 拒绝 |
| E12 | `attestation_missing_signature` | 声称 attestation 记录但无签名域 | L3 | 拒绝 |
| E13 | `attestation_malformed_signature` | 签名非 128 位小写 hex | L3 | 拒绝 |
| E14 | `attestation_signature_invalid` | 载荷被改后旧签名失效 | L3 | 拒绝 |
| E15 | `attestation_payload_fields` | 载荷字段集不精确 | L3 | 拒绝 |
| E16 | `attestation_payload_hash_mismatch` | `payload_sha256` ≠ 实际重算值 | L3 | 拒绝 |
| E17 | `attestation_domain_mismatch` | `domain_separator` 与当刻服务不符 | L3 | 拒绝 |
| E18 | `attestation_expired_at_publish` | `issued_at > signed_at` 或 `signed_at > expires_at` 或（`W` 已设时）`signed_at - issued_at > W` | L3 | 拒绝 |
| E19 | `request_id_reuse` | 同一 `request_id` 第二次用于**不同** `payload_sha256` | L3 | 拒绝新发布；**不**参与历史复验 |
| E20 | `provider_key_untrusted` | fingerprint 不在信任域（含信任域文件缺失的合法零受信） | L3 | 拒绝 |
| E21 | `issuer_key_binding_mismatch` | `issuer` ≠ 该 key 声明的 issuer | L3 | 拒绝 |
| E22 | `key_outside_validity_window` | `signed_at` ∉ [`not_before`,`not_after`] | L3 | 拒绝 |
| E23 | `key_revoked` | 信任域 `status == "revoked"` 的 key 用于**新**发布 | L3 | 拒绝 |
| E24 | `test_key_in_production_trust_domain` | 条目 `environment` 含 `test` 却走正式发布路径 | L3 | 拒绝 |
| E25 | `trust_domain_schema_error` | 信任域文件存在但不可解析 / 键名不符 / 条目缺必填 / 公钥非 32B | L3 前置 | **必须报错**，**MUST NOT** 静默返回空集 |
| E26 | `attestation_absent` | 当前 schema 包未作任何签名声明 | L3 | 落 G3a；保留研究结果；不得升级 |
| E27 | `attestation_missing_record` | receipt 声称 `host_signed` 却无 `publication_attestation` 记录 | L3 | 落 **G4**：**拒绝**，不得静默降级 |
| E28 | `legacy_read_only` | 旧版本包（G1）走消费者正式门 | 消费者 | 只读兼容（本卡只在同仓导出判据，消费者接线属跨仓 OPEN-D6） |
| E29 | `legacy_exemption_not_allowed_for_optin_schema` | 把 opt-in schema 3.8 当 G1 自动旁路 | 消费者 | **拒绝**（本卡判据必须拒；接线属 OPEN-D6） |
| E30 | `input_binding_mismatch` | `input_document` 与 `input_sha256` 不符 | L1 前置 | 拒绝；provider 调用 **0**；registry 新增 **0** |
| E31 | `publication_rollback_required` | output 写失败但 registry 已有行 | 事务 | **属 I-09-A**，本卡只做只读登记 |
| E32 | `provider_capability_unproven` | 路径存在且可打开，但**未完成一次成功握手**（含 `sys.executable`、裸 `.py`、`.txt`） | L3 | 不 `host_signed`；**不得**以存在/可执行/是 `.py` 作为依据；**调用 0**、**不读取该文件** |

**附加冻结码（本卡内部、非规范表成员，须显式标注以免与 E 码混淆）**：
`provider_call_budget_unspecified` — 仅在 `T`/`L` 未配置时用于**拒绝调用**，属 OPEN-D7 的“未裁决 ⇒ 拒绝”落地；
它**不是** E 码，也不得被写成 `E##`。

---

## 2. 三层证明域与 R-LAYER（不得回归）

| 层 | 本卡实现范围 |
|---|---|
| **L1** raw capture 事件签名 | **不改**；`source_receipts[*].signature_present` 一律保持观测原值（R-LAYER-1） |
| **L2** host receipt 签名 | 加严：信任域三元组（E20/E21/E22/E23/E24）；**未签名仍是合法状态**（不得因此回归） |
| **L3** publication 签名 | 本卡新实现：`host_signed` **只能**由 L3 验签通过产出（R-LAYER-2） |

**R-LAYER-2 判定**：L1/L2 全部已签且验签通过，**也不**足以让 publication 成为 `host_signed`。
**R-LAYER-1 判定**：新发布可以 `host_signed`，但**不得**出现任何“原 capture 已受信签名”字段（`NEG-LEGACY-1`）。

---

## 3. 正例（必须成功）— `T-O*`

| id | 输入 | 冻结预期 |
|---|---|---|
| **T-O1** | 受控 fake provider（隔离 Ed25519 测试 key）+ 隔离信任域；合法请求 | 协议调用 **成功**；返回精确字段集；echo 三字段逐字节相同；签名验签通过；`provider_invocations == 1` |
| **T-O2** | 同上，经 `run_forecast`（合成 fixture + 隔离 registry） | `attestation_status == "host_signed"`；`publication_attestation` 记录存在且验签通过；`attestation_failures == []` |
| **T-O3** | 同一 `request_id` + **完全相同**已签字段再次验签（NEG-REPLAY-9） | **允许**；不产生新历史事件；判定为同一物件第二次自证 |
| **T-O4** | 同一 immutable 记录在 `expires_at` **之后**重复验签（NEG-REPLAY-7） | **必须始终通过**；只可附加 `expired_now` 标记，**不得**失败（R-REPLAY-1） |
| **T-O5** | `signed_at == issued_at` 与 `signed_at == expires_at` 两个边界 | 均**通过**（闭区间 `issued_at ≤ signed_at ≤ expires_at`） |
| **T-O6** | `run_forecast` 无 provider | `attestation_status == "unattested"`；`attestation_capability() is False`；**调用 0** |
| **T-O7** | `signed_at` 在 key 的 `[not_before, not_after]` 闭区间边界上 | 通过 |

## 4. 负例（必须失败关闭）— `T-N*`，逐条绑定码值

**判定规则（本卡冻结）**：任何 `*_reject` 期望 = 抛 `AttestationError`（`ForecastInputError` 子类）且 `code` **逐字等于**期望码，
并且**不产生** `publication_attestation`、**不写** `host_signed`、**不新增** registry 行。

| id | 注入点 | 期望码 | 附加必须成立 |
|---|---|---|---|
| T-N01 | `REVENUE_ATTESTATION_PROVIDER` 未设置 | **E01** | 调用 0 |
| T-N02 | 路径不存在 | **E02** | 调用 0；不读取该路径 |
| T-N03 | 路径是**目录** | **E02** | 调用 0 |
| T-N04 | 存在但未证明能力：`sys.executable` | **E32** | 调用 0；**无挂起**；**不读取该文件**（`read_bytes ∈ {0,None}`） |
| T-N05 | 同上：裸 `.py` | **E32** | 调用 0 |
| T-N06 | 同上：`.txt` | **E32** | 调用 0 |
| T-N07 | provider 输出非 JSON | **E04** | 调用 1；不解析 |
| T-N08 | provider 输出 JSON 后面有尾随垃圾 | **E03** | 调用 1 |
| T-N09 | provider 退出码 1 | **E05** | 不解析 stdout |
| T-N10 | provider 输出超 `L` bytes | **E06** | **绝不**解析截断前缀；子进程被终止 |
| T-N11 | provider 睡眠超过 `T` | **E07** | 子进程**被终止**（实测无遗留） |
| T-N12 | 响应缺一个键 | **E08** | 调用 1 |
| T-N13 | 响应多一个键 | **E08** | 调用 1 |
| T-N14 | 响应键类型错 | **E08** | 调用 1 |
| T-N15 | `request_id` echo 被改 | **E09** | 跨载荷重放防线 |
| T-N16 | `payload_sha256` echo 被改 | **E09** | 同上 |
| T-N17 | `domain_separator` echo 被改 | **E09** | 同上 |
| T-N18 | provider 返回 `error: signing_unavailable` | **E10** | 保留 `unattested` + 原因 |
| T-N19 | 载荷 `engine_version` 被改 | **E11** | 拒绝 |
| T-N20 | 记录缺签名域 | **E12** | 拒绝 |
| T-N21 | 签名 127 hex | **E13** | 拒绝 |
| T-N22 | 签名大写 hex | **E13** | 拒绝 |
| T-N23 | 签一字节后改载荷 | **E14** | 拒绝 |
| T-N24 | 载荷多/少一个字段 | **E15** | 拒绝（不得“按已有字段签”） |
| T-N25 | `payload_sha256` ≠ 实际重算值 | **E16** | 拒绝 |
| T-N26 | `domain_separator` 与当刻服务不符 | **E17** | 拒绝 |
| T-N27 | `issued_at > signed_at` | **E18** | 拒绝 |
| T-N28 | `signed_at > expires_at` | **E18** | 拒绝 |
| T-N29 | 窗长 > `W`（`W` 显式设为测试值 `W_TEST`） | **E18** | 拒绝；`W` 未设置时**不得**触发本码（`W_enforced=false`） |
| T-N30 | 同一 `request_id` 第二次用于不同 `payload_sha256` | **E19** | 拒绝新发布 |
| T-N31 | 攻击者 key 签名（其 fingerprint 不在信任域） | **E20** | 拒绝 |
| T-N32 | 信任域文件**缺失** | **E20** | 合法零受信，一律拒绝（不得放松） |
| T-N33 | `issuer` ≠ 该 key 声明（fingerprint 不变） | **E21** | 拒绝 |
| T-N34 | `signed_at` 早于 `not_before` | **E22** | 拒绝 |
| T-N35 | `signed_at` 晚于 `not_after` | **E22** | 拒绝 |
| T-N36 | 信任域条目 `status="revoked"` | **E23** | 拒绝 |
| T-N37 | 条目 `environment="test"` 走正式路径 | **E24** | 拒绝 |
| T-N38 | 信任域：不可解析 JSON | **E25** | 报错并中止；**MUST NOT** `{}` |
| T-N39 | 信任域：顶层键写成 `"keys"` | **E25** | 同上（不得被当作 0 受信 key） |
| T-N40 | 信任域：条目缺 `issuer` | **E25** | 同上 |
| T-N41 | 信任域：`public_key` 非 32 B | **E25** | 同上 |
| T-N42 | 信任域：`status="revoked"` 但 `revoked_at=null` | **E25** | 同上（R-BIND-1 的定点攻击用例） |
| T-N43 | 信任域：`fingerprint` 非 32 hex | **E25** | 同上 |
| T-N44 | 信任域：顶层多一个未知键 | **E25** | 同上（禁止静默忽略未知字段） |
| T-N45 | receipt `attestation_status="unattested"` → G3a | **E26** | 保留研究结果；不得升级 |
| T-N46 | receipt 声称 `host_signed` 但无 `publication_attestation` → G3b/G4 | **E27** | **拒绝**；不得静默降级为 unattested |
| T-N47 | G1 版本（3.0…3.6，**每个版本各一条**） | **E28** | 只读；不得 `host_signed`；不得新建下游 artifact |
| T-N48 | 3.8 被当作 G1 自动豁免 | **E29** | 由 `require_legacy_exemption()` 抛出（谓词 `is_legacy_exempt("3.8") is False`；谓词本身无法"报告"，故码由该入口点承担） |
| T-N49 | `input_document` 被篡改 | **E30** | provider 调用 **0**；registry 新增 **0**；码由 `trust_anchor.verify_input_binding` 抛出，历史消息文本逐字保留 |
| T-N50 | 输入无效（缺必填字段） | 输入契约错误（`ForecastInputError`，无 E 码） | provider 调用 **0**；registry 新增 **0** |

**不属本卡（只登记，不实现、不声称通过）**：`T-N51` = output 写失败后的回滚（**E31**，I-09-A）；
`T-N52` = 消费者侧 3.8 门接线（**E29** 的跨仓落地，OPEN-D6）。

## 5. 重放 / 过期分离（R-REPLAY-1）— `T-R*`

| id | 输入 | 冻结预期 |
|---|---|---|
| **T-R1** | 同签名换不同 `input_sha256` | 拒绝（**E09** 或 **E16**） |
| **T-R2** | 同签名换不同 `result_sha256` | 拒绝（**E09**/**E16**） |
| **T-R3** | 同签名换不同 `schema_version`（3.7→3.6） | 拒绝（**E11**） |
| **T-R4** | 同签名换不同 `issuer` | 拒绝（**E21**） |
| **T-R5** | 同签名换不同 `domain_separator` | 拒绝（**E17**） |
| **T-R6** | `request_id` 一次性：不同 payload 复用 | 拒绝（**E19**） |
| **T-R7** | 历史复验（`expires_at` 之后，同 payload） | **通过**（不得因“用过”失败） |
| **T-R8** | 预签：`issued_at > signed_at` | 拒绝（**E18**） |
| **T-R9** | 同 payload 同字段复用 | **允许** |

## 6. 旧版本分类（§6.1 唯一判据 `classify()`）— `T-L*`

判据（逐字实现，不看版本号决定门；门由“是否作出签名声明”+“是否在 G1 集合内”共同决定）：

```
classify(artifact):
    有 publication_attestation 记录  -> 验签通过 ? G2 : G4
    声称 host_signed 但无记录        -> G4        (E27)
    schema_version ∈ G1_VERSIONS     -> G1        (E28)
    schema_version ∈ {"3.7","3.8"}   -> G3a       (E26)
    其它（未知版本）                  -> G4
```

| id | 输入 | 冻结预期 |
|---|---|---|
| T-L1 | 3.7 + `host_signed` + 有效记录 | **G2**（且 `verified=True`） |
| T-L2 | 3.7 + `host_signed` + 无记录 | **G4**，码 **E27** |
| T-L3 | 3.7 + `unattested` | **G3a**，码 **E26** |
| T-L4 | 3.7 + 无 `attestation_status` | **G3a**，码 **E26** |
| T-L5 | 3.0…3.6 + 无声明（每版一条） | **G1**，码 **E28** |
| T-L6 | 3.8 + `unattested` | **G3a**，码 **E26** |
| T-L7 | 3.8 请求 G1 式自动豁免 | **拒绝**，码 **E29**；`is_legacy_exempt("3.8") is False` |
| T-L8 | 未知版本 `9.9` | **G4** |
| T-L9 | 有记录但记录被篡改 | **G4**，码 **E14/E16** |
| T-L10 | 3.7 + `host_signed` + 记录 + `signature_present=false` 的 L1 旧收据 | 新发布可 `host_signed`，但**不得**出现任何“原 capture 已受信签名”字段（R-LAYER-1） |

## 7. §7.1 验收前置（RED → GREEN）——**本卡的准入条件**

**前置 1（已完成的 RED 观测，代码修改前取得）**

| 观测 | 原始结果 | 冻结预期 | 判定 |
|---|---|---|---|
| `tests/test_attestation.py::…::test_configured_provider_means_host_signed_publication`（基线树） | `1 passed in 0.51s`，raw rc=**0** | 修后该断言在**新语义**下必须是 RED | **现状=假绿**（证据 `before/cmd-run-red1-pytest.stdout.txt`） |
| `attestation_capability()` + provider=`sys.executable` | `True` | `False` | **RED** |
| `attestation_status` + provider=`sys.executable` | `"host_signed"` | `"unattested"`（码 **E32**） | **RED** |
| provider 是否真被调用（spawn witness） | `false`（调用 0 次） | 调用 0 次且**不再**产出 `host_signed` | **RED 在于标签，而非调用** |
| 裸 `.py` / `.txt` 作 provider | `capability=True` | `False`（码 **E32**） | **RED** |
| 不存在路径 | `capability=False` | `False`（码 **E02**） | 已符合 |

原始输出：`before/cmd-run-red2-probe.stdout.txt`（rc=0）、`before/cmd-run-red1-pytest.stdout.txt`（rc=0）。

**前置 2（本卡必须做的改动，不得直接改断言凑绿）**
测试**意图**从“配置了 provider”改为“**bound provider 完成一次成功握手**”：隔离目录内起**有界 fake provider** +
**隔离信任域**（`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` 指向 attempt 内路径；测试私钥**只**在进程内/隔离 env 中流转，
**MUST NOT** 写入仓库 `config/`，**MUST NOT** 进入任何被 schema 校验的文档）。

**前置 3（反向用例，分情形断言）**

| 输入 | 必须可达的码 |
|---|---|
| 变量未设置 | **E01** |
| 路径不存在 / 是目录 | **E02** |
| `sys.executable` | **E32** |
| 裸 `.py` | **E32** |
| `.txt` | **E32** |
| 可执行但协议不合规 | **E03** / **E04** / **E08**（视具体违规） |

所有情形同时必须满足：**不得** `host_signed`、**不得**以读取/执行/import 该文件作为能力依据
（`provider_file_read_bytes ∈ {0, null}`）。

**前置 3 的已披露例外（`sys.executable`，非反例）**：`sys.executable` 是一个**真实可执行文件**，
协议层无法在不启动它的情况下判定其是否有签名能力，因此该例**确实会被 spawn**。
该例因此断言 `provider_invocations` 与**集合** `{E32, E03, E04, attestation_malformed_signature}`
（对应本表"可执行但协议不合规 → E03/E04/E08"一行），而**不**断言 `provider_calls == 0`；
"不得 `host_signed`、不得出现 `publication_attestation`"仍是强断言。
`provider_calls == 0` 对**其余全部**情形（E01/E02/E32 的 .py/.txt/目录/不可启动 exe）继续强制。

**前置 4**：每条用例的 raw rc 与 stdout 进 `before/`|`after/`；只报“全部通过”不算。

**§7.1 补充（独立复核后修订）**：前置 3 表的"`sys.executable` → **E32**"是**设计表的目标码**；
实测在 Windows 上裸 `python.exe` 读完 stdin 后以 0 退出且无输出，故落到 **E04**。两者都在本表
"可执行但协议不合规"的可达集合内，因此用例断言集合而非单码，本卡的记录也不再声称该例必为 E32。

## 8. reviewer 独立复算要求（不得只看本 oracle）

1. 用本 attempt 的 `iso/venv` 重跑 `commands.json` 全部 bound 命令，比对 **raw rc** 与不变量。
2. 至少自造 **1 个本 oracle 未列出**的变异并**先记预期再运行**。建议：(a) 把 `attestation_payload_schema_version` 从 `1.0` 改成 `2.0`（应 **E15**）；
   (b) 信任域条目加一个未知键（应 **E25**）；(c) `not_after == signed_at - 1s`（应 **E22**）；(d) 响应 `signed_at` 非法时间串（应 **E08**）。
3. 独立复算签名对象：`canonical_sha256(payload)` 的 64 字符 ascii hex 是否**就是**被签字节（**不得**由被测函数生成 expected）。
4. 核对三仓 `git status --porcelain` 与 `before/git_status_*.txt` 的 ` M `/`??` **集合**一致（`scripts/`、`config/`、`artifacts/registry/`、`.planning/reviews/` 下零变化）。
5. 核对 `iso/rf/**` 被改文件的 sha256 与 `changes.diff` 一致，且生产同路径文件 sha256 **仍等于** `before/source_hashes.txt`。
6. 核对 `T-N52`/`T-N51` 未被悄悄算作通过；`iso/` 外零写入。
7. **`changes.diff` 的字节级口径（独立复核 P3-1 修订）**：把 `changes.diff` 施加到
   `before/baseline_tree/rf` 后，12 个文件中 **9 个的行尾与 `iso/rf` 不同（CRLF vs LF）**，
   因此"**裸字节**逐字节重现"**不成立**；把行尾归一为 LF 后 **12/12 内容相同**。
   正确表述是：**内容级可重现，字节级因行尾不成立**。reviewer 复算时请用归一 LF 后的比较，
   或直接比对 `binding.json.post_run_measurements.artifact_hashes` 里 `iso/rf/**` 的 sha256。
8. **mtime 不可作准（P3-2）**：本卡窗口内曾有 61 个非 `.planning` 产品文件 mtime 落在同一分钟，
   但 `before/source_hashes.txt` 的 24 个锚点**重算 drift=0**、生产 registry/默认信任域均未变，
   即**内容零变化、mtime 变化与 git 操作时点相关**。任何"文件被动过"的推断必须基于内容哈希，不得基于 mtime。

## 9. 冻结的“不做”

- 不写生产 registry、不改生产密钥/名单、不重签历史 artifact、不进 `.planning/reviews/**`。
- 不引入网络 key service、不引入常驻服务、不让 provider 自报信任域。
- 不把 `T`/`L`/`W` 的任何具体数值写成规范值（只在测试/绑定中显式给值，并在证据里标注“测试显式设定，非规范值”）。
- 不因签名而放松任何既有 receipt/hash 门（F01/F02 保持）。

# 模拟裁定（owner 全权授权 role-play）· 待 owner 终确 · 非外部方真实签署

> **记录性质**：owner-authorized simulated adjudication, pending owner ratification — NOT a real external signature。
> 本文件是 TIER-2 外部方「安全 reviewer」就 **T2-2 / OPEN-6**（函 `A_DW06_OPEN-4-5-6.md`）出具的模拟裁定。
> 依指令，本次角色扮演仅写本文件；**未**在任何函件、卡载体、`RESPONSES.md`、门或产品源码上落一笔，未签任何字，未做 git 操作。

**裁定对象**：`outward_requests/A_DW06_OPEN-4-5-6.md`（2026-09-22 追加更新后定稿 11546 B，签发 sha256 `cd88bd4cece0271d41ee5ccca31b9b70a2a6adcaa65502c5ca7a5a8717e6cde2`，见 `outward_requests/_provenance.json` 的 `issuance_2026_09_22.content_state`）。
**裁定日**：2026-09-22（域=本计划记录当日盘上字节）。

---

## 1. 你的身份与管辖域

**身份**：TIER-2 外部方 #2「**安全 reviewer**」。本裁定为 owner 全权授权下的 role-play 模拟，**待 owner 终确**，不是真实外部方签署。

**管辖域核验（用函件自身章节头核对 covers-order，不用映射表自证）**：

- covers-order 称 **T2-2 / OPEN-6 ↔ 安全 reviewer** —— **属实**。函 A 收件表 L5-9 明载「| **OPEN-6** | `not_detected` / `detected_and_ignored` 的判定归属 | **安全 reviewer** |」；§3 章节标题逐字为「`## 3. OPEN-6 —— detected_and_ignored 的判定归属（安全 reviewer）`」；上游卡 `execution_runs/I-06-A/a20260919-01/handoff.json` L242-247 的 `still_awaiting_other_parties.OPEN-6` 亦记 `awaiting: ["security reviewer"]`（唯一待裁方）。⇒ **OPEN-6 是本角色的专属裁决项，映射一致。**
- **相邻项声明（按指令「若函件赋予你不同/相邻项，裁那一项并声明」）**：函 A 收件表 L7 将 **OPEN-4** 共同指派给「**wiki 来源审核 owner + 安全 reviewer**」，§1 标题同样并列；`handoff.json` L227-233 的 `OPEN-4.awaiting` 亦为两方。⇒ 本角色**另受 OPEN-4 的安全域份额**。本裁定**主裁 OPEN-6（=T2-2）**，并**附裁 OPEN-4 的安全域份额**（4b 全部 + 4a/4c 的安全域约束）；OPEN-4 是**共同管辖**项，须 wiki 来源审核 owner 联署方可闭合，**不**由本裁定单独关闭。
- **域边界（只裁本域能背书的事）**：检测/判定语义、回执完整性与不可伪造性、信任根与身份绑定、旁路面（bypass surface）、下游可见性。**不裁**：OPEN-5 消费/恢复接口形态（RF 消费 owner）、OPEN-1 持久化介质（owner 已裁）、OPEN-2/2b/3（owner 已裁，本裁定只做一致性核对）、任何数值型规范（W/T/L）。

**共同约束确认已读并遵守**（`outward_requests/README.md` L24-33、`_provenance.json`）：不代签、不以「按最佳实践」代替决定、不编造证据、数值未定前不入规范、回执不落在函上。本裁定每项给出**选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案**（函 A §4）。

---

## 2. 裁定原文引用（我的问题，逐字）

**主裁项 —— 函 A §3（逐字）**：

> ## 3. OPEN-6 —— `detected_and_ignored` 的判定归属（安全 reviewer）
>
> ### 3.1 待裁的问题
>
> `not_detected` 与 `detected_and_ignored` 由**谁**判定、依据**什么**、落盘在**哪**？
>
> - 这两个状态是**安全域**的判定，还是**来源审核域**的判定？（若跨域，谁最终署名？）
> - `detected_and_ignored` 是否需要**理由字段**与**谁授权忽略**的记录？
> - 若某 source 被标为 `detected_and_ignored`，
>   它在下游（`I-05-B` 消费、`I-06-B` 恢复）应当**可见**还是**被过滤**？
>
> ### 3.2 起草方确认的当前事实（**没有越权**）
>
> `handoff.json` 的 `still_awaiting_other_parties.OPEN-6.note` 原文：
>
> > "this attempt correctly recorded `observed='not_reviewed'` and produced **zero review rows**"

**附裁项（相邻共同管辖）—— 函 A §1 OPEN-4 段相关句（逐字节选）**：

> **OPEN-4** | 审核方法、reviewer 身份绑定、`source_sha256` × `policy_hash` 双绑定、策略变更后旧回执失效判定 | **wiki 来源审核 owner** + **安全 reviewer**

> **(4b) reviewer 身份绑定**
> 「谁做了这次审核」如何被证明？
> - 身份以何为主体（人 ID / 角色 / 进程 + 凭据）？
> - 是否需要不可伪造的签名链？若需要，与 **I-08-A 的签字信任域**（函 B）是同一套还是两套？
>   ⚠️ **跨函耦合**：若两套，会产生两个信任根。请明确表态。

> **(4c)** …旧回执在**哪一种**变更下失效…失效是**立即**还是**下次读取时**？source 未变而 policy 变更时，旧回执是**作废重审**，还是**增量补审**？

（4a 的「判定枚举是否就是 `{not_reviewed, not_detected, detected_and_ignored, reviewed_ok, …}`？请给出**权威闭集**」与 OPEN-6 的两值语义直接重叠，安全域约束一并给出。）

---

## 3. 【裁定】

# **CONDITIONAL（有条件支持）**

对 OPEN-6 的三个子问题，本域**能够且 hereby 给出确定答案**；但今天盘上的机制**尚不能承载**该答案（理由字段/授权者不存在、身份是自由字符串、扫描器把「检出事实」与「忽略处置」铸进同一个状态串），因此是**有条件**：条件 C1–C8（§5）逐条可检验，未满足前**禁止任何 `detected_and_ignored` 行落盘**。不给 APPROVE——今日形态下照此落盘等于给无授权的「忽略」发合规外衣；不给 REJECT——问题本身是真实、可裁的安全问题，且本域有完整答案。

**选项选择（OPEN-6 的核心二选一，来自 `I-06-A/a20260919-01/decision.md` L70 的「检测命中时是隔离（默认）还是『有证据地 detected_and_ignored』」）**：

- **采 方案 α：默认隔离 + 经显式授权、留证据的 `detected_and_ignored` 处置（限定语义见下）。**
- **拒 方案 β：扫描器自动铸造 `detected_and_ignored` 并放行**（=今日 `scan_text` 直接返回该状态的语义）。
- **拒 方案 γ：一律永久隔离、永不允许忽略通道。**

**三问速答（详理由见 §4）**：

1. **归属**：两段跨域判定——「**检出**」是**安全域**事实判定（只能由具名、版本化的方法铸造，依据=命中清单 + `ruleset_hash`）；「**忽略**」是**安全域**的**处置授权**（来源审核域可**请求**并给业务理由，但**不得自署**）。**最终署名 = 安全域授权者（`ignore_authorizer`）**。
2. **理由字段与授权者记录**：**必须**。`detected_and_ignored` = 派生态，仅当回执携带完整**授权元组**（理由、授权者、授权时点、命中快照）才有效；缺任一 ⇒ fail-closed 按 `not_reviewed` 处理。
3. **下游可见性**：**可见且强制标记**；**禁止过滤**。`I-05-B` 消费与 `I-06-B` 恢复都必须看到该状态；需要 clean 证明的下游对它 **fail-closed**。

**附裁（OPEN-4 安全域份额，共同管辖、须联署闭合）**：

- **4b（本域全权表态）**：需要不可伪造的签名链；与函 B / I-08-A 签字信任域**同一套信任根，不设第二套**。身份主体 =「进程 + 凭据」映射到**受信签名者公钥**（与 attestation 侧同一 loader/信任域），人 ID/角色只能作为签名载荷内的声明字段，**不得**单独作为凭证。
- **4a（安全域约束）**：判定枚举**必须事实/处置分离**——`not_detected` 与 `detected` 是方法事实；`detected_and_ignored` 只能作为**携带授权元组的回执级派生态**进入权威闭集；`reviewed_ok` 之类的放行态不得由安全扫描单方面铸造。闭集最终文本由 OPEN-4 两方联署。
- **4c（安全域底线）**：policy/ruleset 任一变更 ⇒ 旧回执在**评估时点**即失效（fail-closed → `not_reviewed`），字节变更同理；source 未变而 policy 变更 ⇒ **作废重审**，不接受增量补审（增量面本身就是旁路面）。与 OPEN-2 选项 A 键口径的自洽复核属 OPEN-4 联署项，本裁定不代结。

---

## 4. 理由（全部引自盘上真实证据；未读的不写）

### 4.1 Q1 归属（谁判定、依据什么、落盘在哪）

**选择**：检出=安全域事实（依据=具名版本化方法的命中结果）；忽略=安全域授权处置；落盘=审核回执（review receipt）记录，且必须与需求登记（I-06-A 的持久 demand）联动；最终署名=安全域授权者。

**理由（证据）**：

- 方法事实的现行形态已经存在且可核：`execution_runs/I-06-B/a20260919-01/oracle.md` L60、L76-78 —— `scan_text` 返回 `ScanResult(status, matches, ruleset_hash=…)`，INJECT 样本命中 `['ignore_previous_instructions','exfiltration']`（`handoff.json` L34-37 `N1_inject_detection` 实测）；L81「未知 ruleset_hash → `PromptInjectionGuardError`（fail closed）」。⇒ 「检出」已经是**方法绑定**（ruleset_hash `19ace502…`，见 `I-06-B/decision.md` L38）的事实判定，**归安全域**，正确，应保持。
- **但「忽略」今天被铸进方法事实里**：`oracle.md` L76 逐字预期是 `scan_text(INJECT_TEXT)` 返回 `status="detected_and_ignored"` —— 一个**纯扫描器**在没有任何授权行为的情况下就铸造了「ignored」处置。这正是 `I-06-A/decision.md` L70-71 所指的未决归属（「安全 reviewer 决定：检测命中时是隔离（默认）还是『有证据地 detected_and_ignored』」），也正是 `handoff.json` L247 所说「在归属裁定前产出任何 `detected_and_ignored` 行都会**预设一个尚无归属的判定**」。⇒ 归属裁定必须把「检出」与「忽略」拆开，否则任何人调用扫描器就自动获得处置权。
- 落盘形态：回执函数 `record_prompt_injection_review`（`I-06-B/oracle.md` L23、L61）是回执的唯一写入口；`evaluate_review`（L23、L86-88）是读取/失效判定入口。⇒ 判定落盘在**回执记录**，失效判定落盘在**评估路径**；与 I-06-A 的持久需求（`handoff.json` L10「先登记持久需求再阻断」）联动，被检出来源必须留下可恢复的需求项。
- 「若跨域谁最终署名」：来源审核域对「是否继续以数据消费该来源」有业务发言权，但**忽略处置是对安全边界的让步**，最终署名必须是安全域授权者。反向（来源审核域自署）等于让被检出方的利益相关者签字放行自己。

**反例（真实）**：

- **REM-01**（`REMEDIATION_REGISTER.md` L12）：`attestation_status="host_signed"` 是纯标签、消费者完全不验签 ⇒ 指向 5 字节 txt 即可铸造。**一个处置/状态标签若没有受约束的铸造者和验证消费者，就是可伪造品**——`detected_and_ignored` 若由扫描器自动铸造、由自由字符串署名，就是同一缺陷换了名字。
- **REM-42/E21**（register L70；§二十八 L779）：回执的 `issuer`/`key_id` **无密码学绑定**，复审把 `record["issuer"]` 改成 `revenue-forecast/evil` 并重算哈希后**双层接受**。⇒ 「谁授权忽略」若只是回执里的字段而不在签名载荷内，改个名字就换人。
- **N3**（`I-06-B/oracle.md` L90-95、`handoff.json` L59-62）：卡 W06B-N3 要求拦「只写看似完整 receipt 但无实际审核执行」，但实测拦的只是 **evidence_sha256 格式非法**（"evidence_sha256 must be a lowercase SHA-256"）；一个**格式合法但内容虚构**的 evidence 哈希不被拦。⇒ 回执本身分不出「真扫描」与「假回执」，因此「忽略」的合法性只能来自**外部授权元组 + 签名**，不能来自回执自述。

**兼容影响**：`scan_text` 的返回语义必须收窄为事实（或保留 wire 值但把处置判据移出扫描器）；`I-06-B` 冻结 oracle（L76）与 14/14 harness 判据需**追加式**更正（本仓纪律：不回改冻结件，errata 追加，见 register §十四 L226-232 形态先例）；`schema_version="1.0"`（oracle L63）需升版。

**恢复规则**：已存在的扫描器级 `detected_and_ignored` 语义**不追认**（见 §6）；实现收窄后，旧 harness 结果按「演示记录」保留、不得作为产品语义证据引用。

**被拒绝的替代方案**：①维持现状（扫描器铸造 ignored）——被拒：等于无授权处置权默认下发给任何调用方；②把归属判给来源审核域——被拒：安全让步由被审方域署名，利益冲突且与 `START_HERE.md` 必须交专业审查的安全判定清单相悖（函 A §0 引文）；③归属判给「进程 + 环境变量」（如 `RF_W06_*` 注入形态，`I-06-A/handoff.json` 未冻结注入点）——被拒：环境变量是可篡改面，不可作署名主体。

### 4.2 Q2 理由字段与「谁授权忽略」的记录

**选择**：**必须**。授权元组 = `ignore_reason`（非空）+ `ignore_authorizer`（受信签名，含于签名载荷）+ `authorized_at` + 命中快照（`matches` + `ruleset_hash`）+ `source_sha256` × `policy_hash` 双绑定。缺任一 ⇒ 拒写 / 读取时 fail-closed 为 `not_reviewed`。

**理由（证据）**：

- 今日回执门槛**不足以**承载「谁授权」：`I-06-B/decision.md` L39 —— `record_prompt_injection_review` 只要求「非空 document_id、有效 status 枚举、**非空 reviewer**、SHA-256 evidence、schema_version=1.0；**可选** source_sha256 + policy_hash 双绑定」；L44 自认「当前 reviewer 字段为**自由字符串，无身份验证**」。⇒ 今天任何调用方都能写 `status="detected_and_ignored", reviewer="任意串"`。在身份绑定（OPEN-4b）落地前，**没有任何一行 `detected_and_ignored` 能证明授权者**。
- 双绑定今天是**可选**的（同上 L39「可选」），读取侧才把「无绑定」按 tampered 处置（L40「tampered（字节变更/无绑定）」）——方向正确（fail-closed），但**写入侧**留下无绑定回执，其上若挂 `detected_and_ignored` 就是一张无法作废的放行票（失效判定无从谈起）。
- 反伪造先例支持「字段必须进签名载荷」：REM-42（上引）issuer 改名双层接受 ⇒ 授权者、理由都必须被签名覆盖；B1 侧 `result_sha256` 可证不可绑定的教训（register L73 REM-45）⇒ 回执字段若设计成不可绑定，应**撤回该字段声明**而不是留着当证据。

**反例（真实）**：N3 假回执（上引）+ REM-01 标签可铸造（上引）+ REM-42 字段可改名（上引）——三者合起来构成本问题的完整攻击链：**虚构一次「检出后获授权忽略」的回执，署名任意人，下游照单放行**。这与 W06B-N3 卡片本身要防的「不得伪造 review」（函 A §1.1 (4a) 引卡文）直接对撞。

**兼容影响**：回执 schema 需增 4 类字段并升 `schema_version`；旧 schema 回执读取时 fail-closed（不得静默接受）；`evaluate_review` 需增授权元组校验；冻结测试（I-06-B 14/14、ZR-507 14 passed 见 `I-06-A/handoff.json` L18）需按追加式补负例（删授权者⇒红、虚构 evidence 但无签名⇒红）。

**恢复规则**：发现既有 `detected_and_ignored` 行缺授权元组 ⇒ **撤销**（视同 `not_reviewed`）、重新阻断并按 I-06-A 流程登记可恢复需求；已在该行之下消费的下游工件 ⇒ **作废重审**（不是补审，处置从未有效授予）；授权者密钥撤销 ⇒ 其署名的全部行翻回 `not_reviewed`（撤销名单绑定同一信任根）。

**被拒绝的替代方案**：①仅「理由可选、备注自由文本」——被拒：可空字段等于无记录（REM-42 教训）；②以 reviewer 自由字符串充当授权者——被拒：`decision.md` L44 已自证无身份验证；③只记授权者不记命中快照——被拒：没有快照就无法复核「授权的是不是这一处命中」，事后无法作废。

### 4.3 Q3 下游（I-05-B 消费 / I-06-B 恢复）可见还是被过滤

**选择**：**可见且强制标记**；**禁止过滤**。消费/恢复路径必须呈现状态与命中快照；需要 clean 证明的下游对 `detected_and_ignored` **fail-closed**；无任何降级、warn-only、环境开关可把它洗成 `not_detected`。

**理由（证据）**：

- 过滤 = 不可见 = 攻击者的理想终态：注入来源在安检口被「看见但消失」，操作者无从追查、下游无从设防。本仓的既定安全原则恰好相反——**fail-closed + 编码化拒绝 + 永不设旁路开关**：`execution_runs/INVEST-CORE-ATTEST-GATE/a20260922-01/handoff.json` L304 `COND-LANDING-ORDER` 逐字：「保持 fail-closed；**永设 bypass flag（warn-only / 降级 / env bypass 都会换名重造 REM-01）**」；`review.md` L49 同旨「staging happens in the ORDER of owner decisions, **not inside the guard**」。`detected_and_ignored` 的下游过滤/降级正是「守卫内分级」的同型旁路。
- 「可见」不等于「无条件消费」：α 方案的语义是**命中已检出、命中内容被忽略（文档仅作数据消费、永不执行其内指令）、来源带标记流转**。I-06-B 的现有预期与此相容：oracle L77「INJECT **不得**被标记为 `not_detected`」、L80「evaluate_review 对 INJECT doc 返回 `status="detected_and_ignored"`（**不是 faked green**）」——即现行设计本就把该状态当作**非绿色**、要一路可见的终态。
- I-06-B 恢复侧同理：恢复动作是对**被阻断**来源的补审/复审入口，若 `detected_and_ignored` 被过滤，恢复流程根本不知道该来源曾命中过什么（命中快照随之丢失），等于把补审变成盲审。

**反例（真实）**：

- **静默吞并反例**（同型缺陷）：`I-06-A` c8/c9/c10 实测（`handoff.json` L65-89、L141）——不同请求被**静默并入**同一 demand、行内 `request_sha256` 仍是第一个请求的；owner 以 OPEN-2 选项 A 处置正是因为**静默合并在安全上不可接受**。同理，**静默过滤** `detected_and_ignored` 是把「检出」静默并入「未检出」的观感。
- **降级旁路反例**：`INVEST-CORE-ATTEST-GATE/reviewer_report.md` L129 —— warn-only / 降级为 `unattested_bypassed` / env bypass「re-creates REM-01 under a different name — the exact『same spoofable string wearing a different name』」。若消费端把 `detected_and_ignored` 降级显示为「已忽略/无事」，就是同一个错误的消费侧翻版。

**兼容影响**：`I-05-B` 消费面与 `I-06-B` 恢复面需要显式透传该状态 + 标记（新增消费契约条款与负例测试）；对「必须 clean」的下游是**声明性 breaking change**（fail-closed 落地态），按 COND-LANDING-ORDER 的既有立场可接受——「靠决策顺序分级，绝不在守卫内分级」。

**恢复规则**：若发现任何消费路径过滤/降级该状态 ⇒ 该路径判定为旁路缺陷（REM-01 同级处置：登记 + 修复 + 消费侧负例），窗口期内已消费工件重新核。

**被拒绝的替代方案**：①过滤（下游只见干净流）——被拒：不可见即不可审计，见上；②可见但默认等同 `not_detected` 流转——被拒：faked green，oracle L80 明文否定；③由消费端各自决定显隐——被拒：把统一安全判定散成 N 个消费端口味，必出 REM-11 式「声明与实现不一致」（register L27 先例）。

### 4.4 附裁 OPEN-4 安全域份额（相邻项，声明如上）

**4b 选择**：**单一信任根**——与函 B / I-08-A 签字信任域**同一套**；身份主体=「进程 + 凭据」，以受信签名者公钥为证，人/角色为签名载荷内声明。**理由**：函 A §1.1 自警「若两套，会产生两个信任根」；盘上已有唯一信任域加载器先例——`INVEST-CORE-ATTEST-GATE/reviewer_report.md` L57：`_trusted_signer_public_keys` 读 `REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` 或 `config/trusted_signer_public_keys.json`，缺失/损坏 ⇒ `{}`（零信任），指纹不在表 ⇒ `provider_key_untrusted`，验签失败 ⇒ `attestation_signature_invalid`，**每条路径 fail-closed**。第二信任根=第二套可伪造面 + 双份撤销管理。**反例**：REM-42 的 issuer 改名双层接受证明「名字字段」不能当身份；无签名链的 reviewer 自由串（`I-06-B/decision.md` L44）证明「非空字符串」不能当身份。**兼容影响**：reviewer 身份从自由串迁移到签名载荷是 breaking change，旧回执一律 fail-closed。**恢复规则**：密钥撤销 ⇒ 吊销名单同源分发，署名行全部翻 `not_reviewed`。**拒**：两套根（耦合风险实锤）；以 OS 用户/环境变量为身份（可伪造/可继承）。

**4a（安全域约束，非最终闭集）**：事实/处置分离（§3）；`detected_and_ignored` 仅以「携带授权元组的派生态」入集；`not_reviewed` 必须保留为唯一默认 fail-closed 态（`I-06-A` 全程零 review 行、`observed="not_reviewed"` 的克制正确，见 `handoff.json` L247）。**拒**：把 `{not_detected, detected_and_ignored}` 并列为扫描器直产同级值（现状，oracle L60/L76）。

**4c（安全域底线）**：失效判定**不晚于下次读取/评估时点**（读取路径 fail-closed），因为 `policy_hash`/`source_sha256` 在绑定内，变更即不可评估（`I-06-B` L86-87 实测：tampered/ignored ⇒ `not_reviewed`，方向正确）；policy 变更 ⇒ **作废重审**。**反例（增量补审之害）**：增量面无法定义完备边界，规则集从 R1 换 R2 时「只补新增规则命中」会漏掉 R2 对旧文本的**新解释**——检测语义整体变了，只有全量重审能覆盖。**拒**：增量补审；「版本号变但内容不变不失效」的口径（若采纳 content-hash 为判据，需常数时间防碰撞论证——OPEN-4 联署项，本裁定只锁安全底线）。与 OPEN-2 选项 A（`source_sha256 + review_policy + role_set + request identity`）的口径自洽性：本底线与其**无冲突**（键口径管需求幂等，本底线管回执失效，两者均以 source/policy 绑定为轴）；最终自洽复核随 OPEN-4 联署。

---

## 5. 条件逐条（可检验；C1–C8 全部满足前，禁止任何 `detected_and_ignored` 行落盘）

| # | 条件 | 可检验判据（怎么验） |
|---|---|---|
| **C1** | **事实/处置分离落地**：扫描器只产事实（`matches` + `ruleset_hash` + detected 标志）；`detected_and_ignored` 只能经授权写入口铸造 | 产品代码审查：`scan_text` 类路径不再单方面铸造处置态；**负例测试**：无授权元组调用写入口写 `detected_and_ignored` ⇒ 被拒或落 `not_reviewed`（fail-closed），红绿可复跑 |
| **C2** | **授权元组必填**：`ignore_reason`（非空）+ `ignore_authorizer`（签名载荷内）+ `authorized_at` + 命中快照（matches+ruleset_hash）+ `source_sha256×policy_hash` 双绑定；缺任一拒写 | schema/校验层断言 + **变异臂**：逐一删字段 ⇒ 红；写入侧双绑定由「可选」改「必选」（对照 `I-06-B/decision.md` L39 的「可选」现状） |
| **C3** | **身份落地前零行**：OPEN-4b 签名链落地前，任何载体不得出现产品语义的 `detected_and_ignored` 行（I-06-B N1 的 harness 演示行除外，且标注为演示、不得晋升为语义） | grep 产品树与卡载体：产品语义 `detected_and_ignored` 行 = 0 直至 C5/4b 条件满足；I-06-B 现有冻结件以追加式标注「演示、未授权」 |
| **C4** | **下游可见**：`I-05-B` 消费与 `I-06-B` 恢复**可见且标记** `detected_and_ignored`（含命中快照）；禁止过滤/静默降级 | 消费端**负例测试**：注入源到达消费/恢复面可观察到状态与命中；**变异臂**：任何过滤/降级分支 ⇒ 红 |
| **C5** | **无旁路**：不存在 warn-only / 降级为非检出 / env bypass 把该状态洗成 `not_detected` 或解除阻断（COND-LANDING-ORDER 直接移植） | 代码审查 + 负例：设置任意环境开关后 fail-closed 行为逐字节不变（对齐 `N3_paused` 式「字节不变」检验，`I-06-A/handoff.json` L60-63 形态） |
| **C6** | **新鲜度不可由调用方放宽**：回执 TTL 上限由 `policy_hash` 绑定的策略固定；调用方传入的 `now`/`ttl` 只能收紧、不能放宽（现状 `evaluate_review(..., now=<recent>, ttl=86400*30)` 为调用方给定，见 `I-06-B/oracle.md` L70） | **负例**：`ttl=∞` / `now=过去` 复活已过期回执 ⇒ 被拒或被策略上限截断 |
| **C7** | **术语消歧**：`cache_state="ignored"`（策略变更失效，`I-06-B/handoff.json` L49-53）与 `detected_and_ignored` 的「ignored」同词异义须在契约层消歧（改名或显式断言），防消费端误读 | 契约文本/断言存在且冻结测试覆盖两种语义各一负例 |
| **C8** | **登记落地**：本裁定经 owner 终确后，由**编排层**转录登记到卡载体（`I-06-A`/`I-06-B` 的 `decision.md`/`rulings_*.md`）并在 `outward_requests/RESPONSES.md` 登一行（函号/项号/收件方/结论落点/时间），**不改一字裁决内容** | 登记行存在且与本文件 sha256 对得上；本角色不亲手执行（见 §6 边界） |

**条件之间的硬依赖**：C3 是 C1/C2 未落地期间的**替代闸门**——只要 C1+C2 未绿，C3 必须保持；C4/C5 在任何落地顺序下都不得被「先放后收」绕过（对齐 COND-LANDING-ORDER 的「靠决策顺序分级，绝不靠守卫内行为分级」）。

---

## 6. 不予授予项（本裁定明确不给的东西）

1. **不授予、不追认任何既有 `detected_and_ignored` 行**——包括 I-06-B N1 判据下的 receipt_status 实测行（`handoff.json` L34-37）与 oracle L76 的扫描器级语义；它们是 attempt 内演示记录，**不获得产品语义、不获得授权追认**。
2. **不授予「detected_and_ignored = 放行/绿色」的任何读法**——它永远不是 `not_detected`（oracle L77/L80 明文）。
3. **不在条件 C1–C2 满足前授予任何铸造权**——今日起至落地，产品语义 `detected_and_ignored` 行数应为 0。
4. **不关闭 OPEN-4**——附裁仅为安全域份额；4a 权威闭集最终文本、4c 与 OPEN-2 键口径的自洽复核须 wiki 来源审核 owner 联署。
5. **不裁 OPEN-5、不裁数值（W/T/L）、不改任何 status、不在函件/`RESPONSES.md`/卡载体/门/产品源码落笔、不代任何方签署**。函 A §4 要求结论落各卡载体——按 owner 对本次角色扮演的指令，本角色**唯一**写入即本文件；载体登记与 RESPONSES 登记是**编排层**的动作（条件 C8）。
6. **不把 owner 的总授权或本 role-play 膨胀为真实外部签署**——本文件全称「模拟裁定…待 owner 终确…非外部方真实签署」，效力止于 owner 终确之前。

---

## 7. 未验证 / 存疑项

### 7.1 `存疑项__initial`（2026-09-22 初裁，8 条**逐字保留**、不改一字；域=本次实际读过的字节）

> 复核批解析态见 §7.2（`存疑项__reverified`）；本节为初裁原文，**不回改**。

1. **产品源字节未直读**：`prompt_injection_guard.py` / `prompt_injection.py` 的实现本体我未打开核对；本裁定对写入/校验逻辑的判断依据是 `I-06-B` 载体的实测记录（`decision.md` L39-41、`oracle.md` L60-95、`handoff.json` 冻结对账表）与其 `input_hashes`（`handoff.json` L75-80）。**C1/C2 的落地检查必须由复核者对照产品现行字节执行**，不得以本裁定代替代码审查。
2. **`now`/`ttl` 调用方供给面（C6）** 依据 oracle L70/L86-87 的调用形态观察，未读实现；是否存在策略侧上限未验。
3. **假回执的格式合法哈希面**：N3 只实测了格式非法哈希被拒（`handoff.json` L59-62）；「格式合法但虚构」的哈希能否写入**未直接实测**（由 L93-95 预期文本推断只查格式），条件 C2 的变异臂须补此负例。
4. **并发写回执的原子性未验**：register §二十一 L592 记复审 grep iso+生产两树「**零 lock 原语**」；`I-06-A/handoff.json` L147 记「候选未验证 additive migration / 并发 claim / lease 过期」。同一回执表并发写（含撤销/翻回 `not_reviewed`）的竞态无证据。
5. **术语碰撞的实际消费面未排查**：`cache_state="ignored"` 是否已被消费端误读，未见盘上记录。
6. **阻断文案跨仓文本断言未排查**（`I-06-A/handoff.json` L146，随 OPEN-4b 文本契约联动）——与 OPEN-6 相关的是 c7 错误契约「安全判定 + `demand_store_error=`」（OPEN-2b 已裁采纳，`handoff.json` L214），其跨仓断言仍未排查。
7. **I-05-B 消费面的具体入口未读**（OPEN-5 明载接口**今天不存在**，`handoff.json` L240）；C4 的落地判据以「消费/恢复面的契约负例」形态给出，待接口由 OPEN-5 定形后实例化。
8. **role_set 只来自环境变量**（`I-06-A/review.md` L75）——「角色集合变化」维度当前不可观测；OPEN-2b 已裁权威来源维持 `RF_W06_ROLE_SET`，其可篡改面（环境注入）作为 C5 旁路审查的一部分随检，本裁定未单独验证。

### 7.2 `存疑项__reverified`（2026-09-22 复核批 · 父实证 + 在途探针，OPEN-5 方同款三值约定）

> **三值约定**：每条给三值之一 —— **已解除** / **部分解除** / **在途**。
> **改判纪律**：依约**不自行改判**——裁定正文（§1–§6）与条件 C1–C8 **一字不改**；实证推翻/限缩前提的条目只标「**前提变化**」+ 指向受影响条款；其余标「前提无变化」。
> **实证来源**：父 agent 直读产品源字节（`prompt_injection.py` = `7b22f23918d5e6b0…`/6619 B、`prompt_injection_guard.py` = `f900a13d7c22fe3b…`/8382 B，与 `I-06-B/handoff.json` L76-77 `input_hashes` 逐位相符）、grep 工具实测、消费面读数（`readiness_graph.py` 及两测试文件）；探针 5/6（`7073a5f9`）在途。

| # | 初裁条目（§7.1） | 三值 | 复核实证 | 前提判定 |
|---|---|---|---|---|
| 1 | 产品源字节未直读 | **已解除** | 两文件哈希直测与 `input_hashes` 逐位相符 ⇒ 初裁据 I-06-B 载体的推断**零漂移成立**；guard/record 入口行为行直读证实：`prompt_injection.py` L23 `PROMPT_INJECTION_REVIEW_STATUSES` frozenset、L52-58 校验中 **L57-58 reviewer 仅「非空」= 自由字符串实锤**（与 §4.2 引证一致）、L68 `record_prompt_injection_review` 入口在位 | **前提无变化（证实）**。C1/C2 落地检查仍须复核者对照**届时**产品字节执行（§7.1(1) 表述维持，不撤） |
| 2 | `now`/`ttl` 调用方供给面（C6） | **已解除** | `prompt_injection_guard.py` L159 `def _freshness(receipt, now, ttl_seconds)`——**now 与 ttl_seconds 均为调用方入参**；L168 `now_seconds - reviewed_at > ttl_seconds` 纯调用方比较、**无策略侧上限**；L13 docstring「expired — reviewed_at older than the TTL: not_reviewed」与初裁引证一致 | **前提无变化（强化）**：现状=调用方可无限放宽 ⇒ C6 必要性被强化；C6 文本不动 |
| 3 | 假回执的格式合法哈希面 | **已解除**（敞口实测证实） | 探针 5 = 敞口 **CONFIRMED 3/3**（明细见 §7.4-D-续 3-E）：虚构但格式合法 `evidence_sha256` + `not_detected` **ACCEPTED 且可读回**（写入侧敞口实锤；N3「只拦格式非法」成立、**未收窄**）；`reviewer="zr302-test-FAKE"` **ACCEPTED**（身份可冒用）；`detected_and_ignored` 无双绑定 **ACCEPTED**；对照 'ABC' 精确拒绝 ✓ | **前提变化（敞口证实 = C2 描述吻合）**：初裁推断（只查格式）升级为**实测敞口**，C2 授权元组必填 + C3 身份落地前零行的必要性实锤（指向 §5 C2、C3；§4.2 反例）。不改判 |
| 4 | 并发写回执原子性 | **部分解除**（无撕裂已证；丢写 + 裸抛缺陷证实） | 探针 6 = **RECORD-CONFIRMED**（明细见 §7.4-D-续 3-F）：默认 timeout 8/8 写成功、零 lock 异常；658 次交错读**零撕裂零异常**；**但**单 metadata key = **last-writer-wins 静默覆盖**（7/8 写被顶掉无痕迹）= 丢写缺陷；timeout=0 时 7/8 **裸抛** `sqlite3.OperationalError「database is locked」`；与 register §二十一 L592「零 lock 原语」实证相符 | **前提变化（由「竞态无证据」转「缺陷实证」）**：无撕裂面已证；丢写 + 裸抛 = 缺陷证实（指向 C5 适用说明①；静默覆盖与 c8/c9 静默并入同族）。待 P6-A / P6-B 落定验证后终格「已解除」，不改判 |
| 5 | 术语碰撞（`cache_state="ignored"` vs `detected_and_ignored`）消费面 | **已解除** | 消费面实测存在且**无误读**：`readiness_graph.py` L36 `_SAFETY_MAP`「cache_state → (graph verdict, next action)」、L104-105 按状态映射**独立 verdict + next_action**（ignored 自有处置路径、**不并入 clean**）；测试双钉：`test_prompt_injection_guard.py` L190/204/217/230/244/255/271/289 与 `test_readiness_graph.py` L209/226/246/264/288 每状态各一断言 | **前提无变化**：未见误读事故；C7 定位维持为**契约层预防性改进**（非事故修复），C7 文本不动 |
| 6 | 阻断文案跨仓文本断言未排查 | **已解除**（排查缺口已补；「钉住」留置实施） | P4 排查（9 行表）已回 = 本条素材件（明细见 §7.4-D-续 2）：`not_reviewed` 双仓 PINNED；**阻断整句 UNPINNED**（RF `source_preparation.py:154-156` 一处定义 + 2 手抄副本、测试宽松正则）；`demand_store_error=`/`demand_queued` 仅候选定义、产品零断言 = UNPINNED；六拒绝串只钉类型不钉文案 = UNPINNED；resume 文案 ABSENT（正确缺席）；`cases_json_declared_expectation_missing` = runner 词汇、产品零命中 = 正确缺席 | **前提无变化（证实：确为未钉住面）**。排查缺口已补 ⇒ 本条不确定性解除；「钉住」（文案逐字断言 + PIN 测试 + 变异证真）留置 **P4-SCOPE** 修复卡（owner「fail 全修」并入），不改判 |
| 7 | I-05-B 消费面入口未读（OPEN-5 接口今天不存在） | **在途** | 维持初裁表述（`I-06-A/handoff.json` L240「the interface DOES NOT EXIST today; it must not be pretended into existence」）；C4 判据待 OPEN-5 定形后实例化 | **前提无变化** |
| 8 | role_set 可篡改面（`RF_W06_ROLE_SET`） | **部分解除** | grep 实测：`RF_W06_ROLE_SET` 在 RF `scripts/` **零命中** ⇒ 该 env 今日**无生产消费点**，只存在于候选/计划设计层（`I-06-A/review.md` L75 记载形态）；候选层探针由在途探针官覆盖 | **前提变化（限缩）**：§7.1(8) 与 C5 随检句所指「可篡改面」由**现行敞口**限缩为**实施期前瞻约束**（指向：§5 C5、§7.1(8)）；C5 本体与裁定正文不动。若实施引入 env 消费点，前瞻约束即时生效 |

**计分**：已解除 5（#1/#2/#3/#5/#6）· 部分解除 2（#4/#8）· 在途 0 + #7 维持在途（OPEN-5 定形后实例化）。探针 5/6 已全部回收；后续只随修复卡落定更新本节，**不**回改 §7.1，**不**改判。

### 7.3 OPEN-5 方一致性复核三点回文（联署参考，**不改判**）

- **(a)「policy 变 ⇒ 作废重审 + 读取 fail-closed」**：**兼容 ✓**。维持 §4.4 4c 原文；与 OPEN-5 方消费底线主相容，无冲突、无需修正。
- **(b)「role_set / 请求身份变不动回执」**：**兼容 ✓**。与本裁定分域一致：回执失效轴 = `source_sha256 × policy_hash`（§4.2 授权元组、§4.4 4c）；role_set / 请求身份属需求幂等键域（OPEN-2 选项 A），不在回执失效轴上。
- **(c)「role_set 扩大」场景的扫描范围前提 —— 明示定义（本回文的核心交付）**：

  **扫描范围定义（安全域明示，供 OPEN-4 联署文本与 OPEN-5 回文引用）**：安全审核的扫描范围 = **全量 source 字节 × policy（版本化规则集）**，**与 role_set 无关**——扫描**不得**按角色裁剪。
  - **依据**：现行方法事实即整段文本匹配——`scan_text(text)`（`I-06-B/oracle.md` L21、L60-78）**无角色参数**，`ruleset_hash` 绑定的是规则集而非角色集；回执双绑定以 `source_sha256` 代表**全部**被审字节——若范围按角色裁剪，「全字节哈希」就名不副实（REM-42「不可绑定字段」教训，§4.2 反例）。
  - **推论**：「role_set 扩大」**不产生覆盖缝隙**的前提 = 扫描范围与 role_set **正交**；role_set 仅属请求身份/幂等域（OPEN-2 选项 A）与下游角色切片域。role_set 变更**不**使回执失效（与 (b) 一致），恰因范围与角色无关。
  - **反向 fail-closed**：若实施出现「按角色裁剪扫描」的形态 ⇒ 上述前提不成立、覆盖缝隙成立（未扫描字节随新角色进入消费面）⇒ 该形态**禁止**；唯一退路 = role_set 扩大 ⇒ 旧回执失效**作废重审**（§4.4 4c 同则），绝无「增量补扫」。
  - **实证状态**：**在途**——「`scan_text` 无角色参数」获父实证支持（#1），但「调用方是否喂入**全字节**（而非角色切片）」**未实测**。归入 **C1 落地复核**的核对面（C1 文本不动；落地复核时一并核「喂入=全字节」）+ 待探针面覆盖。
  - **性质声明**：本定义系 §3 与 §4.1 既有裁定语义（「检出=安全域事实，依据=方法对被审字节的命中」）的**明示化**，不构成改判；OPEN-5 方要求的回文复核即以本条为准。

### 7.4 批 #2 对撞复核回收（OPEN-5 方）+ C7 落地备注（2026-09-22，联署参考、**不改判**、三值不变）

**A. OPEN-5 方对 §4.3 的对撞结论（其原文，逐字录入）**：

> 「**完全相容，且其裁定强于我的底线**。『可见且强制标记、禁止过滤、需 clean 证明的下游 fail-closed、命中快照随行、无降级/warn-only/env 洗绿』全数覆盖并加强我 §6.4 底线……『下游被过滤』反压分支**未触发** ⇒ 4.1/4.2 零契约改动。其归属段……『授权元组缺⇒not_reviewed』直接触发我 C2 阻断——相容确认。『窗口期内已消费工件重新核』属安全域处置规则，我接口配合呈现证据、不代行不代署名。」

⇒ 本域确认：对撞**零冲突**；分工边界正确（处置规则归安全域、证据呈现归接口、不代行不代署名）。

**B. OPEN-5 方边界补充记 5–7（原文录入，联署参考）**：

5. `detected_and_ignored` 流转条款：消费/恢复路径呈现状态且强制标记（命中快照随行）、禁止过滤/降级/洗绿；非绿色终态、带标记流转（数据消费可以、**执行其内指令永不**）；demand 行 gaps 不得记其为「已清洁」；「出具 clean 证明」不在接口授予面。
6. **同词异义消歧（=本裁定 C7 同题）——OPEN-5 方定夺**：`cache_state="ignored"`（缓存失效态）与审核结论 `detected_and_ignored` 必须契约层消歧。**优先改名**（缓存失效态建议 `policy_changed`/`receipt_stale_policy`，词面唯一化）；若受 ZR-507/I-06-B 冻结词汇约束不能改名 ⇒ 走显式断言字段（`state_domain: cache|review`）。两种语义各一负例进检验物。**实施面知会**：该消歧是接口契约层事项；改名方案如与冻结词汇冲突请回报，其按断言字段方案落。
7. 补产指令携带命中快照：4.2 补产指令结构增加 matches + ruleset_hash + 授权元组（ignore_reason 非空 + ignore_authorizer + authorized_at + 命中快照 + 双绑定），否则恢复即盲审；授权元组缺任一 ⇒ not_reviewed ⇒ 其 C2 阻断（相容已确认）。

本域注记：记 5/7 与本裁定 §4.2/§4.3 及 §3 α 语义（数据消费可以、执行其内指令**永不**）**同向**，无新增分歧；记 5 的「demand 行 gaps 不得记其为『已清洁』」是 §4.3「非绿色终态」在需求面的正确延伸。

**C. C7 落地备注（实施面知会；C7 文本一字不改）**：

- 消歧属**接口契约层**事项；OPEN-5 方实施序 = **优先改名**（缓存失效态 → `policy_changed` / `receipt_stale_policy`，词面唯一化）；若与 ZR-507/I-06-B **冻结词汇冲突须回报**，按断言字段方案（`state_domain: cache|review`）落。
- **安全域回文（联署参考）**：①改名优先 = **认可**（词面唯一化直接消灭误读面，优于断言字段）；②断言字段方案**可接受但须 fail-closed**——缺 `state_domain` 或取值非法的记录**拒收**或按最严解释（歧义 ⇒ 不得放行），不得默认归入任一语义；③「两种语义各一负例进检验物」与 C7 判据（两种语义各一负例）同物，满足 C7 检验面；④回报线：改名与冻结词汇冲突时按其定夺退断言字段并回报，本域不另设条件、不改 C7。

**D. 全景知会（批 #2 探针；**不涉本裁定三值**，#3/#4/#6/#7/#8 状态不变）**：

- OPEN-5 现仅余其 #1/#2 待探针（批 #2）；**探针 P1 已回 = FAIL 实证**：候选 additive migration 升级路径断裂（N-1 表上 `_initialize` 静默不补列、`register()`/`claim()` 炸缺列、`claim()` 连 `DemandStoreUnavailable` 都没包）。与本裁定 #4/#8 无涉，两点记入：
  1. **「claim() 裸抛」与 C5 错误面同族**——实施期 `claim()`/`register()` 的失败必须走**编码化 fail-closed 错误契约**（与 c7 契约「安全判定 + `demand_store_error=`」同族，OPEN-2b 已裁采纳，`I-06-A/handoff.json` L214），不得裸抛、不得静默降级。此为 C5 既有条款的**适用说明**，不新增条件。
  2. P1 实证使 `I-06-A/handoff.json` L147「候选未验证 additive migration」一项由「未验证」转为「**实测断裂**」——处置归 OPEN-5 / I-06-A 轨道，本域仅记录。
- P2（并发 claim）执行中，回报到后随批知会；本裁定 #4（并发写**回执**表原子性）与其（并发 claim **需求**表）分属两个面，P2 不替代 #4 探针。

**D-续（P2/P3 回报 + owner 修复裁定，2026-09-22；三值不变、不改判）**：

- **P2 = PARTIAL**（并发抢单**需求表**）：断言 A（恰好一赢家）候选 **PASS 5/5**（无双写、无双 running）；**断言 B FAIL**——候选输家**裸 `None`**、无定义拒绝，vs 内存队列 `DemandStateError`。与本裁定 #4（并发写**回执**表）分属两面、**不替代**——**探针 6 仍在队列**，#4 维持**在途**。
- **P3 知会**：候选无 resume/complete（lease-expiry 在候选 **ABSENT**）+ 新缺陷 = running + lease 过期需求**永久搁浅、无显式回收**（违 OPEN-3 形状：回收须显式调用、不得自动）；内存队列侧过期 / 错 owner / 显式 expire 全有定义错误。
- **C5 适用说明①被 P2-B / P3 双双实证为必要**：P2-B 的「输家裸 `None`」与 P1 的「claim() 裸抛」同族——候选层多处把应编码化拒绝的路径留成裸返回 / 裸抛 / 无定义。实施期必须按 c7 契约族落**编码化 fail-closed 错误**（OPEN-2b 已裁）；且「lease 过期无显式回收」**不得**以自动回收 / 后台 scheduler 补齐（OPEN-3 明文禁止），须以**显式授权命令**承载、错误面同样编码化。此仍为 C5 既有条款的适用说明，**不新增条件**。
- **owner 已裁定「fail 的全部要修复」**，修复卡 **FIX-W06-GAPS** 开工（P1 / P2-B / P3 增量并入）；落定后本域再更新本注记（按届时事实更新，**不预判验收**）。
- 本域三值**不变**：#3 / #6 = 在途（探针 5/6；探针 6 = 回执表并发面）、#7 = 在途、#8 = 部分解除。

**D-续 2（P4 报告回收 = 本裁定 #6 素材件，2026-09-22；不改判）**：

- **P4 排查（9 行表）录入**：`not_reviewed` 双仓 **PINNED** ✓；**阻断整句 UNPINNED**（RF `source_preparation.py:154-156` 一处定义 + 2 手抄副本、测试仅宽松正则）；`demand_store_error=` / `demand_queued` 仅候选定义、产品零断言 ⇒ **UNPINNED**；六拒绝串同文**只钉类型不钉文案** ⇒ UNPINNED；resume 文案 **ABSENT**（正确缺席，与 `I-06-A/handoff.json` L240「the interface DOES NOT EXIST today」一致）；`cases_json_declared_expectation_missing` = runner 词汇、产品零命中 = **正确缺席**。
- **勘误录入（随报转录，不改判）**：OPEN-5 裁定引 `cases_json_declared_expectation_missing` 处**实指 M01-M04 runner 域**——按勘误理解，本域无异议。
- **安全域读数**：①`not_reviewed`（唯一默认 fail-closed 态，§4.4 4a）双仓钉住 = 关键态在案 ✓；②**阻断整句 UNPINNED + 2 处手抄副本** = 漂移面（三份拷贝可各自漂移、宽松正则抓不住文案弱化）——P4-SCOPE 的「文案逐字断言 + PIN 测试 + 变异证真」是正确修法；建议（联署参考）：整句**收敛单一定义源**、副本引源不手抄；③c7 契约（`demand_store_error=`/`demand_queued`，OPEN-2b 已裁，`I-06-A/handoff.json` L214）产品面零断言 ⇒ 实施时必须同步钉住（C5 适用说明①的落地面）；④六拒绝串只钉类型不钉文案——类型级 fail-closed 已在，文案级留 P4-SCOPE。
- **落置**：owner「fail 全修」已并入修复卡 **P4-SCOPE**（文案逐字断言 + PIN 测试 + 变异证真）；与 C5 适用说明①（编码化错误契约）及 P2-B / P3-B 修复**同向**。落定后随 FIX-W06-GAPS 一并更新注记。
- **勘误（本文件内笔误）**：D-续 末行「#3 / #6 = 在途（探针 5/6）」系笔误；正确映射 = **#3 ↔ 探针 5、#4 ↔ 探针 6**（§7.2 表内原映射为准），#6 的素材件 = P4（本次回收，状态已更新「已解除」）。以本行为准。
- 本裁定 #6 状态更新见 §7.2（**已解除**：排查缺口已补、「钉住」留置实施）；#3 / #4 维持**在途**（探针 5 / 6 随后）。

**D-续 3（探针 5/6 终批回收 = 本裁定 #3/#4 素材件，2026-09-22；不改判；上条末行「#3/#4 在途」以本条终格为准）**：

**E. 探针 5（= #3 格式合法虚构假回执面）= 敞口 CONFIRMED 3/3（原文要点录入）**：

- 虚构但**格式合法** `evidence_sha256` + `not_detected` **ACCEPTED 且可读回** ⇒ 本裁定 §4.2 所指**写入侧敞口实锤**；N3「只拦格式非法」成立、**未收窄**（对照 'ABC' 精确拒绝 ✓——格式门在、内容门缺）。
- `reviewer="zr302-test-FAKE"` **ACCEPTED** ⇒ **身份可冒用** = §4.2 反例「REM-42 改名双层接受」的同族实测版（自由字符串署名实锤，与 §7.2 #1 的 L57-58 读数互证）。
- `detected_and_ignored` **无双绑定 ACCEPTED** ⇒ §4.2 所指「无绑定回执上挂 `detected_and_ignored` = 无法作废的放行票」实锤（写入侧双绑定「可选」的后果实测）。
- **处置分轨（录入）**：P5-a 载荷绑定 + P5-c 双绑定强制 = 修复卡即修；P5-b 身份 = 函 B 信任根外部暂缓。本域确认：**分轨正确**——P5-b 暂缓与 C3（身份落地前零行）/C4 一致，身份面不得以「先修个弱版」绕行（REM-01 教训）。

**F. 探针 6（= #4 回执表并发原子性）= RECORD-CONFIRMED（原文要点录入）**：

- 默认 timeout：**8/8 写成功、零 lock 异常**；658 次交错读**零撕裂、零异常** ⇒ 「无撕裂」面证实（与 register §二十一 L592「零 lock 原语」并读：无显式锁原语、简单写路径下亦未见撕裂）。
- **但两项缺陷实证**：①单 metadata key = **last-writer-wins 静默覆盖**（7/8 写被顶掉、**无痕迹**）= **丢写缺陷**；②timeout=0 时 7/8 **裸抛** `sqlite3.OperationalError「database is locked」` = 违编码化错误契约（C5 适用说明①族）。
- **安全域读数**：丢写同时是**新并发语义面**——多写者同 key 的语义必须定义为「**冲突即拒**（定义错误）」而非「静默覆盖」：**静默 = 敌**（静默覆盖与 c8/c9 静默并入、下游静默过滤同族，见 §4.3 反例）；裸抛属 C5① 错误契约族，与 P1「claim() 裸抛」、P2-B「输家裸 None」三形态同族。
- **处置分轨（录入）**：P6-A（CAS / 冲突即拒定义错误、无静默消失）+ P6-B（锁超时包装定义错误）已并入修复卡。P2-B/P3-B（**需求表**面）与 P6-A/P6-B（**回执表**面）分属两面、各自修复、互不替代（§7.4-D-续 已记分面）。

**G. 终格记**：#3 → **已解除**（敞口实测证实；前提变化标注见 §7.2）；#4 → **部分解除**（无撕裂已证；丢写 + 裸抛缺陷证实，待 **P6-A/P6-B** 落定验证后终格「已解除」）。#7 / #8 照旧（在途 / 部分解除）。修复卡群 **FIX-W06-GAPS + P4-SCOPE + P5-a/P5-c + P6-A/P6-B** 落定知会随后，届时按事实更新、**不预判验收**。

**本节不改动**：裁定正文 §1–§6、条件 C1–C8、`存疑项__initial` 8 条原文——全部一字未动。

---

**签署行（模拟）**：TIER-2 外部方 #2「安全 reviewer」（owner 全权授权 role-play）——**模拟裁定，待 owner 终确，非外部方真实签署**。
**裁定**：OPEN-6 = **CONDITIONAL**（条件 C1–C8）；OPEN-4 安全域份额 = 附裁（§4.4），待联署。

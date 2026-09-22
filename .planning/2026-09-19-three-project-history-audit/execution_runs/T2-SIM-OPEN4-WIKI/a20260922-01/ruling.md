# 模拟裁定（owner 全权授权 role-play）· 待 owner 终确 · 非外部方真实签署

> **性质声明**：本文件系 owner 全权授权的**模拟裁定**（TIER-2 外部方 #1「wiki 来源审核 owner」角色扮演），将提交 owner 终确（ratification）。本文件**不是**外部方真实签署，**不得**被引用为「TIER-2 已签」。本裁定不修改任何卡载体、任何产品源码、任何门；落点仅为本文件。

---

## 1. 我的身份与管辖域

**wiki 来源审核 owner**——管辖来源审核（source review）的数据溯源与审核完整性：审核判定如何产生、以何工件承载、由谁署名、何时失效；不管辖安全判定归属（OPEN-6）、不管辖 RF 消费接口（OPEN-5）、不管辖签字信任根参数（函 B）。

**覆盖映射核验（照函件自身章节头）**：`outward_requests/README.md` 第 18 行记函 A 覆盖「**T2-1**(OPEN-4) · **T2-2**(OPEN-6) · **T2-3**(OPEN-5)」；`A_DW06_OPEN-4-5-6.md` 第 5–9 行表头逐字记：
- 「**OPEN-4** | 审核方法、reviewer 身份绑定、`source_sha256` × `policy_hash` 双绑定、策略变更后旧回执失效判定 | **wiki 来源审核 owner** + **安全 reviewer**」
- 「**OPEN-5** | 消费 / 恢复命令与原请求恢复接口 | **RF 消费 owner**」
- 「**OPEN-6** | `not_detected` / `detected_and_ignored` 的判定归属 | **安全 reviewer**」

⇒ **T2-1 / OPEN-4 ↔ wiki 来源审核 owner 成立**（与安全 reviewer 联席）。本裁定**只裁 OPEN-4**（4a/4b/4c）；OPEN-5、OPEN-6 虽在同一函内，**不是**本方的项，一字不裁（见 §6 第 5/6 条）。

---

## 2. 裁定原文引用（我被问的问题，逐字）

以下引自 `outward_requests/A_DW06_OPEN-4-5-6.md`（签发哈希 `cd88bd4cece0271d41ee5ccca31b9b70a2a6adcaa65502c5ca7a5a8717e6cde2` / 11546 B，见 `_provenance.json.issuance_2026_09_22`）：

> ### 1.1 待裁的三件事
>
> 请逐项给出：**选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 拒绝的替代方案**。
>
> **(4a) 审核方法**
> 一次 source review 的「判定」如何产生、由谁产生、用何种可复核的形式落盘？
> 卡的原始期望是：需求须携带「source/hash/policy、缺口、原请求绑定、下一动作」，
> 且**不得伪造 review**。请裁定：
> - 审核结论以什么工件承载（DB 行 / JSON 收据 / 两者）？
> - 判定枚举是否就是 `{not_reviewed, not_detected, detected_and_ignored, reviewed_ok, …}`？
>   请给出**权威闭集**。
>
> **(4b) reviewer 身份绑定**
> 「谁做了这次审核」如何被证明？
> - 身份以何为主体（人 ID / 角色 / 进程 + 凭据）？
> - 是否需要不可伪造的签名链？若需要，与 **I-08-A 的签字信任域**（函 B）是同一套还是两套？
>   ⚠️ **跨函耦合**：若两套，会产生两个信任根。请明确表态。
>
> **(4c) `source_sha256` × `policy_hash` 双绑定，以及策略变更后旧回执的失效判定**
> - 旧回执在**哪一种**变更下失效：source 字节变？policy 内容变？policy 版本号变？
>   角色集合变？请求身份变？
> - 失效是**立即**还是**下次读取时**？
> - source 未变而 policy 变更时，旧回执是**作废重审**，还是**增量补审**？二者对已下游消费的工件的处理不同。

附带须复核项（§1.2 逐字）：

> - **OPEN-2 已由 owner 裁定为选项 A**：幂等键**必须含请求身份**（`source_sha256 + review_policy + role_set + request identity`，request identity 覆盖 `as_of_date` / `target` / payload digest）。⇒ OPEN-4 的失效判定**须与该键口径自洽**，请复核有无冲突。
> - **OPEN-2b 已由 owner 裁定**：`role_set` 权威来源维持 `RF_W06_ROLE_SET`，规范化形式为**排序去重的逗号串**（候选默认已统一为 `"normalized,sections"`）。

回执纪律（§4 逐字要点 + `README.md` 共同约束）：每项须含**选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案**；「请勿以『按最佳实践』代替决定」；不在函上签字；不伪造证据；裁决前不写规范数值。

---

## 3. 【裁定】**CONDITIONAL**（有条件裁定）

| 子项 | 裁定 |
|---|---|
| **4a 审核方法（载体 + 权威闭集）** | **APPROVE（就本子项无条件生效）**：单一权威载体 + 三值闭集，见 §4.1 |
| **4b reviewer 身份绑定** | **CONDITIONAL**：方向已定（角色+具名主体+进程凭据、不可伪造签名链、与函 B **同一套**信任根），但签名链的可核销落地**取决于函 B 信任根出裁且实测存在**，见 §5 条件 C4 |
| **4c 双绑定与失效判定** | **APPROVE（就本子项无条件生效）**：读取时失效、policy 内容变⇒作废全量重审，见 §4.3 |

总体取 **CONDITIONAL** 而非 APPROVE：4b 的「不可伪造」在今天的产品与今天的信任根现状下**无法成立**（详见 §4.2 反例与 §7 第 2/5 条），我不能在归属可伪造的现状上签「审核方法已定」的完整核准。

---

## 4. 理由（逐子项六要素；全部引自今日实读的仓内证据）

### 4.1 (4a) 审核方法

**选择**
1. **承载工件 = 「两者」的受限形式**：唯一权威载体是 CW `documents.metadata_json["prompt_injection_review"]` 的 **DB 行内 JSON 收据**（`PROMPT_INJECTION_REVIEW_KEY`，schema_version `"1.0"`）；独立 JSON 收据文件**只允许**作为字节级导出副本（证据附件），**永为非权威**。
2. **判定如何产生**：由版本化检测器产生（ZR-302 `scan_text`，规则集哈希入证），经 `record_prompt_injection_review` 写入（fail-closed 写入校验）；「可复核形式」= 回执内 `evidence_sha256` + `source_sha256` + `policy_hash` 三哈希可被第三方独立复算比对。
3. **权威闭集（三层，冻结）**：
   - 回执**可写**状态闭集 = `{not_detected, detected_and_ignored}`；
   - **评估层**状态闭集 = `{not_reviewed}`（仅评估输出，**永不可写入回执**）；
   - 缓存态闭集 = `{hit, ignored, expired, tampered, absent}`；
   - 整体判定词汇闭集 = **`{not_reviewed, not_detected, detected_and_ignored}`**。
4. **`reviewed_ok` 不在闭集内，拒绝加入**（见反例 (ii) 与 §6 第 1 条）。

**理由**：产品现状已具备该形态且写入侧 fail-closed——`company-wiki/src/company_wiki/source_catalog/prompt_injection.py`（今日复算 sha256 `7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618`，与 `I-06-B/a20260919-01/handoff.json` 的 `input_hashes` 记录**逐字符合**，即 2026-09-19 以来未漂移）第 4–12 行明文：收据「lives in `documents.metadata_json["prompt_injection_review"]`」、「Absent receipt == `not_reviewed` … The writer validates fail-closed」、第 23–24 行 `PROMPT_INJECTION_REVIEW_STATUSES = frozenset({"not_detected", "detected_and_ignored"})`、第 53–56 行写入非闭集状态即抛错。FC-905（同文件第 3–4 行）明文「The capture safety status must come from an explicit scanner/reviewer receipt, **never from a consumer's assumption**」。单一权威载体是「不得伪造 review」在存储层的直接推论。

**反例**
- (i) **双权威载体必然分叉**：同类分叉已实测——`I-06-A/a20260919-01/handoff.json` `frozen_vs_measured.c8_c9_same_source_different_request`：两个真实 CLI 请求返回**同一** `demand_id`，而行内 `request_sha256` 停留在**第一个**请求的 `d8afcf319185da071bd364c5d2ef6dfa9264e8bbc929ee737b9cefab963bdd62`，第二个请求实际哈希为 `4bddf9e6963e7d0474e754a89a1a184d8315b059410e98d34dd3e02375e10b84`——两处记录对同一事实给出两种答案。回执若 DB 与文件双权威，同样的「静默不一致」将在审核层重演且无从收敛。
- (ii) **`reviewed_ok` 无产生者、可伪造绿**：今日对 `company-wiki/src/company_wiki/source_catalog/` 全量检索，`reviewed_ok` 零命中；检测器只产 `not_detected`/`detected_and_ignored`（guard 第 105–106 行）。且 `I-06-B/.../after/review-input-and-evidence.json` 第 43–50 行的 FAIL 样本显示：**空文本**也返回 `not_detected`（「Empty text has no injection patterns; this is not a faked result」）——可见任何不经检测器输出的「通过」都只是断言，恰是 FC-905 禁止的 consumer assumption。
- (iii) **独立文件若为权威将绕过写入校验**：`I-06-B/.../after/review-invalidation-matrix.json` INV-5（第 46–55 行）：坏 schema 收据必须按 absent fail-closed；该保障由 DB 写入/读取校验承载，文件系统副本无此保障。

**兼容影响**：零 schema 变更（"1.0" 已含全部所需字段，prompt_injection.py 第 116–126 行）；闭集任何扩充必须 `schema_version` 升级（第 59–62 行强校验版本）并**重新送裁**，不得静默加值。

**恢复规则**：凡发现落在权威载体之外的「review 结论」工件，一律降为 `not_reviewed` 重审；覆盖写旧收据前必须留档旧收据哈希（条件 C6），否则该次覆盖视为无效审核事件。

**拒绝的替代方案**：(a) DB 行与 JSON 文件**双权威**——拒（反例 (i)）；(b) **仅**文件收据——拒（脱离写入校验，与 prompt_injection.py 第 4–5 行的载体约定冲突）；(c) 闭集加入 `reviewed_ok`/`passed`/`safe`——拒（反例 (ii)）；(d) 消费方按上下文推断状态——拒（FC-905 明文禁止）。

### 4.2 (4b) reviewer 身份绑定

**选择**
1. **身份主体 = 「角色 + 具名主体 + 进程凭据」三元组**（可验证主体引用），**不是**裸人 ID、**不是**裸角色、**不是**裸进程；单独任何一项都不足以归责。
2. **需要不可伪造的签名链：需要。** 且与 **I-08-A 的签字信任域（函 B）是同一套**——**明确表态：同一套，不设第二信任根**。
3. **签名链的具体信任根参数（权威副本位置、同步、冲突裁决、缺失行为）不在本裁定授予**——那是函 B `T2-9 / OPEN-D1` 的裁量（函 B 第 7 行：「权威信任根位置（repo 配置文件 / 机器级只读路径 / OS keystore）| **跨仓双方**（安全/运维提选项，项目 owner 择定）」）。本裁定只约束：来源审核签名**必须挂靠**该唯一信任根。
4. **过渡期规则**：信任根建成并核验前，任何回执**不得**宣称为「已签名审核」；只能记为「未签名归属记录」，不得作为完成 D-W06 审核要求的凭据用于产品晋级。

**理由**：我域利益的核心是「谁审的」可归责、不可抵赖、不可伪造。今天的实况相反——`prompt_injection.py` 第 57–58 行对 reviewer 仅校验**非空**；`I-06-B/a20260919-01/decision.md` 第 44 行自认「reviewer 身份绑定：当前 reviewer 字段为**自由字符串，无身份验证**」。两个信任根 = 两套轮换/吊销纪律 = 同一回执跨域不可互证，且与 4c 的失效规则直接冲突（吊销在 A 域生效、B 域仍绿），这是溯源完整性最忌的分叉。函 B 现状佐证唯一根尚不存在：函 B 第 28 行「**不存在可用于生产验证的信任根**」、第 240 行「信任根文件仍实测缺席……与本函 P1『默认零可信签名者』的设计默认一致」——因此「同一套」的表态与「过渡期不得宣称已签名」必须并存，缺一即伪造。

**反例**
- (i) **自由字符串可零成本伪造归属**：`I-06-B/.../after/review-input-and-evidence.json` 第 17 行实测收据 `reviewer: "zr302-test"`——任何有 DB 写权限的进程都能以该名义（或冒用任何名义）调 `record_prompt_injection_review` 写出「审核通过」收据，写入校验（第 57–58 行）只查非空，**不查真伪**。
- (ii) **双信任根的失效判定不可全域一致**：某凭据在 root A 下被吊销后，其在 root B 侧签发的回执在另一域仍验签通过——「旧回执何时失效」（4c）将因信任根不同而答案不同，规则体系自相矛盾。

**兼容影响**：`reviewer` 字段语义收紧为「可验证主体引用」，属 ZR-302 的 additive/N-1 路线（同文件第 86–90 行先例）；旧自由字符串回执按 INV-6 同类 fail-closed 处理（`review-invalidation-matrix.json` 第 56–65 行：「Legacy receipt cannot be proven fresh → fail closed」——归属不可证明的回执同理不可晋级）。签名载体格式（canonical bytes、签名字段名、schema_version 升级）待函 B 出裁后另行落定，**本裁定不预写一个字节的格式**。

**恢复规则**：凭据吊销/轮换 ⇒ 其签发回执在**下次读取时** fail-closed 为 `not_reviewed`（与 4c 时机一致）；信任根缺失 ⇒ 按函 B P1「默认零可信签名者」处理，回执保留为历史记录但不可作为审核凭据消费。

**拒绝的替代方案**：(a) 来源审核域**自建**独立签名体系——拒（第二信任根，正是本问警告项）；(b) 维持自由字符串 + 事后审计——拒（归属可伪造 = 伪造 review 零成本，直接违反卡的「不得伪造 review」）；(c) 仅以进程 ID / 主机名为身份——拒（可复制、不可归责到人/角色）；(d) 由本方现在指定信任根位置与格式——拒（越权预占函 B `T2-9 / OPEN-D1` 的裁量，且该问明文要求「跨仓双方」提选项、owner 择定）。

### 4.3 (4c) `source_sha256` × `policy_hash` 双绑定与失效判定

**选择**
1. **失效触发（逐问作答）**：
   - source 字节变（`source_sha256` 不符）⇒ **失效**（`tampered` → `not_reviewed`）；
   - policy **内容**变（`policy_hash` 不符）⇒ **失效**（`ignored` → `not_reviewed`）；
   - policy **仅版本号变、内容哈希不变** ⇒ **不失效**（绑定字段本就是内容哈希 `policy_hash`，prompt_injection.py 第 86–90 行；检测器对同一规则集字节是确定性的——I-06-B `decision.md` 第 38 行「`scan_text` 是确定性的、基于版本化规则集的扫描器」）；但版本号变化必须留痕可查；
   - `role_set` 变 ⇒ **回执不失效**；
   - 请求身份变 ⇒ **回执不失效**。
   （后两者：回执是 **source×policy 域**的，不是请求域的；请求身份按 OPEN-2 选项 A 入 **demand 键**，产生新 demand，新 demand **复用**仍有效的回执——即 I-06-B `handoff.json` P2 已实测的 `cache_state=hit, reason='receipt fresh and bound'`。）
2. **失效时机**：**下次读取（评估）时**、读取时 fail-closed（`prompt_injection_guard.py` 第 144–170 行 `_binding_mismatch` 与过期判定均为读取时计算；INV-1…INV-7 七个场景全部是读取时语义）。回执字节**保留**为审计记录，不删除、不静默改写。**不做立即批量失效**（无后台调度——与 OPEN-3 已裁「不得起后台 scheduler」自洽）。
3. **source 未变而 policy 变更 ⇒ 作废重审（全量）**，**拒绝增量补审**。已下游消费的工件：旧回执作为**历史记录**保留（证明当时消费有据），但该 source 在新 policy 下自 `policy_hash` 变更时刻起回到 `not_reviewed`，下游（I-05-B 消费、I-06-B 恢复）必须按 FC-905-b 阻断，直至新规则集下的**一次完整重审**通过。

**理由**：绑定字段决定失效域——收据只绑 `source_sha256` 与 `policy_hash` 两哈希（guard 第 10–18 行文档头、`_binding_mismatch` 第 144–154 行逐一比对二者），把 role_set/请求身份耦合进回执绑定会摧毁跨请求缓存复用（P2）语义。全量重审的理由：新回执的 `evidence_sha256` 必须对应**新规则集下的一次真实完整扫描**；增量补审产出的「结论」背后没有这样一次运行，按 FC-905（「must come from an explicit scanner/reviewer receipt」）就是伪造 review。读取时失效的理由：产品语义即如此（evaluate 惰性判定），且立即失效需要枚举全部回执与消费点的后台机制，被 OPEN-3 明文禁止。

**反例**：
- STALE（`run1_results.json.STALE_byte_change`）：`p.15→p.16` 一字节变 ⇒ `cache_state=tampered, status=not_reviewed`——source 字节变必失效，已实测 VERIFIED；
- N2b（`run1_results.json.N2b_ignored_policy`）：`policy_hash='c'*64` ⇒ `cache_state=ignored, status=not_reviewed`——policy 内容变必失效，已实测 VERIFIED；
- **增量补审的伪造绿**：规则集新增一条 exfiltration 模式，若「仅对新规则补审」而不重扫旧文本，新规则对旧文本中既有注入的命中将永远不被发现，回执却焕然一「绿」——这正是本域最不能容忍的假绿；
- c8/c9/c10（同 §4.1 反例 (i)）：若把请求身份误当回执绑定、或把回执绑定误当 demand 键，静默合并（`request_sha256` 停留 `d8afcf31…`）必然重演。

**兼容影响**：**与 OPEN-2 选项 A 无冲突，复核结论为「自洽」**——两者键域不同、各司其职：**demand 键 = 请求域**（`source_sha256 + review_policy + role_set + request identity`，据 `I-06-A/handoff.json` `rulings_applied.D-W06_OPEN-2`）；**回执绑定 = 来源域**（`source_sha256 × policy_hash`，prompt_injection.py 第 116–126 行收据**不含**任何请求字段）。实施侧两条红线：**不得**把 request identity 塞进回执绑定（P2 复用被破坏、语义倒退）；**不得**拿回执绑定当 demand 键（c8/c9/c10 静默合并重演）。INV-6（无绑定旧回执按 tampered fail-closed）维持不变。TTL 过期路径（guard `expired`）维持现产品行为；**TTL 的数值不由本裁定规范**（I-06-B 矩阵第 32 行的 3600s 只是该次测试取值）。

**恢复规则**：重审产生新回执（新 `evidence_sha256`）覆盖写入，旧收据哈希须先留档（条件 C6）；回执失效**不**自动关闭对应 demand、demand 关闭也不改写回执（C5_C6 实测：source 变更后旧 demand 保持 open、2 条 active——两域独立，见 `I-06-A/handoff.json` `C5_C6_changed_source_hash`）。

**拒绝的替代方案**：(a) policy **版本号**变即失效——拒（版本号不是绑定字段；内容哈希不变则检测确定性不变，无谓重审且与 guard 实现相悖）；(b) role_set/请求身份变即失效回执——拒（请求域耦合进来源域，摧毁 P2 复用，且与 OPEN-2 A 的键域划分冲突）；(c) **立即**批量失效——拒（需后台调度，OPEN-3 明文禁止；且无法枚举全部下游消费点）；(d) **增量补审**——拒（伪造 review，见反例）。

---

## 5. 条件逐条（每条可检验）

- **C1（载体唯一性）**：审核结论的唯一权威载体为 `documents.metadata_json["prompt_injection_review"]`（schema_version `"1.0"`）。**检验**：产品代码中 review 结论的写入只经 `record_prompt_injection_review`（对 CW 仓 grep 可验）；任何导出 JSON 均带 non-authoritative 副本标注。
- **C2（闭集冻结）**：判定词汇闭集 = `{not_reviewed, not_detected, detected_and_ignored}`（三层划分见 §4.1）。**检验**：`PROMPT_INJECTION_REVIEW_STATUSES` 保持 `frozenset({"not_detected", "detected_and_ignored"})`（prompt_injection.py:23–24）；向回执写入 `not_reviewed` 或任何闭集外值被拒（:53–56）；新增状态必须 `schema_version` 升级 + 重新送裁。
- **C3（双绑定必填）**：凡用于晋级/消费的回执必须同时携带 `source_sha256` 与 `policy_hash`（各为 64 位小写 hex）。**检验**：record 调用两参均非 None（prompt_injection.py:64–65、123–126）；无绑定回执维持 INV-6 fail-closed（`tampered`，`review-invalidation-matrix.json:56–65`）。
- **C4（身份绑定 + 单一信任根）**：`reviewer` 须为「角色 + 具名主体 + 进程凭据」可验证主体引用，且来源审核签名挂靠**函 B / I-08-A 的同一信任根**。**检验**：在函 B（`T2-9/OPEN-D1` 等）出裁且信任根文件实测存在之前，任何回执不得标称 signed、不得以「已签审核」名义晋级；自由字符串 reviewer 不得出现在晋级路径（现产品 prompt_injection.py:57–58 仅非空校验，即为待改点；I-06-B decision.md:44 已自认该缺口）。
- **C5（失效语义落地）**：按 §4.3 选择实现失效判定（读取时 fail-closed；policy 内容变⇒全量作废重审；版本号单独变不失效；role_set/请求身份变不动回执）。**检验**：I-06-B 可失败用例至少覆盖 INV-1 / INV-2 / INV-3 / INV-6 / INV-7（既有）**加两条新正例**：① policy 版本号变、内容哈希不变 ⇒ 仍 `hit`（不失效）；② role_set / 请求身份变 ⇒ 原回执仍 `hit`、demand 按 OPEN-2 A 得新键。这两条正是本裁定解锁给 I-06-B 的可失败测试清单。
- **C6（覆盖留痕）**：`record_prompt_injection_review` 覆盖旧收据前，须在审核执行事件记录中留档旧收据的 sha256（形态参照 `I-06-B/.../after/review-execution-events.json`）。**检验**：任一覆盖事件可查到前后两收据哈希；缺失则该次审核事件无效。

---

## 6. 不予授予项（明确列出未同意的部分）

1. **`reviewed_ok` 及任何新增「绿色」状态——拒绝授予**（无产生者、可伪造绿；除非新检测器 + schema 升级另行送裁）。
2. **第二信任根 / 来源审核域独立签名体系——拒绝授予**；同时**不授予**共享信任根的任何参数（位置、权威副本同步、冲突裁决、缺失行为、函 B §5 的 α/β 择定）——那是函 B 收件方的职权，本裁定不预判一字。
3. **增量补审——拒绝授予**（只认全量重审）。
4. **文件型 JSON 收据的权威地位——拒绝授予**（仅限非权威副本）。
5. **OPEN-5 四件（消费入口 / 恢复接口 / 持久化介质 / 权限）——不属本方职权（T2-3，RF 消费 owner），一字不裁。**
6. **OPEN-6（`not_detected` / `detected_and_ignored` 的判定归属、`detected_and_ignored` 的理由与授权记录、下游可见/过滤语义）——不属本方职权（T2-2，安全 reviewer），一字不裁。** 本裁定只授予**词汇与载体**（4a），**不授予判定归属**——尤其「`detected_and_ignored` 由谁署名」仍待安全 reviewer。
7. **任何数值规范（回执 TTL、`W`/`T`/`L` 等）——不授予**（README 共同约束第 4 条；本裁定全文未写入任何规范数值）。
8. **UNRATIFIED 候选实现（`I-06-A/.../iso/candidate`）的晋级——不授予**：其幂等键不含请求身份、已被记为 known-insufficient（`I-06-A/handoff.json` `blocked_by` 第 3 条原文：「the candidate's key does NOT satisfy the newly-ruled OPEN-2 option A … must be revised before it can be promoted」），且其 review/receipt 路径不因本裁定自动变绿。

---

## 7. 未验证 / 存疑项（诚实清单）〔`存疑项__initial`：2026-09-22 初裁原文，8 条逐字保留；解析态见 §7-补〕

1. **本裁定系 owner 全权授权的模拟裁定，待 owner 终确；非外部方真实签署。** 在 owner 终确前，不得登记为「TIER-2 已回执」。
2. **函 B 全文未逐字通读**（仅检索其 D7/信任根相关行：第 7、28、96–108、240 行）。若函 B 已有与「同一信任根」相反的在案裁定，本裁定 §4.2 表态须以该裁定为准复核后方可终确。
3. **并发场景未验证**：`I-06-A/handoff.json` `open_questions` 第 7 条明记「候选未验证 additive migration / 并发 claim / lease 过期」——并发下两进程同时写同一 document 回执的交错行为不在本裁定的证据范围内。
4. **阻断文案跨仓文本断言未排查**（同上 `open_questions` 第 6 条）——不属本域，未核。
5. **RF 侧源码今日未读**：今日仅复算核对 CW 侧两文件（`prompt_injection.py` = `7b22f239…139618`、`prompt_injection_guard.py` = `f900a13d…0b9c08`，与 I-06-B `input_hashes` 记录一致）；RF `source_preparation.py` 曾在他卡期间漂移（`5ec16eaf…` → `8070d60d…`，`I-06-B/handoff.json` `current_source_hashes`），本裁定未核其实时字节。
6. **`w06b_review_harness.py` 代码本身未逐行审**——我读的是其结果工件（`run1_results` 引证、`review-input-and-evidence.json`、`review-invalidation-matrix.json`、`handoff.json`、`decision.md`）；C5 的两条新正例在该 harness 中是否易实现，未经代码级核实。
7. **TTL 数值与过期策略的合理性未审**（guard `expired` 路径维持现状即好；数值不属本裁定）。
8. **`detected_and_ignored` 的下游可见/过滤语义未预判**（OPEN-6 三问之一，安全 reviewer 职权）——本裁定的词汇授予不构成对其归属或消费语义的任何暗示。

---

## 7-补. 存疑项__reverified（2026-09-22 追加解析态：父方实证批 + OPEN-5 方三点回文）

> **本节性质**：对 `存疑项__initial`（§7，8 条逐字保留）逐条标注 **已解除 / 仍敞口 / 前提变化**，并收录对 OPEN-5 方三点回文的答复（含扫描范围定义）。**裁定正文（§1–§6）与条件 C1–C6 一字未改**；本节不新增、不删改任何待裁项，不构成对 §6 不予授予项的任何松动。

| # | 初裁存疑项（索引） | 解析态 | 依据 |
|---|---|---|---|
| 1 | 模拟性质、待 owner 终确 | **仍敞口（结构性，按性质持续）** | 待 owner 终确这一事实不因任何实证批改变；终确前不得登记为「TIER-2 已回执」的纪律维持 |
| 2 | 函 B 全文未逐字通读、恐有相反裁定 | **已解除（无矛盾）** | 函 B 信任根相关行全扫（L7「T2-9/OPEN-D1 权威信任根位置…**跨仓双方（安全/运维提选项，项目 owner 择定）**」、L28「**不存在可用于生产验证的信任根**」、L96–108 OPEN-D1 四问、L240「信任根文件仍实测缺席…默认零可信签名者」）：**无任何相反在案裁定**——根参数整体悬置为 OPEN-D1 待裁项，与 §4.2「归函 B T2-9/OPEN-D1、不预占」完全自洽；「同一信任根 + 过渡期不称已签」双句并存与 L28/L240 现状吻合。前提无变化 |
| 3 | 并发写回执交错行为未验证 | **已解除（原疑=未验证）+ 前提变化（部分证实）+ 仍敞口（残余收窄挂账）** | 探针 6（`7073a5f9`）回报 = RECORD-CONFIRMED：658 交错读**零撕裂** ✓；但**单 key 静默覆盖丢写 7/8** + `timeout=0` 裸抛 `OperationalError`——「未验证」缺口已闭，缺陷面实证（部分证实：无撕裂但丢写/裸抛）。本方注记：丢写缺陷 = 「静默覆盖无留痕」的写侧形态，与 §4.1 反例 (i) 同族（静默分叉/静默覆盖正是溯源完整性最忌）；修复卡 P6-A（冲突即拒 + 定义错误）**满足并强于** C6 意图（C6 = 合法覆盖须留痕可审，P6-A = 同 key 冲突直接拒，二者互补）——**无异议**；P6-B（错误包装）属错误契约面。残余敞口收窄 = **P6-A/P6-B 修复落地未验**。**出处勘正**：原文 = `I-06-A/handoff.json:147`（`open_questions` 第 7 条，非 I-06-B）；候选本体 = `I-06-A/…/iso/candidate/processing_demand_store.py` + `w06a_candidate_patch.py` |
| 4 | 阻断文案跨仓文本断言未排查 | **已解除（原疑=排查缺口）+ 前提变化（UNPINNED 证实）+ 仍敞口（收窄为 P4-SCOPE 留置）** | 探针 6 组回报：排查缺口**已补**；断言面 **UNPINNED 证实**（跨仓阻断文案文本断言未钉住 = 可静默漂移，与 c8/c9/c10 静默不一致同族）、「C8 必要性坐实」（转述用语：钉住文案的探针/条件之必要性获实证）；残余**钉住留置 P4-SCOPE**（范围/钉法归修复卡轨道定义，本方不越域）——敞口由「无界未排查」收窄为「有界留置」，方向 fail-safe。**出处勘正**：原文 = `I-06-A/handoff.json:146`（`open_questions` 第 6 条，非 I-06-B） |
| 5 | RF 侧源码今日未读 | **已解除** | 父方实证闭环：`source_preparation.py` blob 链 `b34097dd=65aadf17`→`1dbae639=884b5f4d`→`ff7429e5=fabdf129`→`70dd9f6e=95df2661=37a3eeae`→**`ec307d20=HEAD=91a6dc32`==现盘**；漂移三因（ZR-701 特性工作 / EOL 表示差 `8070d60d`(worktree CRLF) vs `37a3eeae`(blob LF) / REM-49 单行注释修 1085/1085 平价证）——初裁所记 `5ec16eaf→8070d60d` 即第一、二因的组合，良性。本方已核 CW 两文件（`7b22f239…`/`f900a13d…`）经父方独立直测逐位相符（6619 B/8382 B） |
| 6 | `w06b_review_harness.py` 代码未逐行审 | **已解除（父方逐行审 618 行 + 本方独立通读全文复核）** | 逐条相符（两处行号微漂移已订正）：①importlib 直载 iso/cw 两模块（:29–60）；②W06-1 幂等键 = `sha256(canonical_json({entity, as_of_date, document_kind, source_sha256, role_set}))`（:81–99，**role_set 在键内** :93）；③同请求→reuse、同键异载荷→`IdempotencyViolation` fail-closed（:117–143，实测路径 :511–518）；④P1 写入侧已带双绑定（:251–252）；⑤W06_1 键差用例（entity/as_of_date 变→不同键，:508–522）。**C5 两新正例实现成本 = 低**（各约 10 行、纯测试追加、零产品改动）：①「policy 版本号变、内容哈希不变⇒仍 hit」——`evaluate_review` 签名无版本入参（guard:180–188），绑定轴只有 source×policy（guard:144–154），语义天然成立，测试=同 `policy_hash` 复评断言仍 `hit`；②「role_set/请求身份变⇒原回执仍 hit + demand 新键」——键差部分 W06_1 已测（:508–522）+ role_set 在键内（:93），补「改 role_set ⇒ 键变 + 同文档 `evaluate_review` 仍 hit」组合即得。**本方三点版本号语义澄清（防测试误实现；C5 原文一字不动）**：(α) policy/规则集版本号**不是绑定字段**，单独变 ⇒ 不失效（=C5① 场景；若版本号纳入哈希载荷则属「内容变」⇒失效，测试须据此构造）；(β) 收据 `schema_version` 是**有效性门**而非绑定轴（guard:124–125：非 "1.0" ⇒ absent fail-closed）——契约升级后旧回执 fail-closed 属设计内（与 4a「扩充须送裁」一致），不属 C5① 范畴；(γ)「evaluate 不看版本号」仅指签名无版本入参，**不**指跳过 `schema_version` 校验。**交叉发现（如实转录，不越域）**：(i) N3/N3b/N3c（:406–464）只测**写入侧格式非法**拒绝（`"not-a-valid-hash"`、空 reviewer、`"totally_safe"`）——**格式合法虚构假回执**（64-hex 形合 evidence_sha256+非空 reviewer+合法 status）未测，与在途探针之面对应；本方注记：`record_prompt_injection_review` 只验**形式**不验**证据存在**，格式合法伪造收据可过写入校验——即 C4（身份绑定）与 C6（覆盖留痕）不可松的理由；(ii) N1 的 `detected_and_ignored` 由 `scan_text` 直接铸造入收据（:297–322，`status=inject_scan.status`）——即 OPEN-6 裁定「事实/处置分离」的整改点（其 C1），**不影响** §4.1 闭集定义（值仍属可写闭集，铸造者须变）；(iii) harness 自身以 `reviewer="zr302-test"`（:248/:302/:545）/`"fake-reviewer"`（:411）自由串写回执——与 §4.2 反例 (i) 互证 |
| 7 | TTL 数值/策略合理性未审 | **仍敞口（设计性敞开，非缺陷）** | 数值纪律=「数值未定前不入规范」；本裁定全文未写规范数值是**正确的克制**。TTL 归数值裁定轨道（OPEN-5 方同样拒了 3600s 夹具值）。按「设计性敞开」记录 |
| 8 | `detected_and_ignored` 下游可见/过滤语义未预判 | **已解除 + 前提变化** | **前提变化**：OPEN-6 已由安全 reviewer 出裁——归属=检出（安全事实）/忽略（安全处置授权，来源审核可请求、**不得自署**）；授权元组必填；下游=**可见 + 强制标记 + 禁过滤**，需 clean 的下游 fail-closed，无 warn-only/降级/env bypass。与 §4.1 闭集（`detected_and_ignored` 可写但非绿）方向一致。§6 第 6 条职权边界声明**维持**（判定归属仍归安全 reviewer，本裁定只授词汇与载体）；OPEN-4 联署闭合条件（4a 闭集文本）双方文本现已具备 |

### 回 OPEN-5 方 §6.3 三点回文

- **(a) 主相容——确认**：本裁定「policy 变⇒作废重审 + 读取时 fail-closed」与其消费底线无冲突。不改一字。
- **(b) 分域成立——确认**：「role_set/请求身份变不动回执」与其 `request_sha256` 输入绑定分属**回执域**（source×policy）/ **demand 键域**（请求域），与本裁定 §4.3「兼容影响」两条红线一致。不改一字。
- **(c) 扫描范围定义（本方作答，回文确认）**：**审核扫描范围 = 被绑定 `source_sha256` 之整篇字节 × policy 全文扫描，与 `role_set` 无关（非按角色裁剪）**。产品字节实证（今日实读）：
  1. `prompt_injection_guard.py:85` `scan_text(text: str, ruleset_hash: str = RULESET_HASH)`——签名**无** role/section 参数；
  2. `prompt_injection_guard.py:99–106` 对 `text.lower()` **全文**逐模式 `re.search`，无任何分节/分角色逻辑；
  3. `ScanResult`（guard:67–73）仅 `status/matches/ruleset_hash`，**无角色字段**；
  4. 回执 schema（`prompt_injection.py:116–126`）**无角色字段**，只绑**整篇** `source_sha256`（`review-input-and-evidence.json` 各样本 sha256 均为全文哈希）；
  5. `tests/unit/test_prompt_injection_guard.py` 全文检索 `role|section|normalized` **零命中**——产品测试亦无角色化扫描概念。

  ⇒ **推论**：回执覆盖 = 被绑定整篇字节的全部可提取子集；`role_set` 扩大 ⇒ 任何新角色可提取的 section 均为**已审字节的子集** ⇒ **无覆盖缝隙**，「role_set 变不动回执」成立。
  **边界前提（明示，供 OPEN-5 方复核）**：上述结论仅在下游**只消费绑定 `source_sha256` 之字节或其子集**时成立（与 I-05-B「消费者读取已验证字节」口径一致）；凡产生**越出绑定字节域**的新字节流（拼接/转码/重组等派生件），该派生件是**新 source**，须独立新回执（否则即 §4.1 拒绝项 (d) 的「消费方推断状态」变体）。OPEN-5 方的消费/恢复接口应据此阻断派生件绕行——接口设计权仍属 OPEN-5 方，本方只给定义不代设计。

### 边界补充记（2026-09-22 第二追加：OPEN-5 方复核结果，按承诺句补记）

> **性质**：OPEN-5 方（T2-3）已在其 `ruling.md` 落定**接受**本方上述边界前提（记为「边界补充记」、无前提变化、不改正文不改判；理由=fail-safe 正确收紧，与其 §6.2 省缺即抛、C7 不越界铸造同族）。以下 4 条系**其接口层定夺**（其域职权），本方按承诺句补记于此、供联署参考；**非本方裁定、不构成对 §1–§6 或 C1–C6 的任何修改**。

1. **覆盖域定义**（其定夺）= 绑定整篇字节 + **可验证逐字子集**（span/offset 可证、`content_sha256_actual==declared`、provenance 绑同一 `source_sha256`——即 I-05-B `verified_read_events` 现有字段，`company_wiki_source.py:240-247`）。
   **本方联署注记（引用抽核，2026-09-22）**：该文件真身 = **RF 仓** `scripts/company_wiki_source.py`（CW 仓无此文件）；`verified_read_events` 字段实证相符（:240–247 docstring、:319–329 实现：`role, artifact_path, content_sha256_actual, content_sha256_declared, bytes_read, source_sha256, read_status, read_at`）。但**现有字段中未见 span/offset 字段**——「span/offset 可证」若指 section 级子集证明，现有载体只能证**整件哈希相等**（actual==declared），section 级逐字子集证明需补字段或另行计算。此差距**不损害**本方边界前提（其边界是字节域级：子集=已审字节之一部），但条 1 措辞与现有字段的差距如实注记，**请 OPEN-5 方复核措辞或补证**（其域内）。
   **OPEN-5 方修订回执（2026-09-22 第三追加，父方转达）**：其已**接受**本方抽核纠正（承认两处不精确：引文未标仓=RF 仓；「span/offset 可证」超前于载体），条 1 改**两层证明形态**：(i) 现行证 = 整件哈希相等（`content_sha256_actual==declared` + provenance 绑同一 `source_sha256`）；(ii) span/offset 级子集证明 = **实现缺口、补字段后启用**，且补字段前凡需主张「子集覆盖」的场景**一律不得主张覆盖**、按其条 2 归派生件路径（新 source、独立新回执）——缺口方向 fail-closed（更严非更松）。其将 **span 字段补充列入实施面**（与其条 4 派生件负例探针同检验面）。本方确认：修订形态与本方「不损害字节域级边界前提」判断一致，措辞差距**闭合**、无异议。
2. **派生件识别条款（增设）**（其定夺）：不能证明为逐字子集的字节流不得继承原回执、不得以「已审源」身份经消费/恢复接口；被当作 source 消费 ⇒ 新 source、独立新回执（独立 `source_sha256` + 独立扫描），fail-closed。
3. **C3 校验对象精确化（明确）**（其定夺）：校验锚 = 原 request 字节（`request_sha256`）+ 绑定 source 原字节（`source_sha256`）；派生/变换字节不构成「正确字节」；判定必须在哈希域做（actual==declared），**禁止**「内容相似/同路径/同名义 provenance」放行（反例：sections 拼接回读、转码后再消费，哈希必≠绑定哈希）。
4. **检验物补充（挂 C3 检验面）**（其定夺）：派生件负例探针——转码/拼接字节流投喂 resume/消费面 ⇒ 必须拒绝或归类新 source，不得复用旧 demand 审核状态。

**对其并采 2+3 的表态**：本方原句「或」为二选一措辞、实现形态本就留于其域（「接口设计权仍属 OPEN-5 方，本方只给定义不代设计」）；其**并采 2+3**（只做 3 不做 2 ⇒ 派生件可伪装新请求复用旧审核状态；只做 2 不做 3 ⇒ 校验对象仍歧义）属其域内 fail-safe 收紧，与本方边界前提一致——**无异议**，无需修改本方任何条款。

**(c) 面终格闭合记录**：OPEN-5 方确认覆盖缝隙担忧解除（本方五点实证 + OPEN-6 全字节定义双确认）。**留置 1 项（新，仍敞口）**：「调用方喂入 = 全字节而非角色切片」未经运行时实测（本方五点为代码级证据；挂 C1 检验面 / 在途探针），OPEN-5 方与本方一致挂账。

### P5 知会记录（2026-09-22 第三追加：探针 5 报告转达——`prompt_injection.py` 产品写入面）

> **性质**：以下为探针 5（P5）对 `prompt_injection.py` 写入面的实测报告（父方转达；本方**未独立复跑**，按转录知会入册）。P5 与本方存疑 #4 相邻但**不替代**——#3/#4 仍以探针 6（`7073a5f9`）回报为准。产品面处置归 owner/修复卡轨道，非本方裁定。

- **P5-a 格式合法虚构 `evidence_sha256` 被收 + 可读回**——**假回执面实锤**；N3「只拦格式非法」成立未收窄 = 本方 #6 交叉发现 (i) 及「`record` 只验形式不验证据存在」注记**双双实测实锤**。
- **P5-b `reviewer="zr302-test-FAKE"` 被收**——**身份可冒用实锤** = 本方 §4.2 反例 (i)（自由字符串零成本伪造归属）的**实测版**。
- **P5-c 无双绑定可写 `detected_and_ignored` 被收**——写入侧敞口，与 OPEN-6 C2 描述吻合；处置「写入侧双绑定强制化」与本方 C3 同向且**更严**（C3 管晋级/消费用途回执，其修法管写入侧）——**无异议**。
- **P5-d 对照 `'ABC'` 精确错误命中 ✓**（探针对照面成立）。

**处置记录（owner「fail 全修」）**：P5-c 写入侧双绑定强制化 + P5-a 证据载荷绑定 = 修复卡即修；**P5-b 身份链 = OPEN-4b / 函 B 信任根依赖、暂缓登记 BLOCKED-on-external**（「无信任根时身份校验 = 伪修复」）——与本方 **C4**「函 B 出裁且信任根实测存在前不得标称 signed」**完全一致**，再次印证 §4.2 过渡期规则的必要性。owner 终确后 C1/C2 授权元组实施即完整堵法（该实施属 OPEN-6 / 产品面轨道，本方只知会不裁）。

**结语**：裁定正文（§1–§6）与 C1–C6 一字未改；`存疑项__initial` 8 条原文逐字保留于 §7。**终格状态**：#2/#5/#6/#8 已解除（#8 含前提变化）；**#3/#4 已终格**（= 已解除原疑 + 前提变化 + 残余敞口收窄挂账：P6-A/P6-B 修复落地未验、P4-SCOPE 留置）；#1 结构性维持（模拟裁定、待 owner 终确）；#7 设计性敞开。其余留置：「调用方喂入=全字节」运行时未实测 1 条；OPEN-5 条 1 措辞差距已闭合。探针 5 终格 = CONFIRMED 3/3（见 P5 知会记录：#6 交叉发现 (i) 与 §4.2 反例 (i) 实测实锤；P5-b = BLOCKED-on-external 与 C4 一致）。FIX-W06-GAPS 落定知会待收。

---

## 8. 落点声明（照函 §4 与共同约束）

本裁定按本模拟任务的限定落点写入 `execution_runs/T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md`，**未在任何函件上签字、未改动任何卡载体（`I-06-A`/`I-06-B` 的 `decision.md`/`handoff.json`）、未改动任何产品源码、未产生任何 status 变化**。函 §4 要求的「写入各卡自己的载体 + `RESPONSES.md` 登记」由编排层照事实转录（**不改一字裁决内容**），转录动作**不属**本模拟方的写入权限范围。

**终确栏（owner 用）**：□ 接受（转录为正式回执） □ 驳回 □ 附改后接受（改动须重走本裁定 §5 条件核验）。

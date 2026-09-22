裁定转录（owner 终确「全部接受」· 转录不改一字）

## T2-1(OPEN-4)
source: execution_runs/T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md
sha256: 37413f7812bbe4aa21948f0f474a2ceac2ad0f778f1a3c5eb4f6b3af7e1d98bb
----- BEGIN ruling body (byte-exact) -----
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

----- END ruling body (byte-exact) -----

## T2-3(OPEN-5)
source: execution_runs/T2-SIM-OPEN5-RF/a20260922-01/ruling.md
sha256: 74f5c83598355bd43627fbf475260babf2da65b869c02196d889d8b11772b234
----- BEGIN ruling body (byte-exact) -----
# 模拟裁定（owner 全权授权 role-play）· 待 owner 终确 · 非外部方真实签署

> 本文件系 owner 全权授权下的**模拟裁定**，供 owner 终确（final confirmation）前审阅。
> 记录性质：**owner-authorized simulated adjudication, pending owner ratification — NOT a real external signature**。
> 落点说明：按任务指令，本裁定落在本 attempt 目录（`execution_runs/T2-SIM-OPEN5-RF/a20260922-01/ruling.md`），
> **不在任何函件上签字**、**不改任何既有载体**。若 owner 终确采纳，由编排层按函 A §4 转录至各卡载体并登记 `RESPONSES.md`。

---

## 1. 身份与管辖域

- **身份**：RF（revenue-forecast）**消费 owner**（consumer owner），TIER-2 外部方 #3。
- **管辖域**：下游消费语义（forecast 语义稳定性、消费/恢复路径的 fail-safe 行为、消费契约稳定）。
  即：一条 processing demand 被消费、原请求被恢复时，**下游 forecast 消费者看到的世界必须不被伪造、不被静默合并、不被默认值填充**。
- **本次裁定项**：函 `A_DW06_OPEN-4-5-6.md` 的 **OPEN-5**（覆盖序映射 T2-3 ↔ OPEN-5 ↔ RF 消费 owner）。
  **已核验归属**：该函自身小节标题 `## 2. OPEN-5 —— 消费 / 恢复命令与原请求恢复接口（RF 消费 owner）`（第 88 行）与收件表（第 8 行）
  一致指派本角色 OPEN-5；函 A **未**给本角色分派其他或相邻项。OPEN-4（第 43 行）、OPEN-6（第 122 行）分属他方，本裁定不越域。
- **相邻但不属本裁定**：函 `C_I-05-C_gap2_gap3.md` 的 GAP-2（`consumer_analysis` 精确入口）同属本角色名下，但属**另一封函**的另一项；
  本裁定**不**代答 GAP-2（见第 6 节不予授予项 7），只在条件 C6 锁定两函**缺失语义必须一致**（函 C §1.3 对齐要求）。

## 2. 裁定原文引用（OPEN-5 逐字，函 A `outward_requests/A_DW06_OPEN-4-5-6.md`）

节标题（第 88 行）：

> ## 2. OPEN-5 —— 消费 / 恢复命令与原请求恢复接口（RF 消费 owner）

§2.1（第 90–96 行）：

> ### 2.1 关键事实：该接口**今天不存在**
>
> `handoff.json` 的 `still_awaiting_other_parties.OPEN-5.fact` 原文：
>
> > **"the interface DOES NOT EXIST today; it must not be pretended into existence"**
>
> ⇒ 请贵方**确认这一事实**，并裁定**它应当是什么**，而不是裁定「它已经是什么」。

§2.2（第 98–108 行）：

> ### 2.2 待裁的四件事
>
> 1. **消费入口**：从哪个真实 CLI / 函数入口消费一条 active demand？
>    与 `I-05-B` 的「消费者读取已验证字节」如何衔接？
> 2. **恢复接口**：原请求被打断后，恢复路径的**输入**是什么
>    （demand ID？原 request 工件？二者都要），**输出**是什么（补产指令？新工件？）？
> 3. **持久化介质**：与 OPEN-1 已裁定的「单一 CW 持久 owner
>    （扩展 `src/company_wiki/source_catalog/store.py`，`catalog.sqlite3`，经既有
>    `_apply_additive_migrations`）」**同一库同迁移机制**，还是另有介质？
> 4. **权限**：谁有权触发恢复？是否需与 OPEN-3 已裁的「显式单次 `claim(owner, lease_seconds)`」
>    共用同一授权？**不得**自动 resume、**不得**起后台 scheduler（OPEN-3 已裁明文）。

§2.3（第 110–118 行）：

> ### 2.3 ⚠️ 已知的不一致（请一并处置）
>
> `handoff.json` 明确记录：
>
> > "the candidate's key does NOT satisfy the newly-ruled OPEN-2 option A, so the candidate is
> > now **known-insufficient** on that point and must be revised before it can be promoted."
>
> 即：**候选实现仍为 UNRATIFIED**，且**已知不足**。请贵方在裁定 OPEN-5 时明确：
> 消费入口的设计是否**依赖**候选实现被修订，若依赖，请写明**修订后的接口契约**。

§4 回执要求（第 147–152 行，适用于本裁定）：每项须含 **选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案**；
不得以「按最佳实践」代替决定；不在函上签字。

## 3. 【裁定】**CONDITIONAL**（有条件裁定）

- **事实确认（§2.1）**：✅ **确认**——消费/恢复接口**今天不存在**，本裁定是「它应当是什么」的规范裁定，
  **不是**对任何既有实现的验收。
- **对 §2.2 四件事**：四项均给出权威选择（下第 4 节），但**不授予无条件放行**。原因：候选实现已知不足（§2.3）、
  消费语义的关键相邻判定（OPEN-4 失效矩阵、OPEN-6 `detected_and_ignored` 下游可见性）尚未出裁、
  GAP-2 缺失语义仍阻塞（登记册 :902）。在这些条件下无条件 APPROVE 等于替未验证的行为背书——拒绝。
- **对 §2.3**：消费入口设计**明确依赖**候选修订；**修订后的接口契约**见第 4 节【§2.3 附】，并以条件 C1–C8 可检验收口。
- **结论效力**：满足 C1–C8 全部检验通过后，消费/恢复接口方可实施；任一条件未过 ⇒ 该接口**维持不存在**
  （比伪造一个存在更可接受——`handoff.json:240` 明文）。

## 4. 理由（逐项：选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案；证据均为实读）

**实读证据基线（本裁定引用的字节，sha256 实算）**：
`scripts/source_preparation.py` = `91a6dc32466e9d67…c6ebf4d`；
`scripts/processing_demand.py` = `fcdfcad8ebd1fc20…5a820afc1`（与 `I-06-A/a20260919-01/handoff.json:94` 记载的
`fcdfcad8…afc1` 一致 ⇒ 该契约自 I-06-A 以来**未漂移**）；
`scripts/company_wiki_source.py` = `7d1bd8f9d9122dc4…ca9e48ce`；
`scripts/model_registry.py` = `62f864b9ab3f144e…dd985081`。

### 4.0 事实前提（§2.1）

- `execution_runs/I-06-A/a20260919-01/handoff.json:235-241`：`OPEN-5.fact = "the interface DOES NOT EXIST today; it must not be pretended into existence"`。
- 同卡 `decision.md:63-66`：「候选只提供 `list` / `claim` 两个只读/单次授权命令；『从原请求恢复』的接口……未实现」。
- `execution_runs/I-06-B/a20260919-01/after/original-request-resume.json:39-42`：`original_request_resume_cli = blocked, "no demand→source_preparation resume interface"`。
- 生产侧实读：`scripts/source_preparation.py:33` `_preparation_demands = DemandQueue()` 为**模块级内存队列**，
  其注释 `:29-32` 自认「In-memory queue (persistence is a later phase)」；全仓 grep 无任何 consume/resume CLI。
  ⇒ **确认：接口不存在，且现状下跨进程不可恢复**（与 `before/demand.cross-process.json` 的 `database_exists=false` 互证）。

### 4.1 待裁 1 —— 消费入口

- **选择**：消费入口 = **RF 侧唯一生产编排入口 `scripts/source_preparation.py`**（其 docstring `:1` 自我定义
  「WU-1000: the single production orchestration entry — source preparation」，CLI `main()` `:191-227`，退出码 0/1/2/3 `:10-11`）；
  demand 的**读取/查询面**留在 CW 单一持久 owner（OPEN-1 选项 A），但**消费动作（恢复执行）必须重入 `prepare_source()` 原链**，
  不得另设旁路入口。与 I-05-B 的衔接：恢复产出的字节必须经
  `company_wiki_source.verify_artifact_reads`（`scripts/company_wiki_source.py:231-249`，
  「`selected_roles` is the PLAN … these events prove IO」）产生 `verified_read_events`（`content_sha256_actual` 对 `declared`、`bytes_read`、`source_sha256`），
  并经 `select_artifact_roles`（`:154-228`）的 request-scoped 产出范围（`_production_scope` `:129-151`，REM-11 后 bundle=None 与 bundle 在场同一规则）。
- **理由**：恢复路径与首跑路径必须是**同一条**受同一套 fail-closed 检查约束的链。首跑链上已有消费侧硬检查：
  `prompt_injection_status == "not_reviewed"` ⇒ 阻断（`source_preparation.py:153-156`）；
  `parser_calls/llm_calls` 缺席 ⇒ 「fail closed instead of fabricating 0」（`:157-162`）；
  resolution envelope 缺失 ⇒ fail closed（`:123-128`）。只有重入原链，这些检查对恢复路径**自动生效**。
- **反例**：若恢复走旁路（例如直接从 demand 行拼装 `RevenueSourceRecord`），则**恰好在恢复路径上**可以绕过
  「not_reviewed 阻断」——而制造该 demand 的原因就是 not_reviewed。恢复路径会成为全链最弱一环：
  被阻断的请求经『恢复』反而未经安全判定进入下游 forecast。
- **兼容影响**：下游消费契约不变——恢复产出仍是 `prepare_source()` 的 record + `reuse_receipt`
  （`:171-184`，含 `artifact_read`/`producer_events`/`artifact_read_events`/`artifact_failed_events`），
  `revenue_forecast.py` 继续只消费已验证 source record（`:7-8`：「stays pure」）。
- **恢复规则**：恢复执行失败 ⇒ 与首跑同一错误契约（JSON `error_code` + rc=3，`:221-224`），demand 行**保持 open**，不得半途关闭。
- **被拒绝的替代方案**：① 新建独立 `resume` 脚本自行拼装 record（旁路检查，如上反例）；② 让 CW 侧 worker/scheduler 自动消费
  （OPEN-3 明文禁止）；③ 以 `select_artifact_roles` 的 PLAN 代替实际读取证据（`source_preparation.py:141-143` 注释明言
  「selection alone cannot prove bytes were consumed」）。

### 4.2 待裁 2 —— 恢复接口的输入与输出

- **选择**：
  - **输入 = 二者都要**：`demand_id` **且** 原 request 工件（request JSON 字节），并**强制绑定校验**：
    从所给 request 字节重算 `request_sha256`，必须**等于**该 demand 行登记的原请求绑定哈希；不等 ⇒ fail-closed 拒绝（不找「最接近的 demand」）。
  - **输出 = 补产指令 +（经原链执行后）原契约的 RevenueSourceRecord**；恢复接口**本身不直接产出、不改写任何 forecast/publication 工件**。
    补产指令 = 结构化（demand_id、request_sha256、gaps、request-scoped `producer_events`、next_action），随后重入 `prepare_source()`。
- **理由**：(a) OPEN-2 选项 A 已裁「幂等键必须含请求身份」（`handoff.json:200-208`，`source_sha256 + review_policy + role_set + request identity`，
  request identity 覆盖 `as_of_date/target/payload digest`）⇒ demand 是**按请求**的，恢复必须证明「我恢复的就是登记的那一次请求」；
  (b) 仅 demand_id 不够：持有 id 者未必持有原请求字节，行内 `request_json` 若被当作唯一真相，便无人校验「现场在恢复什么」；
  仅 request 工件也不够：无法证明恢复者对哪条持久 demand 行使 lease 权（OPEN-3）。
  (c) 输出不产 forecast 工件：`revenue_core.py:427`「invest-* consumers must only accept `"formal"` artifacts」、
  `revenue_publication.py:29,61`（消费者验证入口 = `validate_forecast_output`）——恢复若另开一条工件铸造通道，
  就是 REM-01 类缺陷（登记册 :12：`attestation_status="host_signed"` 纯标签、消费者完全不验签）的同族重造。
- **反例**：c8/c9/c10 实测（`handoff.json:81-90`、`decision.md:104-115`）：同 source/policy/roles 仅 `as_of_date` 不同的第二个请求
  （实际哈希 `4bddf9e6…`）被并入首请求 demand，行内 `request_sha256` 仍是 `d8afcf31…`。
  ⇒ 若恢复只要 demand_id（或只信行内 request_json），恢复者可以**拿着 A 请求的字节恢复 B 请求的 demand 而无任何告警**——
  as_of_date 错接进 forecast 时间轴，直接污染预测语义。这正是消费侧必须设 C3 的原因。
- **兼容影响**：补产指令的 gaps/角色词汇与 `select_artifact_roles`/`_production_scope` 同构（不造第二套角色语言）；
  record schema 不变（`reuse_receipt` 形状稳定，`:171-184`）。
- **恢复规则**：绑定校验失败 / 链上任一 fail-closed 触发 ⇒ demand 保持 open + 结构化错误；`complete` 只能在重入链**成功产出 record 之后**
  按 OPEN-3 lease 语义落（`processing_demand.py:155-172` 的 complete 语义、须持 lease）。
- **被拒绝的替代方案**：① 仅 demand_id（如上反例）；② 输出直接给「新工件」（绕过 `validate_forecast_output` 消费入口）；
  ③ 补产指令里内嵌默认值/估数填 gaps（与「省缺即抛」的今日产品语义相反——`model_registry.py:402-413` 注释与实现：
  「an omitted driver is legal ONLY when `spec.defaults` carries an [explicit default]」，否则 `ModelRegistryError`；
  同族先例 `source_preparation.py:159-162`）。

### 4.3 待裁 3 —— 持久化介质

- **选择**：**与 OPEN-1 已裁选项 A 同一库、同一迁移机制**——扩展 CW `src/company_wiki/source_catalog/store.py`、
  `catalog.sqlite3` 增表、经既有 `_apply_additive_migrations`。**不另立介质**。
- **理由**：单一 owner ⇒ 「当前是否存在该请求的 active demand」只有一个真相源。候选自己的 option-B 形状
  （独立 SQLite 文件，`decision.md:30`）已被 OPEN-1 否决（`handoff.json:197`：「Do NOT adopt the attempt's internal option-B shape」）。
- **反例**：候选的临时库位于 `%TEMP%\w06a\…`，其恢复规则是「删除即可」（`decision.md:100`）。
  作为探针无妨；作为生产恢复规则则意味着**唯一记录『有请求被阻断』的行可以随临时目录消失**——
  消费者永远丢失『还有一次未完成的请求』这个事实。双库并存同理：消费端须先回答『哪个库权威』，这本身就是缺陷。
- **兼容影响**：随 additive migration 增表，无破坏性变更；**必须**明确 demand 行生命周期——
  `decision.md:25` 已指出 OPEN-1 选项 A 的风险「prune/archiving 会连带影响」⇒ demand 行必须**豁免**于文档目录的 prune/archival，
  或有显式 terminal 态保留规则（否则 I-15-A 类清理会连带删掉未决需求）。
- **恢复规则**：迁移失败/写失败 ⇒ C7 契约 fail-closed（`decision.md:88`、`handoff.json:214` 已裁采用：
  rc=3、stderr 含安全判定 + `demand_store_error=` 附加子句、**无** `demand_queued`、行数不变）；**不做内存兜底**。
- **被拒绝的替代方案**：OPEN-1 表中的选项 B（独立 SQLite）/ C（RF 独立 DB）/ D（复用 JSONL 文件队列）（`decision.md:23-28`）；
  RF 侧建库（会把「CW 单一 owner、RF 只提交/查询」倒置）。

### 4.4 待裁 4 —— 权限

- **选择**：**与 OPEN-3 已裁的显式单次 `claim(owner, lease_seconds)` 共用同一授权，不多不少**。
  恢复 = claim 之后 **lease 有效期内**的动作；触发恢复者必须是该 demand 的**当前 lease owner**（resume 前置 = 有效 claim）。
  **不得**自动 resume、**不得**后台 scheduler、lease 过期回收只能显式触发（OPEN-3 明文，`handoff.json:221`）。
- **理由**：claim 语义已在 ZR-507/RF 契约里有可执行定义（`processing_demand.py:92-134`：claim 授 lease、
  `_require_lease` 校验 owner 与有效期、越权 ⇒ `DemandStateError`）。恢复接口复用它，权限面只有一套；
  另设授权主体会产生第二条『可以动手重跑请求』的路径。
- **反例**：若仅凭持有 request 工件即可触发恢复，则任何拿到请求 JSON 的进程都能在无 lease 下重跑原请求，
  与持 lease 的 worker 并发写同一 demand ⇒ 与「并发 claim 未验证」（`handoff.json:147`）叠加成未定义行为。
- **兼容影响**：无新增权限概念；错误面沿用 `DemandNotFoundError/DemandStateError`（`processing_demand.py:39-44`）。
- **恢复规则**：lease 过期后 resume ⇒ 拒绝（fail-closed），须显式重新 claim；崩溃恢复 = 显式 `expire` 等价物 + 显式重 claim，
  不自动接管。
- **被拒绝的替代方案**：① 宽松权限（持 request 即可恢复）；② 自动 resume worker；③ 后台 scheduler 扫描恢复（OPEN-3 禁）；
  ④ 把 lease 秒数写死为规范值（数值不在我职权，见第 6 节 6）。

### 4.5 【§2.3 附】修订后的接口契约（消费入口所依赖的候选修订）——**是，依赖修订**

候选**明确**依赖修订方可支撑消费入口。修订后的接口契约（消费侧要求的最小闭集）：

1. **幂等键**：`demand_key = sha256(canonical_json({source_sha256, review_policy, role_set, request_identity}))`，
   `request_identity` 覆盖 `as_of_date / target / payload digest`（逐字对齐 OPEN-2 选项 A，`handoff.json:205`）。
   候选的三元组键（`decision.md:36-37`）**不得**作为晋升契约。
2. **原请求绑定列**：保留 `request_sha256` **且** `request_json`（候选表已有，`decision.md:38-40`）；
   `request_sha256` 是恢复时的**校验锚**（4.2 输入绑定），不得只存不验。
3. **状态枚举**：沿用既有 ZR-507/RF 契约闭集 `pending/running/completed/failed/terminal_failed`
   （`processing_demand.py:26,100,178`；两侧「pinned by identical contract tests」`processing_demand.py:9-10`），
   消费语义绑定：`completed` = 原请求已成功重跑并产出 record；`terminal_failed` = 放弃且**必须**留 reason；
   `failed` = 可显式重试（backoff 语义沿用 `:174-198`）。
4. **CLI 最小面**：`list`（只读）、`show --demand-id`、`claim(owner, lease_seconds)`（显式单次）、
   `resume --demand-id --request-file`（仅 lease owner）、`complete`/`fail`（lease 内）。
   **无** `resume --all`、**无**自动推进。
5. **错误契约**：登记与恢复两路径同用「安全判定 + `demand_store_error=` 附加子句」（OPEN-2b 已裁采用，`handoff.json:214`）；
   阻断文案的跨仓文本断言须排查后钉住（`handoff.json:146` 悬置项，见第 7 节）。
6. **gaps 词汇**：与函 C 的 `missing / unsupported / not_applicable` 三值**不得混同**（`C_I-05-C_gap2_gap3.md:72-74,136`），
   demand 行记录角色缺失时用同一套语义（见条件 C6）。

## 5. 条件逐条（全部可检验；C1–C8 全过 ⇒ 本裁定的条件解除）

- **C1（键含请求身份）**：修订候选后重跑 c8/c9/c10 型探针（真实 `source_preparation.py` CLI），
  断言：仅 `as_of_date` 不同的两个请求 ⇒ **两个不同** `demand_id`；行内 `request_sha256` == 该请求实际哈希。
  检验物：探针 JSON（类 `after/request-to-demand-binding.json` 形态）。
- **C2（恢复不绕门）**：对 `prompt_injection_status=not_reviewed` 的 demand 执行 resume ⇒ **仍被阻断**
  （`source_preparation.py:153-156` 同一错误契约），直至审核状态真实翻转；`parser_calls/llm_calls` 缺席时 resume ⇒ fail-closed（`:157-162`）。
  检验物：两条反例测试 + rc/错误码记录。
- **C3（输入绑定）**：`resume --demand-id X --request-file mutated.json`（改 `as_of_date`）⇒ **拒绝**并保持 demand open；
  正确字节 ⇒ 通过。检验物：正反两例。
- **C4（同库同迁移 + 生命周期）**：demand 表经 `_apply_additive_migrations` 落 `catalog.sqlite3`；
  文档 prune/archival **不删除**非 terminal demand 行（或显式 terminal 保留规则入迁移注释/文档）。
  检验物：迁移文件 + 一次 prune 后非 terminal 行仍在的测试。
- **C5（权限=OPEN-3）**：无有效 lease 的 resume ⇒ `DemandStateError` 等价拒绝；lease 过期 resume ⇒ 拒绝；
  全程无自动 resume、无后台 scheduler（grep 证明无 scheduler 启动点）。检验物：三例测试。
- **C6（缺失语义与函 C 一致）**：demand 的角色缺失记录使用 `missing / unsupported / not_applicable` **可区分**三值
  （对齐 `W05C-N3`，函 C `:72-74`）；`consumer_analysis` 缺入口时**不得**记为 `not_applicable` 或伪装 `ok`；
  在 GAP-2 仍阻塞期间（登记册 :902「§12 仍 GAP-2=阻塞/GAP-3=待裁」）该角色只能落**阻断/missing**态。
  检验物：schema 字段 + 每枚举值一测。
- **C7（输出不越界）**：resume 全程**零** forecast/publication 工件写入；产出仅为 record + `reuse_receipt`
  （形状 `source_preparation.py:171-184`）与 `verified_read_events`（`company_wiki_source.py:240-247` 字段集）。
  检验物：一次端到端 resume 后的产物清单 + `content_sha256_actual == declared` 断言。
- **C8（错误契约钉住）**：登记/恢复两路径的阻断文案（安全判定 + `demand_store_error=` 子句）完成跨仓文本断言排查并钉住
  （处置 `handoff.json:146` 悬置项）。检验物：断言清单 + 排查记录。

## 6. 不予授予项（明确不给的东西）

1. **不授予**「接口已存在」或任何对 UNRATIFIED 候选的验收/晋级：候选仍 `known-insufficient`
   （`handoff.json:153`），本裁定不使其晋升，任何后续卡不得引用本裁定当作候选已 ratify。
2. **不授予**恢复路径任何形式的放宽：无默认值填充、无缺席即 0、无「先恢复后补审」。
   今日产品语义是**省缺即抛**（`model_registry.py:402-413`：缺显式 default ⇒ `ModelRegistryError`；
   OWNER_DECISIONS.md :69/:228 同向裁定），恢复接口不得反向漂移。
3. **不授予、不预判 OPEN-4 域**：回执失效矩阵（何种变更使旧回执失效、即时还是读时、作废重审 vs 增量补审）属 OPEN-4 两收件方。
   本裁定仅锁消费侧底线：**消费只接受有效且绑定完好的审核结论，`tampered/ignored/expired/absent` 一律不可消费**
   （词汇取自 I-06-B 实测 cache_state：`handoff.json:44-57`）；OPEN-4 出裁后若与此底线冲突，冲突项以 OPEN-4 为准并回本角色复核。
4. **不授予、不预判 OPEN-6 域**：`not_detected / detected_and_ignored` 的**判定归属**属安全 reviewer。
   消费侧底线（作为兼容要求记入条件）：`detected_and_ignored` 在 I-05-B 消费 / I-06-B 恢复必须**可见且为独立状态**，
   不得被静默过滤为 clean——但这只是消费侧要求，**不构成**对该状态归属或授权忽略机制的裁定。
5. **不授予任何数值规范**：lease 秒数、回执 TTL 等一律不写入规范。注意 I-06-B 的 `3600s TTL`
   （`handoff.json:55` N2c 实测）是**测试夹具值**，本裁定**不**核准其为产品默认——数值须按函 A/B 的数值纪律另裁。
6. **不授予**自动 resume、后台 scheduler、`resume --all`、无 lease 的恢复、以删库/清临时目录为生产恢复规则。
7. **不代答函 C 的 GAP-2**（`consumer_analysis` 精确入口路径 / DAG 入边 / LLM 能力边界）：那是另一封函的另一项回执，
   本裁定只锁 C6 的一致性约束。不在本裁定扩大签署范围。
8. **不在任何函件上签字**；本裁定不改变任何卡的 `status`/`reviewer_status`（I-06-A 维持 `blocked`，
   本裁定只是三道门之一的**条件性**回执）。

## 7. 未验证 / 存疑项

### 存疑项__initial（原叙述，逐字保留，2026-09-22 首裁时点）

1. **候选未验证项原样未解**：`additive migration / 并发 claim / lease 过期` 均未验证（`handoff.json:147`）——
   C4/C5 只给出判据，未给通过证据；实施卡须补。
2. **阻断文案跨仓文本断言未排查**（`handoff.json:146`）——已收进 C8，当前仍是敞口。
3. **RF `source_preparation.py` 字节漂移**：I-06-A 绑定 `5ec16eaf…ce46`（`handoff.json:93`）、
   I-06-B 运行后 `8070d60d…31e7`（其 `handoff.json:86` 自记「CHANGED BY ANOTHER CARD」）、
   本裁定实读 = `91a6dc32…bf4d`。⇒ 本裁定引用行号以**今日磁盘字节**为准；实施时若再漂移，须重核 C2/C7 的行号锚。
   （对照：`processing_demand.py` = `fcdfcad8…afc1` 三处一致，无漂移。）
4. **简报所称 commit `5fd82de7` 未获记录佐证**：`REMEDIATION_REGISTER.md` 仅见 `ec307d20`（:965，「PROMOTION 五脚本，770+/64−」）；
   `OWNER_DECISIONS.md` 无 `5fd82de7` 命中。按「no git」约束未跑 git 核验 ⇒ 该哈希**存疑，未采信**；
   但其指称的产品语义（model_registry 省缺即抛）已由**今日磁盘字节**独立证实（`model_registry.py:402-413`），
   guardrails caller-side 对齐一项**未独立核验**。
5. **GAP-2 状态系转引**：「GAP-2=阻塞 / GAP-3=待裁」取自登记册 :902 对 §12 的复述（该册存在重复 §11–§20 编号系，:905），
   未直接读到 §12 原行；不影响 C6 的约束力，但引用时按转引对待。
6. **OPEN-4/OPEN-6 未裁带来的残余耦合**：若 OPEN-4 的失效矩阵选择「作废重审」而非「增量补审」，
   或 OPEN-6 裁定 `detected_and_ignored` 下游**被过滤**，两者都会反压消费/恢复契约——届时本裁定的 4.1/4.2 须随其结论做一致性复核
   （本裁定已预留该接口：第 6 节 3/4 的「出裁后复核」句）。

### 存疑项__reverified（解析态）

> **更新约定（owner 指令经父 agent 转达，2026-09-22）**：本节在探针/实证回报**到齐后**逐条落定；
> **裁定正文（第 1–6 节）与条件 C1–C8 一字不改**。若实证推翻或限缩某条裁定前提，仅如实标注
> 「**前提变化**」并指向受影响条款，**不自行改判**（改判 = 重新呈报 owner 终确）。
> 证据来源分工：存疑 1/2 = 父派探针（I-06-B 候选隔离：additive migration / 并发 claim / lease 过期三探针
> + 阻断文案跨仓文本断言排查）；存疑 3/4/5 = 父并行实证；存疑 6 = 结构性保留（OPEN-4/OPEN-6 出裁后复核，
> 非本轮证据范围）。**本轮不重跑任何探针。**

| # | 存疑项（对应 initial） | 证据 | 解析态（终值三选一） |
|---|---|---|---|
| 1 | 候选 `additive migration / 并发 claim / lease 过期` 未验证（`handoff.json:147`） | 批 #2 六件全齐（探针官终报 + 证据 sha256） | **已解除（终格）**：「未验证」缺口闭合；内容分项 FAIL/PARTIAL/ABSENT **坐实条件必要性、加固 UNRATIFIED**；留置 = `FIX-W06-GAPS` 10 组修复复审后并入 |
| 2 | 阻断文案跨仓文本断言未排查（`handoff.json:146`） | 批 #2 P4 排查报告（9 行表） | **已解除**（排查缺口已补）+ C8 钉住留置实施（`P4-SCOPE` 修复卡） |
| 3 | RF `source_preparation.py` 字节漂移 | 父实证批 #1（内容链 blob pin） | **已解除**（良性：两因 + 一测量伪影更正） |
| 4 | commit `5fd82de7` 未获记录佐证 | 父实证批 #1（git 实证 + 复审 `399f4e60…`） | **已解除** |
| 5 | GAP-2 状态系登记册 :902 转引 | 父实证批 #1（`OWNER_DECISIONS.md:165` 一手出处） | **已解除**（附编号碰撞警示） |
| 6 | OPEN-4/OPEN-6 残余耦合 | 双方裁定原文 + 三方 (c) 文本到齐 | **已解除（终格）**：两反压分支双双相容、零反压；吸收为边界补充记 7 条；留置 2 项落地核验（实施检验面，不属裁定敞口） |

#### 复验记录（逐条；实证批 #1 + 批 #2 六件全齐；存疑 1–6 全部终格，2026-09-22）

**1 → 已解除（终格：「未验证」缺口闭合，三行为均实测）+ 内容分项坐实条件、加固 UNRATIFIED**
探针官终报双存疑回答：存疑 1 = **RESOLVED-YES**（「未验证」缺口闭合）；按内容分项 = **FAIL/PARTIAL/ABSENT**
——若问「三行为是否成立」则 **RESOLVED-NO**（2 真缺陷 + 1 实现缺失）。二者不矛盾：本存疑本体 = 「未验证」，
现验证完成；验证结果**坐实本裁定条件的必要性、加固 §6.1 UNRATIFIED 不授予**。**无前提变化**。
六件终值（证据 sha256：01=`9a41c4de…`/02=`bd8cad3e…`/03=`e5f99847…`/04=`c1cba4d4…`/05=`6dd180bb…`/
06=`ce83826e…`/oracle-lite=`a1a3647d…`）：
- **P1 = FAIL（坐实 C4 + 4.3）**：升级路径断裂——N-1 库 `DurableDemandStore._initialize()` 静默不补列、
  register→`DemandStoreUnavailable`「no column named request_sha256」、claim→**裸** `OperationalError`
  「no such column: lease_until」、旧行保但新列永加不上。⇒ C4 迁移判据必须覆盖 **N-1 库升级路径**；
  claim 裸抛 = **错误面欠定义化第 1 处**（坐实 4.4）。
- **P2 = PARTIAL（坐实 C5/4.4）**：A（恰好一赢家）5/5 ✓；B 输家裸 `None` FAIL（**错误面欠定义化第 2 处**）。
- **P3 = ABSENT + 新缺陷（坐实 4.4/C5）**：无 resume/complete（C5 候选上不可测；内存队列侧 lease-expiry
  全 PASS）；running + lease 过期需求永久搁浅、无显式回收入口（违 OPEN-3「显式 expire 等价物」形状）。
- **P4 = 9 行表**（已录存疑 2；PINNED×2 / UNPINNED×5 / ABSENT×2，含确认本裁定 0 命中该串）。
- **P5 = 敞口 CONFIRMED 3/3（坐实 §6.3 消费底线 + 边界补充记 2/3 + REM-01 引用）**：假回执 / 冒名 /
  无双绑定三形态均可过候选 + 对照 ✓ ⇒ 候选审核面**不验签、可伪造**——消费侧绝不可以现状放行，
  印证 §6.1/§6.2 不授予与「消费只接受有效且绑定完好的审核结论」底线。
- **P6 = RECORD-CONFIRMED 两缺陷 + 三绿**：单 key 静默覆盖丢写 7/8（并发登记互相吃掉——4.2 反例族
  「静默合并/覆盖」坐实）、`timeout=0` 裸抛 `OperationalError`（**错误面欠定义化第 3 处**）；
  三绿 = 8/8 写、零 lock 异常、658 交错读零撕裂。
**错误面欠定义化三处汇总**（P1 claim 裸抛 / P2-B 裸 None / P6-B `timeout=0` 裸抛）⇒ 全部归
`FIX-W06-GAPS` 修复面，按 4.4 错误面（`DemandNotFoundError/DemandStateError` 语义）定形后钉住。
**FIX-W06-GAPS = 10 组修复面**（P1×3 / P2-B / P3-A/B / P4-SCOPE×4 形态 / P5-a / P5-c / P6-A / P6-B），
副本内修、before/ 留旧、红绿可证；落定复审后以「实证 FAIL → 已修复（复审后）」终表并入呈 owner 终确。
**定位勘正（记录）**：候选锚 `7bc5feb0…8b8f7f`（与 `handoff.json` `r2_hashes`
`iso/candidate/processing_demand_store.py = 7bc5feb0cb5e5022…b8f7f` 互证）；迁移真实名
`DurableDemandStore._initialize()+DEMAND_SCHEMA` = **候选内自命名**——最终契约以 OPEN-1 选项 A 形状为准
（CW `store.py` + `_apply_additive_migrations`，本裁定 4.3 / 4.5 条 3），实施时**不得**沿用候选形状。

**2 → 已解除（排查缺口已补）+ C8 钉住留置实施（无前提变化）**
P4 排查报告（`04_blocked_message_sweep.md` 9 行表）实测结论：
① `not_reviewed` 双仓 **PINNED**（resolver.py:918/1078/1088 + 6 测试断言）；
② 阻断整句仅 **RF `source_preparation.py:154-156` 一处产品定义** + 2 手抄副本（候选 patch:139-142、
   apply 锚:51-52，三份当前一致）、测试仅宽松正则 ⇒ **UNPINNED**（坐实 C8 必要性）；
③ `cases_json_declared_expectation_missing` 两仓 + ruling **零命中**。**勘误对指核实（本角色 grep 实证）**：
   该串在本裁定文件 **0 命中**（正文与条件均无引用，`grep cases_json|declared_expectation` = No matches）
   ⇒ 所谓「本裁定 4.2/条件引此串、请澄清引用域」的勘误**对象错指、已作废**。**归属更正（父 agent 已认错）**：
   错指出自**转达层**（父 agent 转述时把 P4 表③行原文「裁定文本其实**没**点名这个串」方向转反），
   **P4 排查动作与结论本身有效**；该串真实出处 = 登记册 :393（M25-M28 `no_verdict` 判定源）与
   :941（M01-M04 臂表 G=2 反 KeyError），系 **M01-M04 runner / cases_json 语境**词汇，与产品面无关。
   **无需为本裁定澄清引用域**（从未引用）；产品面正确缺席 = 正常缺席。
   教训入册（与登记册 :921「跨卡混贴」同族）：**跨载体引用/勘误必须先在目标文件 grep 定位**；
④ `demand_store_error=` / `demand_queued` 仅候选定义、产品零定义零断言 ⇒ **UNPINNED**（该错误契约由
   OPEN-2b 裁定采用、`handoff.json:214`，本裁定 4.3/边界补充记 5 继承——UNPINNED 坐实 C8 必要性）；
⑤ 六 demand/claim 拒绝串两仓逐字同、但测试只钉异常类型 ⇒ **UNPINNED**（与 P2 断言 B FAIL 同族：
   拒绝面欠定义化 ⇒ C5 必要性再坐实）；
⑥ resume 拒绝文案 **ABSENT**（接口未定形 = 本角色域）——**正常缺席**（接口未实施，符合
   `handoff.json:240`「不得假装存在」）；C8 钉住时按本裁定 4.4 错误面（`DemandNotFoundError/
   DemandStateError` 语义）+ 边界补充记 5 错误契约（安全判定 + `demand_store_error=` 子句）定形后钉住。
**C8 状态**：**REMAINS-OPEN**（属条件检验物、不属裁定敞口）——已按 owner「fail 的全部要修复」并入
修复卡 `P4-SCOPE`（候选文案逐字断言 + RF 产品 PIN 测试 + ABSENT 项结构缺席钉 + 变异证真）；
落定后以「实测 UNPINNED → 已钉住（复审后）」形态随批进终表。

**3 → 已解除（良性漂移，无前提变化）**
完整内容链（提交点 blob，LF 归一）：`b34097dd=65aadf17`/8181 → `1dbae639=884b5f4d`/9022（ZR-701 F1）
→ `ff7429e5=fabdf129`/9382（ZR-701 REV-001）→ `70dd9f6e=95df2661=37a3eeae`/9908（与 initial 所记
I-06-A before pin 同内容）→ **`ec307d20=5fd82de7=HEAD=91a6dc32`/9921 == 现盘**。
漂移三因：① `5ec16eaf→8070d60d` = ZR-701 特性工作的**真实内容变更**（与 I-06-B 自记「CHANGED BY ANOTHER CARD」
其 `handoff.json:86` 一致）；② `8070d60d`（worktree CRLF）vs `37a3eeae`（同内容 LF blob）= **EOL 表示差**；
③ `→91a6dc32` = REM-49 单行注释修（B3 复审平价证 1085/1085，随 B-2 晋升）。
**测量伪影更正（记录在案）**：父首测 `3fe38e54` 系 PowerShell 管道字节伪影，二次 Python subprocess 直采推翻；
本裁定的独立实测（`Get-FileHash`）= `91a6dc32…bf4d`，与二次直采**一致** ⇒ 本裁定全部引用不受该伪影影响。
今日终态自洽（blob==disk），initial 的行号锚（今日磁盘字节）**有效**；
「实施时若再漂移仍须重核 C2/C7 行号锚」的维持条款**不变**。

**4 → 已解除（无前提变化）**
commit `5fd82de75c29e216baa568c3c9ae0eeee129db16` **实存**（author zhengcb81，21:00:11），
恰 2 文件（model_registry + guardrails）`128+/11−` 与声明符实；内容 = I-10-B 字节准重晋升 + 电池调用侧对齐。
initial 中「guardrails caller-side 对齐未独立核验」**现已有独立核验**：MODEL-ORACLE-ALIGN 复审
`399f4e60…`/22499 B 亲核 31 行对齐表（31 explicit-default / 0 assertion-rewrite / 0 STOP）、
31 行集合差 Compare-Object 为空、mutation 砍 `model_registry.py:410` 还原后字节同。
initial 的「未采信」系当时可得证据下的正确处置，现证据到齐 ⇒ 解除。
§6.2 的省缺即抛论据（`model_registry.py:402-413` 磁盘独立证实）不变。

**5 → 已解除（转引准确）+ 编号碰撞警示（无前提变化）**
一手出处已补：`OWNER_DECISIONS.md:165` 原文「GAP-2 | `consumer_analysis` producer **不存在**；
真实 LLM 能力未验证。测试只证明 missing/unsupported 处理 | **仍阻塞**」
⇒ 登记册 :902 转引**准确**，C6 的依据由转引升级为一手出处。
**警示**：`REMEDIATION_REGISTER.md:527` 的「E1E7 四裁定（F2/**GAP-2**/4/5）⇒ CLOSED」是 **E1E7 自编号的另一个
GAP-2**，与函 C 的 GAP-2 不是一回事（登记册重复编号缺陷，:905 已入册）；后续引用须带节标题消歧。
C6 不受影响、不改判。

**6 → 已解除（终格）**——(c) 面闭合（三方 (c) 文本到齐 + 新边界前提经本角色复核接受）+
`detected_and_ignored` 可见性面对撞复核完成（OPEN-6 §4.3 原文到齐）；两方裁定对撞均**相容、零反压**
（按 §6.3 预留接口执行；复核 ≠ 改判）
- **复核对象**：OPEN-4 已出裁（wiki 来源审核 owner 模拟裁定 CONDITIONAL，其载体
  `execution_runs/T2-SIM-OPEN4-WIKI/a20260922-01/ruling.md`，经父转述）：失效矩阵 = **policy 内容变 ⇒
  作废重审（全量）**、版本号单变**不**失效、role_set/请求身份变**不动回执**、读取时 fail-closed。
- **复核结论 a（主相容）**：「policy 变 ⇒ 作废重审 + 重审前 not_reviewed 阻断」与本裁定消费底线
  （`tampered/ignored/expired/absent` 一律不可消费）及 C2（恢复不绕门）**相容**：回执作废 ⇒
  `evaluate_review` 落 `ignored`/`not_reviewed` ⇒ 消费与恢复双双 fail-closed，方向一致。**初核无冲突。**
  （OPEN-4 方回文确认其 (a)(b) 立场与本角色一致。）
- **复核结论 b（分域成立）**：「role_set/请求身份变不动回执」与 4.2 的 `request_sha256` 输入绑定
  **分域、不冲突**——回执域 = `source_sha256 × policy_hash`（审核对象 = 字节 × 策略），
  demand 域 = request identity（OPEN-2 选项 A 键）。请求身份变 ⇒ 新 demand（C1），回执可复用，互不越界。
- **边界观察 (c) 之问 → 双方回文已到，终格闭合**：
  - **OPEN-6 方回文（结构性）**：扫描范围 = **全量 source 字节 × policy（版本化规则集），与 role_set 无关，
    不得按角色裁剪**；`scan_text` 无角色参数（双方实证一致）、`ruleset_hash` 绑规则集非角色集、
    回执 `source_sha256` 代表全部被审字节（按角色裁剪则双绑定名不副实 = REM-42 教训）。
    反向 fail-closed：实施若现「按角色裁剪扫描」形态 ⇒ 前提不成立 ⇒ **该形态禁止**，唯一退路 =
    role_set 扩大 ⇒ 旧回执**作废重审**，绝无增量补扫。
  - **OPEN-4 方回文（五点产品字节实证）**：①`scan_text(text, ruleset_hash)` 签名无 role/section 参数
    （guard:85）；②guard:99-106 全文逐模式 `re.search`、无分节/分角色逻辑；③ScanResult（guard:67-73）
    无角色字段；④回执 schema（`prompt_injection.py:116-126`）无角色字段、只绑整篇 `source_sha256`；
    ⑤测试检索 role|section 零命中。推论：回执覆盖 = 已绑整篇字节的全部可提取子集；role_set 扩大 ⇒
    新角色可提取 section 均为已审字节子集 ⇒ **无覆盖缝隙**、「role_set 变不动回执」成立。
  - **★新边界前提（OPEN-4 明示请本角色复核）**：上述结论**仅在下游只消费绑定 `source_sha256` 之字节
    或其子集时成立**（= I-05-B「消费者读取已验证字节」口径）；**凡越出绑定字节域的新字节流
    （拼接/转码/重组派生件），派生件是新 source、须独立新回执**；消费/恢复接口应**阻断派生件绕行**
    （接口设计权在本角色，对方只给定义不代设计）。
  - **本角色复核（裁定官定夺）：接受该边界前提**，并以**边界补充记**落实接口层（裁定正文一字不动）：
    1. **覆盖域定义（措辞已按 OPEN-4 抽核修订——两层证明形态）**：回执覆盖 = 绑定 `source_sha256`
       整篇字节及其逐字子集，证明形态分两层：
       (i) **现行证（今日载体可证）**：整件哈希相等 = `content_sha256_actual == declared` +
       provenance 绑定同一 `source_sha256`（I-05-B `verified_read_events` 现有字段 = `role,
       artifact_path, content_sha256_actual, content_sha256_declared, bytes_read, source_sha256,
       read_status, read_at`；真身 = **RF 仓** `scripts/company_wiki_source.py`，docstring :240-247、
       实现 :319-329——原条引未标仓、且「span/offset 可证」措辞超前于载体，OPEN-4 抽核纠正，**接受并修订**）；
       (ii) **span/offset 级逐字子集证明 = 实现缺口，需补字段后启用**（现字段无 span/offset）。
       缺口方向 fail-closed：补字段前，凡需主张「子集覆盖」的场景（以切片喂入审核/消费且主张继承原回执）
       **一律不得主张覆盖**，按条 2 归派生件路径（新 source、新回执）⇒ 缺口**不损害**边界前提的
       字节域级安全性（不能证明为子集 ⇒ 更严、非更松）。
    2. **派生件识别条款（选「增设」）**：凡不能证明为逐字子集的字节流（拼接/转码/重组/任何变换）
       **不得继承原回执**、不得以「已审源」身份经消费/恢复接口；被当作 source 消费 ⇒ **新 source、
       独立新回执**（独立 `source_sha256` + 独立扫描），fail-closed。
    3. **C3 校验对象精确化（选「明确」，与 2 并行采用，只记补充、正文 C3 不改）**：校验锚 = **原 request
       字节（`request_sha256`）+ 绑定 source 原字节（`source_sha256`）**；派生/变换字节不构成
       「正确字节」，不得放行。判定必须在**哈希域**做，不得以「内容相似/同路径/同名义 provenance」放行。
       反例：sections 拼接回读、转码后再消费——字节哈希必然 ≠ 绑定哈希，语义域放行即成绕行。
       （二选一不够：只做 3 不做 2 ⇒ 派生件可伪装「新请求」复用旧审核状态；只做 2 不做 3 ⇒ 校验对象
       仍有歧义。故 **2+3 同采**。）
    4. **检验物补充（挂 C3 检验面，随 owner 终确并入 C3 或另卡）**：一条派生件负例探针——以转码/拼接
       字节流投喂 resume/消费面 ⇒ 必须拒绝或归类新 source，**不得**复用旧 demand 审核状态。
  - **留置 1 项（不闭）**：「调用方喂入 = 全字节而非角色切片」未实测（OPEN-4/OPEN-6 双方自认），
    挂其两家 C1/探针面；「按角色裁剪形态」已被明禁且退路 = 作废重审（fail-closed），故消费侧风险已兜底。
- **OPEN-6 可见性面对撞复核（§4.3 原文到齐，终格）**：
  - **复核对象（OPEN-6 `T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` §4.3 逐字要点）**：选择 = **可见且强制标记、
    禁止过滤**；需要 clean 证明的下游对 `detected_and_ignored` **fail-closed**；无降级/warn-only/环境开关
    可洗成 `not_detected`；消费/恢复路径必须呈现状态与命中快照；恢复侧若过滤则「补审变盲审」；
    发现过滤/降级路径 ⇒ 旁路缺陷（REM-01 同级：登记+修复+消费侧负例），窗口期内已消费工件重新核；
    被拒替代 = 过滤 / 默认等同 not_detected（faked green）/ 消费端各自决定显隐。
  - **对撞结论：完全相容，且对方裁定强于本角色底线**。本裁定 §6.4 底线（可见、独立状态、不得静默过滤
    为 clean）被其「可见且强制标记 + 禁止过滤 + clean 证明 fail-closed + 命中快照随行」全数覆盖并加强。
    两个反压分支（「下游被过滤」假设）**均未触发** ⇒ 4.1/4.2 **无需任何契约改动**。
  - **归属段相容确认**：其「检出 = 安全域事实判定；忽略 = 安全域处置授权（来源审核域可请求、不得自署）；
    最终署名 = `ignore_authorizer`；授权元组缺任一 ⇒ fail-closed 为 `not_reviewed`」与本裁定
    §6.4 不越域一致；且「授权元组缺 ⇒ not_reviewed」直接触发本裁定 C2 阻断——**相容，无冲突**。
  - **吸收为边界补充记（接前 4 条，裁定正文仍一字不动）**：
    5. **`detected_and_ignored` 流转条款**：消费/恢复路径呈现该状态**且强制标记**（命中快照随行），
       禁止过滤/降级/洗成 `not_detected`；该状态 = **非绿色终态、带标记流转**（数据消费可以、
       执行其内指令永不）；demand 行 gaps **不得**记其为「已清洁」；「出具 clean 证明」不在本接口授予面
       （需要 clean 证明的下游对该状态 fail-closed，依 OPEN-6 §4.3）。
    6. **同词异义消歧（OPEN-6 其 C7 与本裁定 C7 同题）**：缓存失效态 `cache_state="ignored"`
       （=「policy ruleset changed since review」，I-06-B N2b，`handoff.json:49-52`）与审核结论态
       `detected_and_ignored`（= 命中且经授权忽略）**同词异义**，必须契约层消歧。**定夺**：优先**改名**
       （缓存失效态建议 `policy_changed` / `receipt_stale_policy`，词面唯一化）；若受 ZR-507/I-06-B
       冻结词汇约束不能改名 ⇒ 走**显式断言字段**（如 `state_domain: cache|review`）。两种语义**各一负例**
       进检验物。
       **定夺侧备注（OPEN-6 安全域 §7.4-C 四点回文，已采纳）**：①改名优先获认可（词面唯一化优于断言字段）；
       ②断言字段方案**收紧为 fail-closed**——缺 `state_domain` 或取值非法的记录**拒收/按最严解释**，
       歧义不得放行、**不得默认归入任一语义**（本角色采纳为条 6 组成部分）；③「两种语义各一负例」与其
       C7 判据同物、检验面满足；④改名与冻结词汇冲突时按本定夺退断言字段并回报，对方不另设条件。
    7. **补产指令携带命中快照**：4.2 补产指令结构增加命中快照字段（matches + ruleset_hash + 授权元组
       [ignore_reason 非空 + ignore_authorizer + authorized_at + 命中快照 + 双绑定]），否则恢复即盲审
       （其恢复规则句）；授权元组缺任一 ⇒ `not_reviewed` ⇒ C2 阻断（相容，已确认）。
  - **恢复规则兼容确认**：其「窗口期内已消费工件重新核」属安全域处置规则；本接口配合呈现证据
    （命中快照、授权元组、双绑定），不代行重新核、不代署名。
- **终值**：**已解除（终格）**——存疑 6 本体 = 两方裁定的反压耦合风险，经对撞复核**双双相容、零反压**
  （OPEN-4 作废重审分支 ✓、OPEN-6 可见性分支 ✓），4.1/4.2 无需契约改动；新边界前提与 §4.3 强标记等
  均系**收紧/澄清**，已吸收为**边界补充记 7 条**。**无前提变化**、不改正文、不改判。
  留置 2 项**落地核验**（不属裁定敞口，挂实施检验面）：①「调用方喂入 = 全字节而非角色切片」未实测
  （OPEN-4/6 共同 C1/探针面）；②同词异义消歧落地 + 两种语义各一负例（边界补充记 6）。

---

**签署行（模拟）**：RF 消费 owner（TIER-2 外部方 #3）· 模拟裁定 **CONDITIONAL**（条件 C1–C8）·
2026-09-22 · owner 全权授权 role-play · **待 owner 终确 · 非外部方真实签署** ·
未在任何函件签字 · 未改任何其他文件 · I-06-A 三门仅解其一（本回执为条件性）。

----- END ruling body (byte-exact) -----

## T2-2(OPEN-6)
source: execution_runs/T2-SIM-OPEN6-SEC/a20260922-01/ruling.md
sha256: 8aabac0908b407b8af5108c00b4a26e11476d889b593ade306d1eee519c368d1
----- BEGIN ruling body (byte-exact) -----
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

----- END ruling body (byte-exact) -----

## blocked_by_resolution
OPEN-4/OPEN-5/OPEN-6 三门回执 = owner 终确到位 ⇒ I-06-A 的 still_awaiting_other_parties 首条解除；实施受各裁定条件 C 约束

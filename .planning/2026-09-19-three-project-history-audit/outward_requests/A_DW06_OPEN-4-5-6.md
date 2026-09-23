# 函 A —— D-W06 OPEN-4 / OPEN-5 / OPEN-6 请他方裁决

**收件方**（三问分属三方，请各自作答，不必等齐）：

| 项 | 主题 | 待裁方 |
|---|---|---|
| **OPEN-4** | 审核方法、reviewer 身份绑定、`source_sha256` × `policy_hash` 双绑定、策略变更后旧回执失效判定 | **wiki 来源审核 owner** + **安全 reviewer** |
| **OPEN-5** | 消费 / 恢复命令与原请求恢复接口 | **RF 消费 owner** |
| **OPEN-6** | `not_detected` / `detected_and_ignored` 的判定归属 | **安全 reviewer** |

**授权依据**：`OWNER_DECISIONS.md` §13 **T2-1 / T2-2 / T2-3**（owner 已授权「联系并启动」，最终裁定仍待贵方）。
**上游卡**：`execution_v2/card_I-06-A.md`（`D-W06`）、`execution_v2/card_I-06-B.md`。
**证据目录**：`execution_runs/I-06-A/a20260919-01/`、`execution_runs/I-06-B/a20260919-01/`。

---

## 0. 为什么必须由贵方裁，而不能由 owner 或编排层裁

`START_HERE.md` 的「必须交专业审查」清单**明文列出**这一整类：

> 审核 writer 与 producer 契约变更；跨进程锁与崩溃恢复机制；
> 发布包事务边界；……**部署迁移和自然观察资格**。

I-06-A 要落地的正是「**审核 writer 与 producer 契约**」+「**跨进程锁与崩溃恢复**」。
owner 的总授权（2026-09-20 17:0x「给你所有批准」）在本批已按权限归属拆开：
**OPEN-1 / OPEN-2 / OPEN-2b / OPEN-3 属 owner 职权（已裁）**，
**OPEN-4 / OPEN-5 / OPEN-6 属贵方职权（未裁）**。
owner 的授权在此**只等于「许可联系与启动」**，不含结论。

**当前后果（实测，不是估计）**：
`execution_runs/I-06-A/a20260919-01/handoff.json` 顶层 `status = blocked`，
`blocked_by` 第一条即为：

> "D-W06 OPEN-4 / OPEN-5 / OPEN-6 remain UNSIGNED and belong to OTHER parties … The owner's
> 2026-09-20 blanket grant authorised contacting them and starting their reviews; it does **not**
> constitute their verdicts. Implementation of I-06-A must not begin, and I-06-B must not begin,
> until those parties rule."

**I-06-B 更是硬前置**：在 OPEN-4 出裁决之前，I-06-B **不可写可失败用例**（卡片明文）。

---

## 1. OPEN-4 —— 审核方法与失效判定（wiki 来源审核 owner + 安全 reviewer）

### 1.1 待裁的三件事

请逐项给出：**选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 拒绝的替代方案**。

**(4a) 审核方法**
一次 source review 的「判定」如何产生、由谁产生、用何种可复核的形式落盘？
卡的原始期望是：需求须携带「source/hash/policy、缺口、原请求绑定、下一动作」，
且**不得伪造 review**。请裁定：
- 审核结论以什么工件承载（DB 行 / JSON 收据 / 两者）？
- 判定枚举是否就是 `{not_reviewed, not_detected, detected_and_ignored, reviewed_ok, …}`？
  请给出**权威闭集**。

**(4b) reviewer 身份绑定**
「谁做了这次审核」如何被证明？
- 身份以何为主体（人 ID / 角色 / 进程 + 凭据）？
- 是否需要不可伪造的签名链？若需要，与 **I-08-A 的签字信任域**（函 B）是同一套还是两套？
  ⚠️ **跨函耦合**：若两套，会产生两个信任根。请明确表态。

**(4c) `source_sha256` × `policy_hash` 双绑定，以及策略变更后旧回执的失效判定**
- 旧回执在**哪一种**变更下失效：source 字节变？policy 内容变？policy 版本号变？
  角色集合变？请求身份变？
- 失效是**立即**还是**下次读取时**？
- source 未变而 policy 变更时，旧回执是**作废重审**，还是**增量补审**？二者对已下游消费的工件的处理不同。

### 1.2 请贵方注意的两条既有裁定（避免重复劳动）

- **OPEN-2 已由 owner 裁定为选项 A**：幂等键**必须含请求身份**
  （`source_sha256 + review_policy + role_set + request identity`，
  request identity 覆盖 `as_of_date` / `target` / payload digest）。
  ⇒ OPEN-4 的失效判定**须与该键口径自洽**，请复核有无冲突。
- **OPEN-2b 已由 owner 裁定**：`role_set` 权威来源维持 `RF_W06_ROLE_SET`，
  规范化形式为**排序去重的逗号串**（候选默认已统一为 `"normalized,sections"`）。

### 1.3 起草方实测到的相关反例（供贵方裁决时参考，非结论）

| 反例 | 实测值 | 出处 |
|---|---|---|
| 不同请求被静默并入同一 demand | c8/c9/c10 真实 CLI：请求仅 `as_of_date` 不同，返回**同一** `demand_id`，而行内 `request_sha256` 仍是**第一个**请求的 `d8afcf31…`，第二个请求实际哈希 `4bddf9e6…` | `I-06-A/a20260919-01`（已由 owner 以 OPEN-2 选项 A 处置） |
| 阻断文案的跨仓文本断言未排查 | `handoff.json` open question：`阻断文案（安全判定 + demand_store_error 附加子句）的跨仓文本断言未排查` | 同上 |
| 候选未验证 | `additive migration / 并发 claim / lease 过期` 均未验证 | 同上 |

---

## 2. OPEN-5 —— 消费 / 恢复命令与原请求恢复接口（RF 消费 owner）

### 2.1 关键事实：该接口**今天不存在**

`handoff.json` 的 `still_awaiting_other_parties.OPEN-5.fact` 原文：

> **"the interface DOES NOT EXIST today; it must not be pretended into existence"**

⇒ 请贵方**确认这一事实**，并裁定**它应当是什么**，而不是裁定「它已经是什么」。

### 2.2 待裁的四件事

1. **消费入口**：从哪个真实 CLI / 函数入口消费一条 active demand？
   与 `I-05-B` 的「消费者读取已验证字节」如何衔接？
2. **恢复接口**：原请求被打断后，恢复路径的**输入**是什么
   （demand ID？原 request 工件？二者都要），**输出**是什么（补产指令？新工件？）？
3. **持久化介质**：与 OPEN-1 已裁定的「单一 CW 持久 owner
   （扩展 `src/company_wiki/source_catalog/store.py`，`catalog.sqlite3`，经既有
   `_apply_additive_migrations`）」**同一库同迁移机制**，还是另有介质？
4. **权限**：谁有权触发恢复？是否需与 OPEN-3 已裁的「显式单次 `claim(owner, lease_seconds)`」
   共用同一授权？**不得**自动 resume、**不得**起后台 scheduler（OPEN-3 已裁明文）。

### 2.3 ⚠️ 已知的不一致（请一并处置）

`handoff.json` 明确记录：

> "the candidate's key does NOT satisfy the newly-ruled OPEN-2 option A, so the candidate is
> now **known-insufficient** on that point and must be revised before it can be promoted."

即：**候选实现仍为 UNRATIFIED**，且**已知不足**。请贵方在裁定 OPEN-5 时明确：
消费入口的设计是否**依赖**候选实现被修订，若依赖，请写明**修订后的接口契约**。

---

## 3. OPEN-6 —— `detected_and_ignored` 的判定归属（安全 reviewer）

### 3.1 待裁的问题

`not_detected` 与 `detected_and_ignored` 由**谁**判定、依据**什么**、落盘在**哪**？

- 这两个状态是**安全域**的判定，还是**来源审核域**的判定？（若跨域，谁最终署名？）
- `detected_and_ignored` 是否需要**理由字段**与**谁授权忽略**的记录？
- 若某 source 被标为 `detected_and_ignored`，
  它在下游（`I-05-B` 消费、`I-06-B` 恢复）应当**可见**还是**被过滤**？

### 3.2 起草方确认的当前事实（**没有越权**）

`handoff.json` 的 `still_awaiting_other_parties.OPEN-6.note` 原文：

> "this attempt correctly recorded `observed='not_reviewed'` and produced **zero review rows**"

⇒ 本次 attempt 在贵方裁决前**没有**自作判定、**没有**产生任何 review 行。
这是刻意的：在贵方裁定归属之前，产出任何 `detected_and_ignored` 行都会
**预设一个尚无归属的判定**。请贵方放心据此裁定。

---

## 4. 回执要求

- **落点**：请把结论写入**各卡自己的载体**（`execution_runs/I-06-A/a20260919-01/` 与
  `execution_runs/I-06-B/a20260919-01/` 下的 `decision.md` / `handoff.json` / 新建 `rulings_*.md`），
  **不在本函上签字**。
- 每项须含：**选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案**。
- 请勿以「按最佳实践」代替决定（`START_HERE.md` 明文禁止）。
- 完成后请通知编排层，由其在本目录 `RESPONSES.md` 登记一行，**不改一字裁决内容**。

---

## 5. 本函的自证（起草动作）

| 项 | 值 |
|---|---|
| 起草人 | 编排层（owner 执行人，**非**收件方、**非**签署者） |
| 授权依据 | `OWNER_DECISIONS.md` §13 **T2-1 / T2-2 / T2-3**（TIER-2） |
| 引用前像 | `I-06-A/a20260919-01/handoff.json` 17221 B；`I-06-B/a20260919-01/handoff.json` |
| 本函写入了什么 | 仅新增本 `outward_requests/` 目录下的文件；**未修改**任何 `execution_runs/` 载体、任何产品源码、任何门 |
| 不产生 | 任何裁定、任何签名、任何 `status` 变化 |
| 本函**不**做的 | 不代替任何收件方作答；不把 owner 的总授权膨胀为「结论已出」 |

---

## 更新（2026-09-22，追加式更新段）

> **性质**：本节系 2026-09-22 更新 pass（`OWNER_DECISIONS.md` §十八 C「更新函件」）在原函**之后追加**；原函正文逐字节未动（追加前像与追加后前缀证明见本目录 `_provenance.json` 的 `updates_2026_09_22`）。以下事实全部取自本计划记录并逐条注明出处；本节**不新增、不删改任何待裁项**。

### 一、自 2026-09-20 起草以来的审计状态（截至 2026-09-22）

1. **计划已推进至验收 80 张卡**——登记册 §三十二（blocked 前条件冻结）记「验收 80」「五系闭环」「仓内自主项全部完成」。
2. **三批推送、每批过门**——登记册 §十七记「两批已推毕（`ab20cebe..6f74b056`、`6f74b056..3861f08d`，门各绿一次、四锚全程 disk==HEAD、零生产合并）」；§三十二记「三批推送至 `origin/main=4b1c690b`（门各绿、gitlinks=0、四锚 disk==HEAD、零产品面）」。最新 head = `origin/main=4b1c690b`。
3. **卡 I-09-C（发布面故障注入 / 并发验收）已完成**——PC1-K6 五环（barrier / manifest / `writer_exited` / fresh reader / hook 止于 commit:before）与 PC2-K8 发布 oracle 复审 = `accepted_scoped`（登记册 §二十一，pin `673c10bc…`/86 行）；五系计分板列「8/8 目标卡 + I-09-C ✅ 全套」（§二十七）。
4. **I-06-A 仍 blocked，唯一阻塞即本函三项未裁**——登记册 §十八【状态刷新·Round 11】「待外部」明记「函 A（TIER-2：OPEN-4/5/6 三外部方回执）⇒ 解 I-06-A → 19 卡链」；§三十二记「19 卡门核验全 gated」，并将「函 A 三外部方回执→I-06-A→19 卡链」列为剩余外部门（另一外部待办「INVEST 合入=invest-core owner」为并列事项，不在此链上）。owner 侧四答已于同日出齐（`OWNER_DECISIONS.md` §十八）。
5. **⇒ 就 I-06-A 及其 19 卡链而言，贵方三方的 OPEN-4/5/6 回执是本计划记录中所剩的唯一门**（19 张依赖卡已核验为 gated、无其他阻断；域 = 本计划记录 2026-09-22 截止）。

### 二、对原函的影响

以上仅为**状态更新**，不构成对任何待裁项的预判。原函全部请求项（OPEN-4 三问、OPEN-5 四件、OPEN-6 三问、§4 回执要求与落点）**原样保留**。

**原函请求项不变，以上更新供贵方在裁定时一并知悉。**

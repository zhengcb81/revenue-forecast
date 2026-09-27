# oracle · HYPOTHESES-V4-MERGE（版本裁并：v2 ⊕ v3 → hypotheses_v4.json）

- 工位：`execution_runs/HYPOTHESES-V4-MERGE/a20260926-01`（新建，写入面仅 4 件）
- 角色：`implementer_version_merge`（实现者·版本合并面）—— **非裁决、非 reviewer、不代签、不放行任何参数**
- **本文件是判据冻结件：先写本文件 → 复算其 sha256 → 才允许生成 `hypotheses_v4.json`。冻结后本文件不再改动（若必须改，整轮作废重跑）。**
- 网络：0 请求；git 写：0；**`git status` 禁止执行**；`.planning` 之外写入：0 字节

---

## 0. 授权与边界（回源，不采信转述）

授权 = 编排层派单（会话 `session-19074bf0-0205-4315-af73-9db57597275a`）+ 其引用的登记项：

- **`OPEN2-C2-REGISTRATION/a20260926-01` 登记项 #3 `V2-V3-DIVERGENCE`**（盘上逐字，`registration.md` L177）：
  > 3. **`V2-V3-DIVERGENCE`**：既存 `execution_runs/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json` 已把下标 `0`（`H-CN-ZIJIN-SEG-01`）改为 `approved_frozen` 并写入 `decision_sha256 = 4d4ee106…`。本工位按派单以**封盘原件**为 `supersedes` 基线，**未合并 v2 的改动**，故下标 `0` 在 v3 中 = 封盘原字节 ⇒ **v2 与 v3 在下标 0 上分歧**。这属编排层裁并范围，**本工位不合并不回改**。
- 派单给的「逐字」引文为：「既有 `hypotheses_v2.json` 与本 v3 在下标 0 分歧待裁并」。**盘上未检索到该逐字串**（检索面：计划根 `*.md`/`*.json`、`OPEN2-C2-REGISTRATION/*`、仓库根 `*.md`）；语义上唯一对应物 = 上引 `registration.md` L177 登记项 #3（`handoff.json` L221、L266 为同一登记的 JSON 侧表述）。⇒ `handoff.json.authorized_by` 同时登记两者，并标记 `authorized_by_verbatim_on_disk = false`（派单措辞）/ `true`（L177 原文），**不把派单转述冒充盘上逐字**。

**明确不做（负向边界，任一违反即本轮失败）**：不改封盘/v2/v3 任一字节 · 不解除 `OPEN-2` · 不放行任何参数（`low/base/high` 仍 `null`、`released=false`）· 不改 `_PLACEHOLDER` · 不关任何 `BLOCKED-*` · 不产生 `I-11-B` 的 `ACCEPT` · 不把 v4 说成「已批准」（v4 = **版本合并**，不是裁决）· 不代签 · 不写计划五文件 · 不改 `model_cards.md` · 不写 `execution_v2/` · 禁 git 写、禁 `git status`、禁联网。

---

## 1. 回源三件 + 校验器（本工位实测，非引用自述）

| 文件（相对计划根） | sha256（本工位复算） | 字节 | 角色 |
|---|---|---|---|
| `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 51,697 | **封盘原件（只读）** |
| `execution_runs/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json` | `32c22208573a71d53033c4535e8d0cb598c61710e06174196033d996999d7859` | 55,213 | **v2（只读）** |
| `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json` | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 61,231 | **v3（只读）** |
| `execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py` | `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac` | 28,549 | 校验器（只读，只调 `validate()`） |

三份源的顶层形态：**均为 8 元素 JSON 数组**（`json.load` 后 `type == list`、`len == 8`），UTF-8 无 BOM、CR=0、LF 结尾、`json.dumps(..., ensure_ascii=False, indent=1) + "\n"` **逐字节复现封盘原件**（本工位实测 `match2lf: True`）⇒ 逐下标「逐字节保持」可机器证明。

---

## 2. 冻结时的逐下标差异实测（判据的事实基础；独立复算，不采信 v2/v3 自述）

判等口径：`json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",",":"))` 的字符串相等。

| 下标 | `hypothesis_id` | base≡v2 | base≡v3 | v2≡v3 | 结论 |
|---|---|---|---|---|---|
| 0 | `H-CN-ZIJIN-SEG-01` | **否** | **是** | 否 | 只有 v2 改了 |
| 1 | `H-CN-ZIJIN-SEG-02` | 是 | **否** | 否 | 只有 v3 改了 |
| 2 | `H-CN-ZIJIN-VOL-03` | 是 | **否** | 否 | 只有 v3 改了 |
| 3 | `H-CN-ZIJIN-PLAN-04` | 是 | 是 | 是 | 三份全同 |
| 4 | `H-CN-ZIJIN-ELIM-05` | 是 | 是 | 是 | 三份全同 |
| 5 | `H-US-MSFT-SEG-01` | 是 | 是 | 是 | 三份全同 |
| 6 | `H-US-MSFT-SEG-02` | 是 | 是 | 是 | 三份全同 |
| 7 | `H-US-MSFT-SEG-03` | 是 | 是 | 是 | 三份全同 |

**逐字段差异（base → 各版）**

- `base → v2`：**仅下标 0**，6 个字段路径：
  `/provenance`（新增）、`/state`：`pending_professional_decision` → `approved_frozen`、`/state_reason`、`/decision/decision`：`pending` → `approved_frozen`、`/decision/reason`、`/decision/decision_sha256`：`null` → `4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f`。
  ⇒ **v2 自称「只动下标 [0]」= 属实**（下标 1–7 与 base 全等）。
- `base → v3`：**仅下标 1、2**：
  - 下标 1（3 处）：`/provenance`（新增）、`/additional_parameters#len` 0 → 2、`/decision/decision_sha256` `null` → `1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55`；
  - 下标 2（3 处）：`/provenance`（新增）、`/additional_parameters#len` 1 → 3、`/decision/decision_sha256` `null` → `1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55`；
  - 两处均**未**改 `decision.decision` / `decision.reason` / `reviewer` / `professional_reviewer` / `state` / `state_reason` / `falsifier`（逐路径比对无差异）。
  ⇒ **v3 自称「只动下标 [1][2]」= 属实**（下标 0、3–7 与 base 全等）。

**⇒ 正交性成立：v2 的改动集合 {下标 0} 与 v3 的改动集合 {下标 1, 2} 不相交，且不存在任何「同一 index × 同一字段路径」的取值冲突。**

---

## 3. 判据 J（v4 的构成规则；每条都是可机检断言）

文件形态：`hypotheses_v4.json` = **与三份源同形的 8 元素 JSON 数组**（`json.load` → `list`、`len==8`），UTF-8 **无 BOM**、全文 **CR=0（纯 LF）**、尾随 1 个 `\n`、序列化 `json.dumps(obj, ensure_ascii=False, indent=1) + "\n"`。

| 判据 | 内容 | 来源 |
|---|---|---|
| **J-0** | `v4[0]` ≡ `v2[0]`：`state=approved_frozen`、`state_reason`、`decision.decision=approved_frozen`、`decision.reason`、`decision.decision_sha256=4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f` **逐字节取自 v2**；唯一例外 = `provenance` 字段（见 §4，v4 合并记录取代 v2 的单版本记录，v2 原记录整块嵌套保留） | v2 |
| **J-1** | `v4[1]` ≡ `v3[1]` **整条逐字节**（含 v3 的 `provenance`、2 条新 `additional_parameters`、`decision.decision_sha256=1a7838a1…`） | v3 |
| **J-2** | `v4[2]` ≡ `v3[2]` **整条逐字节**（含 v3 的 `provenance`、2 条新 `additional_parameters`、`decision.decision_sha256=1a7838a1…`） | v3 |
| **J-3…J-7** | `v4[i]` ≡ `base[i]` **整条逐字节**（i = 3,4,5,6,7；含 `state`、`decision.decision_sha256=null`、`falsifier`、既有 parameter_id、`_PLACEHOLDER` id） | 封盘 |
| **J-ID** | 8 个 `hypothesis_id` 的顺序与 base 完全一致（`H-CN-ZIJIN-SEG-01/SEG-02/VOL-03/PLAN-04/ELIM-05`、`H-US-MSFT-SEG-01/02/03`） | 封盘 |

### 3.1 两个 `decision_sha256` 必须都在（缺一即失败）

| 值 | 必须出现的位置 | 来源 |
|---|---|---|
| `4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f` | `v4[0].decision.decision_sha256`（并保持 `state=approved_frozen`） | v2 |
| `1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55` | `v4[1].decision.decision_sha256` **且** `v4[2].decision.decision_sha256` | v3 |

### 3.2 C1（MERGE 七条之一：`approved_frozen = 1`）

- `v4` 中 `state == "approved_frozen"` 的条目 **恰好 1 条**，且是 `v4[0]`（`H-CN-ZIJIN-SEG-01`）；
- 同条 `decision.decision == "approved_frozen"` 且 `decision.decision_sha256 == 4d4ee106…`；
- `v4[1]`、`v4[2]` 的 `state` 仍为封盘原值 `pending_professional_decision`、`decision.decision` 仍为 `pending`（v3 明示「不是批准签署」，v4 不得升级）。
- ⇒ `c1_preserved = true` 当且仅当以上全成立。

### 3.3 C2（注册面：`[1]`/`[2]` 四个新参数在位）

四个新 `parameter_id` 必须全部在位且**各出现一次**（`E_DUPLICATE_PARAMETER` 不得触发）：

1. `ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027`（在 `v4[1]`）
2. `ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027`（在 `v4[1]`）
3. `ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027`（在 `v4[2]`）
4. `ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027`（在 `v4[2]`）

并同时成立：`v4[1].additional_parameters` 长度 = 2、`v4[2].additional_parameters` 长度 = 3（= 封盘既有 1 条 + 新 2 条）；全文件 `parameter_id` 总数 = **18**（封盘 14 + 新 4）；四个新参数的 `low/base/high` 全 `null`、`released=false`。
⇒ `c2_registration_preserved = true` 当且仅当以上全成立。

### 3.4 不放行 / 不占位漂移

- 全文件所有 `low`/`base`/`high` 为 `null`、所有 `released` 为 `false`（与三份源一致）；
- `ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER`、`MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER` 两个 `_PLACEHOLDER` id 原样；
- 不新增/不删除任何 `parameter_id`（相对「封盘 14 + v3 新 4」集合）。

---

## 4. 判据 P（`provenance` 怎么写；冻结如下）

顶层是 JSON 数组 ⇒ **无顶层伴随键**（沿用 `I11A-HYP-APPROVE` 与 `OPEN2-C2-REGISTRATION` 两处先例）。因此 v4 的三方合并记录作为 **`v4[0].provenance`**（键名 `provenance`，`provenance_schema = "hypotheses_version_provenance/1"`），并满足：

| 字段 | 冻结值 |
|---|---|
| `version` | `"hypotheses_v4"` |
| `supersedes_file` | **三方**列表：`[{file, sha256, bytes, role: sealed_original\|v2\|v3}, …]`，三份 sha 必须等于 §1 实测值（即 `source_sha256` 三份齐全） |
| `modified_indices` | `[0, 1, 2]` |
| `unchanged_indices` | `[3, 4, 5, 6, 7]` |
| `new_file_sha256` | **`null`**（自指不可自证；实测值写入同目录 `handoff.json` / `merge_report.md`） |
| `merge_rule` | 逐字说明：`[0]←v2`、`[1]←v3`、`[2]←v3`、`[3..7]←封盘逐字节` |
| `source_versions` | 三份的 `sha256` + 各自 `modified_indices`（v2=`[0]`、v3=`[1,2]`、base=`[]`） |
| `v2_provenance_original` | **v2 原 `provenance` 整块原样嵌套**（不改一字） |
| `decision_sha256s_retained` | 两个值（`4d4ee106…` / `1a7838a1…`）都列出 |
| `sealed_attempt_modified` / `releases_nothing` / `does_not_claim_I11BAcceptance` | `false` / `true` / `true` |
| `file_shape` | 说明「顶层仍为 8 元素 JSON 数组；v4 合并记录附在下标 0 的 `provenance`；下标 1/2 的 `provenance` 逐字节保持 v3 原样」 |

**同时冻结**：
- `v4[1].provenance`、`v4[2].provenance` **逐字节 = v3 原文**（它们是 v3 那次动作的历史记录，`modified_indices=[1,2]` 描述的是 v3 自己，v4 不回改、不覆写）；
- `v4[0]` 相对 `v2[0]` 的**唯一差异 = `provenance` 字段**（这是本判据显式授权的增量；除该字段外 `v4[0]` 与 `v2[0]` 逐字节相同）。

---

## 5. 判据 F（fail-closed）

- **触发条件**：v2 与 v3 在**同一 index × 同一字段路径**上取值不同（不是「不同下标」，也不是「一方新增键、另一方未涉及」）。
- **触发动作**：判 **`blocked`**，停止生成 v4，输出完整逐字段冲突表（index / 路径 / v2 值 / v3 值 / 封盘值），**该结果即为合格交付**。
- **冻结时实测**：v2 改动集合 `{0}` ∩ v3 改动集合 `{1,2}` = ∅，冲突表为空 ⇒ **不触发**。
- **执行中复检**：生成 v4 前重新跑一遍同一比对；若与 §2 冻结表不符（例如源文件 sha 变了）⇒ 同样 `blocked`（源被改动 = 只读纪律被破坏）。

---

## 6. 判据 V（校验器纪律）

- 只调用 `validate(hypotheses, source_map, attempt, doc_texts)`；**绝不执行 `main()`**（不写 `validation_report.json`、不写 ascii log）；
- 运行方式：`PYTHONDONTWRITEBYTECODE=1 python -X utf8 -B -`（脚本经 stdin 传入）⇒ **零脚本文件、零 `__pycache__`、封盘 `tools/__pycache__` mtime 不变**；
- `source_map` 与抽取文本**只读**加载（路径：封盘 attempt 下 `evidence/I-11-A/source_map.json` + `source_map["documents"][*].extraction_output_path`）；
- 绿线：基线（封盘原件）`errors=0` **且** `hypotheses_v4.json` `errors=0`；任一 `errors>0` ⇒ 失败。

## 7. 判据 M（变异清单；冻结的红/绿定义）

**绿** = §3 全部判据为真 + §6 校验器 `errors=0`。
**红** = 指定检查返回非真 / 进程 `rc != 0`。变异在**内存中**施加（不落盘、不产生第 5 个文件）。

| # | 变异（对 v4 的内存改写） | 必须红的检查 | 期望 |
|---|---|---|---|
| **M1** | 把 `v4[0]` 整条换回**封盘原件**的下标 0（`state` 退回 `pending_professional_decision`、`decision_sha256=null`） | `CHK-C1`（`approved_frozen` 恰 1 条且在 `[0]` + `4d4ee106…` 在位） | rc≠0 |
| **M2** | 删掉 `v4[1]` 的 2 条 `additional_parameters`（C2 注册参数） | `CHK-C2`（四新 id 在位 + 计数 2/3/18） | rc≠0 |
| **M3** | 改动 `v4[3..7]` 之一：给 `v4[5].state_reason` 末尾加 1 个字节 | `CHK-BYTE`（`v4[i]≡base[i]` 逐字节，i=3..7） | rc≠0 |
| **M4**（附加） | 保留 `v4[0].state=approved_frozen`，但把 `decision.decision_sha256` 置 `null` | **校验器 `validate()`**（`E_STATE_APPROVED_BY_IMPLEMENTER`） | rc≠0、`errors>0` |
| **M5**（附加） | 把 `v4[2].decision.decision_sha256` 改成 `4d4ee106…`（换值） | `CHK-DSHA`（两个 sha 各在其位） | rc≠0 |

预期说明（预先声明，防止事后找补）：M1/M2/M3/M5 的红来自**本 oracle 的检查**；`validate()` 对 M1/M2/M3/M5 仍可能 `errors=0`（它不校验「来源下标」与 provenance），这正是本 oracle 存在的理由；M4 是**必须由 `validate()` 自己判红**的那一条。

---

## 8. 写入面（只有 4 件）

`oracle.md` · `hypotheses_v4.json` · `merge_report.md` · `handoff.json`，全部位于 `execution_runs/HYPOTHESES-V4-MERGE/a20260926-01/`。

收尾硬门（任一不满足 ⇒ 报失败）：
1. `hypotheses_v4.json` 写后 `json.load` 重解析通过（8 元素）、UTF-8 无 BOM、CR=0；
2. 校验器 `errors=0`；
3. M1/M2/M3（必做）+ M4/M5 全部 rc≠0（红）；
4. `git -c core.quotepath=false diff HEAD --name-only` 中**非 `.planning` 计数 = 0**（**不用 `git status`**）；
5. 封盘/v2/v3 的 sha256 与 §1 冻结值收尾复算一致（= 一个字节没动）。

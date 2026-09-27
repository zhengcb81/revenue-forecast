# merge_report · HYPOTHESES-V4-MERGE（v2 ⊕ v3 → hypotheses_v4.json）

- 工位：`execution_runs/HYPOTHESES-V4-MERGE/a20260926-01`（写入面 = 本目录 4 件）
- 角色：`implementer_version_merge` —— **版本合并，不是裁决**；不代签、不放行、不解除任何 BLOCKED
- 判据冻结件：同目录 `oracle.md`，sha256 `0549211ae5ae02c83a4aeb494ae9148b2b2f3fb9fbefaeaf82e2f3d60d7cf7b5` / 14,815 B（**先冻结后执行**，冻结后未改）
- 网络 0；git 写 0；**`git status` 未执行**；`.planning` 之外写入 0 字节；三份源只读（收尾复算未变）

---

## ① 逐下标差异表（封盘 / v2 / v3 三版对比，本工位独立复算）

判等口径：`json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",",":"))`；三份源实测 sha 见 §⑤。

| 下标 | `hypothesis_id` | 封盘 ≡ v2 | 封盘 ≡ v3 | v2 ≡ v3 | 谁改了 | v4 取自 |
|---|---|---|---|---|---|---|
| 0 | `H-CN-ZIJIN-SEG-01` | **否** | 是 | 否 | **仅 v2** | **v2** |
| 1 | `H-CN-ZIJIN-SEG-02` | 是 | **否** | 否 | **仅 v3** | **v3** |
| 2 | `H-CN-ZIJIN-VOL-03` | 是 | **否** | 否 | **仅 v3** | **v3** |
| 3 | `H-CN-ZIJIN-PLAN-04` | 是 | 是 | 是 | 无人改 | 封盘 |
| 4 | `H-CN-ZIJIN-ELIM-05` | 是 | 是 | 是 | 无人改 | 封盘 |
| 5 | `H-US-MSFT-SEG-01` | 是 | 是 | 是 | 无人改 | 封盘 |
| 6 | `H-US-MSFT-SEG-02` | 是 | 是 | 是 | 无人改 | 封盘 |
| 7 | `H-US-MSFT-SEG-03` | 是 | 是 | 是 | 无人改 | 封盘 |

### 逐字段差异（封盘 → 各版；路径 = JSON 路径）

**封盘 → v2：只动下标 0，6 处**

| 路径 | 封盘值 | v2 值 |
|---|---|---|
| `[0]/state` | `pending_professional_decision` | `approved_frozen` |
| `[0]/state_reason` | 原文（需行业 reviewer 裁定） | v2 裁定正文 |
| `[0]/decision/decision` | `pending` | `approved_frozen` |
| `[0]/decision/reason` | 原文 | v2 裁定正文 |
| `[0]/decision/decision_sha256` | `null` | `4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f` |
| `[0]/provenance` | 不存在 | 新增（`hypotheses_version_provenance/1`） |

⇒ **「v2 只动 [0]」属实**：下标 1–7 与封盘全等。

**封盘 → v3：只动下标 1、2，各 3 处**

| 路径 | 封盘值 | v3 值 |
|---|---|---|
| `[1]/additional_parameters#len` | 0 | **2**（铜/金 `realized_unit_revenue`） |
| `[1]/decision/decision_sha256` | `null` | `1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55` |
| `[1]/provenance` | 不存在 | 新增 |
| `[2]/additional_parameters#len` | 1 | **3**（+锌/银 `saleable_volume`） |
| `[2]/decision/decision_sha256` | `null` | `1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55` |
| `[2]/provenance` | 不存在 | 新增 |

⇒ **「v3 只动 [1][2]」属实**：下标 0、3–7 与封盘全等；`decision.decision` / `decision.reason` / `reviewer` / `professional_reviewer` / `state` / `state_reason` / `falsifier` **逐路径无差异**（v3 未升级任何批准状态）。

---

## ② 为什么这么裁（编排层裁定 + 本工位回源验证）

1. **正交性**：v2 改动集合 `{0}` ∩ v3 改动集合 `{1,2}` = **∅**，不存在「同一 index × 同一字段路径」的取值冲突 ⇒ 不是二选一，而是可叠加。
2. **两者各自只 supersede 封盘原件**（两份 `provenance.supersedes_sha256` 都 = `f2178768…`），**都没吸收对方** ⇒ 若按「最高修订件生效」读 v3，`[0]` 会退回 `pending_professional_decision`、`decision_sha256=null` ⇒ **`C1`（`approved_frozen=1`）静默消失**；反之若只读 v2，`[1]/[2]` 的 4 个注册参数消失 ⇒ **C2 注册面回退**。两种单边读法都会丢东西，所以唯一不丢信息的解是按来源下标拼接。
3. 因此裁并规则（授权：编排层派单 + `OPEN2-C2-REGISTRATION` 登记项 #3「属编排层裁并范围」）：**`[0]←v2`、`[1]/[2]←v3`、`[3..7]←封盘逐字节**，`provenance` 记三方来源。
4. **`fail-closed` 判据未触发**：`oracle.md` §5 的触发条件是「v2/v3 在同一 index 同一字段路径冲突」；实测冲突表 = `[]`（生成前复检一次，与冻结表一致；三份源 sha 与冻结值相同）。**若触发，本工位应输出 blocked + 冲突表而不写 v4 —— 本次没有触发。**

---

## ③ `hypotheses_v4.json` 事实

| 项 | 值 |
|---|---|
| 路径 | `execution_runs/HYPOTHESES-V4-MERGE/a20260926-01/hypotheses_v4.json` |
| sha256 / 字节 | `ebf6fa4e2f708c397165127926475d5426afbdef0d93864a795a8640029c4654` / **68,565** |
| 形态 | 与三份源同形的 **8 元素 JSON 数组**；UTF-8 无 BOM（首三字节 `91,10,32` = `[\n `）、CR=0、尾随 `\n`、写后 `json.load` 重解析通过、再序列化逐字节相同 |
| `provenance` | 附在下标 0 条目内（`version=hypotheses_v4`、`modified_indices=[0,1,2]`、`unchanged_indices=[3,4,5,6,7]`、`new_file_sha256=null`、三方 `supersedes_files`+`source_sha256`、v2 原 `provenance` 整块嵌套在 `v2_provenance_original`）；下标 1/2 的 `provenance` = v3 原文逐字节 |

### 逐下标来源 + 逐字节证明（元素级 sha256，按各文件自身的元素字节区间复算）

| 下标 | v4 元素 sha256 | 来源文件同元素 sha256 | 结论 |
|---|---|---|---|
| 0 | `aaffb000cebe8e7253c43046430bc5214e564708910511d96acae777a530ad43` | v2 = `5dd1cd544f40f82b301b9dca7d524086ef74728a0b182b969c7c30474931af7c` | **不同**（仅 `provenance` 块不同，见下） |
| 1 | `3bacd67710a3d652e95cd2447e40f8081fe818c9352e3ab0af6b6020ce95d1a0` | v3 = `3bacd677…`（同值） | **逐字节 = v3** |
| 2 | `31976c09946c12d00042c2b6fad42d52196e7340b16f237f007be0f911252474` | v3 = `31976c09…`（同值） | **逐字节 = v3** |
| 3 | `21a04c35f082d367b8bf8863ab29eba3f798ef2984cf066318d1dde37020c7f5` | 封盘 = 同值 | **逐字节 = 封盘** |
| 4 | `850bac6249e328233fbc63bebc82850a67e4ceba25c2811d9bd4e90a2f2612f0` | 封盘 = 同值 | **逐字节 = 封盘** |
| 5 | `81d8486573d11f257daebeb646cfcf720d7b3b7e45c78a8ed13420bbc4529e13` | 封盘 = 同值 | **逐字节 = 封盘** |
| 6 | `b70d11245125141ab1e3c7b9e26e305b95eea90783f89832c3ce5ff76a0d6d89` | 封盘 = 同值 | **逐字节 = 封盘** |
| 7 | `b29e46e7e60cbf1740fa775ab9f7d2f8700c13df9f8696fc3c8367b9e635ee20` | 封盘 = 同值 | **逐字节 = 封盘** |

**下标 0 的「除 provenance 外逐字节」证明（机器检查 `index0_delta_only_provenance_bytes = true`）**：
把 v4 的 `[0]` 元素字节与 v2 的 `[0]` 元素字节各自剥掉 `"provenance": {…}` 整块后，两段残余字节 **完全相同** ⇒ v4[0] 相对 v2[0] 的唯一差异就是 `provenance`；`state` / `state_reason` / `decision.decision` / `decision.reason` / `decision.decision_sha256` 逐字节取自 v2。

> 排版说明（不掩饰）：`hypotheses_v2.json` 只在**它自己的 provenance 块内**用了行内短数组（如 `"modified_indices": [0]`），其余部分与 `json.dumps(..., ensure_ascii=False, indent=1)` 规范序列化逐字节一致（本工位实测）。v4 用规范序列化 ⇒ 被替换的 `provenance` 块排版随之规范，这不产生任何**值**差异。

### 两个 `decision_sha256` 是否都保留 —— **是**

| 值 | 位置 | 结果 |
|---|---|---|
| `4d4ee106f4764d5347a9f4b328939eab4da9f27eea6918a70f9feade133e7b6f` | `v4[0].decision.decision_sha256` | 在位 |
| `1a7838a1c48ffbdd176e8f7cf445e64f80d99efa269e69a312c20ab332addb55` | `v4[1]` 与 `v4[2]` 的 `decision.decision_sha256` | 两处都在位 |
| 全文件出现的非空 `decision_sha256` 集合 | — | 恰好 = `{4d4ee106…, 1a7838a1…}`（无第三值、无 null 回退） |

### C1 与 C2 是否都在 —— **都在**

- **C1（`approved_frozen = 1`）= 保留**：全文件 `state=approved_frozen` 恰好 1 条且是 `v4[0]`（`H-CN-ZIJIN-SEG-01`），同条 `decision.decision=approved_frozen`、`decision_sha256=4d4ee106…`；`v4[1]`/`v4[2]` 的 `state` 仍为 `pending_professional_decision`、`decision.decision` 仍为 `pending`（**没有升级成批准**）。
- **C2（`[1]`/`[2]` 四个新参数）= 保留**：`[1].additional_parameters = 2`（`ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027`、`ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027`）、`[2].additional_parameters = 3`（既有 `ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027` + 新 `ZINC`、`SILVER` 两条 `SALEABLE_VOLUME`）；全文件 `parameter_id` = **18 个、零重复**（封盘 14 + 新 4），四个新 id 各出现 1 次。
- 不放行：`low/base/high` 全 `null`、`released` 全 `false`（机器扫描违规数 = **0**）；两个 `_PLACEHOLDER` parameter_id 原样在位。

---

## ④ 校验器 rc（只调 `validate()`，不跑 `main()`）

```
PYTHONDONTWRITEBYTECODE=1 python -X utf8 -B -   # 脚本经 stdin 传入，零脚本文件
只调用 validate_hypotheses.validate(hypotheses, source_map, attempt, doc_texts)
```

| 目标 | hypotheses | errors | rc |
|---|---|---|---|
| 基线（封盘 `hypotheses.json`） | 8 | **0** | **0** |
| `hypotheses_v4.json` | 8 | **0** | **0** |

- 未执行 `main()` ⇒ 未写 `validation_report.json` / ascii log；
- `-B` + `PYTHONDONTWRITEBYTECODE=1` ⇒ 封盘 `tools/__pycache__` 三个 `.pyc` 的 mtime 收尾复核仍为 **2026-09-20 03:45:14 / 03:36:31 / 04:16:53**；
- `source_map.json` 与抽取文本只读加载，零写入。

## 红/绿/变异 raw rc

rc 约定（与 `oracle.md` §7 冻结一致）：**rc=0 = 绿（检查全过 / 未判红）；rc≠0 = 红（检查失败、变异被抓）**。变异在**内存**中施加，不落盘。

| 运行 | 变异内容 | 指定检查 | 结果 | **raw rc** | `validate()` errors / rc |
|---|---|---|---|---|---|
| **绿（基线）** | 无（原样 v4） | ALL（7 项检查全过） | 全绿 | **0** | 0 / 0 |
| **M1（必做）** | 把 `[0]` 换回封盘原条目 | `CHK-C1` | **红**（`CHK-C1`/`CHK-DSHA`/`CHK-PROV` 同时转假） | **1** | 0 / 0 |
| **M2（必做）** | 删掉 `[1]` 的 2 条注册参数 | `CHK-C2` | **红** | **1** | 0 / 0 |
| **M3（必做）** | 改 `[5].state_reason` 加 1 字节 | `CHK-BYTE` | **红** | **1** | 0 / 0 |
| M4（附加） | `[0].decision.decision_sha256 = null`（state 仍 `approved_frozen`） | **`validate()`** | **红**：`E_STATE_APPROVED_BY_IMPLEMENTER` | **1** | **1 / 1** |
| M5（附加） | `[2].decision.decision_sha256` 换成 `4d4ee106…` | `CHK-DSHA` | **红** | **1** | 0 / 0 |

预期声明（写在变异之前，见 `oracle.md` §6/§7）：M1/M2/M3/M5 的红来自本 oracle 的判据检查 —— `validate()` 只校验命题体，**不校验「来源下标」与 provenance**，所以这四条它仍报 `errors=0`（实测一致）；M4 是**必须由 `validate()` 自己判红**的那一条，实测它确实红。五条变异全部按预期红，**零漏抓**。

执行方式：同一段检查脚本经 stdin 分别以 `NONE/M1/M2/M3/M4/M5` 为 `argv[1]` 跑 6 个独立 `python -X utf8 -B -` 进程，逐进程取 `$LASTEXITCODE`（上表 raw rc）。**没有为了跑变异写第 5 个文件、没有落任何变异副本到盘上。**

---

## ⑤ 只读载体收尾复算（开工前 = 收尾）

| 文件 | sha256 | 字节 |
|---|---|---|
| 封盘 `I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 51,697 |
| `I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json` | `32c22208573a71d53033c4535e8d0cb598c61710e06174196033d996999d7859` | 55,213 |
| `OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json` | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 61,231 |
| 封盘 `tools/validate_hypotheses.py` | `cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac` | 28,549 |

**四份全部与开工前相同 ⇒ 一个字节没改。**

**git（只用 `git -c core.quotepath=false diff HEAD --name-only`；`git status` 未执行）**：

| 项 | 值 |
|---|---|
| total | 3,829 |
| **非 `.planning`** | **0** |
| 本工位文件是否进 `git diff HEAD` | 否 —— 4 件均为未跟踪新路径（收尾 `git -c core.quotepath=false ls-files --others --exclude-standard -- '<本工位目录>'` 命中全部 4 件） |
| 本工位文件最终 sha256 | `oracle.md` = `0549211ae5ae02c83a4aeb494ae9148b2b2f3fb9fbefaeaf82e2f3d60d7cf7b5`（14,815 B）· `hypotheses_v4.json` = `ebf6fa4e2f708c397165127926475d5426afbdef0d93864a795a8640029c4654`（68,565 B）· `handoff.json` = `82901c06b0263fb54ac525cd2a791cac470c450490a5dcc47d66a75ce5db824a`（12,956 B，写后 `json.load` 重解析通过、42 顶层键）。**本文件 `merge_report.md` 自身的 sha 不自记（自指不可自证）**，由 `handoff.json.written_files` 登记 |

---

## ⑥ 登记（不回改任何既有文件）

1. **`AUTHORIZED-BY-VERBATIM-MISMATCH`**：派单给的 `authorized_by` 逐字串「既有 `hypotheses_v2.json` 与本 v3 在下标 0 分歧待裁并」**在盘上检索不到**（检索面：计划根 `*.md`/`*.json`、`OPEN2-C2-REGISTRATION/*`、仓库根 `*.md`）。语义唯一对应物是 `OPEN2-C2-REGISTRATION/a20260926-01/registration.md` **L177 登记项 #3**（`V2-V3-DIVERGENCE`，原文见 `oracle.md` §0）与其 JSON 侧 `handoff.json` L221、L266。⇒ `handoff.json` 里 `authorized_by` 同时登记两者，并标 `authorized_by_verbatim_on_disk=false`（派单措辞）/ `true`（L177 原文），**不把派单转述冒充盘上逐字**。
2. **`V2-INLINE-ARRAY-LAYOUT`**：`hypotheses_v2.json` 在其 provenance 块内用行内短数组，与其余两份的规范序列化不同排版；v4 用规范序列化。仅排版差异、零值差异（证明见 §③）。登记不回改。
3. 沿用 `OPEN2-C2-REGISTRATION` 的 `EV-16-SHA-MISMATCH` / `PLACEHOLDER-ID-NOT-ON-DISK` / `I10B-SECTION-BINDING` / `ARITH-INCONSISTENCY-1` 等登记：**本工位不重开、不回改、不关闭**。

---

## ⑦ 本工位**没有**做的事

不改封盘 / v2 / v3 任何字节 · 不解除 `OPEN-2` · 不放行任何参数（`low/base/high` 全 `null`、`released=false`）· 不改 `_PLACEHOLDER` · 不关任何 `BLOCKED-*` · 不产生 `I-11-B` 的 `ACCEPT` · **不把 `hypotheses_v4.json` 说成「已批准」**（它是版本合并件，`provenance.is_not_an_approval` 已写明）· 不代签任何 reviewer/owner · 不写计划五文件 · 不改 `model_cards.md` · 不写 `execution_v2/` · 不改 `validate_hypotheses.py` · 不改 `OPEN2-C2-REGISTRATION` / `I11A-HYP-APPROVE` 任何字节 · 零联网 · 零 git 写 · **未执行 `git status`** · `.planning` 之外 0 字节 · 写入面 = 本目录 4 件（无第 5 个文件、无临时副本）。

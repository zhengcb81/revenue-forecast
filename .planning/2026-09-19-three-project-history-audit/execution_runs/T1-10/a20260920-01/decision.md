# T1-10：`natural_window.py` 两个产品级缺陷 —— 结论为「②早已修好并已落定；①的枚举校验已加但**不是全函数**，留下一个**未闭合的残留**」

- 卡：`T1-10` / attempt `a20260920-01`
- 权限：`OWNER_DECISIONS.md` §13 **T1-10**（TIER-1）
- 性质：**核验 + 残留闭合**。本卡**不改**任何冻结件（SUT / `cases.json` / `frozen_expectations.*` / `oracle.md` / runner），只做测量、登记与移交。
- 状态：`review_pending`（本卡自述；未自签任何 `accepted`）

---

## 1. 裁定原文

`OWNER_DECISIONS.md` §13 **T1-10**（第七节第 4 项）：

> **授权立卡修复**（产品 + 计划双侧）：①`claim.basis` 补**枚举校验**；②修正 `union_of_windows`/`sum_of_windows` 把 quick_check 计入自然观察时长。**注意②已烧进冻结期望**（W1 `union_seconds=2220`）⇒ 修复须同时以**追加式 provenance** 更正期望，**不得回改冻结正文**。

来源为 `findings.md` 第七节第 4 项（I-14-B 的两个产品级缺陷，reviewer 自造、实测被 accept）。

---

## 2. 先厘清一个问题：这里是"产品级缺陷"，但不是"生产树里的文件"

裁定说"**产品级缺陷**"。盘上实测：

- `find` 全仓（排除 `.planning/`）**不存在**任何 `natural_window.py`；`tools/`、`tests/` 下没有任何同名或被引用的副本。
- 该文件的**唯一实例**是被测件 `execution_runs/I-14-B/a20260919-01/iso/natural_window.py`，且 **I-14-B 的 D-6 明写**该产物**刻意不进入生产树**（"不是第二份未签就落地的产物"）。

⇒ 故"**产品级**"在此指的是"**产品级形态的缺陷**"（同一个分类器将来若晋升进生产树会带走的缺陷），**不是**"某个生产文件里的缺陷"。**本卡因此不创建、不修改任何生产文件**；且按 **T1-9**，把该分类器**晋升进生产树**属**另一张卡**、当前无授权。

---

## 3. 缺陷 ② —— **早已修好，且追加式 provenance 已按裁定要求落地**（P-1 PASS）

被测件在盘上的 sha256 = `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796`，**等于** I-14-B 记录的 r2 修订。该修订是为回应独立 reviewer 的 `changes_required` 而做的 **r2 修复轮**，已由该 reviewer 以 **`accepted_scoped`** 结案（`review.md` 尾部裁决节：**P1、P2 两个阻断项经独立攻击电池确认已闭合**）。

②在代码里的落点：观察区间**只由观察阶段**构成，quick_check **永不进入**（`iso/natural_window.py:174-185`），并另加 **J15** 拒绝"把 quick_check 改名成第二个窗"的变体（`R-QC-IN-OBS`）。

裁定要求"**以追加式 provenance 更正期望、不得回改冻结正文**"——**盘上已经是这个形态**，无需再做：

| 要素 | 实测 |
|---|---|
| 新值 | `expected.W1.computed.union_seconds = 1740` |
| 旧值**保留** | `expected_superseded["W1"]["computed.union_seconds"]["old"] = 2220`（**正是裁定引用的数**） |
| 前像 | `pre_image_sha256 = 3ba2bb17…`（= r1 期望文件），且 r1 期望在 `harness/archive/` **逐字节可读** |
| 勘误条目 | `errata[0] = ERR-I14B-R2-01`，含 r1→r2 期望的**机械 unified diff**（182 行） |
| r1 原位文件 | `oracle.md` / `cases.json` **未被覆盖**；17 个 r1 文件全量归档（`harness/archive/MANIFEST.json`） |

**结论：②不存在未完成项。** 裁定的"授权立卡修复"对②而言**已经发生过**（在 I-14-B 自己的 r2 轮内），本卡只需**确认并登记**，不得重复"修"。

---

## 4. 缺陷 ① —— 枚举校验**已加**，但**不是全函数**（P-2 PASS / P-3–P-6 **FAIL 于完全性**）

①要求"`claim.basis` 补**枚举校验**"。盘上确实已有：

```python
BASIS_REGISTRY = {"sample_span", "command_total",
                  "observation_plus_quick_check", "sum_of_windows",
                  "union_of_windows"}                       # set

if basis not in BASIS_REGISTRY:  # J16 / P1
    refusals.append("R-BASIS-UNKNOWN")
```

**标量域上它工作**（P-2）：`basis` 为 `'wall_clock'`（未登记串）/`''`/`None`/`5`（非串标量）**全部** `reject_claim` + `R-BASIS-UNKNOWN`；`'union_of_windows'`（登记值）`accept_claim`。

**但容器域上它崩塌**（P-3）。`BASIS_REGISTRY` 是 **`set`**，而 `basis not in <set>` 对**不可哈希**的值会**抛异常**而不是返回 `True`：

| 探针 | `basis` 的 JSON 类型 | rc | 报告 | 结果 |
|---|---|---:|---|---|
| `registered_str` | `str` | 0 | 有 | `accept_claim` |
| `unregistered_str` | `str` | 0 | 有 | `reject_claim` / `R-BASIS-UNKNOWN` |
| `empty_str` | `str` | 0 | 有 | `reject_claim` / `R-BASIS-UNKNOWN` |
| `null` | `null` | 0 | 有 | `reject_claim` / `R-BASIS-UNKNOWN` |
| `scalar_non_str` | `int` | 0 | 有 | `reject_claim` / `R-BASIS-UNKNOWN` |
| **`list_of_registered`** | **`list`** | **4** | **无** | `internal_error: unhashable type: 'list'` |
| **`dict_object`** | **`dict`** | **4** | **无** | `internal_error: unhashable type: 'dict'` |

`main()` 的异常处理器把整个进程变成 rc=4 并**不写任何报告**（`iso/natural_window.py:468-473`）。

### 4.1 危害形态：这是**剥夺裁决**，不是**拒绝主张**

关键区别：`R-BASIS-UNKNOWN` 是**对该 case 判负**；rc=4 是**对该 case 判不了**——而且**连带把同批所有 case 一起判不了**。实测爆炸半径（P-4/P-6）：

| 臂 | 批次 | rc | 已裁决 case | 连带未裁决 |
|---|---|---:|---:|---:|
| **A** 12 个良构 + 1 个 `basis=[list]` | 13 | **4** | **0** | **13** |
| **B** 12 个良构 + 1 个 `basis='wall_clock'`（串） | 13 | 0 | 13 | **0** |
| **C** 1 个 calendar 良构 + 6 个 window 良构 + 1 个 `basis={dict}` | 8 | **4** | **0** | **8** |

- **对照臂 B** 证明：爆炸半径属于**值的形态**（容器），**不属于**"被拒绝"这件事本身。同样是"不合规的 `basis`"，**串**只伤自己，**容器**伤全批。
- **臂 C** 证明：伤害**跨 class**——一个 `window_accounting` case 的容器 `basis`，会连**与之无关的 `calendar` case** 一起打成"判不了"。

**为什么这在 J16 的语义下是个真缺口**：J16 存在的**全部理由**就是"**把 `basis` 的输入域锁死在封闭枚举内**"。而恰恰在**输入域的最坏一侧**（结构错误的 `basis`），J16 **不开火，而是把整个裁决机关炸掉**。这正是本项目反复记的**"护栏要致命不要误报"的反面**（SKILL 陷阱 13）：护栏本身成了**单点故障**——**一个畸形用例可以让整批合规用例无法被验收**。

### 4.2 该缺口**已由 reviewer 登记**，但**从未闭合**（P-8）

`review.md`「新增发现」**P4**（明确标注**非阻断**）已记下同一现象，并给出最小修法：

> `BASIS_REGISTRY` 由 `set` 改 `tuple`（或在 J16 前加 `isinstance(basis, str)` 守卫）；并在 oracle §11 明确"字段类型错误"属 schema 级 rc 2 还是 per-case 拒绝。

实测：**`oracle.md` §11 未回答该问题**（`字段类型` / `unhashable` / `rc 4` / `internal_error` / `isinstance` 五个关键词**全部缺席**）；`BASIS_REGISTRY` 至今仍是 **`set`**（`iso/natural_window.py:60`）。

⇒ 该残留**既非本卡发现的新漏洞，也非已闭合项**：它是 **reviewer 已指出、实现者未采纳、oracle 未定口径**的**敞口**。

### 4.3 今天**打不到**，但**正是 J16 管的那个面**（P-7）

实测 31 个负例（`cases.r2.json` + `cases.json`）中 **0 个** `basis` 是容器类型 ⇒ 残留**是潜伏的**，与 reviewer 的"非阻断"判定一致。

**但这不构成"可以不管"的理由**：`cases.json` 是**输入**，而 J16 的**职责**就是**管输入域**。用一个"今天恰好没人这么写"的输入来论证"枚举校验够用了"，等于说"样例没覆盖到所以判据不必是全函数"。⇒ 本卡**不同意**把它长期留作"非阻断"。

---

## 5. 附带发现（F 段，P-9/P-10）：I-14-B 的两处**已登记哈希无法从提交字节复算**

本卡在核验②的前像链时，顺带复算了 I-14-B 记录的 7 个关键哈希。**5 个逐字节可复算，2 个不行**：

| 文件 | 记录值 | 盘上（=HEAD blob） | 复算条件 |
|---|---|---|---|
| `harness/frozen_expectations.r2.json` | `6f814d0a…` | `a24d8ab3…` | **仅 `LF→CRLF` 变换后**才等于记录值 |
| `harness/cases.r2.json` | `c00a3a00…` | `23d89fb2…` | **仅 `LF→CRLF` 变换后**才等于记录值 |
| `harness/frozen_expectations.r1.json`（archive） | `3ba2bb17…` | `3ba2bb17…` | 原样 ✅ |
| `harness/cases.json` | `5d8c4592…` | `5d8c4592…` | 原样 ✅ |
| `oracle.md` | `bdd0407a…` | `bdd0407a…` | 原样 ✅ |
| `iso/natural_window.py` | `7fff6f0c…` | `7fff6f0c…` | 原样 ✅ |
| `harness/run_cases.py` | `f2a07d0b…` | `f2a07d0b…` | 原样 ✅ |

**根因**：本仓 `core.autocrlf = true`。那两个文件是 **r2 轮新建**的，其 sha256 是在 **CRLF 工作副本**上算的并写进了 `binding.json` / `commands.json` / `handoff.json`；而**提交进 git 的 blob 是 LF**。⇒ 记录值**不是提交字节的 sha256**，而是**另一个字节域的**sha256。

**关键限定（必须与"篡改"分开）**：HEAD blob 与盘上文件**同**为 `a24d8ab3…` ⇒ **内容自提交以来未变**。坏的**不是内容**，是**"哈希取在哪个字节域上"没写明**。

**这正是本项目第 6 次同源教训的重演**：**判据必须匹配被比对量的形态**——这里"比对面"是**行尾规范化前/后**。而且它**恰好命中 T1-13 的同一条**（内容问题不能用字节哈希回答时，要先固定字节域）。

**登记性质**：**新增、非阻断、不改任何值**。按 **T1-12 ①** 追加式登记即可；`binding.json` 等的原值**不回改**。

---

## 6. 本卡**没有**做的事（边界）

| 事项 | 为何不做 |
|---|---|
| 改 `iso/natural_window.py`（把 `set` 改 `tuple` 或加守卫） | 该文件是 **r2 冻结件**，且其 hash 被 5 处 evidence 引用。改它须**整体重跑重冻、记为新 rN**（同 **T1-11** 的"互锁对"纪律）。**T1-10 授权的是"立卡修复"，本卡性质是核验**；真正动刀应是一张**继承 r2 的新修订卡**，且须先由 owner 定"字段类型错误"的口径（属 §8 退出码契约的解释）。本卡**登记该需要**。 |
| 创建生产 `natural_window.py` | 无生产实例；D-6 明禁晋升；晋升属**另一张卡**且 **T1-9** 未授权。 |
| 改 `oracle.md` §11（补答字段类型归属） | **T1-12 ①** 形态属**编排层/该卡作者**；本卡只**登记缺口**。 |
| 改 `binding.json` / `commands.json` / `handoff.json` 的 CRLF 哈希 | 冻结件；按 **T1-12 ①** 追加式登记，**不回改原值**。 |
| 任何 `status` 转移 | 本卡自述 `review_pending`，无资格授予。 |

---

## 7. 移交（编排层处理）

1. **T1-10 ① 的残留**：授权一张**继承 I-14-B r2** 的新修订卡，把 `BASIS_REGISTRY` 的成员测试改为**对容器安全**的写法（reviewer 已给最小修法），并**同时**在 `oracle.md` §11 追加**"字段类型错误属 schema 级 rc 2 还是 per-case 拒绝"**的裁定——**这一条是专业口径，须由该卡的 reviewer 出具，不可由实现者自填**（同 **T1-24/T1-21** 纪律）。
2. **F 段哈希域缺口**：按 **T1-12 ①** 在 I-14-B 的 `binding.json` / `commands.json` / `handoff.json` **追加**一行，写明"`cases.r2.json` 与 `frozen_expectations.r2.json` 的记录 sha256 取自 **CRLF 工作副本**；提交 blob 为 LF，其 sha256 分别为 `23d89fb2…` / `a24d8ab3…`"。**不回改原值。**
3. **②** 无需移交：已由 I-14-B r2 自轮闭合并经 reviewer `accepted_scoped`。

---

## 8. 边界守住（实测）

- 生产文件改动：**0**（`git diff HEAD --name-only -- . ':(exclude).planning'` 为空）
- 生产锚点：`scripts/model_registry.py` = `9ec65295…` **一致**；`scripts/model_extensions.py` = `9939480b…` **一致**
- **被核验件写入 0 次**：`iso/natural_window.py`、`cases.json`、`cases.r2.json`、`frozen_expectations.*`、`oracle.md`、`review.md`、`run_cases.py`、`binding.json`、`commands.json`、`handoff.json` —— 全部**只读**
- **未做任何删除操作**（含未删本卡早期两次幂等调试遗留的 `run_a.json` / `run_b.json`，见 §9）
- 未推 `status`、未代签、未晋升
- 全部 JSON 可解析；本卡三个产物哈希见 `handoff.json`

---

## 9. 本卡自身的过程披露（如实）

1. **`verify_t1_10.py` 首跑 `TypeError: window_case() missing 1 required positional argument: 'basis'`** —— 我自己的脚本 bug（`window_case` 未给 `basis` 默认值，而良构臂调用时省略了它）。**修正**：给 `basis="union_of_windows"` 默认值。由解释器当场拦下，**未污染任何证据**。
2. **证据文件首版**非幂等**（三次运行三个哈希）** —— 根因：`subprocess` 捕获的 stdout 里回显了**随机 temp 目录**的报告路径。**两轮修正**：(a) 不再记录 temp 路径本身；(b) 仅替换"字面路径"不够——stdout 是 **JSON 编码**过的，反斜杠**已加倍**（`\\`），且 `mkdtemp` 后缀可能含 `_`，故改为**按 `t1_10_<随机>` 形状做正则脱敏**。**终态**：连跑 **4 次同哈希 `22ead5c5…`**、无残留 temp 引用。
   > 这条本身是**同一族教训的又一例**：**"我替换了那个路径"不等于"那个路径不再出现"**——**编码后的形态**是另一个被比对面。（与 F 段的 CRLF 缺口**同源**。）
3. **`run_a.json` / `run_b.json` 两个幂等调试的中间比较文件仍在盘上**。用户已明令"**不要搞删除操作**"，故**原样保留**并在此披露；它们**不是**本卡交付物，本卡 `handoff.json` **不登记**它们。**须由编排层决定**是保留还是清理（**本卡不删**）。

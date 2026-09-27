# sync_report · I-10-B 段绑定同步（stale/clone 2 → 0）

- 工位：`execution_runs/I10B-SECTION-BINDING-SYNC/a20260926-01`｜角色：`implementer_section_sync`
- 判据冻结件：同目录 `oracle.md`（sha256 `e0a2f864d65508413f3a6efd563902b1fe39748ae9dfbc7e0585849a470921c8`，12,099 B）—— **先冻结后动手**
- 边界：网络 0｜git 写 0｜**`git status` 未执行**｜`.planning` 之外写入 **0 字节**｜**未执行生产树的 `validate_execution_pack.py`**（`validation.json` 未被覆写）
- 数据明细：同目录 `sync_result.json`

---

## ① 冻结（先于一切目标写入）

冻结的内容：`stale`/`clone` 判据逐行照抄 `validate_execution_pack.py` L21–L36（**不改判据**）、要改的字段（`dispatch.json` 的 `cards[79].source_section_sha256` + `card_I-10-B.md` 末尾追加）、`model_cards.md` **本体不再动**、`dispatch.json` **为何必须就地改值而非追加**、红/绿/四条变异臂、fail-closed 四条件。冻结顺序：写 `oracle.md` → 复算 sha → 才动 `dispatch.json`/`card_I-10-B.md`。

## ② 改前红复现（只读，生产树 0 写入）

只读工具 `recompute_section_binding.py`（逐行照抄原判定式；**不 import、不执行**原脚本，不写 `validation.json`）：

```
python recompute_section_binding.py <execution_v2>
=> stale=1 clone=1 error_count=2 ；rc=1
```

**两条错误逐条内容**：

| # | 错误名（原脚本 L34/L36 逐字） | 具体失配 |
|---|---|---|
| 1 | `stale extracted card source I-10-B` | 段实测 `sha256 = 3ceb4692e0adf961cc98da8aa91da023ae58930adbe241cee1bd22f18e37e704`（8,404 B）≠ `dispatch.json` 记录 `0ecb7a135b608444c1da25808c7ecc337c96511f2932b0401424faa2ac3ad4d7` |
| 2 | `single-card body differs from source I-10-B` | `card_I-10-B.md` 去头正文 1,499 字符 ≠ 源段 5,402 字符（源段已含追加的附录 A，3,692 字符） |

段组核对：`source_document = model_cards.md` 的卡 **32** 个，`I-10-B` 是**最后一个**标题 ⇒ 段终点 = `len(source)`；追加节标题 `## 附录 A` / `### A.1…A.3` 不匹配任何卡 id ⇒ **只有 I-10-B 扩段**，其余 31 段 0 变化。

## ③ 同步写入（两件，均在 `.planning` 内）

**为什么这么改**：`model_cards.md` 末尾追加（`855b5e2d…/165,695` → `cc24be67…/171,460`，前缀不变）扩了最后一个卡片段 `I-10-B`。判定式要求两个下游同时跟随：段哈希记录值（`dispatch.json`）与卡文正文（`card_I-10-B.md`）。二者正是登记项移交的同步对象；`model_cards.md` 是触发源，**本体 0 字节**。

1. **`card_I-10-B.md` 只追加（T1-12 ① 形态）**
   - 追加内容 = `model_cards.md[165695:]` 的 5,765 字节（sha `9ff74f25…`），按本文件既有 CRLF 约定加 32 个 CR ⇒ **+5,797 字节**；
   - 既有 2,938 字节**一字未动**（前缀证明见 §④）；
   - 效果：卡文正文 == 新源段 ⇒ `clone` 消失。

2. **`dispatch.json` 单点改值（机器文件，无法追加 —— oracle §4.1 已先写明理由）**
   - `cards[79].source_section_sha256`：`0ecb7a13…` → `3ceb4692e0adf961cc98da8aa91da023ae58930adbe241cee1bd22f18e37e704`；
   - 实现：旧 64 位 token 在全文件唯一出现 1 次 ⇒ **仅该 64 字节区间被替换**（实际 58 字节取值不同，偏移 632979–633042）；文件长度、CRLF 数（14,757）、无 BOM 全部保持；`json.load` 重解析通过；
   - **语义 diff 恰 1 处**：`/cards[79]/source_section_sha256`（前后两份 JSON 递归比对）；
   - 前像全文保留在 `preimage_dispatch.json`（`c63764d1…/663,351 B`），卡文前像保留在 `preimage_card_I-10-B.md`（`4129871d…/2,938 B`）。

## ④ 改后绿复现 + 前缀不变证明

```
python recompute_section_binding.py <execution_v2>
=> stale=0 clone=0 error_count=0 ；rc=0   （92 个段绑定，model_cards.md 组 32 个）
```

| 证明 | 实测 |
|---|---|
| 卡文前缀不变 | 改后文件前 2,938 B sha256 = `4129871d7fc6bf8766cb68d0dcf8839799437d286292097e0b8432c21dc02e25` = 前像 ⇒ **`prefix_bytes_unchanged = true`** |
| 卡文后像 | `5bf5232613d0616cbc2d846b29032f7759ce6f2b6487ae44e72ccc7f83c53086` / 8,735 B（与冻结前预计算值逐字符相同） |
| 追加内容同源 | 卡文新增字节（LF 归一后）== `model_cards.md[165695:]` ⇒ `true` |
| dispatch 只改一字段 | 长度 663,351 不变；字节差 58（偏移 632979–633042）；语义 diff 仅 `/cards[79]/source_section_sha256`；`json.load` OK；CRLF 14,757 不变 |
| `model_cards.md` 未再动 | `cc24be67…/171,460` 改后复算相同 ⇒ **0 字节** |
| `validation.json` 未被覆写 | `a14dbf14eac3f5fea215e120c49628fd4af64115e436ed3996d28058ef7767d5/175,007` 前后相同 |
| 判据未改 | `validate_execution_pack.py` `7841d014…/6,556` 前后相同 |

## ⑤ 红 / 绿 / 变异的 raw rc

| 臂 | 载体 | raw rc | stale | clone | 错误 |
|---|---|---|---|---|---|
| **RED 改前** | 生产树（只读复算） | **1** | 1 | 1 | `stale extracted card source I-10-B` + `single-card body differs from source I-10-B` |
| **GREEN 改后** | 生产树（只读复算） | **0** | 0 | 0 | `[]` |
| **M1 同步值改错**（改回 `0ecb7a13…`） | `%TEMP%/…/m1` | **1** | 1 | 0 | `stale extracted card source I-10-B` |
| **M2 卡文 section 改错**（正文 +1 行） | `%TEMP%/…/m2` | **1** | 0 | 1 | `single-card body differs from source I-10-B` |
| **M3a 删掉 `model_cards.md` 追加段（同步态）** | `%TEMP%/…/m3a` | **1** | 1 | 1 | 两条同时回来 |
| **M3b 删掉追加段（原始态）** | `%TEMP%/…/m3b` | **0**（段绑定） | 0 | 0 | 段绑定回到 32 段 0 错基线；此时验证器的红是**另一类**错误（产品源漂移） |

**原脚本（`%TEMP%` 副本内跑，允许项 6）**：`real_red` rc=**1** / `error_count=92`（含 2 条段绑定）· `real_post` rc=**1** / `90`（段绑定 0）· `real_pre` rc=**1** / `90`（段绑定 0）。副本落在 `%TEMP%` 使 `RF=P.parents[2]` 指向临时根，非段绑定错误被布局性放大，但**三臂完全相同**；可归因于段绑定的差值恰为 **2 → 0**，且**三臂 rc 全为 1 ⇒ 整体红/绿结论未变**。

**另一类红（生产树，只读复算）**：`validation.json`（2026-09-21T19:28:12Z）32 条错误**全部**是 `source binding changed or missing`（产品源漂移）、段绑定 0 条；本工位按 L69–L81 只读复算现值 = 121 绑定 / **57 错**（产品 56 + 模型快照 1），其去重集合是 2026-09-21 记录（8 条去重）的**超集** ⇒ 漂移早已存在且在增长，**与本工位写入面无关、本轮 0 触碰**。

## ⑥ 与 `model_cards.md` 追加的关系（因果链）

```
OPEN2-C2-REGISTRATION 按 T1-12 ① 在 model_cards.md 末尾追加附录 A（+5,765 B，前缀不变）
  └─ I-10-B 是该文件最后一个卡标题 ⇒ 段终点 = len(source) ⇒ 段扩 5,765 B
       ├─ 段 sha ≠ dispatch.json 记录值            ⇒ stale（错误 1）
       └─ card_I-10-B.md 正文 ≠ 新源段             ⇒ clone（错误 2）
            └─ 本工位：dispatch 单字段同步 + 卡文只追加同段内容 ⇒ 2 → 0
```

`model_cards.md` 的追加**是触发源，不是缺陷**：附录 A 自身在 `### A.3` 已预先声明该副作用并移交；本工位**不动它**，只让两个下游跟随源文本——这正是 `stale`/`clone` 两条判据的语义（「记录值须等于当前源段」「抽取卡文须等于当前源段」），因此**不改判据、不弱化判据**。

## ⑦ fail-closed：**未触发**

四条检查全过：① 无需改 `validation.json`（只读复算 + `%TEMP%` 副本取证）；② 无需改 `model_cards.md` 任何字节；③ 无需改 `validate_execution_pack.py` 判据；④ dispatch 单 token 变更 + 卡文前缀不变 + `model_cards.md` 不变 + 段绑定 0 错**同时成立**。⇒ `blocked = false`。

## ⑧ 收尾核验

- `git -c core.quotepath=false diff HEAD --name-only`：开工前 **3,827** → 收尾 **3,829**（+2 = `execution_v2/dispatch.json`、`execution_v2/card_I-10-B.md`）；**非 `.planning` = 0（前后皆 0）**；`git status` 未执行；git 写 0。
- 三件 JSON 写后 `json.load` 重解析通过；全部交付 UTF-8 无 BOM；`oracle.md`/`sync_result.json`/`sync_report.md`/`handoff.json` 纯 LF（CR=0）；`dispatch.json`/`card_I-10-B.md` 保持各自既有 CRLF。
- 变异副本留在 `%TEMP%\i10b_sync_a20260926\`（仓库外，未污染生产树）。

## ⑨ 本工位**没有**做的事

不解除 `OPEN-2`；不放行任何参数；不关任何 `BLOCKED-*`；不产生 `ACCEPT`；不改封盘 `I-11-A` 任何字节；**不改 `model_cards.md` 既有行（本体 0 字节）**；不改 `validate_execution_pack.py` 判据（若认为判据本身也错 ⇒ 只登记、不改）；不代签；不写五份计划文件；不跑生产树整脚本（`validation.json` 未覆写）；不改 `model_cards.json`/`dispatch.md`/其他 `card_*.md`；零联网、零 git 写、未执行 `git status`、`.planning` 之外 0 字节。

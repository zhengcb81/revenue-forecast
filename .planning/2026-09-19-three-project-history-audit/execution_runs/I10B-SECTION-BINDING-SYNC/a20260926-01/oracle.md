# oracle · I10B-SECTION-BINDING 同步（段绑定 stale/clone 2 → 0）

- 工位：`execution_runs/I10B-SECTION-BINDING-SYNC/a20260926-01`（新建）
- 角色：`implementer_section_sync`（实现者·段绑定同步面）—— 非 reviewer、不代签、不裁专业问题
- 写入面（唯一）：`execution_v2/dispatch.json`（`I-10-B.source_section_sha256` 一处值）＋ `execution_v2/card_I-10-B.md`（**末尾追加**）＋ 本 attempt 目录交付件
- 网络：0；git 写：0；**`git status` 不执行**；`.planning` 之外写入 0 字节；**不执行 `validate_execution_pack.py` 的生产树运行**（它会覆写 `validation.json`）
- 本文件是**判据冻结件**：先写本文件 → 复算本文件 sha256 → **之后**才动 `dispatch.json` / `card_I-10-B.md`

---

## 1. 授权（逐字）

### 1.1 `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/registration.md` §⑥ 登记项 `I10B-SECTION-BINDING`（逐字）

> 4. **`I10B-SECTION-BINDING`**：`model_cards.md` 末尾追加使 `validate_execution_pack.py` 的最后一个卡片段（`I-10-B`）出现 `stale` + `clone` 两条错误（追加前基线 32 段 0 错，追加后 32 段 2 错，逐条同名于 `oracle.md` §6 的冻结预测）。`dispatch.json` / `card_I-10-B.md` 不在写入面 ⇒ **不修改**，移交编排层按 T1-12 ① 同步。该验证器在本轮之前已因 32 条产品源漂移而不通过，本轮不改变其红/绿结论。

同源同义的移交句（`model_cards_append.md` §④，逐字）：

> - **移交项（给编排层）**：按 T1-12 ① 同步刷新 `I-10-B` 的 `source_section_sha256` 与卡文正文（或把本追加节纳入 `I-10-B` 段的正式勘误流程），再重跑 `validate_execution_pack.py`。

### 1.2 `T1-12 ①` 原文（`OWNER_DECISIONS.md` L218，逐字）

> | T1-12 | **第八节第 11 项：今后编辑已冻结正文的统一规则** | **采纳建议**：一律采用 **① 形态**（追加新节 + 行级「第 X 行已过时，以本节为准」标注）；**不外扩**就地编辑授权。既有 M21–M24「仅此一次、自此冻结」裁决**维持**。 |

同形先例（本计划已落地的追加式更正，逐字）：`execution_v2/START_HERE.md` L228/L231 「`## rc 码表·勘误 append-3（REM-84；owner 授权 2026-09-22「A-2: 授权」；T1-12 ① 形态）`」/「**本节只登记、不回改上方任何字节**：本追加前全文 = 18452 B，前缀 sha256 `a9cb5a4a…`（追加后复算须一致，已验证）。」

---

## 2. 回源读的实测（本工位复算，非引用自述）

| 文件 | sha256（实测） | 字节 | 备注 |
|---|---|---|---|
| `execution_v2/model_cards.md`（触发源，后像） | `cc24be67c06d250342d7624ad7d0190a21f67505317dc4e749d3e809deb0748d` | 171,460 | CR=0；前 165,695 B 复算 = `855b5e2d06cc02a1c103316224a428fcfc7a1cc8fb3cfbf07f1f066a552855ab` = 前像 ⇒ 追加式成立 |
| 追加尾块 `model_cards.md[165695:]` | `9ff74f250a4d31599b1ccded8e289db606159f9d7862c39142a4834dfaabd0cb` | 5,765 | LF=32、CR=0 |
| `execution_v2/dispatch.json`（改前） | 见 §5 前像表 | 663,351 | CRLF；92 卡；旧值 `0ecb7a13…` 在全文件出现 **1** 次、在 `execution_v2` 其他文件出现 **0** 次 |
| `execution_v2/card_I-10-B.md`（改前） | `4129871d7fc6bf8766cb68d0dcf8839799437d286292097e0b8432c21dc02e25` | 2,938 | **CRLF**（CR=36 = LF=36）、无 BOM |
| `execution_v2/validate_execution_pack.py` | 只读，判据不改 | — | 见 §3 |
| `validation.json` | 只读，**本轮不写** | — | 见 §6 fail-closed |

---

## 3. 判据冻结（逐行照抄 `validate_execution_pack.py` L21–L36 的段绑定判定式；**不改判据本身**）

```
source   = (P/c['source_document']).read_text(encoding='utf-8-sig')     # 通用换行：CRLF→LF
own      = [x for x in cards if x['source_document']==c['source_document']]
headings = [(m.start(), other['id']) for other in own
            for m in [re.search(r'^#{2,3} '+re.escape(other['id'])+r'(?=\s|[·—:：]).*$', source, re.M)] if m]
headings.sort()
i        = index of c['id'] in headings            # 必须恰好 1 个，否则 'cannot uniquely bind'
start    = headings[i][0]
end      = headings[i+1][0] if i+1 < len(headings) else len(source)     # 最后一个卡片段 → 文件尾
section  = source[start:end].strip() + '\n'
stale  := hashlib.sha256(section.encode('utf-8')).hexdigest() != c['source_section_sha256']
           → 错误名 `stale extracted card source <id>`
clone  := (P/c['document']).read_text(encoding='utf-8-sig').split('\n\n',1)[-1] != section
           → 错误名 `single-card body differs from source <id>`
```

冻结的三条事实（本工位实测）：

1. `source_document = model_cards.md` 的卡共 **32** 个（`n_own = 32`）⇒ 32 个段绑定；
2. `I-10-B` 是这 32 个标题中**最后一个**（`is_last_heading = true`）⇒ 段终点 = `len(source)`，任何末尾追加都扩它的段；
3. 末尾追加节的标题是 `## 附录 A …` / `### A.1…A.3`，**不匹配任何卡 id** ⇒ 只有 `I-10-B` 的段变化，其余 31 段不变。

**改前红（实测，本工位独立复算）**：32 段、2 错、逐条为

| # | 错误名（逐字） | 值 |
|---|---|---|
| 1 | `stale extracted card source I-10-B` | 段 sha 实测 `3ceb4692e0adf961cc98da8aa91da023ae58930adbe241cee1bd22f18e37e704`（8,404 B）≠ `dispatch.json` 记录 `0ecb7a135b608444c1da25808c7ecc337c96511f2932b0401424faa2ac3ad4d7` |
| 2 | `single-card body differs from source I-10-B` | `card_I-10-B.md` 正文（去首段头后 1,710 字符）≠ 段（5,402 字符，含追加的 3,692 字符） |

---

## 4. 要改哪些字段 / 不改哪些（冻结）

### 4.1 `execution_v2/dispatch.json` —— **必须改值，无法追加**（理由在此写明）

- 要改的**唯一**字段：`cards[]` 中 `id == "I-10-B"` 的 `source_section_sha256`：`0ecb7a13…` → `3ceb4692e0adf961cc98da8aa91da023ae58930adbe241cee1bd22f18e37e704`。
- **为什么不能按 T1-12 ① 追加**：`dispatch.json` 是机器生成的 JSON（`build_dispatch.py` L52 由段内容现算该字段），目标值位于 `cards` 数组中部（约 L14624），JSON 语义要求该键只有**一个**值；在文件末尾追加任何字节都无法改变读取到的值，反而会破坏 `json.load` 结构。⇒ 它属于**必须就地改值的机器文件**，不是可追加的正文。
- **降级到最小改动**（等价于"只改该行"）：对旧 64 位 hex token 做**唯一一次字节替换**（实测唯一出现 1 次），不重新序列化整个 JSON。证明方式：改后文件 = 改前文件在偏移 `k` 处的 64 字节被替换，**其余 663,287 字节逐字节相同**（改后复算：`len` 不变、`json.load` 重解析通过、`diff` 仅 1 行）。
- **前像保留**：改前 `dispatch.json` 全文副本存本目录 `preimage_dispatch.json`（sha 见 §5），改后复算其 sha 必须与前像一致。

### 4.2 `execution_v2/card_I-10-B.md` —— **只追加，既有字节 0 改动**

- 追加内容 = `model_cards.md` 的追加尾块（5,765 B，`9ff74f25…`），按本文件既有换行约定做 LF→CRLF（该块 32 个 LF；本文件 CR=36=LF=36，**全文件 CRLF**）。
- 预期后像：**8,735 B**、sha256 `5bf5232613d0616cbc2d846b29032f7759ce6f2b6487ae44e72ccc7f83c53086`（写前预计算，写后必须相等）。
- **前缀不变证明**：改后文件前 2,938 字节 sha256 必须 = `4129871d7fc6bf8766cb68d0dcf8839799437d286292097e0b8432c21dc02e25`（前像）。
- 为什么 CRLF：保持本文件既有字节风格不变（既有 36 行 CRLF 一字不动）；`validate_execution_pack.py` 用 `read_text` 通用换行读取，CRLF/LF 均归一为 LF 后比对，故对判据中性。**预期 `clone == section = true`**（写前已预演）。
- **前像保留**：`preimage_card_I-10-B.md`。

### 4.3 `execution_v2/model_cards.md` —— **不再动任何字节**（触发源）

- 它是 OPEN2-C2-REGISTRATION 的追加产物，前缀已证不变；本轮**0 字节写入**。若执行中发现必须改它 ⇒ **不改**，转 §6 fail-closed。
- 本轮收尾复算：`cc24be67…` / 171,460 B 必须与开工前相同。

### 4.4 明确不改

`validate_execution_pack.py` 判据本身、`model_cards.json`、`validation.json`、`build_dispatch.py`、`card_*.md`（除 `card_I-10-B.md` 追加外）、封盘 `I-11-A`、`OPEN2-SUBSTITUTE-CALIBER`、`model_cards.md` 既有行、任何 `_PLACEHOLDER`/阈值/放行字段。若判据本身被认为有错 ⇒ **只登记、不改**。

---

## 5. 前像/后像（改前必须记录，改后复算）

| 文件 | 前像 sha256 | 前像字节 | 后像预期 |
|---|---|---|---|
| `dispatch.json` | 开工时复算填入 `sync_result.json.before` | 663,351 | 同长度、仅 64 B token 变 |
| `card_I-10-B.md` | `4129871d7fc6bf8766cb68d0dcf8839799437d286292097e0b8432c21dc02e25` | 2,938 | `5bf5232613d0616cbc2d846b29032f7759ce6f2b6487ae44e72ccc7f83c53086` / 8,735 |
| `model_cards.md` | `cc24be67c06d250342d7624ad7d0190a21f67505317dc4e749d3e809deb0748d` | 171,460 | **不变**（0 字节） |
| `validation.json` | 只读，收尾复算须与开工前相同 | — | **不变** |

---

## 6. 红/绿与变异清单（冻结；变异只在 `%TEMP%` 副本上做，生产树 0 变异）

判定式运行方式：**只读复算**（把 L21–L36 段绑定判定式逐行照抄进本目录 `recompute_section_binding.py`，**不 import、不执行** `validate_execution_pack.py`，不写 `validation.json`）；`rc = 1` 当且仅当段绑定错误数 > 0，`rc = 0` 当且仅当 0 错（与原脚本 `raise SystemExit(1 if errors else 0)` 同形）。另在 `%TEMP%` 副本中跑**原脚本**取其 raw rc（原脚本在 `%TEMP%` 内写它自己的 `validation.json`，与生产树无关）。

| 臂 | 状态 | 预期 |
|---|---|---|
| **RED（改前）** | 生产树当前态（追加后、同步前） | 32 段、`stale=1`、`clone=1`、错误名逐条如 §3、**rc=1** |
| **GREEN（改后）** | 同步后生产树 | 32 段、`stale=0`、`clone=0`、**rc=0** |
| **M1 同步值改错** | `%TEMP%` 副本：把 `I-10-B.source_section_sha256` 改成 `0ecb7a13…`（或任一错值） | 变红：`stale=1`（`clone=0`）、rc=1 |
| **M2 卡文 section 改错** | `%TEMP%` 副本：在 `card_I-10-B.md` 正文尾部增删 1 字节 | 变红：`clone=1`（`stale=0`）、rc=1 |
| **M3a 删掉 `model_cards.md` 追加段（同步态）** | `%TEMP%` 副本：`model_cards.md` 截回 165,695 B（前像 `855b5e2d…`） | 变红：段回到 `0ecb7a13…` ≠ 已同步的新值，且卡文仍含追加 ⇒ `stale=1 + clone=1`、rc=1（**与 M1/M2 各只错一条不同：两条同时回来，证明同步确实绑定在该追加上**） |
| **M3b 删掉追加段（未同步的原始态）** | `%TEMP%` 副本：追加前像 + 追加前的 dispatch/卡文 | 段绑定 **0 错**（回到追加前基线 32 段 0 错），整体验证器仍为**另一类红**——`source binding changed or missing`（32 条产品源漂移，2026-09-21 `validation.json` 本就有）⇒ **红/绿结论未变** |

## 7. fail-closed 条件（触发即判 `blocked` 并写明卡点，属合格结果）

1. 需要改 `validation.json`（或任何非 `dispatch.json`/`card_I-10-B.md` 的生产文件）才能让判定式转绿；
2. 需要改 `model_cards.md` 任何字节（含删/改既有行）；
3. 需要改 `validate_execution_pack.py` 判据、或改 `card_I-10-B.md` 既有字节；
4. 改后不能同时满足：`dispatch.json` 仅 64 B token 变且 `json.load` 通过、`card_I-10-B.md` 前 2,938 B 前缀不变、`model_cards.md` sha 不变、段绑定 0 错。

## 8. 硬性禁令

只读生产树（`dayu-agent`、`company-wiki`、`revenue-forecast` 非 `.planning` 路径 0 字节）；不写 `.planning` 之外任何路径；禁 git 写；**禁 `git status`**；禁联网；不跑覆写 `validation.json` 的整脚本（生产树）；不解除 `OPEN-2`、不放行参数、不关 `BLOCKED-*`、不产生 ACCEPT、不改封盘 `I-11-A`、不代签、不写五份计划文件。

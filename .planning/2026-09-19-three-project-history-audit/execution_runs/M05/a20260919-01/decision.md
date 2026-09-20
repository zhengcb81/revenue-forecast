# M05 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a
professional decision (cross-process locking, publication transaction boundaries, fiscal-period / restatement /
gross-vs-net and payability attribution, unidentifiable model parameters, sample and statistical thresholds,
deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net or deployment decision arises in this card:
the scope is a pure in-process calculator plus read-only disclosure mapping. The decisions that DO arise are
accounting/disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in
`evidence/M05/accounting_decision.md`:

- DEC-M05-1: whether the disclosed daily-proportional recognition policy may enter this model at all
- DEC-M05-2: whether a period-end member count may stand in for the annual average (proposed: no)

## Escalated to the owner (not decided here)

- OQ-04: `scripts/model_registry.py:335` silently zero-fills an omitted optional driver that has no explicit
  default; for `project_backlog.backlog_remeasurements` this is the exact field whose omission can turn into
  fictitious revenue. No position asserted, no product change.

## Hash ledger · document/evidence consistency revision r3 (findings F-M08-06 / -07 / -08 / -09)

本节由 r3 **插入**（位置 = 被折叠的第二段 r2 节的原起点，也就是保留段末尾；该位置同时也是文件末尾。只增不删既有正文）。它只处置独立 reviewer 定点复核提出的文档/证据一致性缺陷。**冻结期望、容差、拒绝条件、披露数值、实现与产品一律未改。**

### 1) `oracle.md`：重复 r2 节折叠去重（F-M08-06）

| 项 | 值 |
|---|---|
| 改前 sha256（整文件） | `fb8213ff988878b31f0bec31231f1542ab34089860cbc3a23fcc94e3eec6612f`（12592 字节） |
| 改后 sha256（整文件） | `7fda03b153fd9a3707fba3a1057c9eb2ed6d2f772cdd79b6c1a33de9bb639320`（14844 字节） |
| 唯一改动 | **折叠**第二段重复 r2 节（1900 字节，sha256 `ecb4175c61734998d389b07c6b97332d90799f1d52bc47f4ff48dca2c942d7ae`；与第一段除「本节追加前 sha256」一行外逐字节相同），并在**该段原起点插入** r3 provenance-gap 说明（4152 字节，sha256 `46f4385605a64ae4f32957c1bcc3af2f44ad0b878f083a743e660bfd2dd56627`）。**字节账：`pre 12592 − 1900 + 4152 = live 14844`；`live[:10692] == pre[:10692]` 逐字节成立**（即 live 以 pre 的完整 r2 正文为前缀，r3 说明紧接其后；这是**插入**，不是尾部追加） |
| 冻结期望文本 | **逐字节未动**：保留段 `[0,10692)` 改前/改后 sha256 同为 `893cf5a59cd1eb31771361f7e44efc6bece6310b6d5591e9678cf4e284930673`；第 0–10 节与第一段 r2 节全在该段内 |
| 权威 v1 基准（保留） | `ae1986f61c03daa6ac633ffcc9eaf36060de08f1f39bf8f8c90e5315fe4e943a`，可在改后文件的前 `5835` 字符（8774 字节）处复现，等于 reviewer r1 记录的 v1 值 |
| provenance gap（原值照录） | `afeefe438e977ad4b449497baeac5c38eb4c003d5f7712d7079da37cbad4e0ce` —— 穷举全部字节切点后它只能复现为「v1 冻结体 + 第一段 r2 正文」这一中间写缓冲，**不是**任何「追加前」的文档状态，故标注为来源不可考、不得用作 hash 基准 |

一条命令即可证明冻结期望部分字节相同（P1 保留段逐字节相同 / P2 增量记账精确，即 live = pre[:K] + 插入段 / P3 全部冻结节逐字节相同 / P4 r2 节恰好剩 1 段 / P5 两个基准值均可复现）：

```
<iso venv python> -X utf8 -B recovery/docfix-r3/f06_verify.py > recovery/docfix-r3/f06_verify.out.txt
```

原始输出：`recovery/docfix-r3/f06_verify.out.txt`；合并前镜像留档 `recovery/docfix-r3/oracle_pre_M05.md`。

### 2) `oq_rulings.json`：计数与署名更正（F-M08-07）

| 项 | 改前 | 改后 |
|---|---|---|
| sha256 | `0b784c6b2ec32a0a133574c90a49cfcfeaef9556b9c23c0d991e0ddff927a83e` | `722a014f7356a7c69f60ef17e9eddea481f016c7762eacbaa1a6adbffe831831` |
| ratio 驱动总数 | 40 | **41** |
| 不在 `[0,1]` 的 ratio 驱动 | 3 | **4**（补 `direct_growth.growth_rate`，其定义域为 `(-1, inf)`） |
| 署名/人称 | 把独立 reviewer 署名为作者、以第一人称「我枚举了…」 | 客观第三方：**由实现者枚举、由 reviewer 复核**（原文保留在 `source_original_r2` / `reviewer_basis_original_r2`） |

实现者自己重算的枚举证据：`evidence/M05/oq_rulings_enumeration.json`（sha256 `f07269cd0f03ee68b4c0750b840845aa5e3857127f5585ebc8a17b411d7fb175`）；枚举脚本 `recovery/docfix-r3/f07_enumerate.py`，原始输出 `recovery/docfix-r3/f07_enumerate.out.txt`。

### 3) r1→r2 重打包的限定说明（F-M08-08）

「冻结件未改」这句话**须限定**为：`oracle.md` 的 v1 冻结正文与全部冻结期望（正例/连续性/默认值/负例/容差/拒绝条件/披露数值）一字未改。但 r2 为了带新注释**重打包**过证据文件，其字节与 hash 已变；差异经证明**仅来自新增注释**，没有任何既有数值被改动。

本卡在 F-M08-08 点名的证据文件上没有变化：`M06/M07 negative_results.json` 与 `M07 run_result.json` 与经校验的 r1 快照**逐字节相同**（见 `f08_named_files.out.txt`）。

| file | sha256 r1 | sha256 now (read from disk) | verdict |
|---|---|---|---|
| `after/rerun_sha256.json` | `5f94f06da96171d1…` | `5a5f5df4123c780c…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `commands.json` | `46ff6bc5c046d3be…` | `92875088938cf0b4…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M05/evidence_hashes.json` | `fe2a73ca356ae5e3…` | `ca955f4c011497ad…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M05/source_manifest.json` | `4505e5800c13a593…` | `894df90294510249…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `handoff.json` | `b9b2f748c57d8854…` | `79943a6c5c927599…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |

- 变化文件全表（含旧/新 sha256）见 `binding.json` / `handoff.json` 的 `docfix_r3_hash_ledger.repack_scope`，以及 `evidence/M05/docfix_r3.json`。
- 「差异仅为注释」的证明：剥离新增注释键后与 r1 对象**深度相等**（逐字节比较既有叶子值：M08 `cases.json` 117/117 相等、`run_result.json` 220/220 相等、`negative_results.json` 189/189 相等）。原始输出：`recovery/docfix-r3/f08_named_files.out.txt`、`f08_repack_diff.out.txt`。
- r1 基线本身经校验：`copy/`（reviewer r1 快照）的四份 `oracle.md` 均等于各卡自载的权威 v1 hash，故该快照确为 r1 态。
- `binding.json` / `handoff.json` 的 `input_hashes` 是**运行前（r1）**的输入 hash，按设计属历史值，**不主张**等于当前字节；其与当前值的差异同样仅为上述注释。**为避免接手者按 `review_and_handoff.md` 的「先重算当前 hash」步骤误停，同一处并排给出 `input_hashes_current`（同名键的当前摘要）与 `input_hashes_current_vs_input_hashes`（逐键列出哪些相等、哪些是历史值）**。
- `after/rerun_sha256.json` 是 r2 时点的清单（其 `generated_after` 自述如此），其中 `oracle.md` 条目为 r2 值；r3 值见上表与 `evidence/M05/docfix_r3.json`。


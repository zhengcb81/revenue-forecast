# M07 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a
professional decision (cross-process locking, publication transaction boundaries, fiscal-period / restatement /
gross-vs-net and payability attribution, unidentifiable model parameters, sample and statistical thresholds,
deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net or deployment decision arises in this card:
the scope is a pure in-process calculator plus read-only disclosure mapping. The decisions that DO arise are
accounting/disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in
`evidence/M07/accounting_decision.md`:

- DEC-M07-1: the utilisation denominator convention (not disclosed)
- DEC-M07-2: whether a back-solved billing rate may be used (proposed: no)

## Escalated to the owner (not decided here)

- OQ-04: `scripts/model_registry.py:335` silently zero-fills an omitted optional driver that has no explicit
  default; for `project_backlog.backlog_remeasurements` this is the exact field whose omission can turn into
  fictitious revenue. No position asserted, no product change.

## Hash ledger · document/evidence consistency revision r3 (findings F-M08-06 / -07 / -08 / -09)

本节由 r3 **追加**（追加式更正，未删除任何原文）。它只处置独立 reviewer 定点复核提出的文档/证据一致性缺陷。**冻结期望、容差、拒绝条件、披露数值、实现与产品一律未改。**

### 1) `oracle.md`：重复 r2 节合并去重（F-M08-06）

| 项 | 值 |
|---|---|
| 改前 sha256（整文件） | `ca4543b16aabb2963694f1c34fa6e5a56021de5db80cacde68eee7246d01d646`（11469 字节） |
| 改后 sha256（整文件） | `b418885668bf8d972287a001c92d259c70045a9cfe6eda17006dfb0394697cfe`（13275 字节） |
| 唯一改动 | 删除**第二段重复 r2 节**（1903 字节，sha256 `c7ae7185301ffa16cd46425702103ffb371dfdf3a2fe85f2ed0d1932bf78192b`；与第一段除「本节追加前 sha256」一行外逐字节相同）+ 追加 r3 provenance-gap 说明（3709 字节，sha256 `26e88983565036d130dd80ceee13bfbbcb1224e23beae6ce38d76d27d258ade2`） |
| 冻结期望文本 | **逐字节未动**：保留段 `[0,9566)` 改前/改后 sha256 同为 `2883780ca072cc72ee2b07842c9767c67e8611140ee1fb38846d577663d5805c`；第 0–10 节与第一段 r2 节全在该段内 |
| 权威 v1 基准（保留） | `1eeb6806b82cb7fc70265fac512d263693e041076d195f4a0720dcbc3c9a3591`，可在改后文件的前 `5305` 字符（7645 字节）处复现，等于 reviewer r1 记录的 v1 值 |
| provenance gap（原值照录） | `9da4b1ec7ea348641ab1f97c37ea2930d69f007e414875eefeed7476a5005d75` —— 穷举全部字节切点后它只能复现为「v1 冻结体 + 第一段 r2 正文」这一中间写缓冲，**不是**任何「追加前」的文档状态，故标注为来源不可考、不得用作 hash 基准 |

一条命令即可证明冻结期望部分字节相同（P1 保留段逐字节相同 / P2 增量记账精确 / P3 全部冻结节逐字节相同 / P4 r2 节恰好剩 1 段 / P5 两个基准值均可复现）：

```
<iso venv python> -X utf8 -B recovery/docfix-r3/f06_verify.py > recovery/docfix-r3/f06_verify.out.txt
```

原始输出：`recovery/docfix-r3/f06_verify.out.txt`；合并前镜像留档 `recovery/docfix-r3/oracle_pre_M07.md`。

### 2) `oq_rulings.json`：计数与署名更正（F-M08-07）

| 项 | 改前 | 改后 |
|---|---|---|
| sha256 | `ea82d38816a987196ccaaece5d5eedf051e29fc666443a54b9c45b52a7c91286` | `3a49462674e8f9ebe5799047a043df3643b406bf0b0c56303303b536a5c7e6f3` |
| ratio 驱动总数 | 40 | **41** |
| 不在 `[0,1]` 的 ratio 驱动 | 3 | **4**（补 `direct_growth.growth_rate`，其定义域为 `(-1, inf)`） |
| 署名/人称 | 把独立 reviewer 署名为作者、以第一人称「我枚举了…」 | 客观第三方：**由实现者枚举、由 reviewer 复核**（原文保留在 `source_original_r2` / `reviewer_basis_original_r2`） |

实现者自己重算的枚举证据：`evidence/M07/oq_rulings_enumeration.json`（sha256 `7daff28f932f6e1185e5c86427947db409506dfbe77699f5d5235f6f831add23`）；枚举脚本 `recovery/docfix-r3/f07_enumerate.py`，原始输出 `recovery/docfix-r3/f07_enumerate.out.txt`。

### 3) r1→r2 重打包的限定说明（F-M08-08）

「冻结件未改」这句话**须限定**为：`oracle.md` 的 v1 冻结正文与全部冻结期望（正例/连续性/默认值/负例/容差/拒绝条件/披露数值）一字未改。但 r2 为了带新注释**重打包**过证据文件，其字节与 hash 已变；差异经证明**仅来自新增注释**，没有任何既有数值被改动。

本卡在 F-M08-08 点名的证据文件上没有变化：`M06/M07 negative_results.json` 与 `M07 run_result.json` 与经校验的 r1 快照**逐字节相同**（见 `f08_named_files.out.txt`）。

| file | sha256 r1 | sha256 now (read from disk) | verdict |
|---|---|---|---|
| `evidence/M07/run_result.json` | `59d8f4b3c8d327cd…` | `59d8f4b3c8d327cd…` | UNCHANGED (byte-identical to r1) |
| `evidence/M07/negative_results.json` | `937874fcd5147d8f…` | `937874fcd5147d8f…` | UNCHANGED (byte-identical to r1) |
| `after/rerun_sha256.json` | `63e575c8c31d7c51…` | `d3f58abf7b392e52…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `commands.json` | `46ff6bc5c046d3be…` | `92875088938cf0b4…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M07/evidence_hashes.json` | `d007ec59a6ec9b29…` | `d1d9fea8eaf8eddc…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M07/source_manifest.json` | `efd7577dc921d378…` | `e45f803645706dc8…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `handoff.json` | `3f458b9fa5a76b17…` | `7432a2fdee2fc94b…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |

- 变化文件全表（含旧/新 sha256）见 `binding.json` / `handoff.json` 的 `docfix_r3_hash_ledger.repack_scope`，以及 `evidence/M07/docfix_r3.json`。
- 「差异仅为注释」的证明：剥离新增注释键后与 r1 对象**深度相等**（逐字节比较既有叶子值：M08 `cases.json` 117/117 相等、`run_result.json` 220/220 相等、`negative_results.json` 189/189 相等）。原始输出：`recovery/docfix-r3/f08_named_files.out.txt`、`f08_repack_diff.out.txt`。
- r1 基线本身经校验：`copy/`（reviewer r1 快照）的四份 `oracle.md` 均等于各卡自载的权威 v1 hash，故该快照确为 r1 态。
- `binding.json` / `handoff.json` 的 `input_hashes` 是**运行前（r1）**的输入 hash，按设计属历史值，**不主张**等于当前字节；其与当前值的差异同样仅为上述注释。
- `after/rerun_sha256.json` 是 r2 时点的清单（其 `generated_after` 自述如此），其中 `oracle.md` 条目为 r2 值；r3 值见上表与 `evidence/M07/docfix_r3.json`。


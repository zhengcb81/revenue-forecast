# M06 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a
professional decision (cross-process locking, publication transaction boundaries, fiscal-period / restatement /
gross-vs-net and payability attribution, unidentifiable model parameters, sample and statistical thresholds,
deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net or deployment decision arises in this card:
the scope is a pure in-process calculator plus read-only disclosure mapping. The decisions that DO arise are
accounting/disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in
`evidence/M06/accounting_decision.md`:

- DEC-M06-1: how the principal/agent gross-vs-net policy determines the activity basis
- DEC-M06-2: whether the `rate` in `monetization_rate` implies a [0,1] probability (proposed: no)

## Escalated to the owner (not decided here)

- OQ-04: `scripts/model_registry.py:335` silently zero-fills an omitted optional driver that has no explicit
  default; for `project_backlog.backlog_remeasurements` this is the exact field whose omission can turn into
  fictitious revenue. No position asserted, no product change.

## Hash ledger · document/evidence consistency revision r3 (findings F-M08-06 / -07 / -08 / -09)

本节由 r3 **追加**（追加式更正，未删除任何原文）。它只处置独立 reviewer 定点复核提出的文档/证据一致性缺陷。**冻结期望、容差、拒绝条件、披露数值、实现与产品一律未改。**

### 1) `oracle.md`：重复 r2 节合并去重（F-M08-06）

| 项 | 值 |
|---|---|
| 改前 sha256（整文件） | `c9c4aa7e9fd207ff188b27f5e2a51a02975606e949f7d8ab66bf9de00a4618fb`（10912 字节） |
| 改后 sha256（整文件） | `206b27b3d8897f77d40007386fc932f114e8cf9c436ebcabe942db5b11615cc3`（12915 字节） |
| 唯一改动 | 删除**第二段重复 r2 节**（1706 字节，sha256 `a4d12cd09b0a9d95a7ce4a6f7c5d0417a01d47ca00cde44d7c6dffb3961d72c8`；与第一段除「本节追加前 sha256」一行外逐字节相同）+ 追加 r3 provenance-gap 说明（3709 字节，sha256 `56a448b39c2be5c909a43c87fb46ecac9f76ca607b8859ceda191ce5eef910ca`） |
| 冻结期望文本 | **逐字节未动**：保留段 `[0,9206)` 改前/改后 sha256 同为 `b4c7b4acdd7b324bd7da8530a879c2279e281e2c8af8e3dd94438fa21f3a81c0`；第 0–10 节与第一段 r2 节全在该段内 |
| 权威 v1 基准（保留） | `d335f5ec2a699bef008686249d77f2f9af6e2b6306510e57a83446f92df7e3eb`，可在改后文件的前 `5152` 字符（7482 字节）处复现，等于 reviewer r1 记录的 v1 值 |
| provenance gap（原值照录） | `c07da2412b2e27faa33405878383001336ef1d8ce88c7c9ffd70a8209ffaea7b` —— 穷举全部字节切点后它只能复现为「v1 冻结体 + 第一段 r2 正文」这一中间写缓冲，**不是**任何「追加前」的文档状态，故标注为来源不可考、不得用作 hash 基准 |

一条命令即可证明冻结期望部分字节相同（P1 保留段逐字节相同 / P2 增量记账精确 / P3 全部冻结节逐字节相同 / P4 r2 节恰好剩 1 段 / P5 两个基准值均可复现）：

```
<iso venv python> -X utf8 -B recovery/docfix-r3/f06_verify.py > recovery/docfix-r3/f06_verify.out.txt
```

原始输出：`recovery/docfix-r3/f06_verify.out.txt`；合并前镜像留档 `recovery/docfix-r3/oracle_pre_M06.md`。

### 2) `oq_rulings.json`：计数与署名更正（F-M08-07）

| 项 | 改前 | 改后 |
|---|---|---|
| sha256 | `ced1c6075b01b1404e56ed8d767cd0fc406d7b65a2e89c2647b94383e151567f` | `e73b23779cec8a78e680d84d66786a926c53bc9130c0ac905b31a747a3cba831` |
| ratio 驱动总数 | 40 | **41** |
| 不在 `[0,1]` 的 ratio 驱动 | 3 | **4**（补 `direct_growth.growth_rate`，其定义域为 `(-1, inf)`） |
| 署名/人称 | 把独立 reviewer 署名为作者、以第一人称「我枚举了…」 | 客观第三方：**由实现者枚举、由 reviewer 复核**（原文保留在 `source_original_r2` / `reviewer_basis_original_r2`） |

实现者自己重算的枚举证据：`evidence/M06/oq_rulings_enumeration.json`（sha256 `95ed73fbce1d26d9084c4db0cdf7b822b6bc2ecc01269344630c7668da6e6e6d`）；枚举脚本 `recovery/docfix-r3/f07_enumerate.py`，原始输出 `recovery/docfix-r3/f07_enumerate.out.txt`。

### 3) r1→r2 重打包的限定说明（F-M08-08）

「冻结件未改」这句话**须限定**为：`oracle.md` 的 v1 冻结正文与全部冻结期望（正例/连续性/默认值/负例/容差/拒绝条件/披露数值）一字未改。但 r2 为了带新注释**重打包**过证据文件，其字节与 hash 已变；差异经证明**仅来自新增注释**，没有任何既有数值被改动。

本卡在 F-M08-08 点名的证据文件上没有变化：`M06/M07 negative_results.json` 与 `M07 run_result.json` 与经校验的 r1 快照**逐字节相同**（见 `f08_named_files.out.txt`）。

| file | sha256 r1 | sha256 now (read from disk) | verdict |
|---|---|---|---|
| `evidence/M06/negative_results.json` | `5d2793c2d8c5d1ea…` | `5d2793c2d8c5d1ea…` | UNCHANGED (byte-identical to r1) |
| `after/rerun_sha256.json` | `02363d139200ce8c…` | `051ff48ee9e5f70b…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `commands.json` | `46ff6bc5c046d3be…` | `92875088938cf0b4…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M06/evidence_hashes.json` | `8fbe99ea71b20b2a…` | `88443257e3f5f23c…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M06/source_manifest.json` | `32aa3beffc5afff7…` | `cd5fdc4119f2dd8a…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `handoff.json` | `991fc034fb27f274…` | `f9fc17473cf9f2c8…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |

- 变化文件全表（含旧/新 sha256）见 `binding.json` / `handoff.json` 的 `docfix_r3_hash_ledger.repack_scope`，以及 `evidence/M06/docfix_r3.json`。
- 「差异仅为注释」的证明：剥离新增注释键后与 r1 对象**深度相等**（逐字节比较既有叶子值：M08 `cases.json` 117/117 相等、`run_result.json` 220/220 相等、`negative_results.json` 189/189 相等）。原始输出：`recovery/docfix-r3/f08_named_files.out.txt`、`f08_repack_diff.out.txt`。
- r1 基线本身经校验：`copy/`（reviewer r1 快照）的四份 `oracle.md` 均等于各卡自载的权威 v1 hash，故该快照确为 r1 态。
- `binding.json` / `handoff.json` 的 `input_hashes` 是**运行前（r1）**的输入 hash，按设计属历史值，**不主张**等于当前字节；其与当前值的差异同样仅为上述注释。
- `after/rerun_sha256.json` 是 r2 时点的清单（其 `generated_after` 自述如此），其中 `oracle.md` 条目为 r2 值；r3 值见上表与 `evidence/M06/docfix_r3.json`。


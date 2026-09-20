# M08 decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a
professional decision (cross-process locking, publication transaction boundaries, fiscal-period / restatement /
gross-vs-net and payability attribution, unidentifiable model parameters, sample and statistical thresholds,
deployment migration and natural-observation qualification).

## DEC-M08-1 · `contract_changes` sign (THIS CARD IS STOPPED BY IT)

| reading | content | positive result on the card input | source |
|---|---|---|---|
| A | subtract the magnitude 10 of `contract_changes`, subtract the -15 remeasurement | 50 | `card_M08.md` L42 arithmetic |
| B | `- contract_changes` applied to signed amounts | 70 | `card_M08.md` L8 + L42 symbols |
| C | `+ contract_changes` applied to signed amounts | 50 | `docs/buy_side_model_audit_2026-09-18.md:42`, `scripts/model_registry.py:228` |

Measured probes (see `evidence/M08/negative_results.json`):

- `contract_changes=+10` -> `85.0` (reading C; A and B would both give 65)
- `contract_changes=-20` -> `55.0` (readings A and C; B would give 95)

Therefore the implementation is uniquely identified as reading C.

**Required adjudication:** the owner (or the I-10 specialist) must state which reading is authoritative and,
if it is C, correct `card_M08.md` L42 and the index (`model_cards.md` L522-552, `dispatch.md`), because
`execution_v2/README.md:20` forbids choosing the more convenient document. Until then this card's `formula`
qualification is **blocked** and no product change is made.

Alternatives rejected: (1) editing the oracle expectation to match the implementation - that is fitting the
expectation to the result; (2) editing `model_registry.py` - no independent counter-example, no adjudicated
specification, and it would break the upstream formula string and the existing tests.

## Other decisions

See `evidence/M08/accounting_decision.md` (DEC-M08-2 the bridge vs accounting revenue, DEC-M08-3 residual risk).

## Escalated to the owner (not decided here)

- OQ-04: `scripts/model_registry.py:335` silently zero-fills an omitted optional driver that has no explicit
  default; for `project_backlog.backlog_remeasurements` this is the exact field whose omission can turn into
  fictitious revenue. No position asserted, no product change.

## DEC-M08-1 · r3 correction (this section supersedes the r1 wording above; the r1 text is preserved verbatim above it)

r1 的 DEC-M08-1 只写到「owner 需裁定哪个读法权威，若是 C 则更正 card_M08.md L42 与索引」。该措辞不足以构成可执行的处置，也**没有绑定「禁止换例子」的约束**。现更正为：**唯一出路是 `handoff.json` → `owner_action_required`（id `F-M08-02-remediation`）记录的三步**，此处逐条复述，使本决策记录自洽、不能被读成可自由选择：

1. **owner 或 I-10 专业人**：裁定读法 **C**（`+ contract_changes`，按带符号金额相加）为权威。依据为四处互证：`docs/buy_side_model_audit_2026-09-18.md:42`；`reviews/revenue/model_ledger.jsonl` 的 `RF-MODEL-project_backlog.original_claim`（第 8 行）；`scripts/model_registry.py:228`（及 `_project_backlog` 的 fsum，第 102 行）；`card_M08.md` L8（「变更与重估为带符号金额」）。两个符号探针已把实现唯一识别为 C（`contract_changes=+10` → 85.0；`contract_changes=-20` → 55.0）。
2. **索引 owner**：更正 `card_M08.md` L42 与索引副本 `model_cards.md`（M08 段）、`dispatch.md`，使印出的算例与权威读法一致。**约束：数值算例与冻结期望 `[50]` 不得改动** —— 读法 C 在同一合成输入上同样得 50，因此只更正**符号呈现**，不是改答案。**明确禁止**为了「让方便的那个读法过关」而重新挑选算例（`handoff.json.owner_action_required.steps[2].explicitly_forbidden` = `re-picking the example so that only the convenient reading passes`）。
3. **独立 reviewer**：索引更正完成后，在**同一 `code_root`**（`9ec65295…`）上复跑冻结卡并留档；此后该卡方可按 `accepted_scoped`（仅 `formula` 资格）签收。

**实施者与 reviewer 都不得执行第 1、2 步，也不得自行改卡**；本处置不允许任何产品改动。第 2 步完成前 `formula` 保持 **blocked**，且不授予 disclosure_adaptation 或 accuracy 资格。

被否决的替代方案（r1 已列，此处维持）：(1) 改 oracle 期望去迁就实现——那是拿结果反推期望；(2) 改 `model_registry.py`——没有独立反例、没有已裁定的规格，且会破坏上游公式串与既有测试。

### DEC-M08-1 不是「已决」

`decision.md` 是决策记录，不是裁定本身。**本节不构成 owner 裁定**：读法 C 的权威性仍待 owner/I-10 拍板，本卡维持 blocked。
## Hash ledger · document/evidence consistency revision r3 (findings F-M08-06 / -07 / -08 / -09)

本节由 r3 **追加**（追加式更正，未删除任何原文）。它只处置独立 reviewer 定点复核提出的文档/证据一致性缺陷。**冻结期望、容差、拒绝条件、披露数值、实现与产品一律未改。**

### 1) `oracle.md`：重复 r2 节合并去重（F-M08-06）

| 项 | 值 |
|---|---|
| 改前 sha256（整文件） | `ff68cc5e01f87035e62d801727ddfa50bf9fd85bb30a4f799a4bf2eda36edbb1`（19745 字节） |
| 改后 sha256（整文件） | `a85e1e62509dbfc0299f99b7e36a0a0a98a5b75549c94d356913d0e4dcbcba22`（19874 字节） |
| 唯一改动 | 删除**第二段重复 r2 节**（3585 字节，sha256 `e6f76ab22366e514bc59ca8f5d7f1710b6e1c7a707766ad62f698b45ba525f03`；与第一段除「本节追加前 sha256」一行外逐字节相同）+ 追加 r3 provenance-gap 说明（3714 字节，sha256 `bf2013e21a6ab7dae77e69d3dc21f0ea20c5db8ad798700f110fa8db6e6936be`） |
| 冻结期望文本 | **逐字节未动**：保留段 `[0,16160)` 改前/改后 sha256 同为 `7aa5805025a2a692be30c148907a4b5473541ebfa0ce45a31c82c1e1d067b7dc`；第 0–10 节与第一段 r2 节全在该段内 |
| 权威 v1 基准（保留） | `47481cab511f2bdf655ffbe3ff1f2d0b0d21c1f8c599cbb101c98124b2d57011`，可在改后文件的前 `8177` 字符（12557 字节）处复现，等于 reviewer r1 记录的 v1 值 |
| provenance gap（原值照录） | `b0d5f2093825dbbe7121cd8ac254669fb95562147a121724dee5c85e29bc7249` —— 穷举全部字节切点后它只能复现为「v1 冻结体 + 第一段 r2 正文」这一中间写缓冲，**不是**任何「追加前」的文档状态，故标注为来源不可考、不得用作 hash 基准 |

一条命令即可证明冻结期望部分字节相同（P1 保留段逐字节相同 / P2 增量记账精确 / P3 全部冻结节逐字节相同 / P4 r2 节恰好剩 1 段 / P5 两个基准值均可复现）：

```
<iso venv python> -X utf8 -B recovery/docfix-r3/f06_verify.py > recovery/docfix-r3/f06_verify.out.txt
```

原始输出：`recovery/docfix-r3/f06_verify.out.txt`；合并前镜像留档 `recovery/docfix-r3/oracle_pre_M08.md`。

### 2) `oq_rulings.json`：计数与署名更正（F-M08-07）

| 项 | 改前 | 改后 |
|---|---|---|
| sha256 | `7e9002c34c1cd3ec567b7e62e233dc5e5df62c7657f7cb35e1bb4e39462d333e` | `fc811ebbaac6ef5a02c8e369ffdb019b3e7a310c4c82c7264648f74241470545` |
| ratio 驱动总数 | 40 | **41** |
| 不在 `[0,1]` 的 ratio 驱动 | 3 | **4**（补 `direct_growth.growth_rate`，其定义域为 `(-1, inf)`） |
| 署名/人称 | 把独立 reviewer 署名为作者、以第一人称「我枚举了…」 | 客观第三方：**由实现者枚举、由 reviewer 复核**（原文保留在 `source_original_r2` / `reviewer_basis_original_r2`） |

实现者自己重算的枚举证据：`evidence/M08/oq_rulings_enumeration.json`（sha256 `71ecb2882be88ecdced6227fcda718fcc910f335d474fa4be504b1e2e28cec0d`）；枚举脚本 `recovery/docfix-r3/f07_enumerate.py`，原始输出 `recovery/docfix-r3/f07_enumerate.out.txt`。

### 3) r1→r2 重打包的限定说明（F-M08-08）

「冻结件未改」这句话**须限定**为：`oracle.md` 的 v1 冻结正文与全部冻结期望（正例/连续性/默认值/负例/容差/拒绝条件/披露数值）一字未改。但 r2 为了带新注释**重打包**过证据文件，其字节与 hash 已变；差异经证明**仅来自新增注释**，没有任何既有数值被改动。

| file | sha256 r1 | sha256 now (read from disk) | verdict |
|---|---|---|---|
| `evidence/M08/cases.json` | `e6c36cf4c3cc8e6e…` | `57459a8f5ea298e1…` | annotation-only (strip added keys -> deep-equal to r1) |
| `evidence/M08/run_result.json` | `f5ae116b315dd630…` | `83015b9d96310f49…` | annotation-only (strip added keys -> deep-equal to r1) |
| `evidence/M08/negative_results.json` | `7b7f60b7637e78e7…` | `9bebe7337395748d…` | annotation-only (strip added keys -> deep-equal to r1) |
| `after/rerun_sha256.json` | `a09498ab8145640f…` | `81de22674673a218…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `commands.json` | `46ff6bc5c046d3be…` | `92875088938cf0b4…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M08/card_conflict.json` | `102e6bf73d4f83fe…` | `b6aa7b134347b4b6…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'REMOVED_KEY'] |
| `evidence/M08/disclosure_mapping.json` | `d46cc48d21847e57…` | `a4c377c6b34145a6…` | r2 response edit, kinds=['ADDED_KEY', 'REMOVED_KEY'] |
| `evidence/M08/evidence_hashes.json` | `888b04b964c562af…` | `c18f4aca75d360bb…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |
| `evidence/M08/historical_reconciliation.json` | `d35829ac11511da2…` | `a3352b2ebad6fbd4…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'REMOVED_KEY'] |
| `evidence/M08/source_manifest.json` | `55fa778c09413f71…` | `7e5ee7e24687c5d1…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION', 'VALUE'] |
| `handoff.json` | `89c081e9a6e1fd7e…` | `49dac6a09d29a2b4…` | r2 response edit, kinds=['ADDED_KEY', 'ANNOTATION'] |

- 变化文件全表（含旧/新 sha256）见 `binding.json` / `handoff.json` 的 `docfix_r3_hash_ledger.repack_scope`，以及 `evidence/M08/docfix_r3.json`。
- 「差异仅为注释」的证明：剥离新增注释键后与 r1 对象**深度相等**（逐字节比较既有叶子值：M08 `cases.json` 117/117 相等、`run_result.json` 220/220 相等、`negative_results.json` 189/189 相等）。原始输出：`recovery/docfix-r3/f08_named_files.out.txt`、`f08_repack_diff.out.txt`。
- r1 基线本身经校验：`copy/`（reviewer r1 快照）的四份 `oracle.md` 均等于各卡自载的权威 v1 hash，故该快照确为 r1 态。
- `binding.json` / `handoff.json` 的 `input_hashes` 是**运行前（r1）**的输入 hash，按设计属历史值，**不主张**等于当前字节；其与当前值的差异同样仅为上述注释。
- `after/rerun_sha256.json` 是 r2 时点的清单（其 `generated_after` 自述如此），其中 `oracle.md` 条目为 r2 值；r3 值见上表与 `evidence/M08/docfix_r3.json`。

### 4) DEC-M08-1 指向 owner 三步（F-M08-09）

`M08/decision.md` 的 DEC-M08-1 已在**本文件上方**的「DEC-M08-1 · r3 correction」节（紧接 r1 原文之后追加）改写为**追加式更正**：明确指向 `handoff.json.owner_action_required` 的三步（含「禁止重新挑选算例」约束），r1 原文逐字保留在更上方，未删除。


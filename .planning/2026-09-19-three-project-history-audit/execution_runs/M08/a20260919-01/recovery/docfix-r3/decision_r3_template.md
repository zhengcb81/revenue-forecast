## Hash ledger · document/evidence consistency revision r3 (findings F-M08-06 / -07 / -08 / -09)

本节由 r3 **插入**（位置 = 被折叠的第二段 r2 节的原起点，也就是保留段末尾；该位置同时也是文件末尾。只增不删既有正文）。它只处置独立 reviewer 定点复核提出的文档/证据一致性缺陷。**冻结期望、容差、拒绝条件、披露数值、实现与产品一律未改。**

### 1) `oracle.md`：重复 r2 节折叠去重（F-M08-06）

| 项 | 值 |
|---|---|
| 改前 sha256（整文件） | `{oracle_before}`（{oracle_before_bytes} 字节） |
| 改后 sha256（整文件） | `{oracle_after}`（{oracle_after_bytes} 字节） |
| 唯一改动 | **折叠**第二段重复 r2 节（{removed_bytes} 字节，sha256 `{removed_sha}`；与第一段除「本节追加前 sha256」一行外逐字节相同），并在**该段原起点插入** r3 provenance-gap 说明（{inserted_bytes} 字节，sha256 `{inserted_sha}`）。**字节账：`pre {oracle_before_bytes} − {removed_bytes} + {inserted_bytes} = live {oracle_after_bytes}`；`live[:{kept_bytes}] == pre[:{kept_bytes}]` 逐字节成立**（即 live 以 pre 的完整 r2 正文为前缀，r3 说明紧接其后；这是**插入**，不是尾部追加） |
| 冻结期望文本 | **逐字节未动**：保留段 `[0,{kept_bytes})` 改前/改后 sha256 同为 `{kept_sha}`；第 0–10 节与第一段 r2 节全在该段内 |
| 权威 v1 基准（保留） | `{v1_claim}`，可在改后文件的前 `{v1_offset}` 字符（{v1_bytes} 字节）处复现，等于 reviewer r1 记录的 v1 值 |
| provenance gap（原值照录） | `{gap_claim}` —— 穷举全部字节切点后它只能复现为「v1 冻结体 + 第一段 r2 正文」这一中间写缓冲，**不是**任何「追加前」的文档状态，故标注为来源不可考、不得用作 hash 基准 |

一条命令即可证明冻结期望部分字节相同（P1 保留段逐字节相同 / P2 增量记账精确，即 live = pre[:K] + 插入段 / P3 全部冻结节逐字节相同 / P4 r2 节恰好剩 1 段 / P5 两个基准值均可复现）：

```
<iso venv python> -X utf8 -B recovery/docfix-r3/f06_verify.py > recovery/docfix-r3/f06_verify.out.txt
```

原始输出：`recovery/docfix-r3/f06_verify.out.txt`；合并前镜像留档 `recovery/docfix-r3/oracle_pre_{card}.md`。

### 2) `oq_rulings.json`：计数与署名更正（F-M08-07）

| 项 | 改前 | 改后 |
|---|---|---|
| sha256 | `{oq_before}` | `{oq_after}` |
| ratio 驱动总数 | 40 | **41** |
| 不在 `[0,1]` 的 ratio 驱动 | 3 | **4**（补 `direct_growth.growth_rate`，其定义域为 `(-1, inf)`） |
| 署名/人称 | 把独立 reviewer 署名为作者、以第一人称「我枚举了…」 | 客观第三方：**由实现者枚举、由 reviewer 复核**（原文保留在 `source_original_r2` / `reviewer_basis_original_r2`） |

实现者自己重算的枚举证据：`evidence/{card}/oq_rulings_enumeration.json`（sha256 `{enum_sha}`）；枚举脚本 `recovery/docfix-r3/f07_enumerate.py`，原始输出 `recovery/docfix-r3/f07_enumerate.out.txt`。

### 3) r1→r2 重打包的限定说明（F-M08-08）

「冻结件未改」这句话**须限定**为：`oracle.md` 的 v1 冻结正文与全部冻结期望（正例/连续性/默认值/负例/容差/拒绝条件/披露数值）一字未改。但 r2 为了带新注释**重打包**过证据文件，其字节与 hash 已变；差异经证明**仅来自新增注释**，没有任何既有数值被改动。

{repack_scope_table}

- 变化文件全表（含旧/新 sha256）见 `binding.json` / `handoff.json` 的 `docfix_r3_hash_ledger.repack_scope`，以及 `evidence/{card}/docfix_r3.json`。
- 「差异仅为注释」的证明：剥离新增注释键后与 r1 对象**深度相等**（逐字节比较既有叶子值：M08 `cases.json` 117/117 相等、`run_result.json` 220/220 相等、`negative_results.json` 189/189 相等）。原始输出：`recovery/docfix-r3/f08_named_files.out.txt`、`f08_repack_diff.out.txt`。
- r1 基线本身经校验：`copy/`（reviewer r1 快照）的四份 `oracle.md` 均等于各卡自载的权威 v1 hash，故该快照确为 r1 态。
- `binding.json` / `handoff.json` 的 `input_hashes` 是**运行前（r1）**的输入 hash，按设计属历史值，**不主张**等于当前字节；其与当前值的差异同样仅为上述注释。**为避免接手者按 `review_and_handoff.md` 的「先重算当前 hash」步骤误停，同一处并排给出 `input_hashes_current`（同名键的当前摘要）与 `input_hashes_current_vs_input_hashes`（逐键列出哪些相等、哪些是历史值）**。
- `after/rerun_sha256.json` 是 r2 时点的清单（其 `generated_after` 自述如此），其中 `oracle.md` 条目为 r2 值；r3 值见上表与 `evidence/{card}/docfix_r3.json`。
{dec_m08_pointer}

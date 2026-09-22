# E1E7-ERRATA-LANDING 决策记录（decision.md）

- 卡：REM-18 编排层勘误落地（append-only，no code，no tests）
- attempt：`a20260921-01`
- status：`review_pending`（实现者不自签；验收留给独立 reviewer / 编排层）

---

## DEC-E1E7-1：四卡 pin 判定（哪一个是「handoff 所 pin 的文件」）

四张卡各自**只有一个** attempt `a20260919-01`，其 `oracle.md` 即该卡 handoff 所 pin 的文件。
逐卡 pin 复核（追加前执行，结果写入 `binding.json` → `targets.<CARD>.pin_check`）：

| 卡 | pin 键（handoff 内） | pin 值 | 实测 | 判定 |
|---|---|---|---|---|
| M05 | `oracle_md_hash_ledger.v1_frozen_body*`（8774 B 前缀） | `ae1986f6…` | 8774 B 前缀 = `ae1986f6…` | **PINNED_OK** |
| M14 | `input_hashes["oracle.md:frozen_body_sha256"]`（= `before/oracle_md_v1.json`，9367 B） | `8d74e94f…` | 9367 B 前缀 = `8d74e94f…` | **PINNED_OK** |
| M20 | `input_hashes["oracle.md"]`（整文件，revision r1） | `b43abd8d…` | 整文件 = `b43abd8d…`（13074 B） | **PINNED_OK（整文件精确匹配）** |
| M24 | `input_hashes["oracle.md_frozen_body"]`（13382 B） | `9c8f6b23…` | 13382 B 前缀 = `9c8f6b23…` | **PINNED_OK** |

### DEC-E1E7-1a：M05 整文件 pin 值不符的归因（**不是**跳过理由）

- 现象：M05 `handoff.input_hashes_current["oracle.md"] = 7fda03b1… / 14844 B`，
  而盘上是 `081a206b… / 14790 B`（差 54 字节）；穷举行边界前缀**复现不出** `7fda03b1…`。
- 归因（实测，不是推测）：该文件被 git 跟踪，`.gitattributes` 有 `*.md text eol=lf`；
  r3 追加区当时是 CRLF。把 append 区（offset 8774 之后）的 LF 还原为 CRLF 后，
  得 `14844 B` 且 **sha256 = `7fda03b1…` 精确匹配 pin 值**（`commands.json` seq 8）。
- 结论：**内容同一，仅行尾被 git 归一化**；v1 冻结体 8774 B 逐字节未变 ⇒ 该文件**就是** pinned oracle，
  判定 `PINNED_OK`，不跳过。差异原样登记（`binding.json` + `evidence/provenance_time_note.json` 同族披露）。

## DEC-E1E7-2：追加机制与证明判据

- **判据用前缀，不用终态**（与 I-10-B DEC-I10B-3 的第 5 次同源教训一致）：
  追加式编辑用**前缀判据**，中部插入用 **difflib**。
- 每卡三证（写入 `evidence/`）：
  1. `prefix_proof/<CARD>.json`：`sha256(after[:bytes_before]) == sha256_before`（前像 = 整个旧文件）；
  2. `after_hash/<CARD>.json`：after-hash、字节数、追加字节数与载荷 hash；
  3. `diff_summary/<CARD>.json`：`difflib` 操作码 ⊆ {`equal`, `insert`}。
- 失败处置：任一证明失败 ⇒ **回写原字节、STOP 该卡、报告**（脚本内置；本轮 `stopped_or_skipped = {}`）。
- 独立复核（`evidence/independent_verify.json`）：4/4 `prefix_sha_match`、4/4 `exact_append_match`，
  且四棵 attempt 树内自 2026-09-21 起被改动的文件**只有 4 个 `oracle.md`**。

## DEC-E1E7-3：落什么、不落什么

- **落**：每卡一个「勘误追认」新节，含 ①provenance（源 = I-10-B handoff sha256 + E 列表所在键 `errata_pending.items`；形态 = T1-12 ①）
  ②该卡 E 项**逐字** + 旧值/新值 ③未晋升声明 ④行级「已过时，以本节为准」标注（旧行一字不改）。
- **不落**：`evidence/**/*.json`（E-1…E-7 点名的载体）**一字未改**。
  理由：①本卡指令的落点是 `oracle.md`；②JSON 无法做合法的行内追加（会破坏结构）；
  ③本卡无任何回改/扩权授权。⇒ 这是**已知残项**，见「剩余缺口」。
- M14 追加四项：E-2（defaults）+ E-5（`OBS-SUPPLY-BOUND`）+ E-6（`OQ-03`，D/E 层追认，登记为
  `carried_not_resolved`、**不代裁**）+ E-7（`signed_driver_probe`，I-10-B handoff 已定义故收录）。

## DEC-E1E7-4：效力边界（写进每一张卡）

**修复未晋升**（仅存在于 `I-10-B/.../iso/rf/scripts/`）⇒ 每节均写明：
在晋升之前现行冻结值仍然权威；本条为前瞻披露（promotion 前置知会），
**不改变任何现行期望、不改变任何 status、不改变任何资格**。
本轮 0 处期望变化、0 处 status 变化、0 处资格变化、0 产品文件、0 pytest、0 git 写、0 自签。

## DEC-E1E7-5：日期标签差异（如实登记，不回改）

- 追加节内写「于 **2026-09-21** 追加」、本卡 `oracle.md` 写「冻结时间：2026-09-21」——
  取自父卡指定的 attempt id `a20260921-01`。
- 本机实际执行时钟：**2026-09-22 09:2x +01:00（UTC 2026-09-22 08:2x）**。
- 二者相差约 1 天。**不回改已追加文字**（回改即违反 append-only / T1-12 ①）；
  真实时间以 `commands.json.execution_time_local`、本文件与 `handoff.json` 为准，
  并登记于 `evidence/provenance_time_note.json`。若编排层认为须在 M 卡内就地更正日期，
  只能再走一次 T1-12 ① 追加（不得就地编辑）—— 本卡不自行追加第二轮。

## 未决 / 待他方

| 项 | 性质 | 状态 |
|---|---|---|
| E-1…E-7 的**验收** | TIER-2：须独立 reviewer / 编排层 | `review_pending`，本卡不自签 |
| I-10-B 修复是否晋升生产 | **owner 职权** | 未晋升；本卡不授权、不预判 |
| `OQ-03` D/E 层是否追认 | D/E 当事方（owner 决定是否启动） | `carried_not_resolved`，本卡只登记 |
| `evidence/**/*.json` 是否也要落 E 项 | 编排层（需另行授权的追加式 pass） | 未做，见缺口 2 |
| 追加节内日期 2026-09-21 vs 实际 2026-09-22 | 编排层 | 已登记，待裁定是否补一轮追加 |

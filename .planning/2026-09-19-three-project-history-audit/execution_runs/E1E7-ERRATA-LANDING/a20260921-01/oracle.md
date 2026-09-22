# E1E7-ERRATA-LANDING — oracle.md（开工前冻结）

- 卡：`E1E7-ERRATA-LANDING`（REM-18 编排层勘误落地；**append-only，no code，no tests**）
- attempt：`a20260921-01`
- 冻结时间：2026-09-21（本文件在**触碰任何 M 卡 oracle.md 之前**写定；其后本文件自身不再改动）
- 上游来源（唯一权威，逐字抄录用）：
  - `execution_runs/I-10-B/a20260919-01/handoff.json`（sha256 `867d59b82a60544a8d7156ca0c3dbef9a9706ede6d82ede7ea50be0e181b54f4`，23563 B）
    —— E 列表所在键 = `errata_pending.items`（E-1…E-7）；同义交叉键 = `carried_findings[id="E-1..E-7"]`；
    逐条正文另见 `execution_runs/I-10-B/a20260919-01/compatibility_impact.md` §5 与 `decision.md` DEC-I10B-5
  - `OWNER_DECISIONS.md` §13 **T1-12 ①**：一律采用 ① 形态（追加新节 + 行级「第 X 行已过时，以本节为准」标注）；不外扩就地编辑授权

---

## 1. 作用对象：恰好 4 张 M 卡

| # | 卡 | 目标文件（唯一被追加的文件） | 冻结 oracle 所在 attempt |
|---|---|---|---|
| 1 | M05 | `execution_runs/M05/a20260919-01/oracle.md` | `a20260919-01` |
| 2 | M14 | `execution_runs/M14/a20260919-01/oracle.md` | `a20260919-01` |
| 3 | M20 | `execution_runs/M20/a20260919-01/oracle.md` | `a20260919-01` |
| 4 | M24 | `execution_runs/M24/a20260919-01/oracle.md` | `a20260919-01` |

四张卡各自只有这一个 attempt，故其 `a20260919-01/oracle.md` 即为该卡 handoff 所 pin 的文件。
**开工前置校验**：每卡须 ①文件存在；②handoff 对 `oracle.md` 的 pin 可复现
（冻结体前缀 hash 匹配 / 整文件 hash 匹配）。任一不成立 ⇒ **跳过该卡并报告，不猜**。

## 2. 追加式（append-only）硬规则

1. **只允许在文件既有字节之后追加**；冻结正文（0..N-1 字节）零字节变化。
   - 前缀判据：`sha256(after[:len(before)]) == sha256(before)`，逐卡各出一份证明。
   - 若某卡 append 后前缀证明失败 ⇒ **立即停止该卡**，报告并保留其原状（不回滚重试、不改写）。
2. 不编辑任何 `evidence/**/*.json`、不编辑任何其他 M 卡文件、不编辑 I-10-B 的任何文件。
3. 无产品文件、无 pytest、无 git 写命令、不自签。
4. 追加内容只新增一节（T1-12 ① 形态），节内以**行级标注**指认被追认的旧行（旧行本身一字不改）。

## 3. 零期望变化（zero-expectation-change）硬规则

1. 追加节**不改变任何现行期望**：`positive` / `continuity` / `defaults` / 负例 / 容差 / 拒绝条件 / 披露数值
   的现行取值与判定一律维持原状；`defaults` 相位在**现行生产注册表**上仍按旧口径成立。
2. **不改变任何 status**：不改任何卡的 `status` / `reviewer_status` / 裁决字段。
3. **不改变任何资格（qualification）**：`formula` / `disclosure_adaptation` / `accuracy` / `production_promotion`
   等资格状态一律不动；本卡不授予任何资格。
4. 追加节必须显式声明：**I-10-B 的修复未晋升**；**在晋升之前，现行冻结值仍然权威**；
   本条为前瞻披露（promotion 前置知会），**不改变任何现行期望、不改变任何 status、不改变任何资格**。

## 4. 每卡追加节必须包含的四件事

1. **E 项逐字**：从 I-10-B E 列表逐字抄录适用于本卡的项（含旧值 → 新值）。
   - M05 ← E-1；M14 ← E-2（+ E-5 / E-6 / E-7，M14 专属）；M20 ← E-3；M24 ← E-4。
   - M14 另须逐字追加两项卡专属条目：`OBS-SUPPLY-BOUND`、`OQ-03`（D/E 层追认），
     以及 `signed_driver_probe`（I-10-B handoff 已定义 ⇒ 必须收录，不得自创措辞）。
2. **未晋升声明**（第 3 节第 4 点的四句，逐字落地）。
3. **provenance 行**：源 = I-10-B attempt（记 `handoff.json` sha256 与 E 列表所在键）；形态 = T1-12 ① 追加式。
4. **行级「已过时，以本节为准」标注**：指向本卡 oracle.md 内具体旧行号（旧行不改）。

## 5. 证据要求（写入本 attempt 的 `evidence/`）

每卡各出三件：
1. `prefix_proof/<CARD>.json` —— `sha256(oracle_old_prefix)` 在 append 前后均匹配（含 before/after 长度）。
2. `after_hash/<CARD>.json` —— append 后的整文件 sha256 与字节数。
3. `diff_summary/<CARD>.json` —— `difflib.SequenceMatcher` 操作码集合 ⊆ {`equal`, `insert`}（insertion-only）。

## 6. 本卡不做的事

- 不落地生产（I-10-B 修复仍只存在于 `I-10-B/.../iso/rf/scripts/`）。
- 不裁定任何 OQ；不代签任何验收；`handoff.status = review_pending`，永不自签。

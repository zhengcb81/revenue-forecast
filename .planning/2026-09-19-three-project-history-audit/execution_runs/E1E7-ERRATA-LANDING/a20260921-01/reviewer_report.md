# reviewer_report — E1E7-ERRATA-LANDING / a20260921-01

- 独立复核（independent review，采样式复算，不重推全部）；复核对象 = `<ATTEMPT>` 的 oracle.md（开工前冻结）、binding.json、decision.md、evidence/**、commands.json。
- 复核方式：从**盘上字节**独立重算（PowerShell SHA256 + python difflib/containment），不采信被审方内存态。
- 边界：本 reviewer 只写 `reviewer_report.md` + `reviewer_report.sha256` 两件；四张 M 卡 oracle.md 全程只读；无产品写、无 pytest、无 git 写、不自签任何 M 卡验收（本报告的 verdict 只针对本卡交付是否 scoped-acceptable）。

## Verdict: **accepted_scoped**

七项声明全部从字节复算通过；附 4 条 minor observations（记账措辞层面，不阻断）与 5 条 unverified（附原因）。

---

## 1. 逐项复核结果

### C1. 前缀证明 4/4 —— **VERIFIED（本人独立重算）**

对每卡 `execution_runs/<CARD>/a20260919-01/oracle.md` 重算 `sha256(after[:bytes_before])`：

| 卡 | bytes_before | before sha256(前缀) | match binding | after 长度 | after sha256 | 期望 after | match |
|---|---|---|---|---|---|---|---|
| M05 | 14790 | `081a206b…da555` | ✓ | 18889 | `a1402ed8…d7b3` | `a1402ed8…` | ✓ |
| M14 | 19339 | `c2f7cc4e…a0988` | ✓ | 28088 | `80bba367…676e` | `80bba367…` | ✓ |
| M20 | 13074 | `b43abd8d…76672a` | ✓ | 17692 | `50e22567…2802` | `50e22567…` | ✓ |
| M24 | 26216 | `67c3cae6…8771ca` | ✓ | 31200 | `7ec4c278…327bd` | `7ec4c278…` | ✓ |

binding.json 的 4 组 before-hash/bytes 与盘上文件逐字节自洽；追加区零字节改写冻结体 ⇒ 冻结正文不可变性成立。

### C2. insertion-only —— **VERIFIED（4/4 全算，超出要求的 2/4）**

`difflib.SequenceMatcher(None, before, after, autojunk=False)`：

- M05: opcodes = {equal, insert}，2 段，insert at j=0 size **4099**
- M14: {equal, insert}，2 段，insert size **8749**
- M20: {equal, insert}，2 段，insert size **4618**
- M24: {equal, insert}，2 段，insert size **4984**

无 replace/delete/change；insert 尺寸 = after − before，且插在冻结体之后。evidence 的 landed_text 与文件追加切片逐字节一致（`lt == slice[1:]`，差的 1 字节仅为文件内分隔用前导 LF）——4/4。

### C3. 逐字源 —— **VERIFIED（含对声明前提的一处澄清）**

- 源 hash 复核：`I-10-B/a20260919-01/handoff.json` = **23563 B / `867d59b8…b54f4`** 与声明一致（✓）。
- **前提澄清（非缺陷）**：`errata_pending.items` 实为 **7 条一行式标签**（如 `"E-5 M14 cases.json OBS-SUPPLY-BOUND"`），**并不含**长引文；长逐字引文在同 attempt 的 `compatibility_impact.md` §5 表 / §3.2 / §3.3、`decision.md` 与 `handoff.carried_findings`。据此我改用「去空白/去 markdown 强调后的包含判定」核对真正的逐字要求：
  - 7/7 E 标签在各自卡的追加节中逐字出现；
  - §5 表行 E-1（M05）、E-3（M20）、E-4（M24）、E-5 / E-6（M14）5/5 行 `row ⊆ landed`；
  - **M14 E-5/E-6 抽查（重点）**：追加节内 10 段「…」引文 + 2 段英文长引文（如 `supply_revenue is NOT a signed driver in this registry…`、`this model has NO signed/unbounded driver…`）**12/12 命中** I-10-B 源文本（含 `carried_findings[OQ-I10B-2]` 的 OQ-03 原文与 §3.3 表原文）。

### C4. 零变化纪律 —— **VERIFIED（git status 部分以替代证据补足，见 U2）**

- 四棵 M 卡 attempt 树 mtime ≥ 2026-09-21 的文件**恰好只有 4 个 `oracle.md`**（mtime 均 2026-09-22T09:25:23，即 append 瞬间）——期望/status/资格载体（`evidence/**/*.json`、handoff、cases/oq/probe JSON）无一被碰；且 C1 的前缀证明已排除冻结正文中任何期望/status/资格行被改写的可能。
- `git diff --name-only HEAD` 中 M 树部分 = 仅那 4 个 oracle.md；全仓另有大量**先前已存在**的改动（OWNER_DECISIONS.md、REMEDIATION_REGISTER.md、I-08-C、I-14-D/E、`tools/pre_push_gate.py` 等），mtime 分别 08:13 / 08:47 / 09:33，均**不在** append 瞬间（09:25:23），不可归因本卡。
- `commands.json` 自报 product_tree_commands=0 / product_files_written=0 / pytest_runs=0 / git_write_commands=0（自报，见 U3）；pytest/mypy 缓存 mtime 落在窗口附近（见 U1）。

### C5. 父层四裁决登记 —— **VERIFIED（只验在场，不重开）**

| 裁决 | 登记位置 | 在场 |
|---|---|---|
| F2 日期标签 → 留置、不自行第二轮 | `decision.md` DEC-E1E7-5 + `evidence/provenance_time_note.json`（+ handoff GAP-1 `carried_not_resolved`） | ✓ |
| GAP-2 → 不做 JSON 编辑 pass | `decision.md` DEC-E1E7-3（「不落 evidence/**/*.json」+ 已知残项）+ handoff GAP-2 | ✓ |
| GAP-4 → M05 LF 披露留在 DEC-E1E7-1a | `decision.md` DEC-E1E7-1a（归因+判定）+ handoff GAP-4（M05 卡内不披露） | ✓ |
| GAP-5 → I-10-B 陈旧键名（`errata_pending_orchestration` vs 实际 `errata_pending`）登记不改 | handoff GAP-5 `carried_not_resolved`；且 I-10-B handoff sha 仍为 `867d59b8…` ⇒ 确未被改 | ✓ |

### C6. M05 pin-drift（LF 归一化）复现 —— **VERIFIED（本人 read-only 重算）**

在**追加前前缀**（`after[:14790]`，其字节已由 C1 证明等于追加前整文件）上执行 `data[:8774] + data[8774:].replace(b"\n", b"\r\n")`：

- 结果 = **14844 B / `7fda03b153fd9a3707fba3a1057c9eb2ed6d2f772cdd79b6c1a33de9bb639320`** —— 与 pin 值**精确相等**（54 个 CR 还原解释成立；8774 B 冻结体不动）。

### C7. 未晋升措辞四节一致 —— **VERIFIED**

每节恰 4 行命中（`未晋升`/`不改变任何`/`仍然权威` 拦截），四节集合**完全相同**（intersection = 4/4）：
路径声明行（`iso/rf/scripts/` … NOT promoted）、`修复未晋升：在晋升之前…仍然权威…until promotion`、`前瞻披露…不改变任何现行期望、不改变任何 status、不改变任何资格`、小节标题行。

### 附加抽查：行级「已过时，以本节为准」标注

M05 `[52,62,64,167]` / M14 `[4,54,64,65,108,128,185]` / M20 `[58,70,72,123]` / M24 `[83,123,125,128,241]` —— 全部落在**旧正文真实行**上且内容对题（defaults 案例、期望输出、OBS/OQ 行、探针行）；旧行由 C1 证明一字未改。

---

## 2. Findings（编号）

1. **F-OK-1**：4/4 前缀证明与 binding.json before-镜像由本人从字节重算通过（C1）。
2. **F-OK-2**：4/4 insertion-only（difflib 全算），无任何 replace/delete（C2）。
3. **F-OK-3**：逐字源核对 12/12（M14 E-5/E-6 重点）+ 5/5 §5 表行 + 7/7 标签；源 handoff hash 一致（C3）。
4. **F-OK-4**：零变化纪律以 mtime 扫描 + 前缀不可变性 + git diff 三角印证（C4）。
5. **F-OK-5**：四裁决全部在场（C5）。
6. **F-OK-6**：M05 LF→CRLF 复现 14844 B / `7fda03b1…` 精确命中（C6）。
7. **F-OK-7**：未晋升四句四节逐行相同（C7）。
8. **F-OK-8**：`evidence/landed_text/*.md` 与文件追加切片逐字节等同（差仅前导 LF），证据文本即落盘文本。
9. **F-MIN-1（记账措辞）**：pre-freeze 主张三处口径不一 —— 本卡 `oracle.md` 「写定于触碰任何 M 卡 oracle 之前」、`binding.json.created_before_touching_any_m_card_oracle=true`，但 `commands.json` seq12 自述「写于**触碰**任何 M 卡 oracle 之后、追加之前」，且 seq5/6/9（读 M 卡 oracle）确在 seq10 冻结之前。若「触碰=修改」则不矛盾，若「触碰=读取」则字面为假。**不影响证明力**（before-镜像由我从字节独立重得）。建议编排层将来以一轮 T1-12 ① 澄清措辞，本卡不可回改。
10. **F-MIN-2（记账措辞）**：失败处置口径微差 —— `decision.md` DEC-E1E7-2 写「回写原字节、STOP」，本卡 `oracle.md` §2.1 写「停止并保留原状（不回滚重试）」。本轮 `stopped_or_skipped = {}`，无实际触发，moot。
11. **F-MIN-3（给编排层的知会，非本卡缺陷）**：行级标注把**期望输出行**（如 M05 L62/L64、M14 L64/L65、M20 L70/L220、M24 L123/L125）标为「已过时」，而同节又声明「晋升前现行冻结值仍然权威」。二者由 ④ 免责句调和，属父层已授权的 T1-12 ① 形态固有张力；仅提示编排层知悉，不构成 changes_required。
12. **F-MIN-4**：日期标签 2026-09-21 vs 实机 2026-09-22 09:2x —— 已按父裁 F2 如实登记、未回改、未自行第二轮；本 reviewer 不重开。

## 3. Unverified（明确列出）

1. **U-1 pytest/mypy 归因**：`.pytest_cache/.../lastfailed` mtime 2026-09-22T09:23:38、`nodeids` 09:35:39、`.mypy_cache/@plugins_snapshot.json` 09:25:13 —— 夹在/贴近 append 窗口（09:25:23）。共享工作区下 **mtime 无法判定归属**（并行会话可能同时在跑）；本卡 `commands.json` 自报 0 pytest、0 产品触达，但那是自报。**未能从字节证明或证伪「本卡 0 pytest」**。
2. **U-2 完整 `git status`**：`git status --porcelain` 因 `.planning/.../reviews/revenue/scratch/model-tests/` 权限拒绝而中断（exit 1）。替代证据 = `git diff --name-only HEAD` + `git diff --cached` + 四树 mtime 扫描（结论见 C4）。staged 区有 4 个 I-14-D 旧路径（前序卡遗留，非本卡窗口）。
3. **U-3 commands.json 自报性**：seq1–16 命令清单无独立旁证（无 shell 历史交叉源）；seq13 `append_errata.py` 未被我重放执行（文件亦不属本 attempt 目录）。
4. **U-4 handoff 侧 frozen-body pin 原值**：我复算了「追加前整文件 vs binding」与 M05 全文件 pin 复现，但**未**逐一回查 M14/M24/M05 handoff 内 9367/13382/8774 B frozen-body pin 键值本身（binding.json `pin_check` 的 expected 值未独立溯源到各自 handoff 字节）。
5. **U-5 E-2 的 §3.4 实跑对照表逐格**：抽查了 §5 表行与 E-5/E-6 引文；M14 ②-a 表的每个 BEFORE/AFTER cell 未逐格回源（其所在源 `compatibility_impact.md` §3.4 整体 hash 已由 binding pin 为 `ab09422e…`，但该 pin 值本身同属 U-4 类未溯源项）。

## 4. 结论

**accepted_scoped**：七项声明全部字节级复核通过，四条 minor observations 均属记账措辞/编排层知会，不改变本卡 append-only、零期望变化、零 status 变化、零资格变化的核心主张；unverified 5 条已明示边界与原因，不以推测充作结论。E-1…E-7 的验收、生产晋升、OQ-03 D/E 追认仍归独立 reviewer / 编排层 / owner，本报告**不代签**任何一项。

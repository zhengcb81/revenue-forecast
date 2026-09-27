# B2-EXHIBIT-GATE-8K · a20260926-01 —— review.md（CARRIER LANDING：裁决由簿记落定工位转录；实现者未自签）

- **落定前 `Test-Path` 断言：`False`。** 写入前对该文件做的存在性断言结果为 `False` ⇒ 本文件原先不存在、无实现者存根需保留，因此本文件为**新建**。
  同一次断言一并执行且同为 `False` 的还有：`evidence\`（目录）= `False`、`evidence\B2-EXHIBIT-GATE-8K\qualification.json` = `False`。
- 断言与写入均由同一个落定工位在 2026-09-26 顺序执行（先断言、后写入）。

Status: **`accepted_scoped`**（`review_pending -> accepted_scoped`）。裁决由**独立复审工位**写在字节钉死的载体 `reviewer_report.md` 里，**不在本文件**。本文件只是把那句已经存在的裁决搬进本 attempt 的 `review.md` 槽位：**纯簿记转录，不是签字，也不产生任何新的接受结论。** 复审自己的话请读 `reviewer_report.md` §1–§7。本落定工位没有撰写任何裁决、复审或接受。

---

## 1. 裁决块（转录）

- 卡：**B2-EXHIBIT-GATE-8K**（按 §三十 把 8-K exhibit 闸门扩到 iso 2 文件改动 + `changes.diff`）
- attempt：`a20260926-01`（`<PLAN>\execution_runs\B2-EXHIBIT-GATE-8K\a20260926-01`）
- 裁决：**`ACCEPT`** —— 复审的字面用词是 **`VERDICT: ACCEPT`**（`reviewer_report.md` **L3** 原文 `VERDICT: ACCEPT`）
- 计数：**L123** 原文（逐字，未加转义字符）：
  > **P1 = 0 ⇒ `VERDICT: ACCEPT`（带 2×P2 + 3×P3）。**
- 裁决作者：**独立复审工位** —— 与实现者非同一人（`reviewer_report.md` L4 原文「**角色**：`reviewer`（独立复审工位，与实现者非同一人）」）；实现者未自签。
- 裁决轮次：本卡第 1 轮独立复审（单轮）。裁决是 **scoped**，不是 clean：**范围严格限于 iso 2 文件改动 + changes.diff**，带 2×P2 + 3×P3。
- 落定工位：carrier-landing bookkeeping executor（父派委派的簿记子代理）—— **只转录，不自签，不新裁。**

### 载体（字节钉死）

| 字段 | 值 |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256（落定时自算） | `74590637384fafc81f1baf4dcedb85dfd99d15e37137ce183f71f4fe857014b1` |
| bytes | 20209 |
| total lines | 157 |
| encoding | UTF-8 without BOM；仅 LF 行尾（全文件不含 CR）；单个结尾 LF（LF 切分得 158 段、末段为空） |
| pin sidecar | `reviewer_report.sha256`（85 B，sha256 `e9f53e054c924642207ca671dab026954c682b84ba0392398dd9db1132a9c0d6`，内容 `74590637384fafc81f1baf4dcedb85dfd99d15e37137ce183f71f4fe857014b1  reviewer_report.md`） |
| 三方一致 | 落定时自算 sha256 == 侧车内容 == 派单给定的 `74590637384fafc8…` ⇒ **三方一致 ✓** |
| **裁决行** | **L3（自行定位）** |
| 裁决行原文 | ``VERDICT: ACCEPT`` |
| 裁决行字节区 | bytes **78..92 inclusive**（end_exclusive 93，15 B，不含行尾 LF），sha256 `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |
| 计数行 | **L123**，字节区 16375..16432 inclusive（58 B），sha256 `f313531e6028cf7ff1c48ac6d503836635636f24cd4abf8be310c77110464919` |
| 全文件去尾 LF | 20208 B，sha256 `8c35e97f5c7c06988a020f2c3924d8b29d40937841a182a7580eb7a19adafb4a` |
| 字节区口径 | 0-based 字节偏移，针对记录 sha256 时的文件字节；区域长度不含行尾 LF |
| 分节行号（1-based 闭区间） | §1 六项独立复核 13–71 ｜ §2 `L1105` 裁定 73–81 ｜ §3① `oracle v3` 87–101 ｜ §3② `U1` 103–108 ｜ §4 发现分级与裁决 112–123 ｜ §5 Unverified 127–135 ｜ §6 我没有做的事 139–150 ｜ §7 证据索引 152–157 |
| producer | 独立复审工位（非实现者、非本落定工位） |

本落定工位对 `reviewer_report.md` 与 `reviewer_report.sha256` 的写入字节数 = **0**。

---

## 2. 接受的范围（转录）

接受是 **SCOPED，不是 clean**。复审的核查范围与结论（转述自 §1–§3，结论原话见各节）：

- 六项独立复核全部复跑一致（红真的红、绿真的绿、6 条变异逐条命中、6-K 逐字节不变、`changes.diff` 独立重算逐字节相同、`L1105` 判断成立）；
- 落定状态：`accepted_scoped`，**范围严格限于 iso 2 文件改动 + `changes.diff`**；
- 携带 2×P2 + 3×P3（见 §3），P1 = 0。

**不在本次接受范围内**（= `qualification.json` 的 `not_granted`，逐条）：`changes.diff` 已入库/已晋升、产品仓任何字节、`OPEN-3`/`BLOCKED-NEEDS-ORIGIN-BYTES`/`B1` 解除、E1/E2 等级、实际下载、`canonical_writer` kind 改动、晋升授权。

---

## 3. 携带的发现（2×P2 + 3×P3，逐字）

来源：`reviewer_report.md` §4（L112–L123）。**本工位不改级、不销项、不处置**，只原样搬运。

计数行原文（L123）：

> **P1 = 0 ⇒ `VERDICT: ACCEPT`（带 2×P2 + 3×P3）。**

| 级别 | 编号 | 发现（逐字） | 处置建议（逐字） | 源行 |
|---|---|---|---|---|
| **P2** | P2-1 | oracle v1/v2 **正文未留存**（只留 sha），先例理由 (2)「冻结体仍是旧值」不可核验 | 后续卡冻结必须留版本正文；本卡不因此回退（实质核已过） | L117 |
| **P2** | P2-2 | **U1 端到端未闭环**：exhibit 停在 staging，canonical 单 receipt 契约不在 2 文件面内 | **owner 按 L17 补第 3 个文件的卡**；在 B3/C3 结论里显式标注「闸门已开 ≠ 已落 `raw/other/`」 | L118 |
| **P3** | P3-1 | M5 实测多红 A4/A5，根因是 harness 把 `include_exhibits_flag` **记进被比对对象**（`_run_scenario` 字段），6-K/10-K 的 staged/payload/receipt 实际**仍逐字节等于冻结件**；oracle/handoff 未解释这一点 | harness 把该元数据移出 blob，或 oracle M5 行注明「A4/A5 属预期元数据红」 | L119 |
| **P3** | P3-2 | 产品 company-wiki `test_fc1204_complexity_ratchet::frozen_files_do_not_worsen` **既有红**：`archive_retired_evidence 19>7`、`observability 27>6`、`prompt_injection 17>15`、`prune_retired_evidence 27>12`（iso 与产品字节逐个相同、B2 未碰这些文件）⇒ U4「不跑真套件」的理由**不只是写权限**，替代证据只对**本卡改动文件**成立 | 属既有状态/他卡范围；请父登记并交对应 owner，B2 不背 | L120 |
| **P3** | P3-3 | `_us_exhibit_assets` 在 meta 缺 `sha256` 时回退为「发现时计算源哈希」，此时校验锚点从 meta 退化为磁盘（只能发现 discover→fetch 之间的改动） | 打通卡里可改 fail-closed；本卡不影响任何判据 | L121 |

**P1 = 0**；P2 = 2；P3 = 3；合计 5 条，全部 **carried（未销项）**。

---

## 4. 三处披露定性（复审已裁定；逐字，本工位不另出定性）

### ① `oracle v3` —— 合法追加式勘误（理由② 不可核验 ⇒ 记 P2-1）

- 小节标题原文（L87，逐字，未加转义字符）：
  > ### ① `oracle v3` 是「事后披露式勘误」还是「事后改期望」？ —— **裁定：合法的追加式勘误，非事后改期望**
- 定性原文（L101）：
  > **裁定：合法追加式勘误（非事后改期望）。** 但记 **P2-1**：v1/v2 正文未随卡留存，先例理由 (2) 在本卡**不可核验**，只能靠 (1)+(时序)+(实质核) 三条旁证。建议后续所有「冻结」必须同时留 `oracle.v2.md` 之类的版本正文（或把每版正文存进 `results/`），否则先例第三条永远缺角。
- 理由② 的对照结论（L94，逐字，未加转义字符）：
  > | **(2) 冻结体仍是旧值（v2 正文可对照）** | **不成立/不可核验**：v1/v2 只留 `sha256 + frozen_utc`（`results/oracle_freeze.json`、`handoff.oracle.versions`），`oracle.md` 是**覆盖写**，attempt 内与 `git HEAD`（该路径 `exists on disk, but not in HEAD`）均无 v2 正文；实现者所指的「M4 行保留在 `mutations/M4_adapter.*`」保存的是**实测结果**，不是 v2 的**预测文本** | ❌ 缺 |
- 结果：**不回退 ACCEPT**，但 **P2-1 保持 carried**。

### ② `U1` —— 记 P2，不升 P1

- 定性原文（L103，逐字，未加转义字符）：
  > ### ② `U1` 未证实 —— **裁定：记 P2，不升 P1**
- 独立确认原文（L105，逐字，未加转义字符）：
  > - **我独立确认 U1 属实（只读代码级）**：`canonical_writer.py L136 import_staged(request, candidate, receipt)` 是**单 receipt 契约**，唯一调用方 `acquisition_service.py:159`、`portfolio_promoter.py:221` 各传**一个** receipt；`import_staged` 只按该 receipt 的 `staged_path` 校验/搬移（`_validate_staged`）。⇒ 已复制进 staging 的 **exhibit 没有 receipt 就不会被 canonical 导入**，`exhibit 是否最终落 raw/other/` **确实未证实**。落点映射本身我复核 = `_destination_subdirectory("current_report") -> Path("other")`（`canonical_writer.py L90-101`，该文件**不在 diff 内**）。
- 定级 P2 理由（L106，逐字）：
  > - **定级 P2 理由**：端到端业务结果（filing-fetch 最终取回 8-K exhibit 原始字节）**本卡尚未闭环**，读者若只看「闸门已开」容易高估；后续**必须**有第 3 个文件（`acquisition` / `canonical_writer` 侧多 receipt 或二次导入）才能打通。
- 不升 P1 的理由（L107，逐字）：
  > - **不升 P1 的理由**：① 卡面**如实登记未造绿样**（`oracle §4 U1`、`handoff.unverified U1`、`self_attest §6` 三处一致）；② 修复**必然越出本卡 2 文件面**，按 `common_filing_cards.md L17` **只能 owner 补卡**，让本卡改第 3 个文件反而是**违规**；③ §三十 授权对象是「闸门」本身，diff 与授权严格对齐，**交付物无缺陷**；④ 落点口径（§三十一）已由只读直调验证，不涉谎报 `kind`。
- 附带（L108，逐字）：
  > - **附带**：staging 中的 exhibit 目前是**孤儿**（既无 receipt 也不会被 `_remove_staged` 按 receipt 清理），属打通卡要一并处理的细节，随 U1 走 owner 补卡。
- 结果：**P2-2 保持 carried**；打通卡由 owner 另行补第 3 张卡。

### ③ `L1105` 判断成立（primary 种子非闸门）

- 定性原文（L73，逐字，未加转义字符）：
  > ## 2. 第 6 项：`L1105` 自曝裁定 —— **判断成立**
- 实测原文（L75，逐字，未加转义字符）：
  > - **实测**：产品 `dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py` **L1105 = `filenames: list[str] = [primary_document]`**，在 `if include_xbrl or include_exhibits:`（L1108）与两处 `if include_exhibits and form_type == "6-K":`（L1112/L1124）**之前无条件执行**，对任何 form 都只播种 primary。
- 结论原文（L81，逐字）：
  > - **结论**：实现者「父派转述的这一行按实测修正、不改 L1105」的处理**正确**，且**收窄到授权范围**（不扩大改动面）。我据此不记任何发现。
- 依据要点（L76–L80，逐字）：
  > - **为什么它是种子不是闸门**：
  >   1. 它不带任何 `form_type` / `include_exhibits` 条件 ⇒ 改它既不会让 8-K 拿到 exhibit，也不构成排除 exhibit 的条件；
  >   2. **反证**：我保持 L1105 原样，仅按 diff 开闸，G1 即绿（8-K filenames 含 `d291965dex991.htm`）⇒ L1105 不阻碍 exhibit；
  >   3. 真正的排除条件是 L1112/L1124 的 `form_type == "6-K"`；且 §三十 **执行映射 1 原文只写**「`include_exhibits` 分支（L1112/L1124）」，L1105 只出现在**提问背景的机制描述**里（`mechanism_scan.json` 的 `line_1105` 同为证据引用，其 `meaning` 是「远端文件清单 = 主文档 + XBRL」）；
  >   4. 若改 L1105（例如置空种子），primary 会对**所有** form 消失，连 6-K/10-K 都会破坏 —— 与本卡第一不变量冲突。
- 结果：**本项复审不记任何发现（0 findings）。**

---

## 5. Unverified（逐条）

### 5.1 实现者原有 `unverified`（U1–U6，6 条）—— 原样保留，一字未改

1. U1 exhibit 资产复制到 staging 之后，acquisition/canonical_writer 的单 receipt 契约不在本卡 2 文件改动面内 ⇒ exhibit 最终是否落 raw/other/ = 未证实（落点映射本身已按 §三十一 只读直调验证 = other）
2. U2 B1 未解 ⇒ 未执行任何真实 filing-fetch ensure/下载；目标 accession 0001193125-26-380280 的真实行为未实测
3. U3 8-K/A 未纳入闸门（授权原文只写 8-K）；非 ex99 命名的 primary-linked HTML 在 adapter 复制面之外（dayu 可下载、adapter 不复制）= 已知边界
4. U4 company-wiki 自身契约套件（fc1204 coverage ratchet 需往产品仓根写 coverage.json、全量 suite）未运行 —— 运行即违反『不写产品仓』；替代证据：同一 AST 规则本地复算 max-complexity = 10 ≤ 46（results/static_checks.json）
5. U5 dayu 产品测试套件未运行（会写产品仓 .pytest_cache/workspace）；替代证据：自建 harness 覆盖 6-K/8-K/10-K 三形态 + 逐字节回归 + 6 条变异
6. U6 未产生 ACCEPT、未代签、未判 E1/E2 等级

### 5.2 复审 §5 Unverified（7 条，逐字，含原编号）

1. **U1 承接**：exhibit 是否最终落 `raw/other/` **仍未证实**（我只做了单 receipt 契约的只读代码确认，未跑通导入链）。
2. **真实下载 / B1**：禁网、company-wiki 本会话不可写 ⇒ 未做任何真实 filing-fetch ensure；目标 accession `0001193125-26-380280` 在真实 SEC 上的行为未实测。
3. **company-wiki 全量 suite 与 `test_fc1204_coverage_ratchet`** 未跑（覆盖率测试要读写产品仓根 `coverage.json`，违反只读纪律）。
4. **dayu 其余 suite**（`test_sec_pipeline_download*.py` 等）未跑；我只补跑了 `tests/fins/test_sec_downloader.py`（41 passed）。
5. **oracle v1/v2 正文不可得** ⇒ 其差分面无法字节级复核（见 P2-1）。
6. 我第一次尝试跑 dayu 测试时被环境挡了两次（`conftest` symlink 探针与 pytest `tmp_path` 的 `0o700` 目录在本沙箱不可读，`WinError 5`）——属**环境 shim 问题**，我用 `%TEMP%` 副本 + `mkdtemp/mkdir` mode shim 解决，**未改任何产品代码**；这些失败尝试未被计入上面的通过数。
7. `handoff.git_boundary.diff_total_lines=3827` 与我收尾时的 3834 有 7 行差（全在 `.planning`、非本 attempt 文件），我**未追查**来源。

**合计已披露未验证事项 = 6 + 7 = 13 条。**

---

## 6. pre_image（改前 handoff）

| 字段 | 值 |
|---|---|
| file | `handoff.json` |
| sha256（改前自算） | `030a32f2006441472b6d995daffb302d5699ee6a8e70cd9b105a33d9149daa1f` |
| bytes（改前） | 25105 |
| 与派单给定值 | `030a32f200644147…` 一致 |
| sha256（改后，本工位写入面） | `0e48d0aef9a4fbb8b3b39851a4ff621a9fd1f24927d526866dbd7a4d96069dc3` |
| bytes（改后） | 43773 |

---

## 7. 本落定工位的写入面与不做清单

**写了（恰好三处，均在 `.planning` 内）：**

1. `handoff.json` —— `status` 状态面转录（`review_pending → accepted_scoped`）+ 追加 `status_before` / `status_transition` / `status_history` / `status_authority` / `carried_findings` / `reviewer_resolved_items` / `unverified_reviewer` / `pre_image` / `bookkeeping` / `verdict_is_transcribed_not_authored`；其余既有键一字未改。
2. `review.md` —— 本文件（新建；写入前 `Test-Path` 断言 `False`）。
3. `evidence/B2-EXHIBIT-GATE-8K/qualification.json` —— 新建目录 + 新建文件。

**没有做：**

- 没有写 `reviewer_report.md` / `reviewer_report.sha256`（写入字节数 = 0，全程只读）。
- 没有写本 attempt 既有产物：`oracle.md`（三版）、`changes.diff`、`regression/`、`mutations/`、`results/`、`self_attest.md`、`iso/`、`harness/`。
- 没有写五份计划文件。
- 没有写 `.planning` 之外任何字节（尤其 `dayu-agent` / `company-wiki`；`changes.diff` 不是已入库实现）。
- 没有 git 写操作；**没有执行 `git status`**；收尾只跑只读 `git diff HEAD --name-only`。
- 没有联网、没有跑任何测试。
- 没有解除 `OPEN-3` / `BLOCKED-NEEDS-ORIGIN-BYTES` / `B1`；没有放行任何参数；没有晋升；没有判 E1/E2 等级；没有实际下载；没有改 `canonical_writer` 的 kind 映射。
- 没有产生新裁决、没有代签：`implementer_signed = false`，`verdict_is_transcribed_not_authored = true`。

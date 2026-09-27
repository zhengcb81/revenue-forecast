# REVIEWER REPORT — `DEF-MSFT-CANONICAL-DUP` / station `a20260926-01`

独立复审工位 · A 级全量档 · 复审时刻 2026-09-27（本地 UTC+01）· 只写本报告，不改卡状态。
写入面 = 本文件 + `reviewer_report.sha256`（2 个新文件）；被审件 / 前像 / 缺陷原件 / 修复码全程只读。

---

## 0. VERDICT（裁决行）

**`ACCEPT`** —— 无 `P1`；带 **`P2 × 1` + `P3 × 3`**，`unverified` 4 条（见 §5）。

P1 逐条排除（全部自跑/自算，不采信被审方声明）：

| P1 触发条件 | 结论 | 依据 |
|---|---|---|
| 红不复现 | 排除 | 自跑 `red_s1` rc=1 `RED_REPRODUCED`，生产签名逐字段命中（§3.3） |
| 绿不过 | 排除 | 自跑 `green_s1`/`green_s4`/`dedup_s5` rc=0 `GREEN_PASSED`（§3.3） |
| 修复引入回归（39 `G4` 单测不再全过） | 排除 | 自跑 **39 passed / 9.67s / exit 0**，跑前后 diff 集合与在树 sha 均不变（§3.4） |
| 改动越出 `canonical_writer.py` | 排除 | 自算 `git diff HEAD --name-only` + 逐文件归属（§4.1） |
| 封盘 `f2178768…` 动 | 排除 | 0 字节，sha `E3B0C442…`（空串哈希），首尾两次复测一致 |

发现清单（详见 §5）：`P2` G3 生产回放未执行（已登记）· `P3` 6 件孤儿未删（已登记）·
`P3` 缺陷原件「最后行」表述过时 · `P3` handoff 的 company-wiki diff 快照与当前树不同步（他方后置写入）。
`destination_preexisting` 修正 **不构成 S1 语义弱化** → 不计 P（§6 裁断）。

---

## 1. 回源（V2-4）

| # | 回源对象 | 自算结果 | 结论 |
|---|---|---|---|
| 1 | 被审 4 件 | `oracle.md` `129CB2FD…` · `fix_diff.md` `B65F6A57…` · `verification.json` `2077962E…` · `handoff.json` `6B618BB5…` | 收尾复哈希与开审时**逐字节相同**（§7）；`verification.json` 内声明的 `oracle.sha256=129CB2FD…` 与实物相符 |
| 2 | `rig/` 夹具与红绿产物 | 11 个 `rig/cases/*.json` + `harness/{run_case,make_variants,summarize}.py` + `variants/*` | 夹具自洽；8 个 variant 文件 sha 与 `verification.json.fix_variants` **全部一致**（`835DAB7F/D3DE75BF/1004D7EC/81DC56C5/DCFA3EE1/AE0B0DAA/A38A7876/E1198E84`） |
| 3 | 缺陷原件 `company-wiki/.source_catalog/acquisition_attempts.jsonl` | 67 行，mtime `2026-09-27T07:27:34+01:00`；**第 64 行** = `sec:0001193125-26-323660` / `reason=canonical_import_failed` / `canonical_path=null` / `content_sha256=095935f9…` / `recorded_at=2026-09-27T06:16:35Z`（**第 59 行**为 09-19 首次 `e3de0053…`） | 缺陷原件**属实**；但**文件最后一行已不是它** → `P3-3`（§5） |
| 4 | 在树修复 `company-wiki/src/company_wiki/source_catalog/canonical_writer.py` | 23,949B，sha `D7F6AFC5…`，mtime `11:34:33` | == 后像 `canonical_writer.fixed.py`，**逐字节相等**（修复码未被复审改动） |
| 5 | 卡文授权 `§四十 裁定二` | `OWNER_DECISIONS.md` L941–946 逐字：开卡 `DEF-MSFT-CANONICAL-DUP`（`MSFT 10-K FY2026 canonical_import_failed`，`canonical_path` 空、索引未建，09-19 起既有）+ 执行纪律 L954「`dayu` 零改零提交 · 封盘 `f2178768…` · 产品仓除授权摄取外零写」 | 授权链成立，与 `handoff.authorized_by="§四十裁定二"` 相符 |
| 6 | 生产 DB（只读） | `sources` 两个 sha 各 **0 行**（全表 43,112 行 / documents 23,530 行）；查询前后 `catalog.sqlite3`/`-wal` mtime 不变 | 与 oracle「零行」证据相符，索引仍未建（G3 未做所致） |

---

## 2. 前像 / 后像核（全部自算）

| 项 | 自算值 | 判定 |
|---|---|---|
| `canonical_writer.preimage_asfound.py` | 17,958B · `835DAB7F2FFDC4B10D8892EDB94BB88E77F840DF59D05CF6C9FEBA7AAD4337DB` | — |
| `git -C company-wiki show HEAD:src/company_wiki/source_catalog/canonical_writer.py`（重定向到 `%TEMP%`） | 17,958B · `835DAB7F…` | **逐字节相等 ⇒ as-found 前像 = 已提交基线** |
| 前像 CRLF 规范化 | `4BC653725FEBCC755E3A01AC48227A6B0799C4C262968356B356F8CB42D3C6BC` | == `reconstruct_preimage.py` 的 `EXPECTED` ✓ |
| `canonical_writer.preimage.py` | `1F2BE3B4…` == `BOM + 前像(CRLF)` | 仅 BOM 差异 ✓（与 `diff_preimage_to_asfound.patch` 1 hunk 相符） |
| 后像 `canonical_writer.fixed.py` | 23,949B (CRLF, 516 行) · `D7F6AFC53F62637BA2B881B3BE629D2AAE392C670182D0A3514A27FA6B2428F8` | **== 在树文件 sha（live_equals_fixed ✓）** |
| 后像 LF 规范化 | `D3DE75BF85AEFDAF926B6CED3934BBEA75622743B7E7FBF028587BA672F6C011` | == `variants/fixed`（`fix_variants.fixed.sha256_lf`）✓，两者仅行尾差 |
| diff 规模（`git diff HEAD -- canonical_writer.py` 自算） | **7 hunks，+102 / −8**（110 变更行） | **与 `fix_diff.md` 声明吻合** |
| 与 rig 产物互证 | 自算 patch 与 `rig/cw_git_diff_canonical_writer.patch`（UTF-16 编码）解码后**逐字节相同**；`rig/diff_report.txt` 的 opcode 段落 = `fix_diff` §2 的 9 段逐条对应 | 一致 |

结论：**前像链条闭合（as-found == HEAD blob），在树 == 后像，diff 规模与 fix_diff 完全吻合**。

---

## 3. 五项全量复核

### 3.1 裁决行 + 发现清单
被审方声明：`handoff.status="review_pending"`（未自签 `implementer_signed=false`）、`gate0.passed=true`、
`verification.summary.all_pass=true`（red ✓ / green ✓ / 6 mutations caught ✓ / `G4 39 passed`）、
`releases_nothing=true`。我方裁决行见 §0，发现清单见 §5。

### 3.2 前像/后像核
见 §2 —— 全部自算通过。

### 3.3 ⭐ 红绿自跑（隔离 `%TEMP%`，零联网零生产写）
环境：`TEMP/TMP/TMPDIR = %TEMP%\zr_rev_run1\tmp`（全新空根），输出落 `%TEMP%\zr_rev_run1\out`
（**不写卡目录**），执行 `rig/harness/run_case.py --case <11 案>`；fixture 字节取自生产（只读），获取阶段由
`FixtureCoordinator` 在 seam 处桩接（不构造 dayu/sec 适配器），无 HTTP/网络调用。

| 案 | variant sha | rc | 我方 verdict | 关键观测 |
|---|---|---:|---|---|
| `red_s1`（前像） | `835DAB7F…` | 1 | `RED_REPRODUCED` | `journal.reason=canonical_import_failed`、**`canonical_path=null`**、**import scan `files_seen=0`** `strategy={company_raw:adapter}` `status=completed_with_errors`、error=`scan_root_strategy: v2 scanner unavailable (fail closed): root 'company_raw' has no adapter_id…`、fixture sha 未索引、committed 文件留孤儿、staging 未消费、`attempt_id=…39d8fd50…` 与生产原件第 64 行**同值** ⇒ **生产签名完全复现** |
| `red_s4` | `835DAB7F…` | 1 | `RED_REPRODUCED` | `immutable provenance sidecar conflict` |
| `green_s1`（在树） | `D3DE75BF…` | 0 | `GREEN_PASSED` | `outcome=downloaded_new`、`status=imported`、suffix 文件落盘、`files_seen=4` `strategy={company_raw:legacy}`、fixture sha 索引=1、**孤儿 sha 也索引=1（无孤儿）**、`every_canonical_file_indexed` ✓、staging 清空、identity 回填 intact |
| `green_s4` | `D3DE75BF…` | 0 | `GREEN_PASSED` | `outcome=deduplicated_after_download`、`status=deduplicated`、同样无孤儿 |
| `dedup_s5` | `D3DE75BF…` | 0 | `GREEN_PASSED` | duplicate 分支：`provenance_path=null`、无新文件、`deduplicated_after_download` |

**比对**：我方 11 份案卷与被审方 `rig/cases/*.json` 逐字段比对，除 `canonical_path` 的临时根路径前缀外
（`zr_rev_run1\tmp` vs `defmsftdup`）**完全一致**（red/m1/m2/m3/m4 案连绝对路径字段都同构相等）。

**隔离复核**：harness 静态扫描无 `requests/urllib/http/socket`（仅 `build_handoff.py` 用 `subprocess` 调 `git`）；
跑后生产态复测 —— `acquisition_attempts.jsonl` mtime 仍 `07:27:34+01:00`、`annual/` 4 个文件 mtime 仍
`09-19 05:52` / `09-27 07:16`、staging 两个 MSFT 载荷仍在、在树 `canonical_writer.py` 仍 `D7F6AFC5…`
⇒ **零生产写**；卡目录 102 个文件在 handoff（`11:51:11`）之后**零新增零改动**（我仅新增本报告 2 件）。

### 3.4 `G4` 回归（自跑）
`python -m pytest -q -p no:cacheprovider --basetemp=%TEMP%\zr_rev_pytest` + 4 个 contract 文件
⇒ **39 passed in 9.67s，exit 0**；跑前后 `git diff HEAD --name-only` 集合相同、在树 sha 仍 `D7F6AFC5…`。
（实现方记录的 39 passed 独立复现。）

### 3.5 ⭐ 变异（抽 3 臂 M4/M5/M6 + 冻结 M1–M3，全自跑）

| 臂 | 我方自跑 | 变异内容（逐臂 diff 核，单点、非乱砍） |
|---|---|---|
| `M4` `m4_s1` | rc=1 `MUTATION_CAUGHT`（`canonical filename collision after hash suffix`） | 删掉 `__<sha12>` 哈希后缀回落两步，仅留冲突检查 |
| `M5` `m5_s1` | rc=0 `MUTATION_CAUGHT`（`identity_backfill_broken_by_mutation`：`resolution.request_id != attempt.request_id`） | 去掉 F-EE1 `replace(exact_resolution, request_id=request.request_id)` |
| `M6` `m6_dedup` | rc=0 `MUTATION_CAUGHT`（`dedup_branch_skipped_by_mutation`：`provenance_path` 非 null） | `_existing_original` 顶部 `return None`（duplicate 分支禁用） |
| `M1` `m1_s1`（冻结） | rc=1 `MUTATION_CAUGHT`，回到 `files_seen=0` + `canonical_path=null` + 生产错误串 | 恢复 `v2_scan_shadow=v2_scan_shadow_from_snapshot(...)` |
| `M2` `m2_s4`（冻结） | rc=1 `MUTATION_CAUGHT`（sidecar conflict） | 恢复 `self._write_provenance(...)` 无条件写 |
| `M3` `m3_s1`（冻结） | rc=1 `MUTATION_CAUGHT`（已索引但被验证拒绝，`files_seen=4`） | 恢复严格 `REUSED_EXACT` 抛错 |

**6/6 全部复现**；每臂变异均为**单一语义点回退**（非破坏性乱改），`M4–M6` 为 oracle 冻结项之外的合理扩展。
`M5/M6` 的 rc=0 属预期（它们破坏的是不变量而非流程），由断言型 check 捕获，判定成立。

### 3.6 边界（逐条自算）

| 边界 | 自算结果 | 判定 |
|---|---|---|
| `company-wiki` 本卡 diff | `git diff HEAD --name-only` = **13 文件**。逐文件归属：`canonical_writer.py`（mtime `11:34:33`，内容==后像）= **本卡唯一改动**；`CLAUDE.md/README.md/__init__.py/archive_retired_evidence.py/artifact_dag.py/error_taxonomy.py/evidence_query.py/test_…_evidence_query.py/test_error_taxonomy.py`（mtime `09-26 22:07`–`09-27 11:31`）= handoff 已登记的 pre-existing；`prompt_injection.py/observability.py/test_observability.py`（mtime `11:53:57/11:56:21/11:57:00`，**晚于 handoff `11:51:11`**）= 他方工位后置写入 | **本卡改动面仍仅 `canonical_writer.py`**；diff 快照不同步 → `P3-4` |
| `dayu` 零改零提交 | 实仓 `Projects\dayu-agent\dayu-agent`：`git diff HEAD --name-only` = `dayu/fins/downloaders/sec_downloader.py`（mtime `2026-09-26`，早于本卡）；`git log -1` = `2115c86d… 2026-05-04` | **零改、零提交** ✓（该单文件为他方既有改动，handoff 已如实登记） |
| 封盘 `f2178768…` | 0 字节 · `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`（首尾两次一致） | **零字节未动** ✓ |
| `G3 生产回放未做（留 owner）` | `oracle.md` L52「G3 … **deliberately not run by this station** — no production writes; left to the reviewer/owner」+ `handoff.not_done[0]` | **如实登记** ✓ → `P2` |
| 6 件孤儿未删 | `handoff.cleanup_items` = **6 条**（2 staging 载荷 + 09-19 孤儿及其 sidecar + 09-27 后缀件及其 sidecar），全部 `action=registered_not_deleted`、`disposition=owner decides (raw/ 与 staging 对本卡只读)`；生产 `annual/` 仍为 4 文件、staging 两载荷仍在 | **如实登记** ✓ → `P3` |
| 写入纪律 | 未用 `git status`；未做任何 git 写（仅 `git show`/`git diff HEAD` 只读）；未联网；实现方 rig 的 11 案我在**自己的隔离根**重跑，未污染卡目录 | ✓ |

---

## 4. 判级

### 4.1 必判项
1. **`G3 生产回放未做` ⇒ `P2`**：唯一的授权生产摄取写（`ensure --allow-download` 对生产）尚未执行，修复目前只有隔离 rig 证据；生产 `catalog.sqlite3` 两个 sha 仍 0 行（我方只读复核）。关闭卡片前须由 owner/复审跑一次并满足 oracle G3 四条（`capture_ready`、新 attempt 行 outcome ∈ {`downloaded_new`,`deduplicated_after_download`}、sha 已索引、`annual/` 至多 +1 且无新未索引孤儿）。**已如实登记**，不构成 P1。
2. **`6 件孤儿未删` ⇒ `P3`**：已按 oracle Non-goals（`raw/`、`.source_catalog/staging` 对本卡只读）登记为 owner 决定项，且是缺陷既有后果、非本卡引入；本卡无权删除。**已如实登记**。
3. **`destination_preexisting` 修正是否引入 `S1` 语义弱化 ⇒ 我裁：否，不计 P**（§6）。

### 4.2 P 清单
- **`P2-1`** `G3` 生产回放未执行（留 owner）——关闭前必做。
- **`P3-1`** 6 件孤儿/暂存载荷未删（已登记，owner 处置）。
- **`P3-2`** 缺陷原件「最后行」表述过时：现最后一行是 `reused_before_download`（`2026-09-27T06:27:34Z`），
  `canonical_import_failed` 实际在第 59/64 行；第 65–67 行（`06:23:58Z` `DayuCliAdapterError` + 两行
  `reused_before_download`）为他方追加，mtime 早于本卡后像与 handoff，**非本卡写入**。
- **`P3-3`** `handoff.company_wiki_diff_files`（10 项）与当前 `git diff HEAD --name-only`（13 项）不同步：
  另 3 项系他方工位在 handoff 之后写入；本卡归属结论（仅 `canonical_writer.py`）不受影响。

### 4.3 `unverified`
1. **零网络**：由 acquisition seam 桩接 + harness 静态检查佐证，**未做网络层拦截/抓包级测量**。
2. 实现方声明的 `network_calls=0 / production_writes=0 / dayu_agent_writes=0` 的**历史**部分：按 mtime、
   diff、commit 时间旁证一致，但历史行为无法完全独立复算。
3. **他方 12 个非本卡改动文件的内容**未复审（不在本卡范围）。
4. 生产 `scan_runs` 两条失败 run（`scan-6f9fd490`/`scan-c4ae2c00`）只经 oracle 引述核对，**未直查 DB 明细**
   （仅核了 `sources` 零行与 journal 原件）。

### 4.4 没做的事
- **没有**执行 `G3` 生产回放（无生产写，属 owner/复审授权动作）。
- **没有**删除/移动任何孤儿或 staging 载荷（oracle Non-goals，owner 决定）。
- **没有**改任何卡状态、没有改修复码、没有 `git status`、没有 git 写、没有联网。
- **没有**复审 `company-wiki` 其余 12 个他方改动文件、没有复审 `dayu` 那 1 个既有改动的内容。
- **没有**在卡目录内写除本报告与 `.sha256` 之外的任何文件（rig 案卷全部落 `%TEMP%`）。

---

## 5. 发现清单（汇总）

| # | 级别 | 发现 | 处置 |
|---|---|---|---|
| 1 | P2 | `G3` 生产回放未做（已登记） | owner 执行后再关卡 |
| 2 | P3 | 6 件孤儿未删（已登记） | owner 处置 |
| 3 | P3 | 缺陷原件「最后行」≠ `canonical_import_failed`（在第 59/64 行） | 文案订正 |
| 4 | P3 | handoff company-wiki diff 快照落后现树 3 文件（他方写入） | 下站刷新快照 |

---

## 6. `destination_preexisting` 修正裁断（S1 语义）

修正内容：`destination_preexisting = destination.exists()`（在 `__<sha12>` 重命名与冲突检查**之后**求值）。
它只驱动两处：(a) `if destination_preexisting and provenance.exists(): _verify_committed_provenance(...) else: _write_provenance(...)`
（L199–202）；(b) 结果状态标签 `DEDUPLICATED_AFTER_DOWNLOAD if destination_preexisting else IMPORTED_NEW`（L297–301）。

- **S1（首次提交后缀文件，生产 09-27 形态）**：最终路径此前不存在 → 标志 `False` → 写全新 sidecar + `downloaded_new`；
  与冻结 oracle 元素 2 原话「when the computed destination … **already exists** byte-identical to the receipt」逐字一致，
  也与元素 2 的注释自洽（草案把标志在"基名被占用"分支里提前置 `True`，反而误报 dedup）。
- **失败面未放宽**：标志为 `True` 时仍走 `_verify_committed_provenance`，`content_sha256/provider/provider_document_id/byte_size`
  任一不符即抛与 `_write_provenance` 同串的 `immutable provenance sidecar conflict`（fail-closed 不变）；
  验证段仍要求 `AMBIGUOUS 且恰好 1 个 capture-ready 且 sha==receipt.sha`，否则照常抛错；scan 不变。
- **不新增放行路径**：该标志无第三处使用（全文仅 L181/195/199/299），草案与修正的差别只出现在
  "基名被占、后缀路径全新"这一种情形，且只影响**日志标签**（G3 明文接受两种 outcome 之一）。

**⇒ 不构成 `S1` 语义弱化，不计 P；该修正是对草案的正确性订正。**

---

## 7. 收尾复哈希（写报告后复测，与开审一致）

| 文件 | 字节 | sha256 |
|---|---:|---|
| `oracle.md` | 8,848 | `129CB2FD665DCC0AE393A638EBA0FD5586CC9EB74156006033C1C0D309410F5B` |
| `fix_diff.md` | 7,993 | `B65F6A5721777430F9282F75AE669EA77C08AED4AB0B8BC7816FE1D6CC3D5309` |
| `verification.json` | 28,091 | `2077962EC1032C41EB6FF85E46BE6B73265A1F8625BDD38EA5AE1C6908122CB3` |
| `handoff.json` | 12,975 | `6B618BB5B67AC53C6B4910E3789D6E6C7ADE1AAB5074176C405477800CB0DB3F` |
| `canonical_writer.preimage_asfound.py` | 17,958 | `835DAB7F2FFDC4B10D8892EDB94BB88E77F840DF59D05CF6C9FEBA7AAD4337DB` |
| `canonical_writer.preimage.py` | 18,383 | `1F2BE3B4077387F573174281708BF1D060917D40B33171B2268F4DCDDDCA6C7B` |
| `canonical_writer.fixed.py` | 23,949 | `D7F6AFC53F62637BA2B881B3BE629D2AAE392C670182D0A3514A27FA6B2428F8` |
| 封盘 `f2178768` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| 缺陷原件 `acquisition_attempts.jsonl`（67 行，mtime `2026-09-27T07:27:34.7342080+01:00`） | — | `C9D7F35A3F3843FAA9D20D65FF210D72AC5D92235ACDE72215130569F3A9E425` |
| 在树 `company-wiki/src/company_wiki/source_catalog/canonical_writer.py` | 23,949 | `D7F6AFC53F62637BA2B881B3BE629D2AAE392C670182D0A3514A27FA6B2428F8` |

`rig/cases` 11 件（开审登记，未被本复审改动）：`red_s1 6F055695…` · `red_s4 396757E6…` ·
`green_s1 2DE41D4B…` · `green_s4 2BDC3E84…` · `dedup_s5 EE85234B…` · `m1_s1 F2FCE575…` ·
`m2_s4 6F5013CC…` · `m3_s1 094144D7…` · `m4_s1 7D706A1A…` · `m5_s1 F05D2FE9…` · `m6_dedup 272A0714…`

---

**裁决：`ACCEPT`（`P2×1` + `P3×3`，`unverified×4`）—— 复审工位，仅出报告，不改卡状态。**

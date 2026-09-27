# B2 · 只读自证（self-attestation）

**card** `B2-EXHIBIT-GATE-8K` ｜ **attempt** `a20260926-01` ｜ **role** `implementer` ｜ **status** `review_pending` ｜ **implementer_signed** `false`

## 1. 我改了什么（且只改了这些）

`changes.diff`（**11,379 B**，sha256 `731bbeeb77d31eec8c2b57ef8eb65418f403480273b25d4638029ca5da8e803e`）**只含 2 个文件**，全部落在本 attempt 的 `iso/` 副本上：

| 文件 | 前像 sha256 | 改后 sha256 | 增/删行 |
|---|---|---|---|
| `dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py` | `543d005c25fabea3431704293e05e79ebfa76de71f031bf6dc6106113e7a5da0`（74,235 B） | `4684933e076e759c8ebc8acc494c0611f763e95364bc4a9d0a9a16165e1e4e1b`（74,543 B） | +6 / −3 |
| `company-wiki/src/company_wiki/source_catalog/dayu_cli_adapter.py` | `bcbbbfd955306c3ed7ca4febff03813ea7dfafeb068c114873bfbfd3456eab5a`（19,775 B） | `32ef1165a4948818e2442c57c78550ad026902539c405d9ae42413bb3ab3f7cb`（25,328 B） | +121 / −7 |

逐 hunk 内容见 `changes.diff`；iso 树逐文件 sha 清单（证明两棵树各自**只有这 1 个文件**变动、无第 3 个文件被碰）见 `results/static_checks.json` 的 `iso_tree_changed_files::*`。

## 2. 产品仓零写入（三条独立证据）

1. **产品文件前像复核**：两个目标产品文件的当前 sha256 与开工时记录的前像**完全一致**（`results/static_checks.json` 的 `product_untouched::*`，`ok=true`；mtime 分别仍为 `2026-05-30T21:42:41Z` / `2026-07-24T18:58:01Z`）。
2. **mtime 窗口扫描**（≥ 2026-09-26T00:40 本地 = 本工位开工时刻）：`dayu-agent` **0**、`company-wiki` **0**、`revenue-forecast` 非 `.planning` **0**。
3. **git 只读核对**：`git -c core.quotepath=false diff HEAD --name-only` → 非 `.planning` = **0**（总行 3827，全部 `.planning`）。**未执行 `git status`、未做任何 git 写操作。**

## 3. 网络与下载

- **网络请求 = 0**：dayu harness 对 `_http_get_bytes` / `_http_get_json` 打 kill-switch（`RuntimeError: network disabled in harness`，由 `_try_*` 兜底为 `[]`，输出见 `results/dayu_gate_check.json` 运行日志），`_http_head` 用本地桩；adapter harness 的 dayu CLI 是本地假脚本（`harness/adapter_copy_harness.py` 内 `_FAKE_CLI`）。
- **未执行任何实际 filing-fetch ensure / 真实下载**（B1 仍阻断；本卡只改代码）。

## 4. 纪律自检（逐条）

| 纪律 | 结论 | 证据 |
|---|---|---|
| 只修隔离副本、只出 `changes.diff` | ✅ | `changes.diff` 2 文件；iso 树各只变 1 文件 |
| 绝不写产品仓 | ✅ | §2 三条证据 |
| oracle 先冻结再改代码 | ✅ | v1 `9467739c…`（2026-09-25T23:47:30Z）、v2 `2ff11de8…`（23:48:42Z）**均早于**首次 iso 编辑 —— 编辑窗口由 `results/rc_log.txt` 夹定：pre-change 红 `23:55:43Z`（iso 仍是前像）→ post-change 绿 `23:58:51Z`（iso 已改）⇒ 首次编辑在 23:55–23:58Z 之间；v3 `00a747bb…` 为 M4 跑完后的**披露式勘误**，未动任何 R/G/V 判据 |
| 6-K 行为逐字节不变 | ✅ | `regression/6k_regression.md`：dayu `649d906c…/3318 B`、adapter `0c9000a1…`、10-K `7507acad…` 前后相同；M2/M3 变异可使其变红 |
| GREEN 附变异证明 | ✅ | `mutations/mutations.json`：M0–M5 共 6 条，`mismatch=0`，每次还原 sha 逐字节回到改动后 sha |
| 禁 `git status`、禁 git 写、禁联网 | ✅ | §2/§3 |
| 不解除 OPEN-3 / BLOCKED-NEEDS-ORIGIN-BYTES、不判等级、无 ACCEPT、不代签 | ✅ | `handoff.json.not_done` / `implementer_signed=false` |
| 不改 `canonical_writer` 映射、不谎报 kind | ✅ | `canonical_writer.py` 未进 diff；`A7` 只读直调 `_destination_subdirectory("current_report")` = `other` |
| 不写五份计划文件 | ✅ | 写入面 = 本 attempt 目录 |

## 5. iso 可行性

**可行**：import、红、绿、6-K 字节回归、6 条变异、落点只读直调**全部在 iso 内完成**，没有出现「必须在产品仓原路径才能跑通」的依赖 ⇒ **不判 `blocked`**。
环境侧的 3 处 shim 全部记录在 `handoff.json.environment_notes`（`EDGAR_LOCAL_DATA_DIR` 重定向、`tempfile.mkdtemp` 默认 mode、fixture 短路径），**均不改任何产品代码**。

## 6. 未证实（不造绿样，逐条见 `handoff.json.unverified` U1–U6）

- **U1**：exhibit 复制进 staging 之后，canonical 导入是**单 receipt** 契约（不在本卡 2 文件内）⇒ **exhibit 是否最终落 `raw/other/` = 未证实**；落点映射本身按 §三十一 只读验证为 `other`。
- **U2**：B1 未解 ⇒ 真实 filing-fetch/SEC 行为未实测。
- **U4/U5**：两侧产品测试套件未运行（运行会写产品仓）；替代证据 = 同一 AST 复杂度规则本地复算（10 ≤ 46）+ 自建 harness 的三形态覆盖与字节回归。

## 7. 签署

- **implementer**：未签署（`implementer_signed=false`）——本卡只交付 `changes.diff` 与证据，**不产生 ACCEPT、不代签**。
- **下一步**：父派**独立复审**；复审通过后按 §三十 走「晋升授权」另行派工。

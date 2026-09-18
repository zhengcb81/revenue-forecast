# R4 最终状态小结（**定稿**，2026-09-17）

> 口径：本文件只写**有证据支撑**的结论；每条都指向可核对的提交/证据文件。**未过独立复审的项**明确标注。
> 最终提交：company-wiki **`c4f5b8a`**（master，CI run `35283319814` success）、revenue-forecast **`65cc18d`**（main，CI run `35283938871` success）。

## 1. 四个工作包的状态

| # | 工作包 | 状态 | 证据 |
|---|---|---|---|
| ① | **B05** 读侧畸形共享列 | ✅ **完成并闭环** | wiki `74ffeeb`→`91a20ec`→`41fdfe1`（run `35146033771` 绿）；两轮复审（`B.VR-b05malformed`、`-verify`）全部处置；变异 15/15 |
| ② | **B08** G8 第②级 | ✅ **完成并闭环** | 隔离根只读引用真实文件、两次 `verified` 读（4,172,424 B，摘要=独立哈希真实文件）、篡改 0 字节、读者占用；零副作用（真实目录递归快照一致、生产主库 49,677,344,768 B / mtime 未变）；`B.VR-b08l2` = APPROVE_WITH_FINDINGS，7 条全处置 |
| ③ | **B09 / B.AR** | ⚠️ **完成（范围受限，越界在案）** | 只读 manifest 执行 + 从原文重核 hash（6/6 摘要、18/18 产物）；`B.VR-bar` = APPROVE_WITH_FINDINGS + **OVERREACH**；owner 授权我裁定 ⇒ 追认授权、越界**保留在案不重做**、边界改**机械强制**（自测 5/5）+ **机器可核对**（102 次对 25 预算）；身份腿补**交易所登记册**独立基准（8/12 跨来源确认） |
| ④ | **B10** 单一读取链 | ✅ **完成并闭环**（四轮复审全部处置） | 见 §2 |

**复审汇总**：`B.VR-b10`（增量 1）accepted_with_findings 8 条已处置 → `B.VR-b10-r2`（批次 1-2）**REJECT**，P0+P1×2 已处置 → `B.VR-b10-r3`（r2 处置）**REJECT**，3 条核心 **FIXED**、6 条已处置 → `B.VR-b10-r4`（最终验证）**APPROVE_WITH_FINDINGS**，1 条活 P2 + 4 条 P3 已处置。四轮记录均在 `reviews/`。

## 2. B10 交付内容（`f92fc71` 为当前形态）

- **单一解析实现**：`store.metadata_state(raw) -> (object, state)`（报告半）+ `metadata_object = metadata_state(...)[0]`（plain 半）；**9 个曾各自解析的站点**收敛（批次 1 的 7 处 + 批次 2 的 `_frontmatter` + P0 的 `normalize_catalog`），`section_query` 的具名报错**声明**保留。
- **旧入口具名**：`reader.resolve_handle` / `bundle` 登记为 v1 adapter，**声明**它们不是字节级（`bundle` 读 artifact 文件：`reads_files=True`，P1 修正后的事实）+ 各自的移除条件。
- **两道计数棘轮**（每作用域站点数；键为 `Class.method` 限定名）：`CONFIRMED_DIRECT_READERS` **1 条**（已声明的 section_query）、`COLUMN_VALUE_HANDOFFS` **12 作用域 / 15 站点**（机器导出；早先写的 13/16 是批次 2 与 P0 收敛前的读数，r3 已指出该陈旧文字并已改）；另有"产品包其余部分 0 处直读"硬规则（**enforced**）；`GATE_BOUNDARIES` 记录**实测**边界（4 种绕过形状 + 库外读者 `scripts/`2、`tools/`0、`tests/`10 —— 后三者是**观察**，注入到 `scripts/`/`tools/` **不会**变红，r3 的 `B-VR-B10R3-02` 已指出并改正措辞）。
- **可读性/可见性**：不可读元数据 ⇒ `metadata_unreadable` flag + identity 判定降级 `unverifiable`（不再"证据缺失=通过"）；**共享列**的解析**不再**能中止整轮（P0 修复，探针阶段 2 + 修前/修后对照证）；**失败 handler 里的姊妹列**解析也不再能中止整轮（r3 的 `B-VR-B10R3-01`，一行修复 + 探针阶段 3 的修前读数证）。
- **仍然存在的整轮中止路径（未修，需 owner 决定）**：主文件缺失 ⇒ unsupported 分支的 `IngestService.ingest` 逃出（会**饿死后面的文档**）；`_atomic_write`（阅读发现，未驱动）。见 [findings.md](findings.md) `F-B10R2-MISSINGFILE`。
- **回退**：逐批次回退点见 [evidence/b10-implementation.md](b10-implementation.md) §9.1；**回退不回滚任何数据**（B10 全程只改读取路径）。
- **不声称**：棘轮是**语法形状**上的（非数据流），四种形状未覆盖；`scripts/` 两处不在门内；`F-B10R2-MISSINGFILE`（主文件缺失中止整轮，**既有**问题）**未修**；`tests/` 10 处夹具直读不在门内。

## 3. 质量证据（可复核）

| 项 | 结果 | 证据 |
|---|---|---|
| 门用例 | **15** | `tests/contract/test_b10_read_chain.py` |
| 变异 | **12/12 KILLED by assertion**（`repository_untouched=true`，副本基线 26 passed） | [evidence/b10-mutations.json](evidence/b10-mutations.json) |
| 本地 CI 两步 | unit **798 passed**；contract **1904 passed / 8 skipped**（**环境相关**：r3 在 Python 3.14.2 且缺 `xlrd`/`fitz` 的环境下得 `7 failed / 1886 passed / 19 skipped`，r3 已证明那 7 条全部**既有且属环境**；r4 在 3.13.9 下**逐字复现**本行数字） | [evidence/b10r7-ci-step1-unit.txt](evidence/b10r7-ci-step1-unit.txt)、[evidence/b10r7-ci-step2-contract.txt](evidence/b10r7-ci-step2-contract.txt) |
| 远端 CI | wiki **`c4f5b8a`**(master) = success，run `35283319814`；revenue **`65cc18d`**(main) = success，run `35283938871`（两条均为最终状态） | GitHub Actions |
| 行为级验证 | 共享列：探针阶段 2 `escaped:false` + `metadata_unreadable` flag（判定读数**不**归因，归因证据在单元用例）；姊妹列：真树 `escaped:false / failed:1`、**退回那一行的副本 `escaped:true` @1727**；主路径 manifest：坏 manifest + 后面健康文档 ⇒ 真树归一化继续、**副本逃逸**（r4 用真实 `.docx` 独立复现） | [evidence/b10-p0-probe.txt](evidence/b10-p0-probe.txt)、`tests/unit/test_b10_manifest_abort_paths.py` |
| 独立复审 | 四轮（见上表），全部结论与处置均在 `reviews/` 与 [evidence/b10-implementation.md](evidence/b10-implementation.md) §7/§7bis/§7ter/§7quater/§7quinquies/§7sexies/§7septies | `reviews/` |

## 4. 边界与残留（不得含糊）

1. **未获授权的写动作**：B.AR 的第五 root **生产**注册（= 写 46.3 GiB 生产 catalog）、跨仓端到端入口调用、`dropbox_stock` 3 份字节核验（读云目录可能水合）、扩大抽样 —— **原样未做**。**其中三项已在 2026-09-18 按 owner 的逐项选择交付**（[owner-scope-decisions-2026-09-18.md](owner-scope-decisions-2026-09-18.md)）：第五 root 以**隔离副本**方式交付、跨仓端到端以 `filing-fetch` 真实入口**只读**跑通、`dropbox_stock` 3 份在水合被接受的前提下**核验 3/3**；**生产四根与第五根共存**仍未验证，**扩大抽样**仍未做。
2. **`F-B10R2-MISSINGFILE`**：主文件缺失仍会中止整轮 normalize（**既有**、非本次引起）；影响面**未量化**；需 owner 决定是否立项。
3. **`scripts/` 两处直读**（`legacy_observer.py:96`、`wu904_remediation_restore.py:65`）不受任何棘轮覆盖。
4. **零副作用主张的残余风险**（复审明示）：生产 catalog 只能 `stat`，故"大小+mtime 不变的内容写入"对工具与复审**都不可见**。
5. **B.AR 抽样仅 12 份**（0.28%）；`dropbox_stock` 的 3 份抽样**已核验（3/3，2026-09-18）**，但其**真实年报 PDF 未核验**，且云文件的**数据局部性在本机不可判定**（[evidence/b-ar-dropbox-bytes.md](evidence/b-ar-dropbox-bytes.md)）。

## 5. 定稿结论

- **四个工作包**：① B05 ✅、② B08 ✅、③ B09/B.AR ⚠️（完成但范围受限 + 越界已裁定在案）、④ B10 ✅ —— 四者均**已实施、已独立复审、发现全部处置、本地两步 CI 与远端 CI 全绿、记录入库**。
- **未完成项全部是"未获授权"或"已登记待 owner 决定"**，不是"做了一半"：第五 root 注册与跨仓端到端需要**写**权限；`F-B10R2-MISSINGFILE` 一族（缺文件/坏行仍可中止整批）、`scripts/` 两处不受棘轮覆盖的读取者、云同步样本不哈希、以及"大小+mtime 不变的写入不可见"这一残余风险，均需 owner 表态。
- **checkpoint**：本文件定稿后由 `evidence/build_checkpoint.py --reviewed-commit <最终 sha>` 生成，并 `--verify-only` 复核（见 `checkpoint.json`）。

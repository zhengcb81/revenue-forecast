# R4 最终状态小结（草稿，待 `B.VR-b10-r3` 结论后定稿）

> 口径：本文件只写**有证据支撑**的结论；每条都指向可核对的提交/证据文件。**未过独立复审的项**明确标注。

## 1. 四个工作包的状态

| # | 工作包 | 状态 | 证据 |
|---|---|---|---|
| ① | **B05** 读侧畸形共享列 | ✅ **完成并闭环** | wiki `74ffeeb`→`91a20ec`→`41fdfe1`（run `35146033771` 绿）；两轮复审（`B.VR-b05malformed`、`-verify`）全部处置；变异 15/15 |
| ② | **B08** G8 第②级 | ✅ **完成并闭环** | 隔离根只读引用真实文件、两次 `verified` 读（4,172,424 B，摘要=独立哈希真实文件）、篡改 0 字节、读者占用；零副作用（真实目录递归快照一致、生产主库 49,677,344,768 B / mtime 未变）；`B.VR-b08l2` = APPROVE_WITH_FINDINGS，7 条全处置 |
| ③ | **B09 / B.AR** | ⚠️ **完成（范围受限，越界在案）** | 只读 manifest 执行 + 从原文重核 hash（6/6 摘要、18/18 产物）；`B.VR-bar` = APPROVE_WITH_FINDINGS + **OVERREACH**；owner 授权我裁定 ⇒ 追认授权、越界**保留在案不重做**、边界改**机械强制**（自测 5/5）+ **机器可核对**（102 次对 25 预算）；身份腿补**交易所登记册**独立基准（8/12 跨来源确认） |
| ④ | **B10** 单一读取链 | 🔄 **主体完成，最终验证复审在跑** | 见 §2 |

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
| 变异 | **10/10 KILLED by assertion**（`repository_untouched=true`，副本基线 24 passed） | [evidence/b10-mutations.json](evidence/b10-mutations.json) |
| 本地 CI 两步 | unit **796 passed**；contract **1904 passed / 8 skipped**（**环境相关**：r3 在 Python 3.14.2 且缺 `xlrd`/`fitz` 的环境下得 `7 failed / 1886 passed / 19 skipped`，并证明 7 条全部**既有且属环境**） | [evidence/b10r5-ci-step1-unit.txt](evidence/b10r5-ci-step1-unit.txt)、[evidence/b10r5-ci-step2-contract.txt](evidence/b10r5-ci-step2-contract.txt) |
| 远端 CI | wiki `f92fc71`(master) ✅；revenue 文档提交 `b7f6847`(main) ✅（**-01 修复后的最终 sha 见定稿**） | GitHub Actions |
| P0/P2 行为级验证 | 探针阶段 2（共享列）`escaped:false` + flag + 判定降级；阶段 3（姊妹列）真树 `escaped:false`、**变异副本 `escaped:true` @1727** | [evidence/b10-p0-probe.txt](evidence/b10-p0-probe.txt)、[evidence/b10_p0_probe.py](b10_p0_probe.py) |
| 独立复审 | `B.VR-b10`（处置完）、`B.VR-b10-r2` = **REJECT**（7 条处置完）、`B.VR-b10-r3` = **REJECT**（核心三条 **FIXED**，6 条新发现处置完） | `reviews/` |

## 4. 边界与残留（不得含糊）

1. **未获授权的写动作**：B.AR 的第五 root 注册（= 写 catalog）、跨仓端到端入口调用、`dropbox_stock` 3 份字节核验（读云目录可能水合）、扩大抽样 —— **一律未做**。
2. **`F-B10R2-MISSINGFILE`**：主文件缺失仍会中止整轮 normalize（**既有**、非本次引起）；影响面**未量化**；需 owner 决定是否立项。
3. **`scripts/` 两处直读**（`legacy_observer.py:96`、`wu904_remediation_restore.py:65`）不受任何棘轮覆盖。
4. **零副作用主张的残余风险**（复审明示）：生产 catalog 只能 `stat`，故"大小+mtime 不变的内容写入"对工具与复审**都不可见**。
5. **B.AR 抽样仅 12 份**、`dropbox_stock` 3 份未核验。

## 5. 定稿待办

- [ ] `B.VR-b10-r3` 结论 → 若有发现，逐条处置并入库（可能再动产品/测试）
- [ ] checkpoint 重建：`python evidence/build_checkpoint.py --reviewed-commit <最终 sha>`
- [ ] 把本文件的"草稿"标记去掉，并把最终 sha 与 CI run 号写进 §3

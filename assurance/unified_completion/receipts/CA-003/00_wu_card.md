# CA-003 工作单元卡（preflight）— CodeGraph 新鲜度与 production reachability manifest

- 领取时间：2026-08-13T22:05Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-003`；机器状态 units.CA-002.status=accepted + closure 存在。
- 依赖：CA-002（accepted ✅，receipts/CA-002/）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01/P10（证据新鲜度与 full-chain 冒称）：让 CodeGraph 索引与 git commit 精确绑定，让每个 full-chain 主张有机器可查的 production caller 证据；登记已知旁路（RuntimeContext/runtime_policy=None 回退）为阻断 finding。
2. **production entrypoint 是什么？** CodeGraph 索引本身（.codegraph/codegraph.db）+ 三仓 product 入口；旧状态：`codegraph status` 只报统计、project_metadata 表空——索引与 commit 无机器绑定。
3. **哪个 current-triplet 行为是 RED？独立 oracle 如何证明？** RED-A：当前 .codegraph 无法证明索引对应哪个 commit（project_metadata 空；status 无 commit 字段）→ 旧索引可被当作 current 证据。RED-B：存在被标 full-chain/三进程的测试实际只覆盖 helper/seam（对具体测试逐条核验并记录）。oracle = codegraph db 元数据查询 + status 输出 + 测试源码/夹具检查。
4. **允许改哪些文件？** 新增 `assurance/unified_completion/uc/codegraph_freeze.py`、`tests/test_codegraph_freeze.py`、`codegraph/` 产物、receipts/CA-003/**。**禁止**：三仓产品代码/配置/CI；.codegraph 的 config.json 不改；catalog/roots 只读。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-004（依赖 CA-002+CA-003）。不解决：旁路的修复（归 phase C/D 的 ZR）、旧 71 FC 处置（CA-004）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-002 accepted（机器状态）；closure 提交 b06cfbf 已落地。
- [x] 三仓 HEAD：revenue `b06cfbf…`（closure 提交后，领取时重读）；filing `83c638e…`；wiki `ef125ed…`。
- [x] 独占索引窗口：三仓 .codegraph 无锁文件；4 个 `codegraph serve --mcp` 进程是读者非索引写入者。
- [x] 冻结规范 hash：manifest-verify 严格 OK；环境基线 env_freeze sha d64535944cb5…。
- [x] 工作文件 allowlist 不重叠；state.json/locks 单 writer。
- [x] 短 ASCII 控制组：测试用 tmp_path；真实索引为三仓独占窗口操作（README 已授权）。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）；三仓均需独占索引。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`still_missing`——无 indexed commit 绑定、无 production caller manifest。
- **Production callers before / after**：before=0（无此工具）；after=codegraph-freeze/verify CLI（assurance 工具）。
- **Scenario IDs / real tier**：治理工具卡；测试层 T0（契约/变异）+ 真实三仓索引。
- **RED command and exact expected failure**：见 receipts/CA-003/red/。
- **Independent oracle**：codegraph db metadata 查询、status 输出、git HEAD 对比、caller 报告交叉核对。
- **Atomic implementation steps**：见 session 计划 A0.3。
- **Negative / fault / mutation / race**：负例（indexed commit≠HEAD、stats 漂移、已删除符号出现、caller 报告缺目标）；fault（codegraph CLI 失败/锁陈旧）；mutation（篡改 freeze 产物）；race（独占窗口内无并发索引）。
- **Side-effect budget**：仅写 assurance/unified_completion/** 与三仓 .codegraph/codegraph.db*（索引重建=本卡授权范围）；产品代码/配置/catalog/roots 零写。
- **Migration, idempotence and rollback**：索引重建幂等；freeze 产物 exclusive publish/CAS；rollback=删除新目录+重跑旧索引（.codegraph 可再 index）。
- **Evidence paths**：`assurance/unified_completion/receipts/CA-003/`。
- **Acceptance criteria**：indexed commit 精确等于领取时三仓 HEAD；已删除符号不出现；每个 full-chain claim 至少一条真实 production path 和 subprocess trace。
- **Stop conditions / handoff**：同 CA-001（弱模型清单 §9）。

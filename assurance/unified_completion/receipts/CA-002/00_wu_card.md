# CA-002 工作单元卡（preflight）— current triplet、upstream、dirty 与环境冻结

- 领取时间：2026-08-13T21:55Z（本地）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-002`；机器状态 `assurance/unified_completion/state.json` units.CA-001.status=accepted + closure 存在。
- 依赖：CA-001（accepted ✅，receipt 见 receipts/CA-001/）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** P01（验收假绿）：旧 gate 只验证"HEAD 是冻结 baseline 的后代"（merge-base ancestry），不验证精确 current triplet、upstream、dirty allowlist 与环境。本卡建立精确 equality 的环境冻结真源，使所有后续卡的 triplet 判定可机器复核。
2. **production entrypoint 是什么？** 控制面 = assurance/unified_completion + 三仓 git 元数据；旧工具 `tools/closure_gate.py`（ancestry-only）与陈旧 `compatibility/current.json` 是当前证据链。helper/seam 不算生产路径。
3. **哪个 current-triplet 行为是 RED？独立 oracle 如何证明？** RED-A：compatibility/current.json 的 current_triplet（revenue 1b41d62/filing 592fae6/wiki f6eb584）与三仓实际 HEAD（0815522/83c638e/ef125ed）全部不符，旧 gate 不报（其代码只读 frozen_baseline_triplet，从不读 current_triplet）；RED-B：三仓 fcap 无 upstream 跟踪、dirty 文件未登记于任何机器账本，旧 gate 无任何检查。oracle = git rev-parse/status 实测 + closure_gate 源码行级证据 + 运行验证。
4. **允许改哪些文件？** 新增 `assurance/unified_completion/uc/envfreeze.py`、`tests/test_envfreeze.py`、`environment/` 冻结产物、receipts/CA-002/**。**禁止**：三仓产品代码/配置/CI、旧计划目录；catalog/roots 只读（指纹=大小/mtime/schema hash/行数，零写）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-003（依赖 CA-002）。不解决：CodeGraph 重建（CA-003 独占窗口）、旧 71 FC 处置（CA-004）、legacy 删除（CA-304）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-001 accepted（机器状态）；本卡无其它 writer（锁目录空闲）。
- [x] 三仓 HEAD：revenue `0815522a3573faef50ab006290e6c57fe0de7489`；filing `83c638e76e40890262746cdf02b6df495dcb4031`；wiki `ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875`。分支均 fcap；upstream 未设置（origin 存在）。
- [x] dirty：revenue 7（audit_review 内 3 个 M + 2 个计划目录 + 2026-08-12 目录 + assurance/runs 未跟踪；README 已随 closure 提交）；filing 0；wiki 4（llm_cost_log.csv 等用户文件）。均非本任务修改，仅登记为 allowlist。
- [x] 冻结规范 hash：manifest-verify 严格模式 OK（closure 后）。
- [x] 前置 receipt 未过期（当日）。
- [x] 工作文件 allowlist 与其它 WU 不重叠；state.json/locks 单 writer（本卡只读 state、新增 environment/ 产物）。
- [x] 短 ASCII 控制组：测试用 tmp_path；真实 catalog 指纹只读。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）；filing-fetch、company-wiki 只读观测。
- **Base triplet / plan hash**：见上；plan hash = CA registry `861e28f9…`。
- **Current-state drift verdict**：`still_missing`——仓库无环境冻结工具；compatibility/current.json 陈旧（current_triplet 与实际 HEAD 全不符）。
- **Production callers before / after**：before=0；after=新增 `uc.cli env-freeze / env-verify`（assurance 控制工具）。
- **Contract/schema compatibility**：不动产品 schema/config/CI；env_freeze.json 为 v1 新 schema（本卡定义，CA-101 版本化）。
- **Scenario IDs / real tier**：治理工具卡，无 197 场景映射；测试层 T0（契约/变异）+ 真实环境采集。
- **RED command and exact expected failure**：见 receipts/CA-002/red/。
- **Independent oracle**：git rev-parse/status、ls-remote（可及时）、toolchain 版本实测、catalog 只读指纹。
- **Atomic implementation steps**：envfreeze.collect → freeze（exclusive publish）→ verify（精确 equality）→ CLI 接线 → 测试 → 真实冻结。
- **Negative / fault / mutation / race**：负例（每字段漂移均检出、local-only≠pushed、infra 错误分类）；fault（remote 不可达→unverifiable 而非异常）；mutation（改冻结产物任一字段→verify 红）；race（冻结产物 exclusive publish 单赢家）。
- **Side-effect budget**：仅写 assurance/unified_completion/**；catalog/roots 只读；零下载、零 LLM、零外部写。
- **Migration, idempotence and rollback**：无迁移；freeze 幂等（已存在→CAS 替换需显式 force）；rollback=删除 environment/ 产物。
- **Evidence paths**：`assurance/unified_completion/receipts/CA-002/`。
- **Acceptance criteria**：精确 equality gate 任一字段漂移即 stale；不因 baseline descendant 放行新组合；local-only/pushed 可验证区分；Git unsafe-directory=基础设施错误分类。
- **Stop conditions / handoff**：同 CA-001（弱模型清单 §9）。

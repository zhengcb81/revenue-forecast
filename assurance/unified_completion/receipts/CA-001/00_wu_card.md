# CA-001 工作单元卡（preflight）— 计划输入锁与并发 CAS

- 领取时间：2026-08-13T20:40Z（本地 2026-08-13 21:40）
- 唯一入口：`audit_review/README.md` §0 `current_next=CA-001`，machine state 尚不存在 → 与 `not_started` 一致。

## 领取前五问（弱模型清单 §1，逐字回答）

1. **推进哪个用户目标/痛点？** 推进"可审计链路"治理层：P01（验收假绿/无漂移检测）与 runbook §2 并发纪律。使 6 个成功条件所需的证据系统有一个单 writer、可 CAS、可离线重算的基底。
2. **production entrypoint 是什么？** 控制面 = `audit_review/README.md` + 冻结规范目录；现有旧工具 `tools/closure_gate.py`、`tools/closure_ledger.py`、`tools/receipt_validator.py` 是旧证据链。helper/seam（测试夹具、dashboard 脚本）不是生产路径。
3. **哪个 current-triplet 行为是 RED？独立 oracle 如何证明？** RED-A：旧工具对共享输出无锁无 CAS，两个并发 writer 都"成功"，last-write-wins，零冲突信号（oracle = 双进程 exit/输出/最终文件 + 仓库内锁工件清单）。RED-B：无任何机器 manifest 校验，plan/registry 内容漂移不可检测（oracle = tools/ 全量盘点 + scratch 副本字节翻转后旧 validator 仍通过）。
4. **允许改哪些文件？** 仅新增 `assurance/unified_completion/**`（工具/测试/receipts/manifests/state/locks），closure 时对 `audit_review/README.md` §0 控制字段做 CAS 小补丁。**绝对禁止**：三仓产品代码/配置、旧计划目录、catalog、roots、CI、`tools/` 旧工具、冻结 annex 文件。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 CA-002（依赖 CA-001）。不解决：严格状态机与 registry schema（CA-101）、receipt 内容寻址 schema（CA-102）、CodeGraph 重建（CA-003）、旧 71 FC 处置（CA-004）、产品功能（ZR-*）。

## 领取前机械门（弱模型清单 §2）

- [x] CA-001 无前置锁；`assurance/unified_completion/locks` 不存在（无并发 writer）。
- [x] 三仓 40 位 HEAD：revenue `c3a0519303d78dfe283bea6247da53163b926dc8`；filing `83c638e76e40890262746cdf02b6df495dcb4031`；wiki `ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875`。分支均 `fcap`，upstream 未跟踪（origin 存在）。
- [x] dirty allowlist：revenue 8 项（audit_review 内 3 个跟踪文件修改 + assurance/runs/、2026-08-12 目录、两个 2026-08-13 计划目录、README.md 未跟踪）；filing 0；wiki 4 项（.claude/settings.local.json 删除、llm_cost_log.csv 修改、.coverage、coverage.json 未跟踪）。均非本任务修改。
- [x] plan/registry/scenario/config 等 hash：8 冻结 annex + 30 输入快照（程序化解析 input_snapshot.md）全部匹配。
- [x] 前置单元：CA-001 无依赖（registry 声明"依赖：无"）。
- [x] 本卡 allowlist 与其它 WU 不重叠；state.json/locks 尚无其它 writer。
- [x] 短 ASCII 控制组：测试使用 pytest 默认 tmp_path（短路径）；中文/长路径不在本卡范围。

## 卡片字段（runbook §4）

- **Owner repo / collaborating repos**：revenue-forecast（控制面所在仓）；filing-fetch、company-wiki 只读。
- **Base triplet / plan hash**：见上；plan hash = 8 annex + 30 输入（见 evidence/red 目录）。
- **Dependencies / decision records**：无前置单元；依据 README §0/§8/§12、CA registry CA-001 卡、runbook §2/§3、弱模型清单 §1/§2/§9。
- **Current-state drift verdict**：`still_missing`——仓库中不存在任何 lock/CAS/manifest 校验工具（grep `tools/` 确认）。
- **Production callers before / expected edge delta**：before=0（无此工具）；after=新增 `uc.cli` 命令行入口（assurance 控制工具，非产品代码）。
- **Contract/schema compatibility**：不动产品 schema/config/CI；state.json 为 v1 最小 schema，CA-101/102 按 N/N-1 策略版本化。
- **Scenario IDs / real tier**：本卡为治理工具，无 197 场景映射；测试层 = T0（纯契约）+ 并发 mutation。
- **RED command and exact expected failure**：见 `receipts/CA-001/red/`（RED-A 双进程 closure_ledger 并发；RED-B scratch 字节翻转）。
- **Independent oracle**：双进程 exit/输出 + 锁工件存在性清单 + manifest 重算。
- **Atomic implementation steps**：见 `receipts/CA-001/red/` 与 task_plan 会话文件。
- **Negative / fault / mutation / race**：负例（冒名释放、过期锁、漂移拒绝）；fault（替换前崩溃不留半文件）；mutation（篡改锁 owner/manifest hash）；race（双 breaker 并发破锁、双 writer CAS）；10 轮并发 mutation 无丢更新。
- **Side-effect budget**：仅写 `assurance/unified_completion/**` 与 README §0 控制字段；产品仓/旧计划/catalog/roots 零写；无下载、无 LLM、无网络。
- **Migration, idempotence and rollback**：无数据迁移；工具全幂等（二次 acquire 同 owner renew、二次 bootstrap 拒绝、二次 verify 同结果）；rollback = 删除新增目录 + 恢复 README 补丁。
- **Evidence paths**：`assurance/unified_completion/receipts/CA-001/`。
- **Acceptance criteria**：10 轮并发 mutation 无丢更新；全部计划输入可离线重算；锁失败不写半状态；漂移/过期锁/冒名/双 writer 均拒绝。
- **Stop conditions / handoff**：冻结规范 hash 漂移、用户 dirty 文件被触碰、其它程序写同一 assurance 目录 → 立即释放并停线（弱模型清单 §9）。

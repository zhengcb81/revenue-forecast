# ZR-902 工作单元卡（preflight）— H 首卡：实际调度每日 Windows T2（schedule/runner/权限/原子报告/<=24h freshness/release 消费全证明）

- 领取时间：2026-08-22T22:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-902`（ZR-806 closure → ZR-902）；锁 ZR-902（owner=zr902-implementer，nonce 2ea05f85…）。
- 依赖：ZR-806（真实 T2 三 root 样本，accepted ✅）、CA-107（证据系统，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H（动态审核实际运行）首卡——把既有 `tools/daily_t2_runner.py`（FC-1102）从"脚本存在"推进到"实际调度 + 报告 freshness + 缺 run 告警 + release 消费门"全证明（CA-202 验收："平台 schedule/权限/runner 身份可查；报告≤24h、atomic complete、精确 triplet；缺 run 本身告警并阻断 release"）。现状缺口（RED G1~G3）：真实 Windows Task Scheduler 396 个任务中零本项目条目（G1 无实际调度）；assurance/runs 最近报告 2026-08-13（9 天前，G2 无 freshness 门——旧绿沿用无人拦）；无 release 消费 daily run 状态的机制（G3）。
2. **production entrypoint 是什么？** `tools/daily_t2_runner.py`（既有 runner，报告隔离/非零退出已具备）+ 新 `tools/daily_t2_schedule.py`（Windows Task Scheduler 注册/查询/注销 + 每日 run 包装：调用 runner + 写 run 台账 + freshness/告警判定）。台账 `assurance/runs/daily_manifest.json`（最近 run_id/started_at/triplet/ok）。
3. **RED？** schtasks 实测 396 任务零命中；assurance/runs 最近 report.json 2026-08-13（stale 9 天）；grep daily_manifest/freshness/release gate → 零命中。
4. **允许改哪些文件？** revenue：新 `tools/daily_t2_schedule.py`（assurance 工具，非产品路径）、新 `tests/test_zr902_daily_schedule.py`；receipts/ZR-902/**、locks、state.json、README 镜像、planning docs。禁止：scripts/ 产品代码改动、真实 catalog/root 写、下载、LLM、真实 Task Scheduler 注册（注册是部署动作——脚本提供 --register/--query/--unregister，测试只验证机制与查询逻辑，不依赖真实注册状态；自然时间证据由 CA-206 soak 收集）。
5. **下一单元解锁？** ZR-903（每周/发布前 T3 调度，依赖 ZR-805 已闭 → 可领取）。本卡不做：真实 7 天 soak（CA-206）、T3 周调度（ZR-903）、SLI/dashboard（ZR-904）。

## Acceptance criteria

- **C1 调度机制完整（杀 G1）**：`daily_t2_schedule.py` 支持 `--register`（schtasks 每日任务，非交互权限）、`--query`（任务存在性 + 上次运行结果，只读）、`--unregister`、`--run-daily`（调 runner + 写台账 + freshness 判定 + 告警）；`--verify` 输出 schedule 状态（registered/missing）+ 最近 run 状态（fresh/stale/missing）——真实注册由部署执行（脚本 + 文档），机制被测试钉死。
- **C2 报告 freshness ≤24h（杀 G2，AUD2-01/02）**：run 台账（daily_manifest.json）记录最近 run_id/started_at/triplet/ok；判定：最近 run ≤24h 且 ok → fresh；>24h → stale（旧绿不沿用）；无 run → missing（脚本存在不算运行）。测试用可控台账时间注入验证三态。
- **C3 缺 run/半报告 → 告警 + 阻断 release（杀 G3，AUD2-03）**：stale/missing/ok=false → 告警记录（alert journal）+ 非零退出（release gate 红）；release gate 消费函数（查询台账 → fresh+ok 放行，否则红）被测试钉死。
- **C4 质量门**：全量回归零回退（基线 813 passed + 106 subtests）、ruff clean、ratchet 绿（新文件 ≤10/函数）、skill-sync MATCH、独立 reviewer 复放。产品代码零改动（git diff -- scripts/ 为空）。

## 边界

- 不注册真实 Windows Task Scheduler（部署动作，脚本提供但测试不触发 --register 对真实任务）；测试全部在临时台账/报告目录运行（hermetic）。
- 自然时间证据（连续 7 次 Daily）由 CA-206 soak 收集，本卡交付机制 + 首次 run 证据。
- 台账与报告写入 `assurance/runs/`（审计输出目录，非生产 catalog）。

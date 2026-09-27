# ZR-903 工作单元卡（preflight）— H：实际调度每周/发布前 T3（<=7d freshness / blocked 告警 / provider 对账）

- 领取时间：2026-08-22T23:35Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-903`（ZR-902 closure → ZR-903）；锁 ZR-903（owner=zr903-implementer，nonce 17fa16e6…）。
- 依赖：ZR-805（T3 下载授权语义，accepted ✅）、CA-107（证据系统，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H 动态审核第二卡——每周/发布前 T3 实际调度（CA-203 验收："报告≤7d；blocked 也阻断 release 并发告警；provider/canonical 调用精确对账"）。现状缺口（RED G1~G3）：T3 套件（filing-fetch `tests/test_e2e_download.py`，opt-in FILING_FETCH_E2E_DOWNLOAD=1）存在但无周调度（G1，AUD2-01）；无 ≤7d freshness 门（G2，旧绿沿用）；无 release 消费 weekly run 状态 + blocked（凭据/网络缺失）告警机制（G3，AUD2-03——"网络/凭据缺失被记 pass"是 CA-203 RED）。
2. **production entrypoint 是什么？** filing-fetch T3 套件（真实 CN/HK/US provider 首次授权下载 + 二次零下载 + amendment + single-flight + provider drift，临时 wiki 零残留）+ 新 `tools/weekly_t3_schedule.py`（周调度包装：调 T3 套件 + 写 weekly ledger + ≤7d freshness + blocked 告警 + release 门 + schtasks register/query/verify——与 ZR-902 同型）。
3. **RED？** grep weekly_t3/weekly schedule → 零命中；schtasks 396 任务零本项目条目；无 weekly ledger/freshness 机制。
4. **允许改哪些文件？** revenue：新 `tools/weekly_t3_schedule.py`（assurance 工具）、新 `tests/test_zr903_weekly_t3.py`；receipts/ZR-903/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动（scripts/、filing-fetch src）、真实下载执行（T3 套件为部署动作——run-weekly 需 opt-in 环境变量 + 真实网络，测试用 fake runner stub）、真实 Task Scheduler 注册、LLM。
5. **下一单元解锁？** ZR-904（SLI/dashboard/release gate，依赖 ZR-902/ZR-903）或 ZR-901（PR 门，需 ZR-801 处置）。本卡不做：真实 2 次 Weekly soak（CA-206）、SLI/dashboard（ZR-904）、provider drift 内容验证（T3 套件内部）。

## Acceptance criteria

- **C1 周调度机制完整（杀 G1）**：`weekly_t3_schedule.py` 支持 run-weekly（调 filing-fetch T3 套件 opt-in + 写 weekly ledger + ≤7d freshness + 告警）、register/query/unregister（schtasks weekly）、verify；真实注册为部署动作，机制被测试钉死。
- **C2 freshness ≤7d（杀 G2，AUD2-02）**：weekly ledger（assurance/runs/weekly_manifest.json）fresh（≤7d 且 ok）/stale（>7d 或 not-ok——旧绿不沿用）/missing 三态；测试注入时间验证。
- **C3 blocked 告警 + release 阻断（杀 G3，AUD2-03）**：stale/missing/not-ok → weekly_alert.jsonl 追加 + release gate 红；**凭据/网络缺失（T3 套件 skip/blocked 类退出）→ 显式 blocked 告警而非 pass**（CA-203 RED 反制）——run-weekly 对 T3 套件的"全 skip"退出码转 blocked 记录。
- **C4 质量门**：全量回归零回退（基线 825 passed + 106 subtests）、ruff clean、ratchet 绿、skill-sync MATCH、独立 reviewer 复放。产品代码零改动。

## 边界

- 不注册真实 Task Scheduler、不执行真实 T3 下载（部署动作）；测试全 hermetic（fake T3 runner stub + 临时台账）。
- 自然时间证据（连续 2 次 Weekly）由 CA-206 soak 收集。
- 台账/报告写入 `assurance/runs/`（审计输出目录）。

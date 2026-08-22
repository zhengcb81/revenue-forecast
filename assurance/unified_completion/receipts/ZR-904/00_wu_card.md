# ZR-904 工作单元卡（preflight）— H：SLI/dashboard/release gate（原子报告/同一 schema/告警 ack 重试/过期不可续命）

- 领取时间：2026-08-22T23:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-904`（ZR-903 closure → ZR-904）；锁 ZR-904（owner=zr904-implementer，nonce 6a7c5e76…）。
- 依赖：ZR-902（daily T2 调度）、ZR-903（weekly T3 调度）——均 accepted ✅；CA-107（证据系统）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H 第三卡——SLI/dashboard/release gate（CA-205 验收："pending 临时文件→完整校验→原子 publish；dashboard/release 读取同一 schema；告警送达有 ack/重试；过期结果不可续命"）。现状缺口（RED G1~G4）：无统一 SLI 汇总与原子发布机制（G1，进程中断半报告无防护）；无报告自身 hash/triplet/sample/command 完整性校验（G2）；无告警 ack/重试（告警 sink 失败无感知，G3）；无"过期结果不可续命"门（future timestamp/旧绿复制可混过，G4）+ AUD2-06（renderer/consumer-ready 率回归 → business SLI 阻断发布，即使 unit 绿）。
2. **production entrypoint 是什么？** 新 `tools/release_gate.py`（assurance 工具）：SLI 汇总（从 daily/weekly ledger + catalog 只读：reuse/download avoidance/artifact/consumer-ready/broker fidelity/misattribution/mine conflict/forecast/backtest/render 指标集）+ 原子报告发布（pending → 完整校验 → fsync+rename 原子 publish，报告含自身 canonical hash）+ 告警 ack/重试（alert journal 加 ack 状态与重试计数）+ release 判定纯函数（业务 SLI 全绿 + 报告新鲜 + 完整性 → ready，否则红）。
3. **RED？** grep release_gate/sli/dashboard/ack → 零命中；无原子发布（ZR-710 的 _atomic_write_text 在产品侧，assurance 报告侧无）；无告警 ack 机制；无报告自身 hash 校验。
4. **允许改哪些文件？** revenue：新 `tools/release_gate.py`（assurance 工具）、新 `tests/test_zr904_release_gate.py`；receipts/ZR-904/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动（scripts/）、真实 catalog/root 写、下载、LLM、真实 Task Scheduler 注册。
5. **下一单元解锁？** ZR-905（审核机制自测试，依赖 ZR-904）或 ZR-901（PR 门）。本卡不做：真实调度 run（ZR-902/903 已交付机制）、审核自测试（ZR-905）、CA-206 soak。

## Acceptance criteria

- **C1 原子报告发布（杀 G1/G2）**：pending 临时文件（assurance/runs/reports/*.pending.json）→ 完整校验（triplet/sample/command 字段齐全 + 报告自身 canonical hash 自洽）→ 原子 publish（fsync + os.replace，无半报告可见）；进程中断的 .pending 残留不参与发布且 release 红。
- **C2 SLI 汇总与 dashboard 同一 schema（杀 AUD2-06）**：SLI 指标集（reuse/download avoidance/artifact/consumer-ready/broker fidelity/misattribution/mine conflict/forecast/backtest/render）从 daily/weekly ledger + catalog 只读计算，输出 schema 与 release 判定消费同一份；任一业务 SLI 回归 → release 红（即使 unit 绿）。
- **C3 告警 ack/重试（杀 G3）**：alert journal 条目支持 ack（mark_acked）+ 未 ack 重试（重试计数/时间）；告警 sink 失败（journal 不可写）→ 显式失败非静默。
- **C4 过期结果不可续命（杀 G4）**：报告 future timestamp → 拒绝；旧报告复制改名（旧绿续命）→ 完整性校验（hash 链）拒绝；release 判定要求报告新鲜 + 完整 + SLI 全绿。
- **C5 质量门**：全量回归零回退（基线 837 passed + 106 subtests）、ruff clean、ratchet 绿、skill-sync MATCH、独立 reviewer 复放。产品代码零改动。

## 边界

- hermetic：临时目录（pending/publish/ledger）；真实 catalog 只读访问可注入或跳过（SLI 计算函数可注入数据源）。
- 报告/台账写入 assurance/runs/（审计输出目录）。
- 自然时间证据由 CA-206 soak 收集。

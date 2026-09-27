# ZR-1104 工作单元卡（preflight）— Phase 11：观察期与真实 rollback drill

- 领取时间：2026-08-31T20:11Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1104`（ZR-1103 closure → ZR-1104）；锁 ZR-1104（owner=zr1104-implementer，nonce e0ca07bd…）。
- 依赖：ZR-1103（真实旅程复验，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** Phase 11 第四卡——观察期与真实 rollback drill（registry："连续 7 次 Daily T2、2 次 Weekly T3、1 次 Monthly 紫金 shadow、1 次告警自检；legacy hit=0；一次 cohort rollback/re-activate；自然时间门不得人工豁免"）。现状缺口（RED）：无组合验收。
2. **production entrypoint 是什么？** soak 窗口纯函数（CA-206：daily/weekly/monthly/drill_window + soak_status）；`legacy_close_gate.close_gate_allowed`（FC-705 两连续零 hit 窗口）；`activation.apply_activation/rollback_activation`（cohort drill）；assertion_service seed（ZR-1003 模式）。
3. **RED？** glob tests/**/*zr1104* → 零命中；无观察完整性+legacy 门+rollback+无豁免+drill journal 组合。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1104_observation_drill.py`；receipts/ZR-1104/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** ZR-1105（closure ledger）→ ZR-801 处置 → 全部闭环。本卡不做：真实自然时间累积（部署/调度累积，CA-206 之后）。

## Acceptance criteria

- **C1 观察完整性**：7 daily + 2 weekly + 1 monthly + 1 acked drill → complete；任一不足 → PENDING。
- **C2 legacy-hit 门**：hits≠0 阻断 closure；两连续零 hit 窗口才允许（FC-705）。
- **C3 cohort rollback drill**：activation→rollback→re-activate 保留 epoch/cohort/policy hash，仅翻转 active flag，receipt 各异。
- **C4 无人工豁免**：open window/复制报告（重复 run id）/stale weekly 全 fail-closed（不可人工改时钟/复制报告豁免）。
- **C5 drill journal**：alert 自检 drill 仅 acked 计入观察窗口。
- **C6 质量门（卡级）**：相邻回归（CA-206/CA-304）零回退、revenue 全量零回归（基线 1048+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 纯函数 + tmp CatalogStore；零网络/下载/LLM；真实自然时间累积为部署/观察动作。

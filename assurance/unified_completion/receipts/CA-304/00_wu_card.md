# CA-304 工作单元卡（preflight）— J：R9 分批删除与真实 rollback drill

- 领取时间：2026-08-31T18:15Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-304`（CA-303 closure → CA-304）；锁 CA-304（owner=ca304-implementer，nonce b5a99272…）。
- 依赖：CA-206（soak）、CA-302（三类旅程）、CA-303（架构终审）、ZR-1008（cutover）（均 accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 J 第四卡——R9 分批删除与真实 rollback drill（registry："把 R9_GATE=1 四 RED 转绿并分批移除 _scan_root_v1、legacy bridge/flags、无生产读者 backfill/promoter；每批全矩阵和 cohort rollback；禁止为绿只删测试/改 skip；两个动态周期 legacy hit 非 0 时禁止删除；符号/flags/callers 均不存在；新链 journeys 绿；真实 rollback/re-activate 结果一致"）。现状缺口（RED）：无删除门组合验收。
2. **production entrypoint 是什么？** `legacy_close_gate.close_gate_allowed`（FC-705 两连续 ≥24h 零 hit 窗口）；`daily_t2_runner` legacy-hits 检查；`final_ratchet.scan_legacy/scan_encoding`（零残留门）；`activation.apply_activation/rollback_activation`（cohort rollback drill）；`assertion_service.upsert_verified_assertion`（seed）。
3. **RED？** glob tests/**/*ca304* → 零命中；无 close-gate/oracle/分批门/rollback/零残留组合；当前 scripts/ 零 legacy callers。
4. **允许改哪些文件？** revenue：新 `tests/test_ca304_r9_removal.py`；receipts/CA-304/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 legacy 删除（CA-304 部署动作）、CI 改动、真实 catalog 写。
5. **下一单元解锁？** CA-305（六问题 machine closure ledger）→ CA-306（旧计划 terminal closure）。本卡不做：真实分批删除执行（部署，需两动态周期零 hit 自然证据）。

## Acceptance criteria

- **C1 close-gate 纪律（FC-705）**：仅两连续 completed ≥24h 零 hit 窗口允许删除；open/missing/short(<24h)/hits>0/nonconsecutive/empty 全 fail-closed。
- **C2 legacy-hit oracle**：daily T2 runner 的 legacy-hits 检查与 observer ledger 同源（run 有 hit → 删除 blocked）。
- **C3 分批门 + rollback 往返**：final_ratchet legacy scan 在当前树零命中（分批门）；activation→rollback→re-activation epoch/cohort/hash 相同。
- **C4 零残留**：scripts 零 legacy callers + 零编码问题；legacy_bridge_enabled 为 migration-only 排除项（flags.EXCLUDES）。
- **C5 rollback drill**：三周期 activation→rollback 仅翻转 active flag，epoch/cohort/hash 持久。
- **C6 质量门（卡级）**：相邻回归（company-wiki ZR-305/ZR-1003）零回退、revenue 全量零回归（基线 1001+106）、ruff clean、独立 reviewer 复放。产品代码零改动、零真实删除。

## 边界

- 纯函数 + tmp catalog（CatalogStore seed）；零网络/下载/LLM；真实分批删除为 CA-304 部署动作（需两动态周期零 hit 自然证据）。

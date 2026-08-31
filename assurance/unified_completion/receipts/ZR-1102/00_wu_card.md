# ZR-1102 工作单元卡（preflight）— Phase 11：独立 reviewer 对抗式三仓审查

- 领取时间：2026-08-31T19:38Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1102`（ZR-1101 closure → ZR-1102）；锁 ZR-1102（owner=zr1102-implementer，nonce 4810f177…）。
- 依赖：ZR-1101（机器 closure gate，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** Phase 11 第二卡——独立 reviewer 对抗式审查（registry："不复用实施者结论；生产 reachability、硬编码、测试孤岛、伪计数全部复核"）。现状缺口（RED）：无对抗式审查组合验收。
2. **production entrypoint 是什么？** `scripts/` 全模块（CLI mains + 库模块 reachability）；`final_ratchet` 扫描器（hardcode/legacy/encoding 独立复扫）；`mutation_patrol.patrol`（mutation 防护）；`tests/` 集合面（孤岛检测）；`.github/workflows`（无 silent-pass）。
3. **RED？** glob tests/**/*zr1102* → 零命中；无组合验收；三门扫描当前零命中。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1102_adversarial_audit.py`；receipts/ZR-1102/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、CI 改动、下载、LLM。
5. **下一单元解锁？** ZR-1103（真实用户旅程复验）→ ZR-1104/1105 → ZR-801 处置。本卡不做：真实旅程复验（ZR-1103）。

## Acceptance criteria

- **C1 生产 reachability**：scripts/ 每模块为 CLI（main/run）或库模块（可导入 + scripts/ 或 tests/ 中至少一个引用）——无孤儿。
- **C2 硬编码复扫**：final_ratchet hardcode/legacy/encoding 独立零命中。
- **C3 测试孤岛**：每个 tests/test_*.py 有真测试（def test_ 或 fixture）；抽查 collect-only 无 error。
- **C4 伪计数防护**：mutation_patrol.patrol 运行产出 mutation 结果；docstring 标签不计为代码（labels allowed）。
- **C5 旁路扫描**：CI 无 `|| true`；无模块级 skip 缺 opt-in marker（FILING_FETCH_E2E_DOWNLOAD/CODEGRAPH_CLI）。
- **C6 质量门（卡级）**：revenue 全量零回归（基线 1033+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 只读扫描 + subprocess；零网络/下载/LLM；mutation patrol 本地运行（seed 42 samples 3）。

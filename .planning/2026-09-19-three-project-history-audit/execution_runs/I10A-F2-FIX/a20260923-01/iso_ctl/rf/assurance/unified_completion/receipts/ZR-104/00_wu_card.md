# ZR-104 工作单元卡（preflight）— 三仓质量基线与 ratchet

- 领取时间：2026-08-14T08:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-104`；units.ZR-103.status=accepted + closure.next=ZR-104。
- 依赖：ZR-002（accepted ✅）。Registry 依赖列=ZR-002。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 契约基座最后一环：冻结三仓的类型（mypy strict target 集）、覆盖率、复杂度、硬编码、死生产 caller 基线，并建立 ratchet——阈值只升不降；新增/改关键函数 complexity≤10；public contracts strict type。
2. **production entrypoint 是什么？** 三仓现有质量资产：wiki FC-1201（root 硬编码冻结 allowlist）+ FC-1204（coverage/complexity ratchet，FC1204_COVERAGE_GATE）+ CI mypy 11 模块；revenue mypy.ini（scripts/contracts strict）+ ruff + CA-003 CodeGraph caller 报告；filing ruff/mypy/CI。本卡冻结这些真实产出的截面为共享基线并加机器 ratchet，不新建第二套度量。
3. **哪个 current-triplet 行为是 RED？** 无共享质量基线注册表；三仓 ratchet 各自为政、无跨仓机器门；阈值可被静默下调。
4. **允许改哪些文件？** revenue `assurance/unified_completion/quality/**`（基线注册表+verify 模块）+ `uc/cli.py`（quality-freeze/verify 子命令）+ `tests/test_zr104_*.py` + receipts/ZR-104/**；三仓各自的 ratchet 测试若需引用共享基线（可选，最小改动）。禁止：下调任何现有阈值、改产品代码语义、改 CI 门为宽松。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-105（current-triplet CI 门，依赖 ZR-101~104）。本卡不修复任何现有质量债（高 CC/硬编码/死 caller 的清理归各自 ZR 单元与 CA-304）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-103 accepted（机器状态；closure.next=ZR-104）。
- [x] triplet 冻结：revenue `313638b25c9dd109af442b666765f4340de2fb8b`（ZR-103 closure，领取时重读）；filing `83c638e…`；wiki `b661755…`。
- [x] 基线数据源预研：wiki FC-1201 allowlist 冻结集在 architecture_gate.py；FC-1204 ratchet 测试在 tests/contract/test_fc1204_*；revenue mypy 目标=scripts（mypy.ini mypy_path=scripts）；CA-003 codegraph caller 报告机器产物在 codegraph/。
- [x] 纪律：基线值一律来自工具真实输出（mypy/coverage/complexity 运行结果、allowlist 冻结集、caller 报告），禁止手写。

## 卡片字段（runbook §4）

- **Owner repo**：三仓（revenue 承载共享注册表；wiki/filing 各自已有 ratchet 被引用）。
- **Current-state drift verdict**：`still_missing`——无共享质量基线+机器 ratchet。
- **Acceptance criteria**：`quality_baseline.json` 含三仓五维基线（类型/覆盖率/复杂度/硬编码/死 caller）且值可复算；`quality-verify` 对当前 triplet 全绿；任一维度下调被拒（ratchet 负例测试）；新增关键函数 complexity≤10 有门可查；public contracts strict type 集合冻结；三仓套件绿。
- **Stop conditions / handoff**：下调阈值、手写基线值 → 立即停止。

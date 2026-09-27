# RED.md — ZR-1102 独立 reviewer 对抗式三仓审查（Phase 11 第二卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1102 验收套件**：glob tests/**/*zr1102* → 零命中。
- **G2 无对抗式审查组合验收**：final_ratchet（hardcode/legacy/encoding）、mutation_patrol（mutation）、ci_checkout_siblings 各自存在；无"生产 reachability + 硬编码复扫 + 测试孤岛 + 伪计数防护 + 旁路扫描"一体验收。
- **G3 真实现状（只读确认）**：scripts/ 三门扫描零命中；83 测试有 main guard；mutation_patrol.patrol 可运行。

## 既有能力（不重复建设）

- final_ratchet 扫描器；mutation_patrol.patrol（seed/samples）；CA-303 零硬编码验证；CA-205 CI 无 || true。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1102_adversarial_audit.py`（9 tests：C1 生产 reachability（CLI main + 库模块可导入被引用，无孤儿）；C2 独立复扫零命中；C3 测试孤岛检测 + 抽查收集；C4 mutation patrol + 伪计数防护；C5 无 silent-pass/无模块级 skip 无 opt-in），产品零改动。

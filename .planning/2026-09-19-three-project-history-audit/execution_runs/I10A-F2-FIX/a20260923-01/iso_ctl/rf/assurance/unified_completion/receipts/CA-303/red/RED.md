# RED.md — CA-303 架构/硬编码/代码质量终审（阶段 J 第三卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-303 验收套件**：glob tests/**/*ca303* → 零命中。
- **G2 无架构终审组合验收**：ZR-906 final_ratchet（六门：hardcode/legacy/complexity/type/coverage/encoding）、codegraph_freeze（caller targets + blocking findings）、manifest-verify 各自存在；无"hardcode/legacy/encoding + CI 无 || true + complexity + mypy 基线 + manifest/state 漂移 + caller 表面"一体验收。
- **G3 真实现状（只读确认）**：final_ratchet scanners-only 三门全绿（hardcode/legacy/encoding）；quality.yml 无 || true；mypy 69 errors == 冻结基线（独立 6s 实测）。

## 既有能力（不重复建设）

- final_ratchet.scan_hardcode/scan_legacy/scan_encoding/gate_type/gate_complexity；test_complexity_ratchet.py；codegraph_freeze.json（caller_report.targets + blocking_findings_registered）；uc.cli manifest-verify；state.json。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca303_arch_quality.py`（11 tests：C1 零硬编码/零 legacy/零编码问题；C2 CI 无 || true；C3 complexity 绿 + coverage 面；C4 mypy 冻结基线；C5 manifest/state 漂移；C6 codegraph caller 表面 + blocking findings 注册），产品零改动。

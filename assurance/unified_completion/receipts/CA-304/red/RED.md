# RED.md — CA-304 R9 分批删除与真实 rollback drill（阶段 J 第四卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-304 验收套件**：glob tests/**/*ca304* → 零命中。
- **G2 无删除门组合验收**：FC-705 legacy_close_gate（两连续 ≥24h 零 hit 窗口）纯函数存在；ZR-305 legacy migration / ZR-1003 shadow assertions / final_ratchet legacy scan / activation 各自存在；无"close-gate + legacy-hit oracle + 分批门 + rollback 往返 + 零残留"一体验收。
- **G3 真实现状（只读确认）**：scripts/ 零 legacy callers（final_ratchet scan_legacy ZERO）；legacy_close_gate 纯函数门在位；flags.py legacy_bridge_enabled 为 migration-only 排除项。

## 既有能力（不重复建设）

- legacy_close_gate.close_gate_allowed（FC-705）；daily_t2_runner legacy-hits 检查；final_ratchet.scan_legacy/scan_encoding；activation.apply_activation/rollback_activation（ZR-1003 已验证）；assertion_service.upsert_verified_assertion + normalized_meta.canonical_hash（ZR-1003 seed 模式）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca304_r9_removal.py`（11 tests：C1 close-gate 六类 fail-closed；C2 legacy-hit oracle；C3 分批门 + rollback 往返；C4 零残留；C5 三周期 rollback drill），产品零改动、零真实删除（CA-304 拥有部署）。

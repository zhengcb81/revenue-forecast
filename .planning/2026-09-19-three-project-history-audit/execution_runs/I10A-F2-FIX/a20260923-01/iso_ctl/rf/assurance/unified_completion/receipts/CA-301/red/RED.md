# RED.md — CA-301 clean checkout 独立复放（阶段 J 首卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-301 验收套件**：glob tests/**/*ca301* → 零命中。
- **G2 无 clean-checkout 复放组合验收**：ci_checkout_siblings（manifest triplet 驱动）与 uc.envfreeze（collect/freeze/verify）各自有测试（test_envfreeze 13 passed）；无"triplet 可重建 + env collect/verify + 全量 receipt/hash 重算 + 状态重放一致 + 新鲜证据门"一体验收。
- **G3 真实现状（只读确认）**：188 个 published receipts 中 **11 个 canonical mismatch**（ZR-709/802/803/804/805 的 11+12：result/base_triplet.revenue 为 7 字符短 hash，如 ac68807/1b55f6f）——receipt/hash 重算抓出真实历史缺陷（同 ZR-1004 手拼 hash 教训）。

## 既有能力（不重复建设）

- ci_checkout_siblings（FC-1101 manifest current_triplet 驱动，禁浮动 main/硬编码 pin）；uc.envfreeze collect/freeze/verify（精确相等门 + 字段漂移检测）；uc receipt canonical 算法（json.dumps sort_keys ensure_ascii=False）；CA-206 soak 窗口（新鲜证据门）。

## 结论

G1~G2 为真实缺口（`still_missing`）；G3 为 CA-301 发现并修复的真实缺陷（11 个短 hash receipt 补全 40-hex + 重签）。实施 = revenue `tests/test_ca301_clean_checkout.py`（9 tests：C1 triplet 可重建；C2 env collect/verify + 漂移；C3 全量 receipt 重算（188 全过）+ 状态 hash 确定性；C4 重放一致；C5 新鲜证据门），产品零改动。

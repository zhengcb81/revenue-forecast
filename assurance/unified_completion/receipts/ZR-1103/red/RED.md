# RED.md — ZR-1103 真实用户旅程复验（Phase 11 第三卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1103 验收套件**：glob tests/**/*zr1103* → 零命中。
- **G2 无真实旅程复验组合**：ZR-806/1004/CA-302/709 各自旅程存在；无"三 root + 已处理复用 + CN/HK/US + broker/mine + Windows 中文路径"一体验收。
- **G3 真实现状（只读确认）**：CN/HK/US 跨市场在 filing-fetch test_e2e_download（opt-in）；中文实体旅程 ZR-806/1004 已证。

## 既有能力（不重复建设）

- ZR-806 真实 T2 三 root 样本；ZR-1004 四 root 旅程；CA-302 三类旅程终验；CA-203 spy wiki 复用（LT-09）；ZR-709 紫金 journey；golden corpus broker 7。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1103_journey_reverify.py`（6 tests：C1 三 root 复验；C2 已处理复用 single-flight；C3 CN/HK/US 市场面；C4 broker/mine 链；C5 Windows 中文路径），产品零改动。

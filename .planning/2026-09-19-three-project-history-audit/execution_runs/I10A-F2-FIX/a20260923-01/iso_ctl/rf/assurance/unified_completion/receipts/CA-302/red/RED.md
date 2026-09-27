# RED.md — CA-302 三类真实用户旅程终验（阶段 J 第二卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-302 验收套件**：glob tests/**/*ca302* → 零命中。
- **G2 无三类旅程终验组合**：ZR-709（紫金 journey）、ZR-609（第二矿企）、CA-204 C4（非矿）各自存在；无"从 revenue 入口三类旅程 + receipt 链完整 + side-effect budget=0 + 无旁路/无特例"一体验收。
- **G3 机制在位（不重复建设）**：prepare_forecast draft/formal/replay（ZR-701/709）；validate_publication_receipt（ZR-705）；SourceResolver 真实 catalog 只读（ZR-806/1004）；scripts/ 零公司硬编码（此前 CA-204 C5 已证）。

## 既有能力（不重复建设）

- ZR-709 _zijin_document fixture + J1~J3；ZR-609 第二矿企链；CA-204 C3/C4 非矿引擎路径；ZR-705 receipt 门。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca302_three_journeys.py`（8 tests：C1 紫金 canary 旅程 + 缺失 fail-closed；C2 第二矿企链闭合；C3 非矿旅程；C4 receipt 链完整；C5 side-effect budget=0；C6 无旁路/无特例），产品零改动。

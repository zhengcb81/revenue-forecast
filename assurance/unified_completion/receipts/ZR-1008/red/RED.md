# RED.md — ZR-1008 source/revenue 新链 cohort cutover（阶段 I 第八卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1008 验收套件**：glob `tests/**/*zr1008*` → 零命中。
- **G2 无 cutover 组合验收**：ZR-701（prepare_forecast draft/formal 确定性 + registry 区分）、ZR-705（draft/formal swap/rehash 攻击门）、ZR-709（Zijin 用户旅程 draft 渲染/formal 重放）均存在但各自独立；无"用户旅程 + SLO + side effects 精确计数 + rollback/观察期"综合验收。
- **G3 机制在位（不重复建设）**：prepare_forecast/validate_publication_receipt/build_publication_receipt/publication_registry（链式 line hash + _set_read_only/_clear_read_only）/create_snapshot/validate_snapshot/render_markdown；test_zr709._zijin_document 可复用为 journey 输入。

## 既有能力（不重复建设）

- ZR-701 draft/formal 语义；ZR-705 门（REV-08a/b）；ZR-709 完整 Zijin journey fixture（_zijin_document + registry fixture）；conftest registry 隔离。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1008_new_chain_cutover.py`（10 tests：C1 旅程/注册/replay；C2 draft/formal 分离；C3 SLO；C4 side effects 精确计数；C5 rollback/观察期稳定性），产品零改动。

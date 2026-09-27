# ZR-803 工作单元卡（preflight）— G：chaos/property/mutation 六类故障幂等恢复

- 领取时间：2026-08-23T10:30Z；current_next=ZR-803（ZR-802 closure 推进）；锁 owner=zr803-implementer。
- 依赖：ZR-801（CA-105 吸收）、ZR-802 ✅。
- 目标：锁/中断/磁盘/篡改/顺序/时钟六类故障 × 故障后幂等恢复的旅程级矩阵；critical mutation 100% kill 门由 CA-108 套件继续持有。
- production entrypoint：source_preparation 三进程链（锁注入）、prepare_forecast/publication_registry（中断注入）、revenue_forecast CLI（磁盘）、validate_forecast_output（篡改）、create/evaluate_snapshot（乱序）、validate_document（时钟）。
- RED：grep zr803/chaos → 零命中；探针确认六类真实错误形态与两处正面行为（WAL 写锁不阻只读旅程=READ-06）。
- allowlist：新 tests/test_zr803_chaos_recovery.py + receipts/state/docs；产品代码禁改。
- AC：每类故障有结构化失败证据 + 故障后恢复断言（同身份复用/精确一次注册/无半写/原工件仍有效/正常顺序成功/干净输入不受影响）。

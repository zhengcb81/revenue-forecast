# RED.md — ZR-1002 Reader 先上线（阶段 I 第二卡，company-wiki）

## 探针（全部在当前机器实跑）

- **G1 无"reader-first 上线"综合验收**：既有测试覆盖单点（FC-202 snapshot 语义、FC-203 事务/回滚、ZR-203 rewiring、catalog_reader 只读查询、observability 延迟计算），但无**端到端 golden 对比**（激活前 store 查询 = 激活后 reader 路径输出，shadow→active 零字节漂移）+ **SLO 门**（reader 查询延迟预算）+ **rollback 路由旅程**（激活→golden→回滚→shadow 恢复→数据不删→二次回滚拒绝）+ **无 schema/data 迁移断言**（激活/回滚前后 schema 版本与行数不变）的综合套件。
- **G2 无"writer 保持原行为"断言**：无测试证明激活后 legacy writer（upsert/activation journal）不受影响。

## 既有能力（不重复建设）

- company-wiki `activation.py`（preview/apply/rollback + activation_journal + visibility_state active/shadow——FC-203 已建）；`reader.py`（ReadOnlyCatalogReader 只读协议——ZR-201/202）；`resolver.py`（只读 resolver）；`assertion_service.upsert_verified_assertion`（WU-402）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = company-wiki `tests/contract/test_zr1002_reader_first.py`（5 tests：golden/SLO/writer/rollback/无迁移），产品零改动。

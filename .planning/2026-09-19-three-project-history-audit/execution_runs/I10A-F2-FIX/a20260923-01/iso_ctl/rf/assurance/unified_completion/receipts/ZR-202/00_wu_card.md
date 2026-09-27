# ZR-202 工作单元卡（preflight）— Reader 上的 typed queries

- 领取时间：2026-08-14T11:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-202`；units.ZR-201.status=accepted + closure.next=ZR-202。
- 依赖：ZR-201（accepted ✅）。Registry 依赖列=ZR-201。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C：在 CatalogReader 上实现 typed identify/query/status/resolve/bundle/health 查询——读路径从“裸 SQL + 写能力 store”升级为类型化只读 API。ZR-201 已交付协议与工厂；本卡在其上加类型化查询层，不接线生产（ZR-203）。
2. **production entrypoint 是什么？** wiki `src/company_wiki/source_catalog/reader.py`（CatalogReader/ReadOnlyCatalogReader，本卡扩展）；参照 service.py 现有读查询语义（query_source_bundle/bundle_for_resolution/status 计数）与 resolver 的 identify/resolve 形状。
3. **哪个 current-triplet 行为是 RED？** Reader 只有裸 fetchone/fetchall；identify/query/status/resolve/bundle/health 无类型化入口；无 schema-mismatch fail-closed 检查；无 query-only 属性暴露。
4. **允许改哪些文件？** wiki `src/company_wiki/source_catalog/reader.py`（扩展）+ 新 `reader_queries.py`（如需）+ `tests/unit/test_catalog_reader_queries.py`（或扩展原测试）；revenue 侧 receipts/ZR-202/** 与 state.json。禁止：改 CatalogStore/service/resolver/CLI、接线生产调用方（ZR-203）、真实 catalog。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-203（生产只读入口重接 Reader）。本卡不重接生产；不实现锁 taxonomy（ZR-204）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-201 accepted（机器状态；closure.next=ZR-202）。
- [x] triplet 冻结：revenue `81ece1d1…` 之后的最新 closure 提交（领取时重读）；filing `83c638e…`；wiki `a46db08…`。
- [x] 参照物确认：service.py `query_source_bundle`（365）/`bundle_for_resolution`（426）/status 计数（1176-1199）；resolver identify/resolve 形状。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——无 typed query 层。
- **Acceptance criteria**：typed 方法 identify（entity 精确/候选）、query（text/kind/status 过滤）、status（计数）、resolve（handle 组装形状，只读）、bundle（SourceBundle 组装，只读）、health（schema_version+计数）；schema mismatch（未知 catalog schema_version）fail closed（明确异常，不降级）；`query_only` property 暴露且恒为 True；无任意写 SQL API（协议无 execute/commit）；全部 hermetic 测试 + wiki unit 绿。
- **Stop conditions / handoff**：接线生产、改 store/service、真实 catalog 访问 → 立即停止。

# ZR-201 工作单元卡（preflight）— CatalogReader 协议与只读连接工厂

- 领取时间：2026-08-14T10:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-201`（ZR-105 closure 后，DAG 解锁 ZR-201）。
- 依赖：ZR-101、ZR-104（均 accepted ✅）。Registry 依赖列=ZR-101,ZR-104。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 核心：真只读。ZR001-W1 反例已重放（构造不存在 DB 创建 237,568B WAL 库；OS 只读文件报写错误）——读路径必须有零写能力的 CatalogReader。
2. **production entrypoint 是什么？** wiki `src/company_wiki/source_catalog/store.py` CatalogStore（读/写一体：`_initialize` mkdir+WAL+DDL+migration+seed+commit）；service/resolver 的所有读查询都走它。
3. **哪个 current-triplet 行为是 RED？** CatalogStore 构造即写（ZR001-W1 fresh 证据）；不存在 CatalogReader 协议。
4. **允许改哪些文件？** wiki `src/company_wiki/source_catalog/reader.py`（新模块：协议+工厂+实现）+ `tests/unit/test_catalog_reader.py`（或 contract）；revenue 侧 receipts/ZR-201/** 与 state.json。禁止：改动 CatalogStore 本体、任何写路径、生产接线（接线归 ZR-203）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-202（typed queries on Reader）。本卡不重接生产调用方（ZR-203）；不实现 typed queries（ZR-202）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-105 accepted（机器状态；closure.next=ZR-201）。
- [x] triplet 冻结：revenue `93d0042f…` 之后的最新 closure 提交（领取时重读）；filing `83c638e…`；wiki `b661755…`。
- [x] RED 素材：ZR001-W1 重放证据（237,568B 创建 + readonly 写错误）为本卡验收的反面基准。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——无 CatalogReader。
- **Acceptance criteria**：`CatalogReader` protocol 声明无写 API（类型层面无 execute/commit/migrate）；只读连接工厂：`file:...?mode=ro` + `PRAGMA query_only=ON`；构造不存在的 DB → 报错且**不创建文件/目录**；OS 只读 DB 上成功打开并查询；全程无 mkdir/WAL/DDL/migration/seed/commit（测试用文件指纹+sqlite 状态断言）；wiki unit 套件绿。
- **Stop conditions / handoff**：改动 CatalogStore、触发生产写路径、真实 catalog 写 → 立即停止。

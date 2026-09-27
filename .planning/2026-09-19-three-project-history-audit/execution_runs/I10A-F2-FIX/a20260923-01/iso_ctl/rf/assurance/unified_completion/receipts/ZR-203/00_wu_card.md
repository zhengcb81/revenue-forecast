# ZR-203 工作单元卡（preflight）— 生产只读入口重接 Reader

- 领取时间：2026-08-14T12:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-203`；units.ZR-202.status=accepted + closure.next=ZR-203。
- 依赖：ZR-202（accepted ✅）。Registry 依赖列=ZR-202。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 核心收口：把全部只读生产入口从 CatalogStore 重接到 CatalogReader——修掉 ZR001-W1（读路径构造即写）与 08-12 发现 36/38（reuse-only 需要写权限/写锁）。
2. **production entrypoint 是什么？** `SourceCatalog.store` 惰性建 CatalogStore（service.py:46-49，读写共用）；CLI 只读子命令（status/query/evidence-list/sections-list/resolve/worker-status/identify）经 `get_catalog().store`；resolver 读路径。本卡给这些只读入口加 Reader 构造（service.reader + CLI read-only 路径用 `reader_from`），写入口保持 Store。
3. **哪个 current-triplet 行为是 RED？** 只读入口构造 CatalogStore（ZR001-W1 证据）；无 caller gate 证明只读入口 writer initializer=0。
4. **允许改哪些文件？** wiki `src/company_wiki/source_catalog/{service.py,cli.py,resolver.py}`（只读路径重接，最小 diff）+ 新测试 `tests/contract/test_zr203_reader_rewire.py`（或 unit）+ revenue 侧 receipts/ZR-203/** 与 state.json。禁止：改 CatalogStore 写路径语义、改 worker/写命令、真实 catalog 写。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-204/206/301/401（依赖 ZR-203）。本卡不解决锁 taxonomy/retry（ZR-204/205）、不解决 SLO（ZR-206）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-202 accepted（机器状态；closure.next=ZR-203）。
- [x] triplet 冻结：revenue `3ebafb25…` 之后的最新 closure 提交（领取时重读）；filing `83c638e…`；wiki `0bc9ac70…`。
- [x] 重接面清单（预研）：service.py `status`(183)/`query`(465)/`query_source_bundle`(365)/`bundle_for_resolution`(426)/`scan_health`(1210 对应 store)；CLI 只读子命令 status/query/evidence-list/sections-list/resolve/worker-status/identify；resolver read path。写入口（scan/normalize/summarize/worker/close-gap 等）保持 Store。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——只读入口未重接。
- **Acceptance criteria**：`SourceCatalog.reader` 惰性构造 ReadOnlyCatalogReader；全部只读生产入口经 Reader（CodeGraph production caller gate：只读入口 CatalogStore 构造 caller=0）；Writer initializer 仅写入口可达；golden 等价——同一 temp catalog 上 Reader 结果与 Store 结果逐字段相等（status/query/bundle/resolve）；wiki unit+contract 套件绿；T1 复用场景在 ZR-102 runner 上仍绿（reuse-only 不再触发写初始化——可用 runner 复跑）。
- **Stop conditions / handoff**：写入口被错接 Reader、真实 catalog 写、行为语义变化无 golden 对照 → 立即停止。

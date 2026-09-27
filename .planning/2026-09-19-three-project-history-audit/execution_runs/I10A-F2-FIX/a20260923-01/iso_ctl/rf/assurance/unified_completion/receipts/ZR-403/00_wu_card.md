# ZR-403 工作单元卡（preflight）— 泛化 document/location dedupe 与 resolver，分离全局 canonical 与本次 eligible location

- 领取时间：2026-08-18T20:20Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-403`；units.ZR-402.status=accepted + closure.next=ZR-403；锁 ZR-403（owner=zr403-implementer）。
- 依赖：ZR-402（accepted ✅）。Registry 依赖列=ZR-402。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D dedupe/resolver 泛化验收。legacy FC-303/503（scanner/admission seam、path/identity 候选资产）implemented_not_independently_verified → 本卡独立验收。现有机制：content-addressed document_id（同内容跨根=同一 document，多 location）；`service._annotate_locations` 读时派生全局 canonical（健康过滤 active+original_primary+source_id → 按 (root_priority, root_id, relative_path, location_id) 排序取首）；`resolver.resolve()` 本次 eligible（policy=reusable_root_kinds → 健康=active/rejections/capture_ready → canonical 位置）；`_pick_latest` (published_date, provider_document_id, source_id) 稳定 tie-break。
2. **production entrypoint 是什么？** 验收侧：`tests/contract/test_zr403_dedupe_resolver_generalization.py`（新增）；产品零改动预期（机制已实现）。生产入口：`scanner.scan_catalog`（跨根 upsert+priority 合并）、`service._annotate_locations`（canonical 派生）、`resolver.SourceResolver.resolve`（eligible 链）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 四上下文矩阵缺 future_lake**：FC-603 跨根去重矩阵只覆盖 company_raw/dayu/Dropbox 三根；future_lake（adapter 化未来根）未进入 dedupe/canonical 矩阵（registry 证据="companies/dayu/Dropbox/future_lake 同算法"）。
   - **G2 health→priority 顺序链未钉死**：无测试钉死"更高优先级根上的不健康位置（retired/.rejections）不得成为 canonical，健康低优先级副本获胜"（_annotate_locations 结构上 health 先于 priority，但无 killer；rejections 测试只测单位置拒绝，不测跨根优先级竞争）。
   - **G3 读取不写 canonical 未显式钉死**：无测试断言 canonical 是纯读时派生（locations 表无 is_canonical 列）且 resolve() 前后 catalog 文件字节不变（reader 侧 query_only 结构性保证，dedupe 语义层无显式 pin）。
   - **G4 配置顺序随机化只测了 2 排列**：FC-603 用 forward/reversed 两排列；无 N 次随机 shuffle（含四根）→ canonical/duplicate 组不变的 property。
   - 既有已钉死（不重复造）：policy 门（reusable_root_kinds 增删根 kind 的行为，test_source_catalog_reusable_roots）、priority>字母序（fc603_ex04_priority_beats_alphabetical）、exact 选择/amended 规则/artifact 共享（FC-603）、100 次 INSERT 顺序确定（determinism）。
4. **允许改哪些文件？** company-wiki 新增 `tests/contract/test_zr403_dedupe_resolver_generalization.py`（如发现真实行为缺口则最小改 service.py/resolver.py，逐条记录）；revenue 侧 receipts/ZR-403/** 与 state.json。禁止：真实 catalog 写、下载、v1 scanner 重写。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-404~409。本卡不做：dedupe 算法变更（机制已实现）、语义重复（dayu 多实体语义档移交 ZR-501/502）、下载授权（ZR-407）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-402 accepted（机器状态；closure.next=ZR-403）。
- [x] triplet 冻结（领取时重读）：revenue `7d111999…`（ZR-402 closure commit）、filing `df66796…`、wiki `57cd72e…`。
- [x] 现状代码事实：`_annotate_locations`（service.py:607-649，健康过滤→(root_priority, root_id, relative_path, location_id) 排序，canonical=ordered[0]，读时派生不落库）；`resolve()`（resolver.py:680-966，policy=reusable_root_ids→canonical 位置过滤→_handle→capture_ready）；`_pick_latest`（published_date/provider_document_id/source_id）；`_handle` canonical=next(is_canonical+active+original_primary+非rejections)；scanner document_id=content-addressed（跨根同内容=同 document，priority 合并 `root.priority <= existing metadata_priority`）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（验收测试）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——机制已实现；四证据钉死缺失（G1 future_lake 矩阵、G2 health→priority killer、G3 读不写显式 pin、G4 N-shuffle property）。
- **Acceptance criteria**：
  - **C1 四上下文同算法（杀 G1）**：同字节放 company_raw/dayu/Dropbox/future_lake（sidecar adapter 未来根）四根 → 恰一 document、四 active original_primary location、canonical=priority 最低根（含 future_lake 胜出/落败两个方向）。
  - **C2 health→priority 链（杀 G2）**：更高优先级根位置不健康（retired 或 .rejections 路径）+ 低优先级根健康副本 → canonical=健康低优先级位置；duplicate 组完整；resolver 仍 REUSED_EXACT 且 canonical_path 指向健康副本。
  - **C3 读取不写 canonical（杀 G3）**：locations 表 schema 无 is_canonical 列（PRAGMA table_info 断言）——canonical 纯读时派生；resolve()+查询前后 catalog DB 文件 sha256 不变。
  - **C4 配置顺序随机化稳定（杀 G4）**：≥10 次随机 shuffle 四根配置顺序分别建独立 catalog 扫描 → canonical (root_id, relative_path)、duplicate_group_id、exact_duplicate_location_count、document_id 集合全部一致。
  - hermetic 全绿；wiki unit/contract 无回归；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、需要改 dedupe 语义 → 立即停止并登记。

## Annex：canonical 选择矩阵

| 场景 | 位置分布 | 预期 canonical |
|---|---|---|
| 四根同字节（p10/p20/p30/p40） | 全健康 | p10 根位置 |
| future_lake p5 vs company_raw p10 | 全健康 | future_lake |
| company_raw p10 unhealthy(retired) + dayu p20 healthy | 混合 | dayu（health 先于 priority） |
| dropbox p10 .rejections + future_lake p40 healthy | 混合 | future_lake |
| 任意 shuffle 后同上各行 | — | 不变（稳定） |

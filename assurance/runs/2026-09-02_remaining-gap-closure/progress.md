# 剩余缺口关闭实施进度

> 起始状态：2026-09-02 全面审查发现 12 项缺口（3 项已修复、9 项待实施）。
> 每完成一个 GP，更新本页对应行。

## 状态总览

- **起点**：117/117 accepted（机器真源 state.json）；三仓 CI ALL GREEN
- **当前阶段**：GP-001 完成，开始 GP-002（v2 scanner 生产切入）
- **锁**：无（无活动 lease）

## GP 进度表

| GP | 内容 | 状态 | 证据 |
|---|---|---|---|
| A-1 | llm_summarizer 空 source_sha | ✅ 完成（afe5eb1） | worker 36 passed |
| A-2 | artifact validator 放行空 sha | ✅ 完成（afe5eb1） | artifact 30 passed |
| A-3 | policy hash 漂移 | ✅ 完成（生产 CAS） | envelope=export 匹配 |
| GP-001 | A 类三仓回归验证 | ✅ 完成（wiki 4e6a523） | 三仓全绿：wiki 2630p/0f、revenue 945p、filing 352p |
| GP-002 | v2 scanner 生产切入 | 未开始 | — |
| GP-003 | worker privacy 过滤 | 未开始 | — |
| GP-004 | receipt 重签发 | 未开始 | — |
| GP-005 | scenario 证据回填 | 未开始 | — |
| GP-006 | 真实 roots E2E 进 CI | 未开始 | — |
| GP-007 | privacy_class 3.0 config | 未开始 | — |
| GP-008 | legacy 观测起点注册 | 未开始 | — |
| GP-009 | 动态审核调度注册 | 未开始 | — |
| GP-010 | 研报 cutover 授权申请 | 未开始 | — |

## 变更记录

- 2026-09-02：计划创建；A-1/A-2/A-3 已修复并 push（wiki afe5eb1）。

- **2026-09-02 GP-001 中期**：A 类修复三仓回归。
  - revenue：945 passed（除 pre-existing manifest 陈旧 1 项：contract filing hash 绑 current_triplet 592fae61，本地 HEAD 已推进——正确提示需 GP-007 刷新 manifest）；ZR-901 8 passed（CRLF 规范化修复后）。
  - filing：352 passed + 78 subtests（全 hermetic）。
  - wiki：修复 summarizer.py + section_extractor.py 空 source_sha（SELECT join sources + INSERT 绑定）+ fc906a 测试契约改读 SQL 列；fc906a 4 passed + 相关套件 93 passed。全量重跑中。
  - 修复 commit：revenue 8943f33（CRLF 测试规范化）；wiki 0eddb35（summarizer/section_extractor/fc906a）。

- **2026-09-02 GP-001 完成**：A 类三仓回归全绿。
  - revenue：945 passed（manifest 陈旧 1 项为 pre-existing，归 GP-007 刷新）；filing：352 passed；**wiki：2630 passed / 7 skipped / 0 failed**（11m32s）。
  - wiki 全量遗留 4 failed 全部修复（commit 4e6a523，已 push master）：
    1. fc1203 `_summary_handle` 改从 artifacts SQL 列读 schema_version/source_sha256（同 fc906a 模式）——extractive summary 产物通过 A-2 fail-closed 绑定门；
    2. observability.REASONS + STAGES_BY_REASON 注册 `artifact_source_sha_missing`（A-2 新拒绝码，taxonomy 1.1 additive）；
    3. CONFIG-DBX-02 同步 ZR-409：directory-kind 白名单 {dropbox_stock} → {dropbox_stock, future_lake}（既有登记漂移 ZR907-FIND-001 / findings L158；fixture 改捕获第 3 个目录根）。
  - 检查点：A-1/A-2 修复经 2630 测试全量验证无回归；A-3 生产快照已 MATCH（envelope=export）。
  - GP-001 正式 close。

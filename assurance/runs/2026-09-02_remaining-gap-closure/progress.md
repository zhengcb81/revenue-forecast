# 剩余缺口关闭实施进度

> 起始状态：2026-09-02 全面审查发现 12 项缺口（3 项已修复、9 项待实施）。
> 每完成一个 GP，更新本页对应行。

## 状态总览

- **起点**：117/117 accepted（机器真源 state.json）；三仓 CI ALL GREEN
- **当前阶段**：计划制定完成，待开始实施 GP-001
- **锁**：无（无活动 lease）

## GP 进度表

| GP | 内容 | 状态 | 证据 |
|---|---|---|---|
| A-1 | llm_summarizer 空 source_sha | ✅ 完成（afe5eb1） | worker 36 passed |
| A-2 | artifact validator 放行空 sha | ✅ 完成（afe5eb1） | artifact 30 passed |
| A-3 | policy hash 漂移 | ✅ 完成（生产 CAS） | envelope=export 匹配 |
| GP-001 | A 类三仓回归验证 | 未开始 | — |
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

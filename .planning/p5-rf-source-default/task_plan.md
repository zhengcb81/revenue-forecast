# task_plan — P5-RF 默认来源迁至 SourceRef v2

目标：RF `prepare_source` 默认走 v2（一律 `--source-ref-v2` + 必需 catalog config，缺配置在
外发前具名失败）；legacy 解析器仅作为隔离的历史离线 fixture 入口保留；`--source-reader-v2`
留为兼容 no-op。不接预测计算/assurance/跨仓。

## 事实快照（2026-10-05）
- 分支 `codex/p5-rf-source-default`，baseline = origin/main `8a153f33`。
- 唯一生产 legacy 调用者：`scripts/source_preparation.py::_prepare_legacy_source`
  （`company_wiki_source.select_artifact_roles/verify_artifact_reads`），入口 `prepare_source`
  默认 `source_reader_v2=False`；CLI flag opt-in（scripts/source_preparation.py:280,310）。
- v2 能力已在 main：`open_source_version_v2`（company_wiki_source_reader_v2.py:318）、
  `build_revenue_source_record_from_verified_read`（company_wiki_source_v2.py）、
  三仓 E2E（tests/test_source_ref_v2_three_repo_e2e.py）。
- 复杂度 ratchet 冻结 `source_preparation.py: max 17`（tools/tests/test_complexity_ratchet.py:41）。

## 步骤
1. [x] 建独占 worktree/分支，读卡与总计划
2. [x] 定位活动调用者（findings.md 调用者清单）
3. [x] 新增 RED：tests/test_p5_source_default_v2.py（默认无 flag 走 v2、缺配置外发前具名失败、
       legacy 正文读取 tripwire、artifact_read 空语义、重复 prepare 去重）
4. [x] 实现默认翻转：prepare_source v2-only；CLI `--source-reader-v2` no-op；help 文案同步
5. [x] 迁移受影响既有测试到新默认/隔离 legacy fixture：
       test_source_preparation.py、test_fc1002、test_fc1003、test_fc1004、test_zr709、
       test_zr802、test_zr803、test_zr804、test_zr805、test_preparation_e2e_success、
       e2e/run_cross_repo_chain_e2e.py（CODE_PINS + argv + S2/S3 断言）、SKILL.md
6. [x] 新增 tests/test_p5_source_default_cli_e2e.py（真实三仓 CLI E2E，env-gated，本机执行）
7. [x] 相关节点发布门：ratchet、ruff、单 owner guard、相关 pytest 包
8. [x] 提交 + handoff（docs/implementation/handoffs/P5-RF/）

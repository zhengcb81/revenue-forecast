# progress — P5-RF 默认来源迁移

## 状态：实现完成，已提交（详见 docs/implementation/handoffs/P5-RF/）

- [x] worktree cwp-lanes-20261005/rf-source-v2，分支 codex/p5-rf-source-default，基线 8a153f33
- [x] prepare_source 默认 v2-only：--source-ref-v2 必传、company_wiki_catalog_config 必需
      （缺/坏配置在外发前具名失败）、legacy 解析器 _prepare_legacy_source 隔离为
      历史离线 fixture 入口、--source-reader-v2 兼容 no-op
- [x] TDD：tests/test_p5_source_default_v2.py RED(8 failed/1 passed) → GREEN(9/9)
- [x] 验收 E2E：tests/test_p5_source_default_cli_e2e.py（公共 CLI 无 flag、
      IsolatedWiki 配方、删 derived 仍成功、坏 raw fail-closed 后自愈）2/2 实跑绿
      （需 FF_V2_CODE_ROOT/CWP_V2_CODE_ROOT，CI pinned FF 无 --source-ref-v2 → skip+hold）
- [x] 级联迁移 15+ 文件（fc904/905b/1002/1003/1004、zr701/709/802/803/804/805、
      preparation_e2e、source_preparation、isolated_lake fixture 升级、message_pins CW_DIR、SKILL.md）
- [x] 门：ruff 全绿、complexity ratchet/单owner/skill-doc 9/9、98/98 相关回归
- [x] 大扫描失败归因：lanes 布局/本地环境/CWP HEAD API 漂移/live-data 既有失败
      （关键文件 baseline 双侧对照，零 P5 回归）
- [x] HANDOFF.md + handoff.json

## Hold（详见 handoff）
- pinned FF 89c8bdb 无 --source-ref-v2 → CI real-roots 链路 E2E 需 MAIN 重绑 compatibility
- CWP HEAD 1cfec10 删 evaluate_review → message_pins 单测本地漂移（pinned wiki a640400 有）
- e2e/run_cross_repo_chain_e2e.py S1-S6 legacy 场景 + CODE_PINS 标 historical fixture
- 生产 CWP derived(2.826GB) 删除仍归 MAIN S5

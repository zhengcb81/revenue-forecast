# Task Plan: G3-RF-ASSURANCE 历史质量工具与技能包装职责收敛

## Goal

收敛三处真实遗留：`uc.quality` 委托当前 mypy 入口且历史阈值退休不再被当数字资格门；`uc.manifest` 默认改 SHA+size 校验、mtime 降诊断；`sync_installations` 按实际技能 runtime 依赖划定包装职责——全部以 TDD 绿灯交付并产出 MAIN 交接包。

## Next Step

Phase 7 收尾：commit 后清理 scratch、推分支；MAIN 按 HANDOFF 接线表处理边界外 caller 与三安装副本。

## Current Phase

Phase 7

## Phases

### Phase 1: 探索与结构盘点

- [x] 读本卡与 quality/manifest/cli/sync_installations 源码及测试
- [x] CodeGraph/grep 列出实际入口、返回值、caller、写副作用
- [x] 判定 legacy freeze/verify/strict_targets/compute_baseline 中哪些是历史解码、哪些是真当前用户工具
- [x] 记录到 findings.md
- **Status:** complete

### Phase 2: RED 测试

- [x] 委托当前mypy入口的workflow
- [x] coverage门退休
- [x] 邻仓不在时 not_available/范围
- [x] 干净checkout同SHA/size不同mtime通过
- [x] 同size换字节失败
- [x] 进程return2但无FAILED字样仍失败
- [x] 独立安装包不带repo tools却能运行真实技能入口
- **Status:** complete

### Phase 3: quality 层改报告

- [x] 委托 tools/pre_push_gate.py 的类型目标入口
- [x] 历史阈值/coverage/复杂度改为报告字段，不作数字资格门
- [x] 旧字段保持可解码导入API
- [x] 无邻仓报告 not_available/范围，不造0
- [x] 显式用户输入不可读/损坏明确失败
- **Status:** complete

### Phase 4: manifest 默认 SHA+size

- [x] verify(check_mtime=False) 默认；mtime 诊断或显式 strict
- [x] 库/CLI/current test 语义统一
- [x] 缺文件/路径逃逸/同size换字节仍非零
- [x] 只读，不 build/update 自动修复
- **Status:** complete

### Phase 5: 包装职责划定

- [x] 按技能入口 runtime 闭包划定 installable_files
- [x] check 默认不写；显式 sync 定点更新、保留未知/config/output
- [x] 兼容旧 caller；installable/manifest/installation_diff/sync_installation
- [x] 仓内工程测试留仓内
- **Status:** complete

### Phase 6: 集中测试与 E2E

- [x] 单元/集成/E2E 集中跑
- [x] 责任测试包 + pre_push_gate 一次
- [x] Ruff 核实际改动
- **Status:** complete

### Phase 7: 交接交付

- [x] HANDOFF.md / handoff.json / findings / progress
- [x] 正常 commit，推自己分支
- **Status:** in_progress

## Key Questions

1. `uc.quality` 哪些函数是当前真实 caller 使用的？哪些只被历史测试解码？
2. 类型目标（mypy）当前的权威入口是 `tools/pre_push_gate.py` 的哪段？
3. `sync_installations` 的 installable_files 当前集合与真实技能 runtime 闭包差集是什么？
4. manifest verify 的 CLI/库调用点分别在哪，默认值如何统一？

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| 施工仓用独立 worktree `C:/Users/郑曾波/Projects/_g3/RF-ASSURANCE/revenue-forecast` | 卡要求独占工作目录，不动原仓 owner 三日志 |
| 计划文件放交付路径 `docs/implementation/g3-rf-assurance/` | 卡明确交付清单即该路径 |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes

- 禁止写原仓 `assurance/runs/*`；禁止改 pre_push_gate/workflow/hook/G2工具/audit_review/冻结control。
- 全离线，模型/下载/生产写 0；scratch 根 `.planning/g3-rf-assurance/scratch`，finally 恢复。

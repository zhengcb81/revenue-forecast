# 计划交付清单

> 生成时间：2026-08-13T07:03:55+01:00  
> 计划状态：编制完成；产品实施未开始。  
> 并发所有权：本目录由本任务独占；旧计划和三个产品仓库只读。  
> 自身说明：本清单不记录自己的 hash，避免自引用；下表 12 个内容文件在生成本清单后不得再静默修改。

## 1. 观察到的仓库状态

这只是清单生成时的观察值，不是未来实施基线。实施必须从 ZR-001 重新冻结。

| 仓库 | HEAD | 备注 |
|---|---|---|
| revenue-forecast | `ac6ac35726c33d61499079c6dbe12b70ccab2e8c` | 编制期间从 `5f76fcf...` 漂移；存在其他程序的 untracked assurance/audit/closure-gate 文件，本任务未触碰 |
| filing-fetch | `83c638e76e40890262746cdf02b6df495dcb4031` | 只读审查；本任务无改动 |
| company-wiki | `d17d8b82e8d650b02693b343f7d87ca5fdf53e99` | 有用户/环境侧 dirty files；本任务无改动 |

## 2. 内容文件 hash

| 文件 | 字节 | SHA-256 |
|---|---:|---|
| `architecture_target.md` | 12,630 | `288995a9b9e4c2f6848fd28d35d6fc9297248f5fc674f18a61dc2ac79de34f6b` |
| `dynamic_assurance_plan.md` | 7,818 | `81b8fec2a40b0142b31e42bd5ada36f503336d97963fa5c9ecdd88746d036b2e` |
| `findings.md` | 18,663 | `09ebcdc74e8bed03f25033033063ef129690e26319686ce07106ac2066f5da19` |
| `implementation_runbook.md` | 9,152 | `b20a8b886261118a0b1449809f63db8de4f57f6099061115c9af8761c95ba132` |
| `legacy_plan_disposition.md` | 6,135 | `dedf73e1f325af84a19cb6f0791bc2bc772503ea1a4438eb9a966820c88fec8a` |
| `migration_rollout_plan.md` | 8,375 | `e58986d6a5a87b47dc8cf250a94d2ec3d17c26a404a66962ad05f657339fbde9` |
| `plan_self_audit.md` | 11,817 | `035b0ab64b959011a6229add9ef093d3082558def1c03ce8f3fe1cbfccadf91e` |
| `progress.md` | 4,912 | `88a5e745855e346fd5f9eec86c09b66afadb6a867d0c76c18d57b1337bd56a98` |
| `scenario_matrix.md` | 15,796 | `e08cbe4e93b933bd01bc758dcef5aeee194417bde0d23d05ea0bc011e03cac8a` |
| `task_plan.md` | 26,407 | `0289eff42396659941650373c30cb0e6183357cb88732441b83f49b862141639` |
| `traceability_matrix.md` | 9,309 | `c04c49846d8cf8a8fd50c52439b199cfd005b3bf458051b31c7431eea55a309b` |
| `work_unit_registry.md` | 20,435 | `72c70eb6df9bf9cd04e8a9e42ad795477da9c28f30db291d7b8d1dda3d5de709` |

## 3. 继承资产冻结值

| 旧计划文件 | SHA-256 | 用法 |
|---|---|---|
| `2026-08-09_full_completion_assurance_plan/scenario_matrix.md` | `21e9201296aa048bd61e1125525a0eadb8ac1deb5bed76a641f05b3099f1d3c5` | 95 个旧场景继续 mandatory |
| `implementation_runbook.md` | `faae79f3afebc92591f16674df4e2e3e146d3b58b18047c38af4e85aeaf2ecff` | 治理思路来源；不继承完成状态 |
| `dynamic_assurance_plan.md` | `5c14d0b8f729f6de89b00b13e473a58310233d1e3377359a0560c9a73aec8fd4` | 动态审核来源；由本计划扩展 |
| `architecture_target.md` | `49c2f6fa615987e2db08306bd91c92bed8dc9a7565b9e204abeae3d2ff8d7bd5` | 三仓边界来源；由本计划细化 |

## 4. 结构验证结果

- 计划编制 P0、P1、P2：全部 `completed`。
- 产品实施 Phase 0～11：全部 `pending`。
- ZR 工作单元：92 个定义，92 个唯一；精确引用均有定义；无自依赖；实施状态全部 pending。
- 新场景：102 个定义，102 个唯一；与冻结旧 95 项合计 197 个 mandatory 场景。
- Markdown：本地相对链接、标题重复、零字节、临时/锁文件和关键表格行检查通过。
- 旧场景来源 SHA-256：与冻结值一致。
- 产品变更：本任务没有修改代码、配置、数据库、索引、测试、CI、旧计划或其他程序文件。

## 5. 交接规则

1. 开始实施前先重算本表 12 个内容文件 hash；任一不符就先审查 plan drift。
2. 不得直接从 Phase 1 或某个“看起来简单”的修复开始；第一张卡必须是 ZR-001。
3. 不能把编制期 HEAD 当作 implementation triplet；当前代码仍在变化。
4. 不能因新提交看似修复缺陷就删除场景；应在当前用户旅程上证明后标 `already_satisfied`。
5. 旧计划由其 owner 更新；本计划只通过 `legacy_plan_disposition.md` 提供只读状态建议，避免并发覆盖。
6. 任一 required 场景 skipped/blocked、证据过期、receipt 自签或 hash 漂移，整体状态保持未完成。

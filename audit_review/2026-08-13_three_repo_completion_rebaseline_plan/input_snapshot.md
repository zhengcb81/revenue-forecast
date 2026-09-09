# 只读输入计划快照

> 冻结时间：2026-08-13 本次审计。  
> 用途：证明本计划审查的是哪些具体版本，并检测其他 planning-with-files 程序后续改动。输入目录仍归原 owner，本任务不写。若任一 hash 漂移，未来实施先走 CA-001 plan-drift，不能静默混用。

## `2026-08-09_full_completion_assurance_plan`

| 相对文件 | bytes | SHA-256 | mtime |
|---|---:|---|---|
| `architecture_target.md` | 5525 | `49c2f6fa615987e2db08306bd91c92bed8dc9a7565b9e204abeae3d2ff8d7bd5` | 2026-08-09 21:50:49 |
| `code_quality_plan.md` | 4264 | `14cb5786cebc688f3792a7154f15ffeee06695a202ea5c7a3e921c165edad01e` | 2026-08-09 22:09:46 |
| `command_registry_plan.md` | 4278 | `69c57dce9f401044a92298cd76c2c12cf8ced526466f7f3e95d938c9edd549bc` | 2026-08-09 22:07:05 |
| `dynamic_assurance_plan.md` | 4293 | `5c14d0b8f729f6de89b00b13e473a58310233d1e3377359a0560c9a73aec8fd4` | 2026-08-09 22:09:46 |
| `execution_matrix.md` | 8998 | `1fe5ccf7ca7c044b761738d83af5d33fa7f8922923121ec78a0127422ddfd005` | 2026-08-09 22:10:09 |
| `fc_904_change_contract.md` | 3807 | `6e45fe704a84f82088e32fe160498d2f091904a9e746f5405935da0f9a400e11` | 2026-08-11 09:39:37 |
| `fc_906_preflight_blocker.md` | 5341 | `b8fef4df25696f85e8e312e629cc2c170858a37ab672a49c98e60df9ffe69a77` | 2026-08-11 21:46:24 |
| `fc_execution_packet_template.md` | 5089 | `938d0534611d1c1495a25bf1062f29ae167f94a313c83c537353a64d4d54ac91` | 2026-08-09 22:09:46 |
| `findings.md` | 90297 | `c87af463342e7e9ae22438b621381e8945c200d15ecae2281a0f871eecaddc02` | 2026-08-13 06:18:00 |
| `implementation_runbook.md` | 9880 | `faae79f3afebc92591f16674df4e2e3e146d3b58b18047c38af4e85aeaf2ecff` | 2026-08-09 22:04:36 |
| `independent_review_protocol.md` | 5150 | `8c986a4f733eb48b6e68a6b072432b8b07ecb7a8b22aa9b545cd045bb955e76c` | 2026-08-09 22:07:05 |
| `legacy_plan_disposition.md` | 11898 | `8891f4ab6eaa7eaa3953204e09d5422149eb8a442df6743b107cc5663052ae04` | 2026-08-09 22:32:40 |
| `plan_self_audit.md` | 2068 | `c0f937cadf2a92a771b6c7c34613f12ca3dddcce31d409bc9f1cf50f8cf586ae` | 2026-08-09 22:25:16 |
| `progress.md` | 7946 | `adbef79e54214c1442d2ff2db5b122ea00b77e8c8799137131a24a05bee4cd5b` | 2026-08-13 04:48:45 |
| `scenario_matrix.md` | 14380 | `21e9201296aa048bd61e1125525a0eadb8ac1deb5bed76a641f05b3099f1d3c5` | 2026-08-09 22:03:53 |
| `task_plan.md` | 43081 | `6214a36b2321336e004301db16902d25771b1f7927bfafac270d83076cfd1a09` | 2026-08-13 04:32:01 |
| `work_unit_registry.md` | 24374 | `1b5f87e7a79b00e3a12f9bc7255c6379f43013b56b88fa3d7276edb9e55e5341` | 2026-08-13 07:02:27 |

汇总：17 files，250,669 bytes。最新文件为 `work_unit_registry.md`，说明旧目录在本次审计前仍有其他程序写入；这正是本任务使用新目录的原因。

## `2026-08-13_zijin_data_lake_remediation_plan`

| 相对文件 | bytes | SHA-256 | mtime |
|---|---:|---|---|
| `architecture_target.md` | 12630 | `288995a9b9e4c2f6848fd28d35d6fc9297248f5fc674f18a61dc2ac79de34f6b` | 2026-08-13 06:40:30 |
| `dynamic_assurance_plan.md` | 7818 | `81b8fec2a40b0142b31e42bd5ada36f503336d97963fa5c9ecdd88746d036b2e` | 2026-08-13 06:51:04 |
| `findings.md` | 18663 | `09ebcdc74e8bed03f25033033063ef129690e26319686ce07106ac2066f5da19` | 2026-08-13 07:01:42 |
| `implementation_runbook.md` | 9152 | `b20a8b886261118a0b1449809f63db8de4f57f6099061115c9af8761c95ba132` | 2026-08-13 06:40:31 |
| `legacy_plan_disposition.md` | 6135 | `dedf73e1f325af84a19cb6f0791bc2bc772503ea1a4438eb9a966820c88fec8a` | 2026-08-13 06:53:28 |
| `migration_rollout_plan.md` | 8375 | `e58986d6a5a87b47dc8cf250a94d2ec3d17c26a404a66962ad05f657339fbde9` | 2026-08-13 06:53:27 |
| `PLAN_MANIFEST.md` | 4276 | `209114007a1ceff1acc72860ca2ed8b3c00d3516cc7aa96ee05183055522bf60` | 2026-08-13 07:04:33 |
| `plan_self_audit.md` | 11817 | `035b0ab64b959011a6229add9ef093d3082558def1c03ce8f3fe1cbfccadf91e` | 2026-08-13 07:01:41 |
| `progress.md` | 4912 | `88a5e745855e346fd5f9eec86c09b66afadb6a867d0c76c18d57b1337bd56a98` | 2026-08-13 07:03:40 |
| `scenario_matrix.md` | 15796 | `e08cbe4e93b933bd01bc758dcef5aeee194417bde0d23d05ea0bc011e03cac8a` | 2026-08-13 06:47:19 |
| `task_plan.md` | 26407 | `0289eff42396659941650373c30cb0e6183357cb88732441b83f49b862141639` | 2026-08-13 07:02:57 |
| `traceability_matrix.md` | 9309 | `c04c49846d8cf8a8fd50c52439b199cfd005b3bf458051b31c7431eea55a309b` | 2026-08-13 06:51:03 |
| `work_unit_registry.md` | 20435 | `72c70eb6df9bf9cd04e8a9e42ad795477da9c28f30db291d7b8d1dda3d5de709` | 2026-08-13 06:55:19 |

汇总：13 files，155,725 bytes。本文只把其中架构、92个ZR、102场景和弱模型手册作为冻结annex；其他文件是审查输入，不形成第二个状态入口。

## 输入漂移处理

1. 开始任何实施前重新hash全部30个文件。
2. 若旧FCAP漂移，只读比较变化，更新CA-004 disposition候选；禁止覆盖。
3. 若冻结annex四个权威文件漂移，停止领取，独立review变更是否扩大/缩小目标，并更新新manifest版本。
4. 旧95场景或新102场景hash变化时，不得自动删除/替换场景。
5. 本快照不代表旧文件可以删除；历史证据一直保留。

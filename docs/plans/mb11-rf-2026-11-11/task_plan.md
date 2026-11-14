# RF B37 差额接收与边界改造

> **状态对齐（RF-PLAN-WORKTREE-CLOSEOUT，2026-11-14）**：canonical 状态入口是根 [PLANNING_STATUS.md](../../../PLANNING_STATUS.md)。本卡 **MERGED**：`codex/mb11-rf`（bf314bfb）是 main 祖先；handoff.md §9（ROOT 并线推送 origin/main=6b045b76）为最终状态，其 §7「main 未合并」为过时段落。

## 目标

在 RF 自己的 codex/mb11-rf 工区，把 B37 compare/scope/publication 的最小 19 路径合同差额接到当前 main，保留现有 durable job、concurrency/recovery、D4 source port 与报告入册行为。严禁把旧 release 整树覆盖到 main。

## 当前状态

- 基线：b005a179280ee19695578bdba9427b4dd44cdd73
- 参考候选：28d646d306e8f0b5f90d402e204676cf97d2b5a1
- 独立工区：C:/Users/郑曾波/Projects/mb11-rf
- 已确认全候选会触及 628 个文件；本次范围严格限制到卡片指定 19 个产品路径与当前合同测试。B37 的 19 个产品路径中 4 个已同 blob、9 个有差异、6 个主线缺失。
- compare owner模块与CLI已由 `e060a8607` 提交并进入RF `main`；main上的PWF进度记录为 `33d880826`。其52项聚焦测试、Ruff/mypy和独立审查已通过。
- 新增的部署/来源测试已独立复核通过，修正锁文件断言后MB-RF相关组合为171 passed、1 skipped；提交 `058be4fd6` 已推送并进入 RF `main` / `origin/main`。
- scope/subject/verified-compare 已通过公开 DTO / reader 实现并接入；整卡复核的两项历史基线失败另行记录，不影响产品提交是否入线。
- B2 已完成公开 DTO/reader 重做、独审、集成测试、主线快进与远端推送；最终状态见本文件末尾 ROOT 并线收尾。

## 步骤

1. A0：已完成compare合同RED、目标写集合核对与compare模块边界确认。scope合同仍为待重构差额，不能由候选测试通过率代替架构审查。
2. B1：compare纯模块/CLI已提交并入main；publication-source现行能力已满足候选测试，不需生产代码改动。部署和来源回归已独立审查通过，作为下一独立测试提交推送。
3. B2（待做）：重新设计scope/subject/verified-compare接线。先定义跨市场、不同会计准则/财年、多个分部与来源缺失时的公开DTO；只经ReportCatalog公开方法读数，不导入其他模块私有符号、不直接访问catalog私有方法。管理CLI必须保留已发布的 `import-rf-job`。
4. B2 TDD/C：覆盖多准则、多财年边界、多分部、含/不含可选证据、显式scope冲突与幂等；移除无配置依据的IFRS/12-31/单分部特判及固定结果/行数门槛。owner的实际资源预算仍可执行，记录/返回必须完整。
5. 每个可独立并入的范围由独立只读审查检查源码与新增测试对应最终HEAD；受影响回归通过后按该提交并入RF main并推送，更新本卡及总控PWF。真实SW/CWP组合仍由ROOT公开接口验收，不能在RF卡中伪报。

## 不在范围内

候选其余 609 条路径、118 个研究材料、旧 job facade 全树、重新跑公司预测、收费调用、修改 CWP/StockWiki/Dashboard。


## ROOT 并线收尾（2026-11-13）

- [x] RF B2 scope/subject/verified-compare 按公开接口实现并通过独立审查。
- [x] 在隔离集成树运行整卡组合回归；两个失败均在原基线复现并留证。
- [x] 快进 RF main 并验证远端推送。
- [x] 保留原工作区 daily_alert 变更、delivery/output 与历史 PWF。
- [x] 更新最终交接与并线 SHA。

## Next Step

无；MB-RF 卡已完成并入主线。整项目组合验收由 company-wiki 总控计划负责。


## ROOT 工区清理（2026-11-13）

- [x] 移除已确认 clean 的两个专用 worktree。
- [x] 保留 RF 主工作区既有 tracked 业务状态与未跟踪交付资料。
- [x] 本卡收尾完成，无下一步。

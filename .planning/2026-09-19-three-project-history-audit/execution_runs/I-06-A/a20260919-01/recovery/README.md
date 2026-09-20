# recovery/ — I-06-A / a20260919-01

**NA 声明（review_and_handoff.md 允许 NA，但必须写明理由）。**

本 attempt **没有产品实现**，因此没有可恢复的产品持久化状态：

1. **产品仓零改动**：D-W06 未签，`source_preparation.py` / 两个 `processing_demand.py`
   的字节与生产完全一致（`after/prod-anchor-hashes-after.json`）。
   没有新表、没有 migration、没有 journal，故不存在"迁移失败后恢复"的对象。
2. **候选的持久层只存在于 attempt 与 `%TEMP%`**：候选 DB 位于
   `%TEMP%\w06a\a20260919-01\<work>\processing_demands.sqlite3`；损坏或失败时删除该文件即可，
   **从未触碰生产 pending**（`after/demand.cross-process.json` 记录 DB 绝对路径）。
3. **候选的失败路径已被真实覆盖**：
   - 写失败（store 路径位于普通文件之下）：`after/cli-logs/c7-store-unwritable/` —— rc=3、
     结构化失败、0 行落库、无内存回退；
   - 未在任何路径上探测到自动 resume：`after/paused-before-after.json` 前后字节一致。
4. **worker 状态**：本 attempt 只在 `%TEMP%` 维护一个 fixture `worker_control.json`，
   真实 `control/` / `runtime_policy` / 后台 worker 全程零接触，故无需恢复动作。

若 D-W06 签署后进入实施卡，恢复证据的要求（迁移 journal、失败副本、隔离快照恢复）应由该
卡按 START_HERE §"失败停止与恢复界限"重新冻结；本 attempt 不预置任何产品侧恢复脚本。

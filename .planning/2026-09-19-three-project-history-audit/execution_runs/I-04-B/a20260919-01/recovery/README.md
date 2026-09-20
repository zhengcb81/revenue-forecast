# I-04-B recovery 边界（无状态性卡片，按 recovery_and_handoff 说明 NA 理由）

本卡**没有**触及任何持久状态：产品侧改动全部落在隔离副本
`execution_runs/I-04-B/a20260919-01/iso/filing-fetch/`，生产仓库零改动（`fetch_filing.py`
sha256 `046cc7dc…088` 每次运行后复核不变）。因此"异常后恢复"没有需要恢复的产品副作用，
`before/` 与 `after/` 的差异只存在于副本与 attempt 目录内。

## 回退配方（若本卡被 owner 撤回）

1. 删除 `execution_runs/I-04-B/` 整个 attempt 目录即可——生产不受影响（本卡从未写入生产）。
2. 如果将来把该补丁移植到生产，回退顺序为：`_request_remaining`/`_cleanup_timeout` 与
   `_PID_PROBE_MAX_SECONDS` 是新增 API，先回退 `__enter__`/`__exit__`/`_register`/`_unregister`
   的调用点，再删常量与两个方法；最后回退 `_run_company_wiki_json_retry` 的"返回后重算剩余"。
   `changes.diff` 提供逐 hunk 依据。
3. 不得用 `git checkout/reset/stash` 操作主树（主树含用户 dirty 文件）。

## 未覆盖

- 本卡未做真实 worker 暂停/恢复（卡片禁止），也未经真实 provider/wiki（属 I-07/I-16 资格）。
- 跨进程 lease 与崩溃恢复（含多参与者 refcount 竞争）属 **I-04-C/D**；本卡只保证单进程路径
  的预算与记账正确。

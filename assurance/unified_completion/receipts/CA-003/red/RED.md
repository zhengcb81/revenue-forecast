# CA-003 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：CodeGraph 索引与 git commit 无机器绑定——旧索引可冒充 current

**证据（2026-08-13 实测）**：

| 事实 | 值 |
|---|---|
| `codegraph status -j` 输出字段 | initialized/projectPath/fileCount/nodeCount/edgeCount/dbSizeBytes/backend/nodesByKind/languages/pendingChanges —— **无任何 git commit 字段** |
| `.codegraph/codegraph.db` 的 `project_metadata` 表 | **空**（0 行） |
| 结论 | 无法证明当前索引对应哪个 commit；README/计划中要求的 "indexed commit" 机器证据不存在 |

`codegraph status` 报 "Index is up to date" 只证明索引器认为文件无变化，不证明索引
对应某个审计基线的 commit——旧索引可被当作 current 证据使用。

## RED-B：full-chain 主张用静态源码检查冒充生产 trace

**证据（revenue tests/test_fc1002_three_process_e2e.py）**：
`test_chain_is_three_real_processes` 声称"链是真三进程（无进程内捷径）"，其证明机制是：

```python
src = inspect.getsource(source_preparation.prepare_source)
assert "subprocess.run" in src and "FILING_FETCH_CLIENT" in src
client = inspect.getsource(resolve_filing)
assert "subprocess.run" in client and "fetch_filing.py" in client
```

即：对生产源码做**字符串包含断言**（inspect.getsource + `in`），而非对真实调用
trace 的 machine 验证。测试名与 docstring 声称 full-chain，证据机制却是 helper/
静态层——正是 CA-003 卡声明的 RED（"只测 helper/seam 的测试被标 full-chain"）。

## 新工具对照（本卡实现）

`uc.codegraph_freeze`：每仓独占 `codegraph index -f` 重建 → 记录
`{indexed_commit(=git HEAD), codegraph_version, files/nodes/edges, db_size}` 于
`codegraph/codegraph_freeze.json`（exclusive publish）→ `verify`：HEAD 精确等于
indexed_commit、status 统计精确相等、sentinel 查询（已删除符号 0 命中、
核心符号 ≥1 命中）；production caller 报告用 codegraph query 对 9 个目标生成
（CatalogStore 写初始化、v1 scanner、RootPolicy flags、artifact bindings、
ProcessingDemand 缺失登记、filing handle validation、source preparation、
publication registry、dynamic runners），并把 runtime_policy=None 缺省构造的
生产调用点登记为阻断 finding（修复归 phase C/D）。

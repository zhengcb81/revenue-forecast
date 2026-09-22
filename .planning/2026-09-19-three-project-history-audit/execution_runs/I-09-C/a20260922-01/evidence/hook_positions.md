# hook 位置登记（card 按序动作 1 —— 供独立 reviewer 核对“正常提交顺序未改变”）

- card: I-09-C；attempt: `a20260922-01`
- 设计（本卡采用并披露）：**产品文件零编辑**。故障/ barrier hook 全部位于本 attempt 的
  `harness/i09c_hooks.py`，只在 harness writer 进程内、且 `--fault != none` 时通过包装模块
  属性安装。因此「正常提交顺序不变」可由两件事直接证明，而无需逐行审产品 diff：
  1. 生产树字节与预检时一致（`after/production_and_iso_hashes_after.txt`：6 个脚本 hash 与
     `preflight_anchors.md §4` 测量值相同；`git status -- scripts/` 为空）；
  2. 被测 iso 树 = I-09-B accepted 树，6/6 hash 与 I-09-B handoff 一致（零编辑）；
  3. `--fault none`（seed / recovery / T-PUB / CLI 矩阵 / 并发）时 hook **根本不安装**，
     代码路径就是 I-09-B 原路径。

## 被包装的调用点（hook 位置 = 以下 6 个 wrap target）

| # | wrap target（iso 树内，文件:符号） | 触发点名（hook_trace 记录） | 故障种类 |
|---|---|---|---|
| H1 | `scripts/revenue_forecast.py:run_forecast`（`prepare_forecast` 内的全局引用） | `err_raised(op=prepare_mid)` | OSError（F2：prepare 中失败） |
| H2 | `scripts/revenue_forecast.py:prepare_forecast` | `prepare:before` / `prepare:after` | kill（prepare 前 / 后） |
| H3 | `scripts/revenue_forecast.py:_atomic_write_text` | `member:<role>:before` / `member:<role>:tmp_opened` / `member:<role>:after`；作用域内 `builtins.open`、`os.fsync`、`os.replace` 被门控替换 | kill（JSON/Markdown 写前、写中、写完）+ OSError@write/flush/fsync/replace |
| H4 | `scripts/revenue_forecast.py:main` | `return:before`（`main` 返回后） | kill（返回前，F10） |
| H5 | `scripts/publication_registry.py:_append` | `registry:before_append` / `registry:after_append`；`err_raised(op=append_registry)` | kill（registry 持久化前后，F6/F8）+ OSError@registry（F9） |
| H6 | `scripts/publication_registry.py:commit_publication` | `commit:before` / `commit:after` | kill（commit 前后，F6/F10） |

`<role>` 由**调用顺序**判定：`main` 第 1 次调用 = `output_json`（先写 JSON），第 2 次 = `output_markdown`。
（这也正是审查点：hook 不改变该顺序；顺序由产品 `main()` 决定，hook 只在其前/后/间插桩。）

## 正常路径（未武装）等价性

- 未武装时 wrapper 只做 `checkpoint()` 追加一行 trace 后**立即调用原函数**——除 trace 文件外零副作用；
  seed/recovery/矩阵运行根本未安装 wrapper（`writer.py: fault == none ⇒ 不 install`）。
- T-PUB 与 CLI 矩阵直接调用 `scripts/revenue_forecast.py`，不经过 `writer.py`，**完全无 hook**。

## 触发轨迹证据（每例独立）

- `evidence/cases/<case>/state/hook_trace_<pid>.jsonl`：逐点时间戳 + armed 值；
- `evidence/cases/<case>/state/barrier_<pid>.json`：kill 点命中记录（pid + point）；
- `evidence/cases/<case>/state/pid_<pid>.json`：new_run manifest（pid + parent_pid，kill 前必核）；
- `evidence/cases/<case>/fault.json`：armed、barrier、kill 执行、raw rc、退出记录缺席。

## reviewer 复核清单（建议顺序）

1. `after/production_and_iso_hashes_after.txt`：生产 6 脚本 = 预检值；iso 6 文件 = I-09-B handoff 值。
2. 任取一 kill 例：`pid_*.json`（登记）→ `barrier_*.json`（点位）→ `fault.json`（kill.ok、无
   `writer_exited_<target>.json`、raw=4242）→ `hook_trace_*.jsonl`（点位序列）。
3. 任取一 err 例：`fault.json.stderr` 含注入的 OSError 文案 + rc=2；`hook_trace` 含 `err_raised`。
4. 确认 `harness/` 之外（除本 attempt 目录）本卡零写入：`changes.diff` 头部声明 + `after/` 证明。

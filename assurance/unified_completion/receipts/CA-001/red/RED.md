# CA-001 RED 证据

> 规则：RED 必须从公开/生产入口触发、先证明当前行为确实失败、再由独立 oracle 验证。
> 全部实验在 scratch 副本/临时目录进行；真实仓库的冻结文件、产品代码、catalog、roots 零改动。

## RED-A：共享输出并发写 last-write-wins，零冲突检测

**目标缺陷**：领取工作单元后，任何进程都能改写 registry/plan/状态文件；旧工具
`tools/closure_ledger.py` 用纯 `write_text` 覆盖输出（无锁、无 CAS、无冲突信号）。

**实验（真实旧工具，双进程并发写同一目标）**：

```text
命令1: python -B tools/closure_ledger.py --output %TEMP%\ca001-red-a\ledger.json
命令2: python -B tools/closure_ledger.py --output %TEMP%\ca001-red-a\ledger.json
（两个进程并发启动，写同一输出文件）
```

**结果（oracle 数据）**：

| 观察 | 值 |
|---|---|
| p1 stdout（GBK 解码后）== 最终 ledger.json | True |
| p2 stdout（GBK 解码后）== 最终 ledger.json | True |
| p1/p2 stderr 中冲突/锁信号 | 0 行（零冲突检测） |
| 仓库中锁工件（locks 目录） | 不存在 |
| 单进程对照运行 exit code | 1（gate 诚实 FAIL，见 `ledger_single.json`） |

证据文件：`p1_out.txt`（sha256 `7ffcef26…d253f`）、`p2_out.txt`（同）、`ledger.json`
（`0e63fb4a…bccb60`）、`p1_err.txt`/`p2_err.txt`（空）。

**结论**：当前 tooling 对并发写无任何防护——两个 writer 都"成功"，无冲突信号。
这正是 CA-001 卡声明的 RED。

## RED-B：plan/registry 内容漂移不可被任何机器工具检测

**目标缺陷**：冻结计划输入没有任何机器指纹校验；内容被篡改后旧工具结论不变。

**实验 1（工具盘点）**：`tools/*.py` 中不存在任何对冻结计划文件
（30 输入快照 / 14 内容文件 / 8 annex）的 SHA-256 校验；`closure_gate.py` 用
Markdown 子串判定状态，`verify_plan_claims.py` 只检查 checkbox/证据文本。

**实验 2（scratch 字节翻转）**：

```text
1. 复制冻结 task_plan.md + progress.md 到 scratch 目录
2. python -B tools/verify_plan_claims.py --plan scratch\task_plan.md --progress scratch\progress.md
   -> rc 0（基线）
3. 字节翻转：102 -> 101（2 处，语义改变：新场景数量 102 变 101）
4. 重跑同命令 -> rc 0（结论不变）
```

**结果**：内容漂移（2 处语义字节改变）后旧工具结论完全不变——漂移不可检测。

**新工具对照**：`uc.manifest.verify` 对每个冻结输入重算 SHA-256，
任何字节改变都会被报告为 `hash drift`（由
`test_offline_verify_detects_hash_drift` 及真实仓库 `manifest-verify` 覆盖）。

## 验收条件 → 证据映射

| CA-001 验收 | 证据 |
|---|---|
| 10 轮并发 mutation 无丢更新 | `tests/test_concurrent_10.py`：10 轮 × 3 跨进程 writer（CAS append 与锁竞争），断言无丢失/重复更新、每轮恰一个锁赢家 |
| 本计划所有输入可离线重算 | `manifest-verify` 真实仓库通过：30 输入 + 14 内容 + 8 annex 全部重算匹配；`tests/test_manifest.py::test_real_repo_offline_reverification` |
| 锁失败不会写半状态 | `tests/test_casfile.py::test_atomic_replace_fault_leaves_target_intact`；`tests/test_lock.py` 全套（过期锁破锁代际守卫、冒名释放拒绝、损坏记录可破） |
| 漂移/过期锁/冒名 owner/双 writer 均拒绝 | `tests/test_manifest.py` 漂移族测试；`tests/test_lock.py` conflict/impersonation/race 测试 |

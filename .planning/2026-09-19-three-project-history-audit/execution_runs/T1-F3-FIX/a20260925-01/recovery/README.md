# recovery — T1-F3-FIX / a20260925-01

**状态：N/A（纯函数被测物，无异常后恢复面）。** 逐条说明：

1. **被测物无持久状态**：`iso/natural_window.py` 是纯函数分类器 —— 输入 JSON → 输出 JSON 报告。
   它不写库、不持锁、不建状态机、不与外部服务交互。一次失败的运行不留下需要回滚的中间态。
2. **隔离面即本 attempt 目录**：全部写入落在
   `execution_runs/T1-F3-FIX/a20260925-01/`（两份 worktree、`evidence/**`、`_pytest_tmp/g1_*`、
   `changes.diff`、`handoff.json`）。源树、两前置卡、I-14-B oracle **0 字节写入**。
3. **每次命令独立输出目录**：`cmd_*` 在写盘前先 `rmtree(目标目录)`，因此重复运行不会把旧证据
   当成新证据；`run_cases.py --out-dir` 每条命令一个目录，`pytest --basetemp` 每条命令一个新建目录
   （且按 START_HERE 要求指向 attempt 内的新目录，不指 attempt 根 / 证据根 / 上次目录）。
4. **已知不可删的环境遗留（不是待恢复项）**：`_pytest_tmp/before_test_i14b_natural_window_{bas,con,tim}`
   三个 0o700 目录 —— 本沙箱把 `os.mkdir(..., 0o700)` 映射成**创建者自己都无法列举/删除**的 ACL
   （实测 `Remove-Item` 拒绝）。它们是 IC-3 那两次 plugin-less 仪器运行留下的，**已被 `g1_` 前缀永久
   绕开**，不参与任何判定；原样留存并登记在 `evidence/instrument_runs/README.md`。
   与 T1-F2-FIX handoff 记录的 `_pytest_tmp` 三目录同类。
5. **上一个完整版本仍可使用**：左像
   `baseline/natural_window.t1_f2fixed.pristine.py`（`9b1ebda2…` / 23534 B）是修前影像的**字节副本**，
   任何时点都可直接运行它复现 RED；`evidence/before/**` 全量留存。若本次修复被复审否决，
   把 `worktree/i14b/iso/natural_window.py` 换回该副本即回到合并序末态（两前置不受影响）。
6. **无 `commands.json` 之外的隐式命令**：所有实际执行的 argv 都登记在 `commands.json`。

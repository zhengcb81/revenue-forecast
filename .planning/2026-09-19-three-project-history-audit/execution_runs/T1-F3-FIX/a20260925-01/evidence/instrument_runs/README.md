# 仪器纠偏记录（instrument corrections）—— T1-F3-FIX / a20260925-01

本目录保存**仪器侧（探针脚手架）自身的失败/纠偏**，与 SUT 无关。每条都如实登记，
不覆盖、不删除既有输出。

## IC-1 `probes --phase before` 首跑：direct-classify 子探针读错输入

- 现象：7 条 CLI RED 判据 **12 条里的 7 条全绿**，但 5 条 `direct classify() raises` 全红。
- 根因：`scripts/verify_t1_f3_fix.py` 的 `-c` 内联脚本写成
  `case=json.load(open(sys.argv[2]))['cases']` 的**前一版**（读到整个
  `{"frozen_now_utc":..., "cases":[...]}` 文档），于是 `classify(文档)` 走 unknown-class
  分支返回 `reject_claim / ["R-UNKNOWN_CLASS"]`、rc=0 —— 是**仪器 bug**，不是被测物。
- 纠偏：改为 `['cases'][0]` 后**整族重跑**，12/12 绿（`evidence/before/probes/results.json`）。
- 未触碰：SUT 字节、oracle、任何期望值；7 条 CLI 判据两次取值相同。

## IC-2 `ncmissing --phase before` 首跑：S9 期望的**排序**写错

- 现象：7 行里 6 行绿，`S9` 红。
- 实测值：`["R-CLAIM-EXCEEDS","R-EMPTY-EVIDENCE","R-FUTURE-CLOCK","R-SAME-INSTANT"]`
  —— 正是 T1-F2-FIX 的 `C1_REF`（SUT 输出为 `sorted(set(refusals))`）。
- 我的期望表把 `R-CLAIM-EXCEEDS` 排在了末位（未按字典序）。
- 纠偏：`NC_STABLE["S9"]` 改为字典序；**实测值自始未变**，改的是我的期望表。
- oracle §5 I-2 只冻结了「S9 = 四码」与「7 行 before==after 全等」，未冻结码序，
  故此纠偏**不构成 oracle 违规**；但按纪律仍在此登记。

## IC-3 `suites --phase before` 两次 plugin-less 运行（沙箱 ACL）

- **第 1 次**（`_pytest_tmp` 父目录不存在）：`tmp_path` 夹具 `FileNotFoundError [WinError 3]`
  ⇒ 计数 = r1 32/0、r2 18/0、basis23 **22 passed 1 error**、container29 **28 passed 1 error**、
  新族 **1 passed / 2 failed / 16 errors**（新族几乎全部测试都收 `tmp_path`）。
- **第 2 次**（父目录已建、仍无 plugin）：pytest 在 `cleanup_dead_symlinks` 抛
  `PermissionError [WinError 5]`，**在打印汇总之前崩溃** ⇒ 计数解析为 0。
  产物已原样留存于 `instrument_runs/before_suites_run2_pluginless/`。
- 产物目录 `_pytest_tmp/before_test_i14b_natural_window_{bas,con,tim}` 因
  **mode 0o700 → 本沙箱 ACL** 而**创建者自己都无法列举/删除**（实测 `Remove-Item` 拒绝），
  留存为环境遗留（与 T1-F2-FIX handoff 记录的 `_pytest_tmp` 三目录同类）。
- 纠偏：**逐字节复制** T1-F2-FIX 的 `scripts/pytest_tmp_acl_plugin.py`
  （sha256 `e96890fe3275a6ef72063b0c112afdd6607a2b4ae50c08cdd8664594f0002aa3` / 1725 B，
  与其 `decision.md` 登记值相同），以 `-p pytest_tmp_acl_plugin` + `PYTHONPATH=scripts`
  加载；basetemp 名加 `g1_` 前缀以避开上述三个不可删目录。
- 该插件**只放宽 pytest 申请的目录 mode（0o700 → 0o777）**，不改任何断言、夹具、
  测试文件或 SUT 字节；加载点仅在本卡 `cmd_suites` 的 argv/env 中。
- **第 3 次（canonical，带插件）**：见 `evidence/before/suites/suites_summary.json`。

> 纪律核对：三次仪器运行都发生在 **SUT 修改之前**，SUT 字节在三次之间恒为
> `9b1ebda2…`（= `evidence/freeze.json` 记录的冻结值）；`oracle.md` 一字未改。

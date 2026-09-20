# recovery/ — M29 attempt a20260919-01

本卡是纯函数公式卡：没有共享状态、没有 worker、没有锁、没有事务，因此没有“崩溃后恢复”这一步。目录里留下的东西有三个用途：

| 路径 | 是什么 | 怎么复现 |
|---|---|---|
| `selfcheck/` | 变异自证（先红后绿）的**副本**现场：A/B0/B/C/D/E 六次 runner 运行的`run_result_*.json` 与 `stdout_*.txt`；冻结证据从未被写入 | 重跑 `E-mutation-selfcheck` 单元（`scripts/mutation_selfcheck.py`），它每次都会重建 `recovery/selfcheck/` |
| `selfcheck_result.json` | 与 `evidence/M29/mutation_selfcheck.json` 同内容的副本，便于只看 recovery/ 的人也能读到结论 | 同上 |
| `regen_verify/` | 逐字节重生成证明的 scratch 树：`evidence/M29/{input,oracle,cases}.json` 在空目录里被重新生成并与冻结件比 sha256 | 重跑 `D-oracle-regen-verify` 单元 |
| `line_boundary_demo/` | r2 规则的机制演示：把 `oracle.md` 追加一节后，按真实行边界截断能复现追加前 sha256（只在 scratch 副本上做） | 重跑 `G-pack-evidence` 单元（`scripts/pack_card.py`） |
| `venv_probe/` | attempt 解释器记录（路径 + sha256 + 版本） | 重跑 `A0-iso-venv-record` |

**恢复规则**：本 attempt 的任何一步失败都不需要“回滚产品”，因为产品从未被写入；正确动作是修脚本后**在同一个 attempt 内重跑该单元**，并把失败现场保留在 `evidence/M29/runs/<unit>/`（每次运行都覆盖同一 unit 的 rc/stdout/stderr，`pipeline_run.json` 记录最后一次驱动的逐单元原始返回码）。

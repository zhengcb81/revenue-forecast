# I-14-E-TESTSIDE-R3 / a20260926-01 — after/analysis.md（三臂对照与判据逐条判定）

## 1. 三臂 + 变异对照（全部 cpu8、N=6、90 s driver 超时、逐次全新 basetemp）

| 臂 | 文件面 | H 来源 | pytest rc | 通过/失败 | 失败形态（逐次同形） |
|---|---|---|---|---|---|
| 红（修前） | 原始字节 `32515aa6…c005c1` | 写死 0.5 | 1,1,1,1,1,1 | 0/6 | rc-gate `assert 1 == 0`（`completed.returncode`）；事件 `starting → launcher_exception` |
| 绿（施加后） | `a1cfeb13…67fb0` | `min(max(2.0,4*t0),t0+3)` | 1,1,1,1,1,1 | 0/6 | 同上 |
| 变异 M1 | `7896ef85…7211` | 写死 0.5（t0 探针保留） | 1,1,1,1,1,1 | 0/6 | 同上 |
| 变异 M2-upper | `51756220…6c3c` | `min(max(2.0,4*t0),t0+10)` | 1,1,1,1,1,1 | 0/6 | 同上 |

- 绿臂 t0 实测（`green/tside-trace.jsonl`）：0.1915 / 0.1590 / 0.1822 / 0.1919 / 0.1794 / 0.5265 s
  ⇒ 导出 H：2.0×5、2.1059×1 —— 公式**逐次机械生效**（地板与 4*t0 两条腿都被观测到）。
- M2-upper 臂 t0：0.2950 / 0.6958 / 0.5606 / 0.5396 / 0.3422 / 0.3479 s ⇒ H：2.0 / 2.7833 /
  2.2423 / 2.1586 / 2.0 / 2.0 —— 全部 = `max(2.0, 4*t0)`，钳制腿 `t0+10` 未触发（4*t0 恒 < t0+10），
  与预注册的"唯一被变异元素 = 上界钳制"一致。

## 2. 冻结判据逐条判定（expected 不重算，逐字引 R1 oracle §3）

| 判据 | 冻结要求 | 本会话实测 | 判定 |
|---|---|---|---|
| §3.C 红 | ≥1 红，形态 `assert … == 2` / `TimeoutExpired`（不是 `launcher_exception`） | 6/6 红但形态 = rc-gate + `launcher_exception` | **形态不可证**（计数 6/6 达标、形态不达标） |
| §3.D 绿 | 6/6 绿 + 四条子判据 | 0/6（全部死于 rc-gate） | **不可证** |
| §3.E / R2 §4 变异 | ≥1 红且与绿有判别力 | 两个变异各 6/6 红，但与绿**同因**失败 | 计数达标、**判别力不可证** |
| §3.F 边界 | iso/src、iso/scripts、真仓逐字节不变；`changes.diff` 只含 `tests/**`；git 非 `.planning`=0 | `all_required_equal=true`；diff 1 文件；非 `.planning`=0 | **成立**（唯一披露：iso/tests 与"当前"真仓的漂移，见下） |

**结论**：失败形态在四臂之间完全同形 —— 每次都在**看门狗之前**的
`source_catalog_worker.ps1:340-341`（`Start-Process` 重定向分支 `.Handle=null` → `Assign` 抛
`Cannot convert null to type System.IntPtr`）处红。时序机制（0.5 s 看门狗 vs 启动带宽）在本会话
**根本未被触发**（`child_started=0` ×24），故红的时序形态、绿 6/6、变异判别力三者
**在本会话不可演示** —— 与 R1 `oracle-addendum-C §C3` 的降级完全一致，不造绿样。

## 3. 边界判定的唯一披露（`after/disclosure-drift.json`）

`boundary_check.json` 的 verdict 串是 `BOUNDARY_BREACH`，其**唯一**驱动项是
`iso_tests_copy_was_faithful`（iso/tests vs **当前**真仓 tests）：真仓 `company-wiki/tests`
在 `a20260924-01/iso` 拷贝**之后**推进了 3 个无关模块（2 改 1 增；被钉住的 bootstrap 锚文件
仍与本卡 pin 同值）。逐字节证据：本 attempt `iso/tests` manifest
`369aa19e…1c8e` = R1 拷贝时的 iso 与真仓 manifest（即对拷贝源忠实）；变化只来自外部推进。
所有 P1 面（CW/{src,scripts,tests,pytest.ini,conftest.py}、iso/{src,scripts,config,pytest.ini,
conftest.py}）before==after 逐字节相等；`iso/tests_changed_files` = 恰好本卡施加的 1 个文件；
`git_diff_non_planning=0`。交付的 `after/changes.diff` 因此**只含本卡施加**（1 文件，
sha256 `3952cff5…6db72`，与 R1 交付逐字节相同），外部漂移的原始 4 文件全量 diff 另存
`after/disclosure-iso-vs-cw-full.diff` 供 reviewer 判定。

## 4. 未证实（缺证据写未证实）

1. 红的时序形态（`assert N == 2` / `TimeoutExpired`）——本会话不可演示（继承）。
2. 绿 6/6 ——本会话 0/6（继承）。
3. 变异判别力 ——本会话不可演示（与绿同因失败，继承）。
4. 节点②（15/15/20 s 三预算）——仍不施加（源卡 16/16 通过、复现不出红，理由逐字不变）。

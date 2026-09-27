# T1-10-FIX recovery（a20260923-01）

## 这是什么 / 中断后如何续

卡：**T1-10-FIX** —— 闭合 M-T-REVIEW T1-10 `changes_required` 的缺陷①（claim.basis 枚举校验非全函数）。
交付 = `changes.diff`（源树 READ-ONLY，写入 0 次，无 git、无删除）。**本卡已跑完全部九步**；若需复核或重跑：

## 状态锚（sha256，先核这些再信任何文字）

| 对象 | sha256 |
|---|---|
| 基线 SUT（= I-14-B r2 源文件） | `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` |
| 修复后 SUT（`worktree/i14b/iso/natural_window.py`） | `064e5381444d35a8ab1184d6c8d2eaa839a40f96c704ae7995fa3b660c7e273d` |
| `changes.diff` | `625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac` |
| 新增负例族测试 | `316e369c9afc9d8df04a425945b97e41378e87f3ac17c721d0ab9ddf90904bfd` |
| `oracle.md`（运行前冻结） | `afe8b61a3274e2473fe08db116e362bacf30e7c99facc90ec13d9453c929e4fb` |
| 22 个输入 pin | `evidence/pin_hashes.sha256.tsv`；跑后复核 `evidence/boundary_check.txt`（0 mismatch） |

## 目录状态（全部保留，**未删除任何东西**）

- `worktree/i14b/` —— **已修复**的隔离副本（SUT = `064e5381…`；含新增测试文件）；after 侧所有命令在此树执行。
- `worktree_before/i14b/` —— **修复前**快照（SUT 仍为 `7fff6f0c…`，含同一新增测试文件供 RED 跑）；
  `harness/scratch/mutants-r2/` 与 `evidence/mutations-r2/` 内是它自己那轮 20 臂变异的 scratch 产物（**保留**；
  其哈希已录于 `evidence/before/mutations.json` 各 `mutant_sha256`）。
- `worktree/baseline/natural_window.r2.pristine.py` —— 基线字节（diff 左侧、probe --phase before 的配对对象）。
- `evidence/before/**`、`evidence/after/**` —— RED/GREEN/MUTATION/负控/invariants 全部 raws 与 JSON（**冻结证据，勿覆盖**）。
- `_pytest_tmp/`、`evidence/after/mutation/scratch/`、`evidence/after/negative_control/*_poisoned.json` ——
  运行中间物，按「不做删除」规则原样保留；它们不是交付物，`handoff.json` 不登记其哈希。
- `evidence/boundary_check.txt` 里的 UTF-16/UTF-8-BOM 编码差异见 `commands.json` disclosures（第 3 条）——
  读这些 txt 时用 BOM 探测（`utf-8-sig` / `utf-16`），与 T1-10 F 段 CRLF 教训同族。

## 重跑顺序约束（复核者注意）

1. **先跑 before 后跑 after**：`mutate.r2.py` 的 SUT 路径硬编码为**所在树**的 `iso/natural_window.py`，
   before 轮必须在 `worktree_before/`（未修复树）里跑；after 轮在 `worktree/` 里跑。
2. `verify_t1_10_fix.py probe` **带配对守卫**：`--phase before` 断言 SUT sha == 基线，
   `--phase after` 断言 != 基线；配错即刻失败，不会静默出假绿。
3. pytest 需要 `--basetemp` 的**父目录已存在**（懒建且不递归）：先 `New-Item -Force <attempt>/_pytest_tmp`。
4. 全部命令见 `commands.json` steps（**无 git**）；Python 用 I-14-B venv 解释器（只读复用，`-X utf8 -B`）。

## 失败/降级路径

- 若 `evidence/after/invariants.json` 读出 FAIL：先看 `failed_checks`；`I-2` 字节不等 ⇒ 有第三方改过
  `worktree/` 树（对照 `worktree_before/` 与 pin 表定位）；`pin mismatch` ⇒ 源树被写过（严重，须上报，
  因为本卡边界声明源写入 0）。
- 若 `changes.diff` 无法应用：核对左侧 sha 必须是 `7fff6f0c…`；`--fixed` 右侧 sha 必须是 `064e5381…`；
  `make_diff.py` 可无 git 重建（命令见 commands.json step 18）。
- 收口**不在本卡**：按返修块须**独立验收**；F-1/F-2/F-3（decision.md §6）是移交项，重开新卡，不在本卡补刀。

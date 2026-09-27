# I-14-E-TESTSIDE oracle.md — Addendum A（**追加式** erratum，运行前追加；上文一字未改）

记录时刻：**2026-09-25T20:47Z**，在本 attempt 的**任何一次红/绿/变异运行之前**（红臂第一次 pytest
启动在此之前未发生；`before/freeze_instant.json` 仍是 `oracle.md` 主文的冻结记录）。
本 addendum **只改 §5 第 1 条的"运行目录落点"**；§2 修法、§3 expected、§4 负载与 N、§6 禁止事项
**一字不改**。

## A1. 冻结后、首跑前观测到的两个事实（诚实登记，不用于生成 expected）

1. **8.3 短名路径救不了 pytest 的 basetemp**：pytest `_pytest/tmpdir.py:154-159` 先
   `basetemp.mkdir()`，随后 **`basetemp = basetemp.resolve()`**；Windows 上 `Path.resolve()` 走
   `GetFinalPathNameByHandle`，把 8.3 短名**展开成长名**。实测：
   - 短根（75 字符）+ `\w\r1` 的 `os.path.abspath` = **80** 字符；
   - 同一路径 `resolve()` = `…\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-E-TESTSIDE\a20260924-01\w\r1` = **136** 字符；
   - 再加该节点最长后缀 124（`test_<30>\fake-project\.source_catalog\worker_stdout-<32hex>-attempt-0001.log`）
     ⇒ **260 > MAX_PATH(259)** ⇒ 必然 `WinError 206`。
   - 同向证据（`r/` 探针，09-24 23:04-23:12 生成的空目录链）：长路径下 `Set-Content` 与
     Python `open()` 分别报 `Could not find a part of the path` / `FileNotFoundError`；
     `LongPathsEnabled` 未启用；`subst Z:` 被沙箱拒绝（`Access denied`）。
   ⇒ **"basetemp 物理落在本 attempt 目录"在本机 OS 约束下不可行**，与判据无关，属客观限制。

2. **本会话 `TEMP` 是会话专属短目录**：`%TEMP%` = `C:\Users\郑曾波\AppData\Local\Temp\dsh-k4uKNt`
   （**42** 字符，运行时由驱动读 `os.environ["TEMP"]`，不写死）。

## A2. 修正后的运行目录落点（判据不变）

| 项 | 冻结原文 §5.1 | 本 addendum 修正为 |
|---|---|---|
| pytest `--basetemp` | `短根\w\<tag>`（attempt 内） | **`<TEMP>\i14ets\<tag>`**，长度 **52–60** |
| pytest `cwd` | `短根\w`（attempt 内） | **`<TEMP>\i14ets`**（与源卡 M-B 同形：源卡 `cwd=run_dir` 也在 `%TEMP%`） |
| iso 代码 / 证据 / 三臂输出 | attempt 内 | **不变**（仍全部 attempt 内） |

**与产品约定的一致性（关键）**：`iso/conftest.py`（产品 I-14-F 的短 basetemp 约定，owner §16 E-1）
判据是 `len(resolved_basetemp) + 150 > 210` 才迁移：
- 本方案 `len = 52–60` ⇒ `60 + 150 = 210` **不 > 210** ⇒ 判 **`within-budget`，不迁移**
  ⇒ **不会**创建 `%TEMP%/cw-pytest-basetemp/…`，也就不触发该约定的 cleanup 分支；
  每次运行的 decision 行照常由 `CW_BASETEMP_DECISION_FILE` 落盘（证据）。
- 生成路径最坏 `60 + 124 = 184 ≤ 210`（产品自己的干净包络），比源卡有效 basetemp（78–84 ⇒ 203–209）
  **更短** ⇒ 路径长度只会更安全，不会给红臂"送分"（源卡记录 173/174 ⇒ 12/12 失败的那种
  WinError 206 型失败在本方案下不可能出现；因此红臂的红**只能**来自被测时序机制本身）。

## A3. 对写入边界的如实登记（留给 reviewer 判定）

- **偏差**：pytest 的 basetemp/cwd 这两处**临时 scratch**落在 `.planning` 之外（`%TEMP%\i14ets\*`）。
  它们由被测测试框架创建/删除，内容 = 该次运行的 tmp 项目与 capture 输入；**源卡 M-B 也是同样落点**
  （`%TEMP%\i14e-*`，其 `recovery/README.md` 明确登记为"scratch，故意保留"）。
- **不因此放宽的部分**：`company-wiki`（真仓）与 `iso/src`、`iso/scripts` **零写入**（由
  `before/hashed_before.json` → `after/hashed_after.json` 的逐字节比对自证）；`changes.diff` 只含
  `tests/**`；`git diff HEAD --name-only` 非 `.planning` **= 0**（`%TEMP%` 不在任何 git 仓内）。
- 本 attempt 自己的**全部代码、oracle、三臂原始证据、交付物**仍只在 attempt 目录内产生。
- 如 reviewer 认为该偏差不可接受，请判 `changes_required` 并注明；实现者**不**据此自签。

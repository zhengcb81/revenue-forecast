# evidence/red_first_run_recovered/ — F-01 抢救件（首跑残存证据）

创建：2026-09-22 23:4x（复审 F-01 增补；复审 ACCEPT WITH FINDINGS，报告 = `../reviewer_report.md` §3 F-01）。

## 背景（如实）

`evidence/red/{A..M2}.json` 与 `evidence/red/run_log.txt` 现盘全部是**末次运行**（run3, 23:06:27–30）
的产物。前两次运行的同名工件被末次运行**覆盖**（同名覆写，非删除命令）：
- **run1**（23:05:37–39）：GBK 控制台 `UnicodeEncodeError` 在 case G 打印处崩溃，写了 A..G 的 JSON + 部分 run_log；
- **run2**（23:05:54–56）：完整跑完 18 例，但 I/J 结果被 harness 自身 `record_kwargs` reviewer kwarg
  重复 TypeError 污染（首版 I.json/J.json 即此）+ 完整 18 行 run_log；
- 两者均被 run3 覆写 ⇒ attempt 内原始字节 **0 残留**（复审 grep `record_kwargs|TypeError` 于 evidence 下
  0 命中，属实）。

## 本目录内容

1. `run1_gbk_crash_230537-39/`（13 目录）与 `run2_kwarg_typeerror_230554-56/`（20 目录）：
   从 `%TEMP%\i06b_*` **原样拷贝**的两批 scratch（sqlite 夹具库），按 CreationTime 窗口
   23:05:37–39 / 23:05:54–56 筛选（与复审 §1/§2.1 所述批次一致；%TEMP% 原件未删未动）。
   ⇒ 证明两次首跑真实发生（目录创建时刻 + 各 case 夹具库状态），是 run1/run2 存在过的**盘上物证**。
2. `manifest.json`（sha256 `e5736d7a3d3da9074da4b9911cf2171e83fb1bfbf83cfdc83daffa350e95985b`）：
   33 条逐目录清单（源路径、CreationTime、文件数、字节数、逐文件 sha256 前16位）。
3. `transcription_first_run_observed.md`：**执行者会话内直接读到的** run2 首版 `I.json`/`J.json` 全文
   与 run1 崩溃控制台输出——**标注为转录**：原文件已被覆写、原始 sha 未记录、此件不可作原始字节自证，
   仅为「执行者当时逐字读到的内容」的如实保留（不伪造为原始工件）。

## 不可恢复部分（如实 ABSENT）

- run1/run2 的 `evidence/red/*.json` **原始字节**：ABSENT — 被 run3 同名覆写，无法恢复，未伪造。
- run1 部分 run_log 与 run2 完整 run_log 的**原始字节**：ABSENT — 同上（run1 控制台输出以转录件保留）。
- run2 除 I/J 外其余 16 例 JSON：ABSENT — 同上（其结论已被 run3 同型复跑覆盖且两版判定一致面见
  `evidence/red/summary.json`；I/J 两版差异 = harness 缺陷，已由本目录 + 三处文字自述记载）。

## 索引（本行即三处文字自述所指）

- `commands.json` → `commands[CMD-I06B2-RED-ORIGINAL].notes` + `commands[CMD-I06B2-RED-ORIGINAL].__historical`
- `decision.md` → §4.3（honesty notes 修订）与 §4.4（首跑覆盖缺陷记录）
- `handoff.json` → `honesty_notes[2]` + `evidence_paths`

## 复跑注意

本目录为**冻结抢救件**：请勿在其中执行任何脚本（执行会改 mtime/pycache）；如需复核，先整目录另行拷贝。

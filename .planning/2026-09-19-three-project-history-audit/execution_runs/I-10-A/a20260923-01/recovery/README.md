# I-10-A a20260923-01 recovery/README.md

## 恢复原则（继承 I-07-B 声明3逐字）

> 恢复：保留已取得raw，只回退当前隔离变更。

- 本卡无生产写入、无 CW 写入、无 git 操作 ⇒ **无可回退的产品面变更**（实测 anchors_identical）。
- 全部隔离面写入 confined to `execution_runs/I-10-A/a20260923-01/**`；如需回退本次隔离变更，
  删除/归档该 attempt 目录即可，**不得**删除三份来源 raw、sidecar、旧审计证据（均已实测未变）。
- `_scratch/fixtures/**`（RED/MUT 夹具）与 `command_runs/**`（原始运行留档）保留供复核；
  不得覆盖 `evidence/I-10-A/run_log.jsonl`（判据运行时刻链，creation-time 证据）。

## 异常后重启/重试规则（review_and_handoff 第6条）

- 判据运行失败重试须新建 run 目录（run_log 逐条追加，不改旧行）；本卡的重试痕迹：
  ① 16 个探针首跑 rc=1（iso import 闭包缺 `asset_ownership` 等模块，harness 失败）→ 补齐 iso 副本后
  全量重跑（旧行留 run_log）；② GREEN 首跑 rc3 → 转写更正 → GREEN-2/3/4；③ MUT-F-B 首臂存活
  （验证器 R12 缺口）→ 补实现 → MUT-F-B-2/MUT3 击杀。
- **死亡留自洽**：任何中途停止状态下，oracle.md（冻结）+ run_log.jsonl + command_runs/** 已可独立
  解释已发生的一切；已交付 8 件证据中缺失者按 handoff.evidence_paths 核对。

## 保留清单（不得清理）

- `evidence/I-10-A/source_extracts/`（含 superseded_pdftotext/ 双份失败抽取、page_renders/ 6 页渲染、
  ref/ 两张参考 CMap 及其否定检验记录）——原文可核性链。
- `evidence/I-10-A/probe_runs/**`（20 臂 probe_result.json + argv/stdout）。
- `command_runs/**`、`before/`、`after/`、`_scratch/fixtures/**`。
- 无 %TEMP% 使用（本卡未用全局临时目录——binding.forbidden 载明；实际未触碰）。

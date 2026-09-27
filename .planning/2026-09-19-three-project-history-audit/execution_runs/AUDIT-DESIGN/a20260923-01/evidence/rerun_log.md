# 复跑实证原始记录 — AUDIT-DESIGN / a20260923-01

全部运行副本位于 `%TEMP%\AUDIT-DESIGN-a20260923-01\`（I-07-D、I-07-B、I-07-C、E2E-EXPAND、REM79-MECHANIZATION、B5-fix-g1a-g3、GATE-TIMEOUT-1200 的事前整树副本）。
本文件为命令-结果对照的审计员记录；结论引文见 `audit_report.md` §5。

## R1a — REM-79 检查器 vs PWF 三文档（documented: REM79-MECHANIZATION/a20260922-01/commands.json:56）
命令：`python -X utf8 -B tools/check_domain_assertions.py --json <PLAN>\task_plan.md <PLAN>\findings.md <PLAN>\progress.md`（cwd=%TEMP% 副本，PYTHONIOENCODING=utf-8，三文档只读）
结果：rc=1；tool `check_domain_assertions` v`1.2.0-correction2`；totals files=3 violations=4：
- task_plan.md:1630 marker「全部」
- findings.md:633 marker「all」
- findings.md:684 marker「none」
- progress.md:1060 marker「全部」

## R1b — REM-79 检查器 vs REM79 oracle.md（commands.json:65）
结果：rc=0，`0 violation(s) across 1 file(s)`。

## R2 — I-07-D 故障矩阵判决重算（documented: I-07-D/a20260923-01/commands.json:30-39；子命令 `run_d_matrix.py <cell>v|verdicts`）
| 子命令 | rc | 输出 | 与在案 evidence/verdicts.json 比对 |
|---|---|---|---|
| f01v | 0 | `{"cell":"F01","all_ok":true,"fetches_total":3,"fetches_run1":1,"failed":[]}` | 一致 |
| f02v | 1 | FileNotFoundError: `%TEMP%\i07d\cases\F02\cwroot\companies\小米集團－Ｗ\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf` | **不可重算** |
| f03v | 1 | 同上（F03 路径） | **不可重算** |
| f04v | 3 | `{"cell":"F04","all_ok":false,"killed":1,"failed":["raw_committed_before_kill","provenance_committed","raw_intact_after_recovery"]}` | 与在案（all_ok=true）**不同**；经核 `%TEMP%\i07d` 整树已不存在 ⇒ 三项均为缺失输入的静默降级，**不可重算** |
| f05v | 0 | `{"cell":"F05","all_ok":true,"cause_survival":"FAIL — finding F-F05-cause: su…"}` | 与在案一致（含 F-F05-cause） |
| f06av/f06bv/f06cv | 3 | 各 `{"all_ok":false,"trigger_count":1,"failed_checks":["fault_audit_clean","rec2_audit_clean"]}` | **与在案逐字一致**（红可复现） |
| verdicts | 3 | `{"all_ok":false,"blocked":[],"trigger_counts":{F01..F06C:1}}` | 与在案一致（all_ok=false、trigger 8/8） |

注：`%TEMP%\i07d` = 原 attempt 的产品工作树（`evidence/build.json` 记 `f01_config.config` 等绝对路径指向它）；attempt 目录内未留存被哈希的 raw 字节（pdf/source.json 检索 = 0 命中）。

## R3 — I-07-B WPROBE 复跑（documented: I-07-B/a20260923-01/commands.json:54-59）
命令：`python -X utf8 -B harness/run_case.py wprobe <evidence>/wprobe_rerun`
结果：rc=0；`{"totals":{"scan":2,"read":2,"provider":2},"zero_insert":true,"rc":0}`；
与在案 `evidence/wprobe.json` sha256 逐字节相同 = `e01c8c905d65609dad150df36a95cd2d4207b415450387a24bc3dc6537aef96c`。
（实现注记：脚本未采纳我传入的输出目录参数，写的是副本内 `evidence/wprobe.json`；写入发生在 %TEMP% 副本内。）

## R4 — E2E 跨仓链离线复跑（documented: E2E-EXPAND/a20260923-01/commands.json:75）
命令：`python -X utf8 -B e2e/run_cross_repo_chain_e2e.py --scenarios S5,S6 --live never --work-root %TEMP%\...\e2e_work --evidence-dir %TEMP%\...\e2e_evidence`
结果：rc=0；`E2E-S5: PASS [21.513s]`、`E2E-S6: PASS [15.142s]`、`E2E EXIT 0 (total 36.66s)`；summary.json 落 %TEMP%。零网络（--live never）。

## R5a — B5 `scripts/verify_append_fixed.py`（documented: B5-fix-g1a-g3 handoff/report F-7 链证）
结果：rc=0；`anchors: 19 embedded / 19 distinct / live-extraction match=True`；`append1 vs PRE : +126/-0 prefix_ok=True insert_only=True`；`append2 vs POST1: +52/-0 prefix_ok=True insert_only=True`；`frozen_anchor_lines_all_intact: true`；`APPEND_ONLY = True`。
**事故**：输出写回原 attempt `evidence/start_here_append_proof_fixed.json`（脚本内嵌绝对路径）→ 已按 handoff pin 逐字节还原（`7c4c95dc…`）。详见 audit_report.md §0。

## R5b — B5 `scripts/verify_boundaries.py`
结果：rc=1；runner census 68/68 PASS=True；frozen cases 31/31 total=347 bad=0 PASS=True；`START_HERE unchanged: False`（B5 之后的 owner 授权追加所致）；`production anchors PASS: False`（后续卡合法演进）；`B5 handoff mismatches: 1 — binding.json recorded 06ff8064… actual 96733875…`。
**事故**：同上写回 `evidence/boundary_verification.json` → 已还原（`0aacaac8…`）。

## 哈希钉复算（audit_report.md §4）
- M01/M17/M29 `scripts/run_card.py` = `b5fcc685…`/`94619a98…`/`9ea69c72…` → MATCH（对在案声明）
- I-07-D `reviewer_report.md` = `1a1d1c05…` → 与侧车 MATCH；`oracle.md` = `576ddfc57c2c949d6a9e5f875114d8c7e49c833d69b5bd8cd81bcf2417718846`（27211 B）→ 与 review.md:84 声明 MATCH（我方首次比对因自拼期望值误报 DIFF，已更正）
- I-14-F-R1 `oracle.sha256` 侧车：`b5fee00f…`/13851 B/`frozen_at_local 2026-09-22T08:35:44+01:00`
- I-15-A handoff 2/2、I-08-C binding 1/1 MATCH
- B5 boundary_verification：18 项中 17 一致、`binding.json` MISMATCH（D7）

## 审计工具
`evidence/verify_hash_manifests.py`（本审计员新增，只读）：解析 attempt 自带 manifest 中 (path,sha256) 对并复算。局限：跨根相对路径条目报 MISSING（假阳性，已在报告 §4 注明）。

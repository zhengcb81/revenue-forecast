# 独立复核 — I-02-A / a20260919-01

结论：**accepted_scoped**

独立 reviewer 只读复核（重算 hash、iso venv 重跑 scripts/w02a_cases.py override），未修改三仓任何文件，未连接生产 .source_catalog DB，未启动 worker/网络。重跑仅重新生成 attempt 内 after/ 四个证据文件（此为复核动作 2 的授权范围），before/ 证据未触碰。

## 逐项核对

1. **oracle 冻结与具体性**：oracle.md 在最终验收运行前成文（明示开发期有过工程调试运行，最终证据按本文件判定）；五组判据具体冻结——各分支独立错误短语（completion_status=… / target_not_registered / scan did not complete / exact_resolve_identity_mismatch / roots not completed）、字段名、枚举值，expected 与 decision.md(D-W02) 手推判据一致，未发现"实现后回填 expected 语义"的贴合痕迹。
2. **重跑用例（本轮 reviewer 实际执行）**：`iso/venv/Scripts/python.exe -X utf8 -B scripts/w02a_cases.py override` → rc=0、`failed_cases: []`，新 run_id 全套证据再生成且与冻结判据一致。抽验：
   - P1：completion=completed、target_files registered=True（含 source/document/location/root_id/relative_path/role）、imported_new、reused_exact 且 matches[0].content_sha256==目标 hash、canonical_path 相等、sources 行存在、staged 清理 — 通过。
   - N1：scan_runs 行 status=completed_with_errors（非 interrupted，扫描正常返回）、sources 表无目标 hash 行、writer 报 scan 阶段失败、raw+sidecar 保留且 hash==staged hash（cd1d3707…）— 通过。
   - N2：报告健康（completed/errors=0/files_seen=2）但 target_files registered=False/target_not_registered；SQL 仅 OTHER_SHA（b97e4fd7…）出现 sources 行、目标不出现；writer 拒绝 — 通过。
   - N3a：scan_runs 最新行 status=interrupted、report_json=NULL、writer 报 `post-import scan failed (scan did not complete)` 与 identity 阶段可区分、staged 保留 — 通过。
   - N3b/N3c：completed_with_errors + 两 root 分列（company_raw=completed、archive_extra=failed/scan_strategy_error）；伪造 reused_exact 被拒 — 通过（读 scan-return-contract/case_results/SQL 快照）。
3. **生产 hash 未触碰**：重算 models/scanner/canonical_writer/service 四文件 sha256 全部与 card 锚点、binding.json 一致（6523…/f039…/c23a…/32b7…）。三仓零写入。
4. **diff 范围与四道门实现**：changes.diff 只覆盖允许的 models.py/scanner.py/canonical_writer.py（service.py hash==生产，零差异转发）。在 override 源码逐行核实（非仅信 diff）：gate0 中断异常包装 `post-import scan failed (scan did not complete)`；gate1 任何非 `completed` 拒绝；gate2 per-root 非全 completed 拒绝且不清理已提交行；gate3 target_not_registered 拒绝；gate4 exact resolve 必须 reused_exact 且 content_sha256==receipt hash 且 canonical_path==本次写入路径。models.py 枚举 `__post_init__` 校验真实存在（SCAN_COMPLETION_STATUSES/SCAN_ROOT_STATUSES/SCAN_ROOT_ERROR_CLASSES/SCAN_TARGET_REASONS）。
5. **registered 判据**：scanner.py `_target_registration_results` 以 `sources.content_sha256=? AND locations.last_seen_run=?(本 run) AND location_status='active'` 为准；oracle/decision 均明确不得以 errors==0/files_seen>0 推定（writer gate3 只读 target_files，不读计数）；service.py 仅转发。
6. **未决项留痕如实**：handoff.open_questions 三条与 decision.md 末节一致 —— D-W02 journal/事务/错误信封留给 I-02-B/C/D；CMD-W03 pytest nodeid 留 I-00-B（venv 无 pytest）；MAX_PATH 用 %TEMP% 短物理路径 + after/case_scratch_retained 留快照（iso_patching.md 第 4 条）。
7. **结构偏差裁定（不阻断）**：before 证据放于 `after/before/` 而非顶层 `before/`，结构与 review_and_handoff 模板有偏差，可接受并记录；另发现 `after/c/p1/project` 为早期 subst 试错的残留 scratch 树（小垃圾，不构成证据混淆，记录为清理项）。reviewer 重跑对 raw-before-after 类"bytes_unchanged_after_rejection"字段为断言式而非程序化前后 diff（N1 前后对比缺 before 侧），但因 canonical hash==已知 staged hash（cd1d3707…）独立成立，不遮挡。

## 限定申明

- 本接受**不授予生产部署**、不修改生产 company-wiki 四文件。
- ScanReport 回执契约及四道门仅在本 attempt 的隔离 override（iso/）中获得资格；生产 py 未经修改。
- journal 持久化/事务边界/恢复键/错误信封版本等 D-W02 其余必决项资格留给 I-02-B/C/D owner，不在本卡。
- pytest 结点绑定资格留给 I-00-B（CMD-W03）。
- 本次复核重跑重新生成了 after/ 四个 json（新 run_id），属证据再验而非篡改；before/ 保持原样。

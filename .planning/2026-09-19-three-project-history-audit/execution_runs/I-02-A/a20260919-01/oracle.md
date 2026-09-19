# W02A oracle（冻结预期，手推判据，非被测函数生成）

冻结时间：2026-09-19（最终验收用例运行之前已成文；开发期间曾有工程调试运行，最终证据目录
after/ 与 after/before/ 的运行全部按本文件判据执行与判定）。
锚定对象：``ScanReport`` 新回执字段 + `CanonicalSourceWriter.import_staged` 的四道门；
判据全部按 decision.md 手推。

## 通用判据

- 目标注册判据：一个 content hash 记为已注册 ⇔ 本扫描 run 在 sources + locations
  中存在 `location_status='active'` 且 `locations.last_seen_run = 该 run_id` 的行；上一轮旧行不算。
- writer 成功判据（全部满足才成功）：scan 完成状态为 completed 且 per_root 全 completed 且
  目标以 target_files registered=True 上报，且 exact resolve 为 reused_exact 且 resolver 命中的
  content_sha256 == receipt.content_sha256 且 canonical_path == writer 本次写的目标路径。
- raw/sidecar 保留判据：任何拒绝路径后，canonical raw 字节 hash == staged 字节 hash，
  sidecar 字节 hash 未变；staged 文件保留（未来恢复用）。
- 每个隔离库独立（%TEMP%/w02a/a20260919-01_case_scratch/<case>，证据树最终复制回
  after/case_scratch_retained/）。

## W02A-P1 / positive（真实 scanner + 真实 resolver + 真实 writer）

布局：company_raw 根（company_raw_v1 adapter）+ archive_extra 根（sidecar_filing_v1，含一个
不相关 .txt+sidecar 的健康原件）。staging 放入目标 bytes（PAYLOAD_A）。

预期：completion_status=`completed`；per_root_results 含 company_raw=completed 与
archive_extra=completed；target_files 对 receipt.content_sha256 的条目 registered=True
（reason=registered，含 source_id/document_id/location_id/root_id/relative_path/role）；
status=imported_new；resolution=reused_exact 且 matches[0].content_sha256 == 目标 hash 且
canonical_path == import 目的地；staged 被清理；sources 表存在 hash=目标且 byte_size 正确的行；
活动的 location 指向该 document；raw+sidecar 字节 hash = staged hash。

## W02A-N1 / negative（scan 报 errors=1、files_seen=0，正种 scanner 但 root 级 seam 失败）

注入（harness 层）：scanner_module.scan_root_strategy 抛 ScannerFacadeError → 真实 scan_catalog
正常返回报告。

预期：报告 completion_status=`completed_with_errors`、errors==1、files_seen==0；
per_root_results 中 company_raw=failed 且 error_class=`scan_strategy_error`；
target_files 全部 registered=False（reason=`target_not_registered`）。
writer：抛 CanonicalImportError，文本含 `post-import scan failed: completion_status=
'completed_with_errors'`（scan 阶段错误，与 identity 失败阶段可区分）—— 不落成功 import、
无 usable handle；raw+sidecar 保留（hash 不变）；表内无目标 hash 的 source 行；
scan_runs 行 status=`completed_with_errors`（不是 interrupted——扫描正常返回）。

## W02A-N2 / negative（errors=0、files_seen>0，但只有别的文件被看到）

注入（harness 层）：scanner scan_root_strategy 过滤掉"样本公司" 的候选（真实逻辑、仅裁剪候选），
别家公司的一个健康原件（PAYLOAD_B，带 sidecar）被注册。

预期：报告 completion_status=`completed`、errors==0、files_seen>0（健康外观）；
target_files 对目标 hash 条目 registered=False、reason=`target_not_registered`；
别家公司 bytes（OTHER_SHA）确实出现 sources 行，目标 bytes 不出现（总文件数充足不构成目标
注册推定）。writer：抛 CanonicalImportError 含 `target_not_registered`；raw+sidecar 保留且
hash 等于 staged hash；表内无目标 hash 的 source 行。

## W02A-N3三分支 / negative

- **N3a（scan_run interrupted）**：harness 注入 scan_root_strategy 抛非 ScannerFacadeError 的
  RuntimeError（真实 wrapper 存续）。预期：writer 抛 CanonicalImportError 含
  `post-import scan failed (scan did not complete)`（区分于 identity 阶段）；
  scan_runs 最新行 status=`interrupted`、report_json 为 NULL；报告没有以任何成功形态返回
 （scan_reports 计数不增加）；raw+sidecar 字节保留；staged 保留。
- **N3b（部分 root 成功）**：两根（company_raw 健康 + archive_extra 注入失败），直接调用
  scanner 层 scan_catalog（mapper 注入仅 harness 内）。预期：报告 completion_status=
  `completed_with_errors`（绝不报 completed）；per_root_results 显示 company_raw=completed
  与 archive_extra=failed（error_class=`scan_strategy_error`）；company_raw 的已提交
  （active）locations 不被误删、archive_extra 旧 committed 行不因失败被删除（不做收缩清理）。
- **N3c（目标 identity 不符）**：scan 正常（目标真实注册：target_files registered=True），但
  harness 注入伪造 resolver 返回 reused_exact 且命中无关 handle（OTHER_SHA、伪造路径）。
  预期：writer 抛 CanonicalImportError 含 `exact_resolve_identity_mismatch`；拒绝在
  exact resolve 命中非目标身份时的成功；raw+sidecar 保留；staged 保留；DB 中没有任何
  bogus source 行（伪造仅存在于 resolver 结果对象，不落库）。

## 退出判据映射

- writer 不能忽略错误/中断/未注册目标：N1（completed_with_errors 拒绝）、N2
 （target_not_registered 拒绝）、N3a（interrupted→scan 阶段失败）、N3b（部分成功不靠绿）、
 N3c（identity 一致性）各有一处被测 gate。
- scan 成功与 exact resolve 成功分别有原始证据：P1 的 scan-return-contract（completion/target
 注册）与 target-registration.sql-results（sources/locations/documents 行）与 raw 证据分离。

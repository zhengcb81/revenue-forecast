# I-02-D / a20260919-01 — Independent Review

日期：2026-09-19。reviewer：独立复核（只读 + iso venv 重跑 + 复算 hash；除本 review.md 外无写）。

## 结论：**ACCEPT**

依据 card_I-02-D.md 全部核对点逐条通过；产出与 oracle.md 冻结预期一致；产品改动限于
canonical_writer.py 的 dedup 分支，未扩大恢复授权、未加新锁、未伪报幂等成功。

## 逐核对点

1. **重跑与抽验**：attempt cwd 下 `iso/venv/Scripts/python.exe -X utf8 scripts/w02d_cases.py`
   → rc=0，`failed_cases: []`（8 case 组全过，含 P2 两进程）。
   - **P2 two-process-trace**：两 worker 为真实 `subprocess.Popen` 进程（独立 PID、独立
     退出码）：worker1 exit=0 status=reused（幂等成功，REUSED_EXACT 同一 source_id）；
     worker2 exit=2 status=setup_exception error_type=CatalogOperationLockedError
     （"catalog operation already running: pid=…"，明确可重试锁竞争）。共享 catalog
     sources/documents/locations 各 1 行；journal 1 行可读无损坏。符合 oracle P2.1–P2.4。
   - **logical-rows-vs-attempts**：P1 四次调用 SQL 逻辑层恒为 sources=1 /
     documents(active)=1 / locations(active original_primary)=1，而 journal attempts
     按真实 outcome 落行（registered_existing_raw 1 行 + reused_before_download 1 行，
     同内容 hash 去重）——审计保留不压缩、业务资产唯一，符合 oracle I0.3/I0.4 与
     decision §1 冻结的「完成键 vs attempt 键」双层语义。
   - **N1**：实测报 `CanonicalImportError: canonical file was written but exact
     provider identity did not resolve`（I-02-A 冻结词汇，见 I-02-A decision 错误信封表
     及 I-02-A/I-02-C 既有产物原文）；`staging_kept=true`（恢复证据保留）；journal 无
     deduplicated_after_download 成功行；逻辑层 0 新行；provider 计数 0。补齐了
     DEDUPLICATED 未成功返回证据。
2. **oracle.md 具体且冻结在先**：mtime oracle.md 15:41:06 < iso/override/
   canonical_writer.py 修改 15:44:40（其余 override 为 15:40:19 的 I-02-C 基线拷贝、
   本卡零差异）；runner 脚本 自 15:41:5x 起未再改（重跑前后 hash 与 handoff 一致）。
   expected 独立推导（样本 hash 取卡/binding 固定值、错误短语取 I-02-A/C 冻结词汇表、
   逻辑行数用 runner 内直连 sqlite3 的独立 SQL，不经被测 store API）——不似被测函数生成。
3. **changes.diff 与 iso 源码**：
   - 独立 diff（I-02-C accepted baseline vs 本卡 override）逐字节复核 == changes.diff
     Part 2：唯一产品 delta 为 canonical_writer.py import_staged dedup 分支；
     **acquisition_service.py / acquisition_journal.py 零差异**（diff 输出为空）。
   - dedup 语义核对（iso/override/canonical_writer.py:166-216）：命中既有同 bytes 后，
     先以 **下载自身身份**（candidate.provider / candidate.provider_document_id，与 import
     成功路径同语义）构建 exact_request → resolve 必须 REUSED_EXACT 且 match 的
     content_sha256 == receipt hash、canonical_path == 既有 canonical → 证明通过后才
     `_remove_staged` 并返回 DEDUPLICATED；任一失败抛 CanonicalImportError 且回路径
     **先于 `_remove_staged`**（staging 的清理时点晚于可恢复证据的持久化/核证）。未命中
     exact 成功绝不返回 DEDUPLICATED 成功。未沿用 caller request 身份（避免异身份搭车）。
   - 未加新锁：仅现行 `CatalogOperationLock(canonical_import)`；lock.py 与 I-02-C 基线
     零差异；无 worker scope 锁复制。I-04 owner-scope open 保留。
4. **生产未触碰**：`git -C company-wiki status --porcelain src/company_wiki/source_catalog/`
   为空；prod 三源文件 SHA256 与 binding 卡锚点逐一相符（c23a93… / 017ca7… / 104d73…）；
   tests/contract/ 目录也干净。samples/real_roots 四文件逐个重算 sha256+size 与卡固定值
   + sidecar hash 一致（HK ffd73376…/4405561、sidecar 8228741d…、US e3de0053…/8585615），
   全程只读。
5. **自评未决项三条如实**（handoff.json）：① 跨进程锁 owner-scope → I-04（本卡未新增锁，
   已核实）；② CLI 层并发 harness 不在本卡（服务级双进程 barrier 已证 P2）；③ N2a 变体
   文件名 same.pdf 与既有 canonical 无碰撞（新 hash 走 hash-suffix 纠偏），同路径冲突
   属 I-02-A 既有契约范围——三条与实测/代码一致，无隐藏未报。
   **N3a dayu 同 bytes**：实测 IMPORTED_NEW、canonical 落 company_raw、dayu 副本原样——
   与契约测试 `test_writer_dedup_ignores_dayu_portfolio_locations`（CW tests/contract/
   test_source_catalog_canonical_writer.py:316，断言 IMPORTED_NEW + canonical 不落在
   portfolio）界定一致。N3b（register 路径 retired → `existing_raw_status_not_active`
   拒绝、spy 证实 `_reactivate_if_retired` 计数 0）与 N3c（import 路径 Phase 15.6 显式
   重获权）边界均按 I-02-C 契约原样保留——**未扩大恢复授权**。
6. **越界实现核查（退出判据）**：未发现「幂等=删除审计历史」（P1 审计行保留、journal
   append-only 内容 hash 去重语义与 acquisition_journal.py:87 现行一致且本卡零改动），
   也未发现「跳过 exact resolve」（dedup 分支反而**新增** exact-resolve 资格+identity
   校验，只有通过才报成功）。幂等建立在业务资产与资格稳定之上，符合卡退出判据。

## 限定申明

- 本次接受授予的权限范围 = **同 bytes 幂等重入根（同 request 重入、同 bytes 同身份
  dedup 资格、staging 恢复证据时点）这一类资格**；仅此。
- **不授予**跨进程锁资格（锁机制变更需 D-W02 及 I-04 owner 确认；I-04 owner scope
  保持 open）；监管/并发设计（CLI 层并发 harness、acquisition 级独立锁）留 I-02-E/I-04。

## Reviewer notes（披露）

- 复核重跑会按 commands.json 设计**原位再生成** after/idempotency-matrix.json、
  two-process-trace.json、logical-rows-vs-attempts.json、case_results.json、
  case_scratch_retained/ 及 raw-cli-logs 的 P2 日志（%TEMP% scratch 树一并重建）。
  重跑前已先只读记录全部 committed 证据（worker1 pid38244 exit0/reused、worker2
  pid41228 exit2/CatalogOperationLockedError、共享计数 1/1/1、journal 1 行、N1
  staging_kept=true 等）；重跑后各值除 P2 进程 PID（41756/40068，进程本身敏感）外
  与重跑前记录完全一致。属命令定义内的验证行为，非范围外写入。
- 生产仓库另有 CLAUDE.md/README.md/.coverage/coverage.json 未提交改动，均不在本卡
  允许路径（src/company_wiki/source_catalog/ 与 tests/contract/ 干净），与本卡无关。

## 复核抽验记录（本 review 独立执行）

- 重跑命令：`iso/venv/Scripts/python.exe -X utf8 scripts/w02d_cases.py`，cwd=attempt，RC=0。
- hash 复算：prod 3 文件、iso/override 17 文件、scripts 3 文件、samples 4 文件——与
  handoff.json / binding.json / hashes.json 全部一致。
- 独立 diff：I-02-C accepted baseline vs 本卡 override（canonical_writer / acquisition_service /
  acquisition_journal 三文件）== changes.diff Part 2 声明。

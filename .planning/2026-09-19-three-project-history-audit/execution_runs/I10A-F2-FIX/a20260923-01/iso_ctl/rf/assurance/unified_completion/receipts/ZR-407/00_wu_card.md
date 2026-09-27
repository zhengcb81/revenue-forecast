# ZR-407 工作单元卡（preflight）— authorization-bound GapPlan / CloseGap：missing 与 newer_revision

- 领取时间：2026-08-18T21:12Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态 `assurance/unified_completion/state.json`；`current_next=ZR-407`，`ZR-406.status=accepted`，`closure.next=ZR-407`。
- Lease：`ZR-407` / `zr407-implementer` / nonce `cca57044767a444ab807c9d4630ace10` / TTL 1800s。
- 冻结输入：`python -m uc.cli manifest-verify` → `OK: all frozen inputs re-verified offline`。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 已有旧版时，用户获得的授权必须只用于当前 `GapPlan` 中精确列出的新修订版；未授权时 discover/fetch/commit 均为零。该卡使 `missing ∪ newer_revision` 都成为授权闭环的 actionable set，而不把“已有旧文件”伪称为“最新”。
2. **production entrypoint 是什么？** filing-fetch `scripts/fetch_filing.py::resolve_filing` 的 `ensure` GAP 分支 → `_close_gap_and_return_handle` → company-wiki CLI `close-gap` → `CloseGapTransaction.execute`。`GapPlan` 纯函数只提供输入，不是下载生产入口。
3. **哪个 current-triplet 行为是 RED？独立 oracle 是什么？** 当前 filing-fetch 仅以 `gap_plan["missing"]` 决定是否调用 close-gap（`fetch_filing.py:765-771`）；company-wiki 的外锁/内锁重验均只检查 `current_plan.missing`（`close_gap.py:237,362`）并选取 `missing[0]`（:251）。因此 `newer_revision=[candidate], missing=[]` 在具备精确、未过期授权时仍零次 close-gap/fetch。Oracle 是 subprocess spy（close-gap argv / binding JSON）及 adapter `fetch_calls`，不是返回状态推断。
4. **允许改哪些文件？**
   - `company-wiki/src/company_wiki/source_catalog/close_gap.py`
   - `company-wiki/tests/contract/test_close_gap_fc801.py`（或新 `test_zr407_*` 合同测试）
   - `filing-fetch/scripts/fetch_filing.py`
   - `filing-fetch/tests/test_fc802_gap_orchestration.py`
   - **用户于 2026-08-18 明确授权的 gate 修复扩展：** `company-wiki/src/company_wiki/source_catalog/cli.py`、`company-wiki/tests/contract/test_zr407_ensure_readonly.py`（或最小相邻合同测试）。仅限无 `--allow-download` 的 `ensure` 只读 missing/reuse 路径；不得改变有授权下载、close-gap、canonical writer 或 acquisition journal 的写入语义。
   - `revenue-forecast/assurance/unified_completion/receipts/ZR-407/**` 与本卡的状态回执。
   - 绝对禁止：真实 catalog、production/外部 roots、provider discover/fetch、产品配置、冻结计划/registry、CI、schema版本、其它文件。
5. **下一单元解锁条件；本卡明确不做什么？** ZR-408 在本卡被 reviewer/closure 接受后才可领取；它拥有 staging→commit、recovery 与更广的并发下载验收。本卡不做真实下载、canonical writer 改造、multi-gap 批量下载（一次事务仍只执行一个精确、已授权 candidate）、future-root 生产切换（ZR-409）。

## 当前 triplet 与工作树

| repo | HEAD | dirty allowlist / verdict |
|---|---|---|
| revenue-forecast | `5e5902d762a0b2e6b89453465f9e26b9981d5361` | 既有未跟踪 assurance/audit 目录；本卡仅写 `receipts/ZR-407/**` 与 lock，绝不覆盖其它条目。 |
| company-wiki | `45ae72124cf6b26dec90b20d89f9bbbde2030074` | 既有 `.claude/settings.local.json` 删除、`llm_cost_log.csv`、`.coverage/`、`coverage.json`；均禁止纳入 diff。 |
| filing-fetch | `3087f28926fc36fd0cdad19a0fa0495de42f35ec` | clean。 |

PowerShell 的全局 ignore 文件与 wiki `.pytest_cache` 无读取权限，仅产生 Git warning；不是产品测试失败，也不触碰这些路径。一次检视命令在 `foreach (...) |` 处触发空管道 ParserError，已改为先赋值数组再格式化，后续不重复该语法。

## Current-state drift verdict：still_missing

- **F1：filing-fetch actionability 漏掉 newer_revision。** `has_missing` 是唯一开关；因此调用方已给 `authorization` 时仍返回结构化 gap，`close-gap` 子进程和 provider fetch 都未发生。
- **F2：company-wiki transaction 漏掉 newer_revision。** 外锁和内锁重验将 `missing=[]` 误当作 `gap_already_closed` / `gap_closed_by_concurrent`，并且 candidate 选择固定为 `missing[0]`。
- **既有防线必须保留。** `CloseGapBinding` 已绑定 request/gap/policy/provider/accession/caps/TTL；`validate_download_authorization` 再核 candidate provider、accession、TTL、items/bytes。ZR-407 复用这条验证链，不新建平行授权模型。

## Acceptance criteria 与 RED

1. **C1 actionable union：** `missing ∪ newer_revision` 的 deterministic candidate 集合；只有有该集合时 filing-fetch 才执行 authorized close-gap。`newer_revision`-only 的 RED 必须从 filing-fetch public `resolve_filing` 触发并检查 close-gap 子进程/binding。
2. **C2 exact authorization：** 事务在外锁和内锁重验都以同一 actionable set 判定；选中的 candidate 必须在 current plan 且 provider/accession 与 binding/TTL/caps 一致。将 binding 中允许但不在当前 plan 的 accession 作为 negative test，不能下载。
3. **C3 true-gap / idempotence：** 计划既无 missing 也无 newer_revision 时仍 zero fetch、`gap_already_closed`；修订版下载并 re-resolve 后第二次为 zero fetch。已有 missing 行为、stale gap/policy/authorization、并发 single-flight 不得回归。
4. **C4 zero authorization side effect：** 无 authorization 或 unauthorized accession 的 GAP 不执行 close-gap/provider fetch，返回结构化 GAP / rejected；不把 metadata discovery 当作 download。
5. **C5 user-authorized owner-gate repair：** 无 `--allow-download` 的 `ensure` 在 OS-read-only catalog 上不触发 `CatalogStore`/writer initializer，也不追加 acquisition journal；保持结构化 `resolution.status=missing`（或既有 reused 结果）且无 provider discover/fetch。写式 ensure / close-gap 仍显式初始化 writer。

## 执行与验证计划

- 先在两仓新增 public-entrypoint RED：filing-fetch revision-only auth 正例与无授权负例；wiki revision-only transaction、plan-external accession、empty actionable idempotence。
- 最小实现共享 `_actionable_candidates(plan)`，只使 `CloseGapTransaction` 与既有 binding 驱动的 staged request 识别 union；不改 `GapPlan` schema。
- focused：两仓新增/相邻 close-gap、gap-plan、FC-802 套件；随后 owner repo lint/format/unit/contract 与当前 triplet T1。无 T2/T3/T4 授权，本卡不得声明这些层通过。
- side-effect budget：真实 provider discover/fetch=0、真实 catalog mutation=0、external root writes=0、LLM/parser=0；测试只在 temp roots 运行。

## Stop conditions / handoff

- 任何需要多 candidate 一次性下载、修改 authorization schema、变更 staging/canonical commit、真实下载/生产 root 写入，立即停止并移交 ZR-408 或登记 ADR。
- 本卡实施者至多写 `independent_review`；reviewer/closure 才能标 `accepted` 并推进 ZR-408。

## 执行进度（2026-08-18）

- RED→GREEN 已完成：filing-fetch revision-only authorization 由 3 次子进程（未调用 close-gap）变为授权 close-gap；company-wiki revision-only plan 由 `fetch_events=0` 变为精确 candidate staging。相关 focused/相邻合同与 wiki unit 均绿，详见 `11_implementer_receipt.json`。
- owner gate 尚未关闭：filing-fetch 全套的 complexity ratchet 已由纯 helper 修正并复绿；real-tool conformance 的 `ensure` 在未开启下载时仍先强制 `get_catalog().store` 写式 SQLite 初始化（company-wiki `cli.py:1072-1077`），而测试配置指向只读生产 catalog；之后才可能追加 journal。该既有入口语义与本卡的零生产写入边界相冲突，未超范围修改。
- receipt validator 已复现并通过：本会话须使用 `PYTHONUTF8=1` / `python -X utf8`，并以仅本进程生效的 `GIT_CONFIG_COUNT=3` 及三个 `safe.directory` 值覆盖 revenue/filing/wiki。此前失败并非 SHA 不存在，而是路径解码后 Git 以沙箱账户触发 `dubious ownership`；该运行时配置未写入全局 Git 设置。receipt-validate 已返回 OK，仍未因 owner SQLite gate 而推进 state/closure。
- 用户已授权扩大本卡以修复 owner SQLite gate：仅处理 no-download `ensure` 的真实只读路径和 temp-root 合同测试；不得写入 production catalog、journal 或外部 roots。
- 授权扩展已完成：exact/no-download `ensure` 使用 `SourceResolver`/reader，返回原有结构化 `missing`/`reused` envelope 且 `attempt=null`，不触发 writer initializer 或 acquisition journal；`latest_as_of` 与 download-capable ensure 继续原写流程。目标 real-tool conformance 与 filing-fetch 全套均绿（358 passed、12 skipped、78 subtests），wiki 扩展合同/ratchet 与 787 unit 均绿。一次 1,631 项 wiki 全量 contract 仍有 18 个既有 sandbox/Windows/依赖环境失败；初始其中唯一 ZR-407 complexity failure 已由 `_run_ensure_command` 抽取后复绿，未把剩余项伪称为本卡回归。
- T1 current-triplet 已通过：`filing-fetch/tests/test_e2e_isolated_wiki.py` 在受控 temp roots/catalog 中 15 passed，以真实 filing-fetch 与 company-wiki subprocess 覆盖 CN/US/HK reuse、missing、身份故障、锁、暂停 worker 等路径；没有 T2/T3/T4 声明。

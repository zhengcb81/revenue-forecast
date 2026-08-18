# ZR-408 工作单元卡（preflight）— CloseGap staging → validate → canonical commit / recovery

- 领取时间：2026-08-18T22:13Z（UTC）。
- 唯一入口：`audit_review/README.md` §0 与机器状态 `assurance/unified_completion/state.json`；两者均为 `current_phase=D_lifecycle_roots_freshness`、`current_next=ZR-408`，并且 ZR-407 已 accepted / closure→ZR-408。
- Lease：曾以 `ZR-408` / `zr408-implementer` / nonce `f3dcf95859e14d9aae322de8d170fe91` / TTL 900s 领取；用户要求收尾时已显式 release，当前 state 为 `active_owner=null`、`lease=null`。
- 首次 lock 调用未设置 `PYTHONPATH=assurance/unified_completion`，报 `ModuleNotFoundError: uc`；未变更任何状态。按 README 的受控入口补齐该进程环境后 lock-acquire 成功。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 对一个精确、已授权的 GapPlan candidate，下载必须先在受控 staging 中完成验证，随后只向 canonical `companies/` 根提交；提交后重新解析确认实际可读。并发请求不能重复 fetch/commit；中断后同一 binding 必须能安全恢复，成功重跑不得再次下载。
2. **production entrypoint 是什么？** `company_wiki.source_catalog.cli::main` 的 `close-gap` 分支 → `CloseGapTransaction.execute` → `_fetch_and_commit` → canonical writer import / journal finalization → `SourceResolver.resolve` 的 re-resolve。`GapPlan` 与测试 adapter 仅是输入/测试替身，不是生产写入口。
3. **哪个 current-triplet 行为是 RED？独立 oracle 是什么？** 尚未假定存在缺口。先以现有 FC-801/FC-804 合同在临时 catalog 复跑，逐项检查：实际 adapter `fetch_events`、writer/import call、canonical 文件根、journal/re-resolve 结果以及独立进程/线程并发计数。若当前行为已覆盖任何目标，仍须寻找未由 oracle 覆盖的中断或 root-containment 反例，才可决定最小 RED；不得以旧测试名称代替证据。
4. **允许改哪些文件？** `company-wiki/src/company_wiki/source_catalog/close_gap.py`、其直接的 canonical writer/recovery helper（仅发现具体缺口时）、`company-wiki/tests/contract/test_close_gap_fc801.py`、`company-wiki/tests/contract/test_close_gap_concurrency_fc804.py` 或一个最小 `test_zr408_*` 合同测试；以及 `revenue-forecast/assurance/unified_completion/receipts/ZR-408/**`。绝对禁止：filing-fetch、真实 provider、production/external catalog root、配置、冻结计划/registry、CI、schema 版本和其它产品文件。
5. **下一单元解锁条件；本卡明确不做什么？** 只有 C1–C4 的 temp-root 证据、独立复核及 closure accepted 后才解锁 ZR-409。该卡不变更 `future_lake` 配置或生产根，不扩展授权模型，不进行真实下载，也不支持一次 transaction 的多 candidate 批量下载。

## Acceptance criteria / side-effect budget

- **C1 staging / canonical containment：** payload 在 staging 验证后才可 import，最终写入仅在 `companies/` canonical root；失败不得留下可解析的半成品。
- **C2 re-resolve / idempotence：** commit 后必须用 resolver 确认同一实际 source；成功后的相同 binding 再跑为 zero fetch / zero canonical commit。
- **C3 single-flight：** 两个并发的同 binding 请求最多一次 fetch 和一次 canonical commit，第二方得到明确的并发/已完成语义。
- **C4 recovery：** fetch、validation、import 或 finalization 中断均有可检查 journal/状态；重跑 fail-closed 或幂等恢复，不能双写或把未验证文件当成功。
- **预算：** 真实 provider discover/fetch=0；真实 catalog / production / external root 写入=0；只允许测试 fake adapter 与受控 temp roots 写入；LLM/parser=0。

## 执行计划与停止条件

1. 复跑现有 FC-801/FC-804，读取实现与测试 oracle，记录基线。
2. 仅当定位到可复现的 ZR-408 语义缺口时，先写最小 RED，再实现最小修复并在 temp roots 验证。
3. 对每一种失败注入至少检查 fetch/import 计数、可解析性和二次运行，而非只断言返回字符串。
4. 所有新增临时目录均在 `revenue-forecast` writable root 下，验证后以精确路径清理。若需要真实 provider、变更 root policy/配置、或多 candidate transaction，立即停止并移交 ZR-409 / ADR。

## 执行进度 / 停止点（2026-08-18）

- 基线：`test_close_gap_fc801.py + test_close_gap_concurrency_fc804.py` 为 13 passed（仅测试 temp roots；pytest cache permission warning）。
- 发现与补强：历史 FC-804 的 single-flight 只以两个线程共享同一 transaction 覆盖，不能单独证明跨 CLI 进程的文件锁。已仅修改 FC-804 合同测试：新增 Windows `spawn` 双进程用例，每个 child 新建 catalog/coordinator/writer，两个 child 共享 binding/temp root。独立 adapter fetch log 必须为一条、两结果 `fetch_events=[0,1]`、documents=1；首次单跑通过。
- 合集：FC-801 + FC-804 + canonical writer 为 **20 passed**。`ruff check --no-cache` 针对改动文件通过；格式化检查会重排整份既有 FC-804，未进行无关全文件格式化。
- 结论：未定位需修改产品 source 的 RED；新增的进程级 oracle 验证当前 file-lock 实现。未写 provider、真实/production catalog、外部 root、配置、授权模型或冻结输入。
- 未完成：两次 `tests/unit` 在工具 30 秒回传边界中截断且无 exit code，不能作为 owner-suite 通过；停止其 Python PID 20528/25964 被 Windows 拒绝，25964 后续退出而 20528 尚可见。收尾时已释放 `ZR-408` lease；不写 implementer receipt、不申请 review、不推进 closure；待有该进程权限的后续会话先核实/清理精确 temp roots 后再作业。

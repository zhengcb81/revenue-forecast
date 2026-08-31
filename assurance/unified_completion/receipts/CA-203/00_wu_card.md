# CA-203 工作单元卡（preflight）— H：Weekly/发布前 T3

- 领取时间：2026-08-31T14:49Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-203`（CA-202 closure → CA-203）；锁 CA-203（owner=ca203-implementer，nonce 26c3423b…）。
- 依赖：ZR-805（T3 下载授权，accepted ✅）、CA-107（accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H CA 部分第二卡——Weekly/发布前 T3（registry："真实 CN/HK/US provider 首次授权下载、二次零下载、amendment、single-flight 和 provider drift；报告≤7d；blocked 也阻断 release 并发告警；provider/canonical 调用精确对账"）。现状缺口（RED）：ZR-903 有 schedule 层（ledger/blocked）；ZR-805/FC-805 有授权下载与三市场；无"首次下载→二次零下载→amendment→single-flight→provider drift→对账"组合验收。
2. **production entrypoint 是什么？** filing-fetch `tests/test_e2e_download.py`（opt-in T3 真实下载套件）；revenue `tools/weekly_t3_schedule._suite_outcome/run_weekly`（blocked 永不 pass）；IsolatedWiki + spy adapter（真实跨进程 json_command_v1，LT-01~09 语义）。
3. **RED？** glob tests/**/*ca203* → 零命中；无 T3 全语义组合验收。
4. **允许改哪些文件？** revenue：新 `tests/test_ca203_weekly_t3.py`；receipts/CA-203/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实网络下载（opt-in T3 套件不触发）、Task Scheduler、真实 wiki 写。
5. **下一单元解锁？** CA-204（Monthly 泛化审核）→ CA-205/206。本卡不做：真实 provider 网络下载（部署/授权动作）、Windows 调度注册。

## Acceptance criteria

- **C1 套件纪律门 + blocked 语义**：T3 套件 opt-in only（FILING_FETCH_E2E_DOWNLOAD=1 + skipUnless）+ 三市场 + 损坏拒绝 + 二次零下载语义存在；_suite_outcome：all-skipped → blocked（永不 pass）、exit≠0 → not-ok、passed → ok。
- **C2 首次授权下载 + 二次零下载（LT-09/DL-04/single-flight）**：spy wiki 首次 capture_ready + fetch=1 + bytes>0；二次同请求 status=gap + missing=[] + fetch 仍 1 + bytes 不变。
- **C3 amendment（LT-02）**：as-of 切换新 accession 后只下载缺失的新期间（fetch +1）。
- **C4 provider drift（LT-05）**：provider_unavailable 时本地复用保留 + 零新 fetch（不伪造 pass）。
- **C5 provider/canonical 精确对账**：fetch actions == downloaded_new journal outcomes == bytes 记账；二次请求后三者均不变。
- **C6 质量门（卡级）**：相邻回归（ZR-903/805/fc1103）零回退、revenue 全量零回归（基线 937+106）、ruff clean、独立 reviewer 复放。产品代码零改动、真实 T3/调度零触发。

## 边界

- IsolatedWiki（temp wiki + spy 跨进程真实 adapter）；零网络、零真实 wiki 写、零 Task Scheduler；opt-in T3 套件仅结构检查不执行。

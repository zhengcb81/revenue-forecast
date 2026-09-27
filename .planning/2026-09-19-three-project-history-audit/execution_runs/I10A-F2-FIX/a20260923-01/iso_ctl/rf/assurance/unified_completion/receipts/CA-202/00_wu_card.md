# CA-202 工作单元卡（preflight）— H：Daily T2 实际 scheduler

- 领取时间：2026-08-31T14:24Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-202`（ZR-1009 closure → CA-202，DAG 权威：阶段 H CA 部分解锁）；锁 CA-202（owner=ca202-implementer，nonce 1cfc9275…）。
- 依赖：ZR-806（真实 T2 三 root 样本，accepted ✅）、CA-107（closure 2.0，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H CA 部分首卡——Daily T2 实际 scheduler（registry："真实 Windows runner 每天抽样 companies/dayu/Dropbox unique 样本，测试 Reader/live WAL、exact reuse、artifact/readiness、零写、锁和 SLO"）。现状缺口（RED）：ZR-902 有 schedule/ledger/freshness 纯逻辑；无"真实 runner 对 production catalog 的完整报告（checks/triplet/ok）+ 三 root unique 样本 + 零写 oracle + 只读连接/SLO + 缺 run 告警/阻断 release"组合验收。
2. **production entrypoint 是什么？** `tools/daily_t2_runner.run_checks`（真实 catalog mode=ro + PRAGMA query_only：triplet/policy freshness/samples/scan health/legacy hits/latency/roots fingerprint/trends）；`tools/daily_t2_schedule`（ledger/freshness/alert/release_gate）；company-wiki SourceResolver（三 root 只读 resolve）。
3. **RED？** glob tests/**/*ca202* → 零命中；ZR-902 无真实 runner 报告验收；无"三 root unique 样本 + 零写 + SLO"组合。
4. **允许改哪些文件？** revenue：新 `tests/test_ca202_daily_t2_runner.py`；receipts/CA-202/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog 写、Task Scheduler 注册/删除（部署动作）、下载、LLM。
5. **下一单元解锁？** CA-203（Weekly T3）/CA-204（Monthly 泛化）→ CA-205/206。本卡不做：真实调度任务注册（部署）、T3 下载（CA-203）。

## Acceptance criteria

- **C1 真实 runner 报告**：run_checks 对 production catalog（mode=ro）产出完整报告 {run_id/checks/triplet/ok}；triplet 精确等于三仓真实 HEAD；checks 含 triplet/policy_freshness/samples/scan_health/latency/roots_fingerprint；exit ∈ {0,1} 不崩溃；samples bound_artifacts≥3 + producer_events≥3。
- **C2 零写 oracle**：run 前后 catalog 行数（documents/sources/locations）与三 root 浅指纹不变（ZR-806 oracle）。
- **C3 unique 样本**：production resolver 只读：companies 紫金 FY2025 REUSED_EXACT、dayu 金斯瑞 1548 FY2021 REUSED_EXACT、Dropbox 星环 fail-closed MISSING。
- **C4 锁/SLO**：只读连接（query_only，写尝试抛 OperationalError）；runner 采样延迟 < LATENCY_P95_BUDGET（5s）。
- **C5 缺 run 告警/阻断**：ledger missing/stale(>24h)/not-ok → alert 追加 + release blocked；fresh+ok → ready。
- **C6 质量门（卡级）**：相邻回归（ZR-902/806/1004）零回退、revenue 全量零回归（基线 927+106）、ruff clean、独立 reviewer 复放。产品代码零改动、Task Scheduler 零触碰。

## 边界

- production catalog 只读（mode=ro + query_only）；Task Scheduler 注册/删除为部署动作不在本卡（task_status 只读）；零网络、零下载、零 LLM。

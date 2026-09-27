# ZR-001 工作单元卡（preflight）— current triplet 冻结与生产反例重放

- 领取时间：2026-08-14T02:25Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-001`；units.CA-109.status=accepted + closure.next=ZR-001。
- 依赖：无（registry 依赖列=无）；按 README §7，治理部分（计划锁、triplet、历史处置）已由 CA-001～004 实现，本卡只补产品 drift 重放并引用 CA receipt。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** A0 基线：把三仓 current triplet 冻结为唯一验证基线，并把“紫金 exact reuse、旧 artifact、Dropbox、draft renderer”等生产反例在当前代码上逐项重放分类，使 phase C+ 的 RED 有诚实基线（P03/P06/P07/P11）。
2. **production entrypoint 是什么？** revenue `scripts/revenue_forecast.py` / `generate_input_template.py` / `lint_input.py` / `run_forecast`+`render_markdown`；wiki `CatalogStore`（resolve/query 的构造路径）；filing `validate_handle` / `_run_company_wiki_json`；真实 catalog `company-wiki/.source_catalog/catalog.sqlite3`（只读 SQL）。
3. **哪个 current-triplet 行为是 RED？** 反例本身即 RED：generator 骨架被 linter/engine 拒绝；`--validate-only` 写 676B registry；draft 被公共 renderer 拒（gate_ids mismatch）；publication 先注册后写文件（孤儿/重复行）；CatalogStore 构造不存在 DB 会创建 237,568B 写库；OS 只读 DB 上 resolve 失败；外部 root handle 被 companies 默认拒绝；raw `database is locked` 被标 fatal；catalog 中 artifact 绑定/sidecar 污染/prompt review 缺口。
4. **允许改哪些文件？** `assurance/unified_completion/replays/**`（重放脚本+evidence）、`receipts/ZR-001/**`、`tests/test_zr001_drift_ledger.py`。禁止：三仓产品代码/配置/CI、真实 catalog 与 roots 的一切写入、旧计划文件。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-002/ZR-003/ZR-004（依赖 ZR-001）。本卡不修复任何反例：修复归属 ZR-201～710 各卡；本卡只分类并登记 successor。

## 领取前机械门（弱模型清单 §2）

- [x] CA-109 accepted（机器状态 2026-08-14T01:54:49Z；closure.next=ZR-001）。
- [x] 三仓 HEAD 冻结（本卡三重取）：revenue `dc41ef335b0c71fc22610201b235a33528d3e950`（fcap）；filing `83c638e76e40890262746cdf02b6df495dcb4031`（fcap）；wiki `ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875`（fcap）。
- [x] dirty allowlist（均为用户/环境侧既有，非本卡产物）：revenue 见 `git status`（planning 文件 + 计划目录，未纳入 diff）；filing 空；wiki `.claude/settings.local.json`(D)、`llm_cost_log.csv`(M)、`.coverage`(?)、`coverage.json`(?)。
- [x] 真实 catalog 只读策略：所有查询 `mode=ro` + `PRAGMA query_only=ON`；before/after size+mtime 指纹记录在 evidence 内。
- [x] manifest-verify 严格 OK（CA-001 基线，本卡未改任何冻结输入）。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（控制面）；三仓产品只读重放。
- **Current-state drift verdict**：`still_missing`——尚无 current-triplet drift_ledger。
- **Acceptance criteria**：`drift_ledger.json` 存在且逐项带四分类（still-failing/already-satisfied/superseded/blocked）+ 新证据 hash + successor；禁止仅引用旧 receipt；真实 catalog 零写入指纹。
- **Stop conditions / handoff**：生产 catalog/root 写入、网络/provider 调用、旧计划修改 → 立即停止并 blocked。

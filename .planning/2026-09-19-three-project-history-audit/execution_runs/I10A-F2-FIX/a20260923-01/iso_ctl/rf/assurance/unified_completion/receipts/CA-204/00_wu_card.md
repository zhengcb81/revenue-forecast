# CA-204 工作单元卡（preflight）— H：Monthly broker/mine/forecast 泛化审核

- 领取时间：2026-08-31T15:11Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-204`（CA-203 closure → CA-204）；锁 CA-204（owner=ca204-implementer，nonce 3e968e23…）。
- 依赖：ZR-510（attribution，accepted ✅）、ZR-609（Zijin pilot，accepted ✅）、ZR-709（紫金 journey，accepted ✅）、CA-107（accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H CA 部分第三卡——Monthly broker/mine/forecast 泛化审核（registry："轮换真实 broker 样本、紫金 shadow、第二矿企、非矿企；复验表格/错归、逐矿 bridge、draft/formal、backtest/confidence；报告≤35d；样本 registry 固定+轮换；样本缺失是 blocked；产品代码特例扫描为 0"）。现状缺口（RED）：ZR-609/709/713 分项存在；无 Monthly 泛化一体验收。
2. **production entrypoint 是什么？** revenue 全链（MineYearOperation → commercial_terms → asset_ownership → reconciliation → prepare_forecast draft/formal → create_snapshot/validate_snapshot → rolling backtest）；confidence_policy；golden_corpus.json 冻结样本 registry。
3. **RED？** glob tests/**/*ca204* → 零命中；无固定+轮换 registry/缺失 BLOCKED/零硬编码组合验收；scripts/ 当前零硬编码（紫金矿业/601899 ZERO）。
4. **允许改哪些文件？** revenue：新 `tests/test_ca204_monthly_generalization.py`；receipts/CA-204/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、registry 写、下载、LLM、真实 catalog 写。
5. **下一单元解锁？** CA-205（原子报告/freshness/告警/release 消费）→ CA-206（soak）。本卡不做：真实 Monthly 调度（部署）、自然时间累积（CA-206）。

## Acceptance criteria

- **C1 固定+轮换样本 registry**：golden corpus 12 samples（broker 7 含 changjiang 多实体比较 + audited_filing 2 + revenue anchors）全部冻结 sha256；缺失样本 → BLOCKED 永不 pass（AUD2-05）。
- **C2 紫金 shadow journey**：draft 零写 → formal bit-identical replay → mine 贡献 reconcile 到 segment（reconciled_modeled）。
- **C3 第二矿企泛化**：纯金生产商（单层 100% 链、单货币）F2 链闭合（operation→terms→ownership→reconcile）。
- **C4 非矿企泛化**：direct_growth/unit_sales 非矿模型走生产引擎路径（trading segment 5 年正值 + model 层手算 110/121）。
- **C5 表格/错归复验 + 零硬编码**：changjiang 多实体 anchor 冻结（含紫金实体）；broker corpus ≥7；scripts/ git grep 紫金矿业/601899 → ZERO。
- **C6 backtest/confidence**：snapshot 往返同 id + confidence_policy 资产在（detect_gaming_mutations/recompute_rating/validate）。
- **C7 质量门（卡级）**：相邻回归（ZR-609/709/713）零回退、revenue 全量零回归（基线 945+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 纯内存/本机计算；registry 只读；零网络/下载/LLM；不生成真实 Monthly 报告（部署动作）。

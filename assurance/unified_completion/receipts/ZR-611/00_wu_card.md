# ZR-611 工作单元卡（preflight）— F2：通用多矿合成 E2E

- 领取时间：2026-08-22T06:50Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-611`，ZR-608 accepted + closure→ZR-611；锁 ZR-611。
- 依赖：ZR-605~608（✅ 输入合同/商业量价/内部流/对账）+ ZR-610（✅ 会计 ADR）。Registry 依赖列=ZR-605~608,ZR-610。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 通用多矿合成 E2E——把 ZR-601~608+610 的全部契约层组合成一个合成多矿公司的完整旅程，验证 8 类场景（控股/权益法/多金属/内供/跨币种/爬坡/gap/residual）每类公式/对账/突变可重算；生产代码零公司/矿名硬编码。
2. **production entrypoint 是什么？** 组合既有模块：mine_year_operation + commercial_terms + asset_ownership + internal_flow + reconciliation + model_registry——test-only E2E 钉死全链。
3. **RED？** 无单一产品缺口——RED = 组合旅程不存在（8 类场景未串起来）。探针：每模块单测已绿，但无跨层合成验证。
4. **允许改哪些文件？** revenue：新 `tests/test_zr611_synthetic_e2e.py`（合成多矿 E2E）；若探针发现组合缺口则修对应模块；revenue receipts/ZR-611/**。禁止：公司/矿名硬编码进生产代码、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-609（紫金 pilot 合流）。本卡不做：真实紫金数据（ZR-609）、第二家公司泛化（ZR-609 后半）。

## Acceptance criteria
- **C1 八类场景可重算**（杀 RED）：合成多矿公司（2 矿 + 控股链 + 多金属 + 内部流）全链旅程——每类场景公式/对账/突变确定性可复现：
  - 控股：effective_group_share 链式连乘（60%×70%=0.42）
  - 权益法：apply_ownership_share basis 语义（one_hundred_percent 恰一次 / equity_share 拒绝）
  - 多金属：byproduct 独立加项不重复计价
  - 内供：eliminate_internal_revenue gross/net 桥
  - 跨币种：FX 折算
  - 爬坡：多期 volume 爬坡 → 收入逐年变化
  - gap：缺字段 fail-closed（不默认 0）
  - residual：reconcile 不闭合 → gap 回退（不伪造）
- **C2 生产代码零硬编码**：grep 生产 scripts/ 无公司/矿名（zijin/kamoa/porgera 等）——合成场景只存在于测试。
- **C3 全链一致性**：MineYearOperation → derive_saleable_volume → commercial terms → ownership → elimination → reconciliation 每层手算一致。

# ZR-1009 工作单元卡（preflight）— I：legacy 路由/代码删除门（阶段 I 收官卡）

- 领取时间：2026-08-31T13:47Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1009`（ZR-1008 closure → ZR-1009）；锁 ZR-1009（owner=zr1009-implementer，nonce b407350c…）。
- 依赖：ZR-1008（cutover，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 收官卡——legacy 路由/代码删除门（registry："≥2 动态周期 zero-hit、CodeGraph caller=0、N-1 结束批准；删除后全矩阵/回滚绿；CA-304 唯一拥有"）。现状缺口（RED）：legacy_gate/codegraph_freeze/legacy_disposition 工具在位（CA-003/004/109）但无"删除门组合验收"（caller 诚实报告 + ≥2 周期 zero-hit + N-1 批准目标 + 删除后全绿）。
2. **production entrypoint 是什么？** `uc.legacy_gate`（三仓 caller 扫描/分类，successor CA-201）；`uc.codegraph_freeze`（freeze/verify：commit 绑定 + 统计相等 + sentinel 查询）；`uc.legacy_disposition`（71 FC 处置 registry 验证 + closure_items）；真实三仓扫描 + scratch 三仓 codegraph CLI。
3. **RED？** glob tests/**/*zr1009* → 零命中；无"删除门"组合验收；真实扫描当前 callers_found（quality.yml→closure_ledger，2 findings）——诚实证明删除未批准。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1009_legacy_removal.py`；receipts/ZR-1009/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实代码删除（CA-304 唯一拥有）、registry 写、下载、LLM。
5. **下一单元解锁？** 阶段 J（CA-301~306：动态审核调度/发布/归档）。本卡不做：真实 legacy 删除（CA-304）、N-1 批准执行（人工/CA 流程）。

## Acceptance criteria

- **C1 caller 门**：真实三仓扫描结构（schema_version=1、verdict ∈ {isolated, callers_found}、findings 每条 severity=P2 + successor=CA-201）；callers_found 时 quality.yml 在 findings 中（删除未批准诚实状态）；scratch 干净仓库 isolated=True。
- **C2 ≥2 动态周期 zero-hit**：scratch 三仓两轮 freeze→verify 均 []（absent sentinel 零 hit + 无漂移）；删除符号重现 → verify fail-closed。
- **C3 N-1 结束批准**：frozen legacy_disposition 验证通过（71 FC 行、I/C/S/P 精确计数、每行 successor 已定义、合并图无环）；5 个 pending closure items（FC-150x）为 N-1 批准目标，CA-304 在 known_units 可达。
- **C4 删除后全绿**：删除 legacy 工具后旧 freeze verify ≠ []（索引统计漂移——删除被门检测）；新 freeze verify == []（矩阵可重放）；absent sentinel 零 hit；legacy-gate isolated。
- **C5 质量门（卡级）**：相邻回归（ZR-1001/1004/1007/1008 + assurance 工具 13）零回退、revenue 全量零回归（基线 918+106）、ruff clean、独立 reviewer 复放。产品代码零改动、零真实删除。

## 边界

- 真实三仓只读扫描（不修改）；scratch 三仓由 codegraph CLI 索引（temp）；不做真实删除（CA-304 唯一拥有）；零网络/下载/LLM。

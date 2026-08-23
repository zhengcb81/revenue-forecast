# ZR-1002 工作单元卡（preflight）— I：Reader 先上线（writer 保持原行为）

- 领取时间：2026-08-23T03:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1002`（ZR-1001 closure → ZR-1002）；锁 ZR-1002（owner=zr1002-implementer，nonce 2ba3186e…）。
- 依赖：ZR-1001（release 预备，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 第二卡——Reader 先上线（registry："Reader 先上线，writer 保持原行为；read shadow/golden/SLO；rollback 路由；无 schema/data 迁移"）。现状缺口（RED G1~G2）：company-wiki 已有激活机制（FC-202/203）、只读 reader（ZR-201/202）、rewiring（ZR-203），但无**端到端 golden 对比 + SLO 门 + rollback 旅程 + writer 保持 + 无迁移**的综合验收套件。
2. **production entrypoint 是什么？** company-wiki `activation.py`（apply/rollback + visibility_state active/shadow）+ `reader.py`（ReadOnlyCatalogReader）+ `assertion_service.upsert_verified_assertion`——测试在临时库走完整旅程。
3. **RED？** grep zr1002 → 零命中；无综合套件（既有测试为单点：FC-202 snapshot 语义/FC-203 事务/reader 只读查询/observability 延迟计算）。
4. **允许改哪些文件？** company-wiki：新 `tests/contract/test_zr1002_reader_first.py`；revenue：receipts/ZR-1002/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动（wiki src/ 与 revenue scripts/）、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** ZR-1003（lifecycle/safety/RootPolicy shadow assertions）。本卡不做：真实生产激活（部署动作——release owner 在发布窗口执行）、shadow 断言扩展（ZR-1003）。

## Acceptance criteria

- **C1 golden（杀 G1）**：临时库建断言 → apply_activation → ReadOnlyCatalogReader 读取 active 断言 == 激活前 store 查询的 golden 值（shadow→active 零漂移）。
- **C2 writer 保持原行为（杀 G2）**：激活后 upsert_verified_assertion 仍可写 + activation_journal apply 记录完整。
- **C3 SLO**：reader 查询延迟 < 冻结预算（5s）。
- **C4 rollback 路由**：rollback_activation → visibility 回 shadow（active 断言 reader 不可见）、行未删、二次回滚拒绝（ActivationError）。
- **C5 无 schema/data 迁移**：激活→回滚前后 catalog schema 版本与断言行数不变。
- **C6 质量门**：company-wiki 相关回归（activation/resolver/reader 套件）全绿 + revenue 全量零回归（基线 889 passed + 106 subtests）+ ruff + ratchet + 独立 reviewer 复放。产品代码零改动。

## 边界

- hermetic：临时 catalog；生产 catalog 零触碰。
- 真实生产激活 = 部署动作（release window 内由 release owner 执行，ZR-1001 授权机制已就绪）。

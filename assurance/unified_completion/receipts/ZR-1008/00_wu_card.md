# ZR-1008 工作单元卡（preflight）— I：source/revenue 新链 cohort cutover

- 领取时间：2026-08-31T13:22Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1008`（ZR-1007 closure → ZR-1008）；锁 ZR-1008（owner=zr1008-implementer，nonce 0539f658…）。
- 依赖：ZR-1007（mine shadow，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 第八卡——source/revenue 新链 cohort cutover（registry："用户旅程、draft/formal、SLO、side effects、rollback；观察期"）。现状缺口（RED）：ZR-701/705/709 有 draft/formal 与 journey 分项；无"新链 cohort cutover"综合验收（完整用户旅程 + draft/formal 分离 + SLO + 精确 side effects + rollback/观察期稳定性）。
2. **production entrypoint 是什么？** revenue `prepare_forecast`（draft 零写 / formal 注册，ZR-701）；`render_markdown`（draft 可渲染）；`build_publication_receipt`/`validate_publication_receipt`（ZR-705 门）；`publication_registry`（链式 line hash + 只读保护）；`create_snapshot`/`validate_snapshot`（回放）。
3. **RED？** glob tests/**/*zr1008* → 零命中；无"cutover 用户旅程 + SLO + side effects 精确计数 + rollback/观察期"组合测试。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1008_new_chain_cutover.py`；receipts/ZR-1008/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、registry 真实写（测试用 tmp 隔离）、下载、LLM。
5. **下一单元解锁？** ZR-1009（legacy 路由/代码删除，三仓，CA-304 唯一拥有）。本卡不做：真实生产 cutover（部署动作）、观察期自然时间门（ZR-1104）。

## Acceptance criteria

- **C1 用户旅程**：draft 渲染（markdown >500 字符、formal_output_mode=draft、零注册）→ formal 注册恰好 1 条（input_sha256/result_sha256 绑定）→ replay bit 一致（== + result_sha256 同）；snapshot 往返 replay 同 id。
- **C2 draft/formal 分离**：draft receipt gate_ids=[]；draft flip→formal 拒绝；formal gate_ids 非空 + attestation ∈ {host_signed, unattested}；formal 降级→draft 拒绝；无 VerificationContext 自签 formal 抛 TypeError。
- **C3 SLO**：draft+formal+replay 全程墙钟 < JOURNEY_SLO_SECONDS（60s 冻结预算）。
- **C4 side effects**：draft 零副作用（registry 不存在 + 无 stray 文件）；formal 恰好 +1 条（result_sha256 匹配 + validation_status=validated）。
- **C5 rollback/观察期**：删除 cutover 条目（_clear_read_only 后）恢复 cutover 前状态；观察期内同输入重放 result_sha256 不变（零漂移）+ 重新 formal 干净再注册；3 周期观察 bit 一致 + 每周期可审计 1 条。
- **C6 质量门（卡级）**：相邻回归（ZR-701/705/709）零回退、revenue 全量零回归（基线 908+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- publication registry 全部由 fixture 隔离到 tmp（conftest + registry_path fixture）；纯内存/本机计算；零网络、零下载、零 LLM；不生成真实生产 formal 注册。

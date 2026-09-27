# ZR-305 工作单元卡（preflight）— legacy artifact 五桶 dry-run/migration + 生产 SourceBundle 命中

- 领取时间：2026-08-17T22:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-305`；units.ZR-304.status=accepted + closure.next=ZR-305；`uc next` 解锁列表含 ZR-305。
- 依赖：ZR-304（accepted ✅）。Registry 依赖列=ZR-304。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D legacy 迁移。ZR-304 已建唯一 artifact read model 与 artifact_bindings；`artifact_backfill.py`（FC-901）已有五桶分类（bindable/hash_mismatch/missing_bytes/unknown_generator/legacy_unbound）+ dry-run/apply + 幂等/可逆测试（ab01~ab11）。本卡补齐 registry 要求的**端到端证据**：apply 后**真实 SourceBundle 命中**（`build_source_bundle` 消费绑定产物）、两次 dry-run 字节一致、100% legacy artifact 恰入一桶。
2. **production entrypoint 是什么？** 本卡测试/验收侧：`tests/contract/test_zr305_legacy_migration.py`（新测试，复用既有 backfill + source_bundle）；不改产品代码（FC-901 已实现五桶+apply）。若发现缺口则最小补。
3. **哪个 current-triplet 行为是 RED？** 无"apply 后真实 SourceBundle 消费绑定 artifact"的端到端测试（现有 ab 测试只验 bindings 行）；两次 dry-run hash 一致性未在 ZR-305 名义下显式钉死。
4. **允许改哪些文件？** company-wiki 新增 `tests/contract/test_zr305_legacy_migration.py`（如产品缺口则最小改 artifact_backfill.py/source_bundle.py）；revenue 侧 receipts/ZR-305/** 与 state.json。禁止：真实 catalog 写、下载、删除 artifacts、接生产入口。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-306（role DAG 最小失效）。本卡不实现 role DAG 失效（ZR-306）；不接生产入口。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-304 accepted（机器状态；closure.next=ZR-305）。
- [x] triplet 冻结（领取时重读）：revenue（ZR-304 closure commit 后）、filing `0e5d209…`、wiki `838fc46…`。
- [x] 现状代码事实：artifact_backfill.py 五桶 + dry-run/apply + ab01~ab11 测试（幂等、可逆、bucket 守恒、每 artifact 一桶）；source_bundle.build_source_bundle 消费 artifacts + registry 校验；ZR-304 read model 已归一。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（测试/验收）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——端到端 SourceBundle 命中测试 + dry-run 字节确定性显式钉死。
- **Acceptance criteria**：
  - 五桶 dry-run：100% legacy artifact 恰入一桶（bindable/hash_mismatch/missing_bytes/unknown_generator/legacy_unbound）；两次 dry-run 结果字节一致（确定性）。
  - apply 后真实 SourceBundle 命中：`build_source_bundle`（生产唯一 view）能消费已绑定 artifact 并产出 valid handle；未绑定/未通过校验的 artifact 进 invalid（fail closed）。
  - 不猜、不删、幂等、可恢复：apply 幂等（重复 apply 零重复绑定）；artifacts 表零删除；shadow 绑定可逆删除恢复（复用 ab10 语义）。
  - hermetic 测试全绿；wiki unit/contract 无回归；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、删除 artifacts、接生产入口 → 立即停止。

## Annex：测试矩阵（test_zr305_legacy_migration.py）

| 场景 | 断言 |
|---|---|
| 五桶 dry-run 全覆盖 | 每 artifact 恰一桶 + reason |
| 两次 dry-run | 结果 JSON 字节一致 |
| apply → SourceBundle 命中 | valid_handles 含绑定 artifact；invalid 含被拒 artifact |
| apply 幂等 | 重复 apply 零新增 binding |
| 不删除 | artifacts 行数不变 |
| 可恢复 | 删 shadow binding 后回退（不触碰 artifacts） |

# ZR-1005 工作单元卡（preflight）— I：legacy artifact 分桶与最小 canary backfill

- 领取时间：2026-08-23T13:05Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1005`（ZR-1004 closure → ZR-1005）；锁 ZR-1005（owner=zr1005-implementer，nonce e094dea7…）。
- 依赖：ZR-1003（shadow assertions，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 第五卡——legacy artifact 分桶与最小 canary backfill（registry："先 dry-run；不可证明不绑定；幂等/resume；零删除；artifact reuse T2"）。现状缺口（RED）：FC-901 已有 dry-run/apply 机制，但无 ZR-1005 验收套件证明"只绑定可证明 artifact、零删除、幂等、真实 catalog dry-run 稳定"。
2. **production entrypoint 是什么？** company-wiki `run_artifact_backfill`（FC-901：dry-run 纯 SELECT 零写；apply INSERT OR IGNORE shadow bindings 零删除）+ `validate_artifact` 门（status/schema_version/source_sha256/path/generator/created_at）。
3. **RED？** grep artifact_backfill/bucket/dry-run → 零测试命中；FC-901 有实现无验收；schema_version 需 "1.0"、created_at 需 ISO 8601 UTC（`\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z`）等门无契约测试。
4. **允许改哪些文件？** company-wiki：`tests/contract/test_zr1005_artifact_backfill.py`（新，5 tests）；revenue：receipts/ZR-1005/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** ZR-1006（broker processing demand 最小 cohort）。本卡不做：真实 production apply（部署动作）、legacy artifact 删除（ZR-1009）。

## Acceptance criteria

- **C1 真实 catalog dry-run**：生产 catalog（documents=23530、sources=43112、locations=46606、artifacts=7712）dry-run closed=True、result_hash 跨 run 稳定（确定性排序）、行数零变化（零写）。
- **C2 apply shadow bindings（temp catalog）**：schema_version="1.0" + ISO 8601 created_at + 真实文件路径 seed → bindable artifact 生成 shadow bindings；legacy artifacts 表零删除（行数不变）。
- **C3 幂等/resume**：二次 apply 跳过已绑定（skipped_already_bound>0、created=[]）；dry-run result_hash 跨 cycle 字节一致。
- **C4 only-bindable**：bound_ids == bindable_ids；source_sha256 不匹配 / schema 不支持（2.0）→ legacy_unbound 不绑定；generator 不在 registry → 不绑定。
- **C5 质量门**：全量回归零回退（基线 896 passed + 106 subtests）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 真实 catalog 只读（dry-run 纯 SELECT）；apply 仅在 temp catalog seed 上验证；零网络、零下载、零 LLM；T2 artifact reuse（绑定不复制文件）。

## 变更（自领取以来）

- **实施（已完成）**：company-wiki `tests/contract/test_zr1005_artifact_backfill.py`（+180 行，5 tests）commit `abeaca8f`。
- 本卡无产品代码改动；revenue 侧仅 receipts/locks/state/docs。

# ZR-801 工作单元卡（preflight）— 吸收卡验收：scenario machine registry（终局处置）

- 领取时间：2026-08-31T20:44Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-801`（ZR-1105 closure → ZR-801，DAG 最后解锁单元）；锁 ZR-801（owner=zr801-implementer，nonce f582b5d9…）。
- 依赖：无（吸收卡；registry 由 CA-105 唯一实现，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 吸收卡终局验收（README §7："scenario machine registry 由 CA-105/106 唯一实现，ZR-801 只定义业务场景，不新建 registry/coverage 算法"）。现状缺口（RED）：无吸收验收（registry 存在但未验收 ZR-801 业务面被覆盖）。
2. **production entrypoint 是什么？** `assurance/unified_completion/scenarios/scenario_registry.json`（CA-105 唯一 registry，197 unique）；`uc.cli scenario-build/scenario-verify`（唯一算法）。
3. **RED？** glob tests/**/*zr801* → 零命中。
4. **允许改哪些文件？** revenue：新 `tests/test_zr801_scenario_registry.py`；receipts/ZR-801/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、registry 重建、下载、LLM。
5. **下一单元解锁？** 无——本卡为 DAG 最后单元，closure 后全部 117 卡闭环。

## Acceptance criteria

- **C1 registry 完整**：197 unique（old95+new102）+ tier T0~T4 复合合法 + id 唯一。
- **C2 唯一权威**：uc.cli scenario-build/verify 消费该 registry（一 authority 一算法）。
- **C3 业务面覆盖**：AR/BR/MINE/READ/REV/AUD 家族 ID 在位（ZR-801 业务场景需求）。
- **C4 无第二 registry**：repos 内无其他 scenario registry 文件。
- **C5 吸收文档**：README §7 记录 CA-105 唯一实现 + ZR-801 吸收。
- **C6 质量门（卡级）**：revenue 全量零回归（基线 1063+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 只读 registry + uc CLI --help；零网络/下载/LLM；不重建 registry（CA-105 唯一 owner）。

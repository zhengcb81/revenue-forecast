# ZR-907 工作单元卡（preflight）— H 收官：contract/doc/sample/skill-package drift patrol

- 领取时间：2026-08-23T02:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-907`（ZR-906 closure → ZR-907）；锁 ZR-907（owner=zr907-implementer，nonce 064fc926…）。
- 依赖：ZR-701（F1 入口，accepted ✅）、ZR-906（最终 ratchet，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H 收官卡——contract/doc/sample/skill-package 漂移巡逻（卡描述："schema 版本/字段/引用文件/installed skill hash 不一致即 CI 失败"）。现状缺口（RED G1~G3）：既有 `tools/drift_patrol.py`（R6.4）查 version/installation/config/docs/dependencies 五类，但**无 schema 版本字面一致性扫描**（"3.6" 等旧字面量无持续门）、**无 manifest 引用 hash 聚合**（uc manifest-verify 独立）、**无字段/引用存在性检查**。
2. **production entrypoint 是什么？** 扩展 `tools/drift_patrol.py`：patrol() 增加 `schema`（contracts/constants.py 真源 FORECAST_SCHEMA_VERSION=3.7/OPT_IN=3.8 vs scripts/ 字面版本字符串扫描——旧字面量如 "3.6" 检出）+ `manifest`（uc manifest-verify 子进程——引用文件 hash 不一致即红）；既有 installation check（skill-sync MATCH）保留。
3. **RED？** 旧 patrol 无 schema/manifest check（grep drift_patrol 的 patrol() 五类）；"3.6" 无持续门；manifest 引用 hash 无聚合。
4. **允许改哪些文件？** revenue：`tools/drift_patrol.py`（扩展 patrol() 加 schema/manifest check）、新 `tests/test_zr907_drift_patrol.py`；receipts/ZR-907/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog/root 写、下载、LLM、真实 skill-sync --apply（只读 check 模式）。
5. **下一单元解锁？** 阶段 H 出口（ZR-901 PR 门 / CA-201~206 动态审核 / CA-206 soak）。本卡不做：PR 门集成（ZR-901）、真实 skill 安装变更。

## Acceptance criteria

- **C1 schema 版本一致性（杀 G1）**：扫描 scripts/（及 contracts/）中字面 schema 版本字符串（"3.6"/"3.7"/"3.8"），与 constants 真源（FORECAST_SCHEMA_VERSION=3.7 + OPT_IN_SCHEMA_VERSION=3.8）比对——未知/旧版本字面量（非真源声明处）→ 检出；测试注入旧版本字符串 → 红。
- **C2 引用文件 hash（杀 G2）**：uc manifest-verify 对真实 manifest → 0 问题（引用文件 hash 一致）；注入漂移 → 检出（复用 ZR-905 AUD2-07 已验证机制，本卡聚合）。
- **C3 installed skill hash（杀 G3）**：sync_installations 默认 check 模式 → MATCH（exit 0）；注入差异（临时 destination）→ DIFF/非零。
- **C4 质量门**：全量回归零回退（基线 874 passed + 106 subtests）、ruff clean、ratchet 绿、skill-sync MATCH、独立 reviewer 复放。产品代码零改动。

## 边界

- hermetic：漂移注入用 tmp 副本；真实 manifest/skill 目录只读。
- 本卡不做：真实 PR 门 CI 集成（ZR-901）、filing/wiki 仓深度漂移（三仓 docs 侧由 ZR-901/CA 覆盖）。

# ZR-401 工作单元卡（preflight）— RootPolicy 3.0 schema/strict loader/snapshot hash

- 领取时间：2026-08-18T11:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-401`；units.ZR-307.status=accepted + closure.next=ZR-401；`uc next` 解锁列表含 ZR-401。
- 依赖：ZR-203（accepted ✅）。Registry 依赖列=ZR-203。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 跨 roots 通用复用。现状：`policy_2x.py`（FC-301）已有 2.x loader（显式 per-root 策略、write-target 限制、fail-closed 未知字段/adapter/profile/外部可写/重复 root），`policy.py` 有 1.0 export+hash，`runtime_policy.py` 有 snapshot hash/validate/CAS。但：**(a)** `privacy_class` 默认 "public"——Dropbox 类私密 root 若未显式声明 `private_user` 即被隐式当作 public（权限扩大）；**(b)** 无 **RootPolicy 3.0** schema 版本（当前 loader 接受 YAML schema_version "1.0" + policy 2.x 语义，版本语义混乱）；**(c)** 无 3.0 的 snapshot hash 导出统一入口（ZR-404 envelope 需要 policy/epoch/cohort/source hash 一致）。
2. **production entrypoint 是什么？** `policy_2x.py`（loader/doctor/export）+ `policy.py`（export_policy hash）+ `runtime_policy.py`（snapshot）；config 加载路径 `config.py`。本卡：新增 **RootPolicy 3.0 strict loader**（`policy_3x.py` 或扩展 policy_2x，minimal diff）+ 强制 Dropbox 类 root `privacy_class=private_user` + snapshot hash 导出。
3. **哪个 current-triplet 行为是 RED？** Dropbox root 未声明 privacy_class 时隐式 public（私密数据权限扩大）；无 3.0 版本化 schema 与严格字段白名单；外部 root 的 write target 在 2.x 已有检查但 3.0 需在"配置加载即失败"层面显式（2.x 已部分实现——核对并钉死）。
4. **允许改哪些文件？** company-wiki `policy_2x.py`（或新 `policy_3x.py`，minimal diff）+ `policy.py`（export 3.0 hash）+ `config.py`（生产加载切换，若需）+ `tests/unit/` + `tests/contract/` 测试；revenue 侧 receipts/ZR-401/** 与 state.json。禁止：真实 catalog 写、下载、接 resolver 语义变更。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-402（adapter registry）。本卡不实现 adapter registry（ZR-402）；不做 dedupe/resolver 泛化（ZR-403）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-307 accepted（机器状态；closure.next=ZR-401）。
- [x] triplet 冻结（领取时重读）：revenue（ZR-307 closure commit 后）、filing `df66796…`、wiki `a608980…`。
- [x] 现状代码事实：policy_2x loader（2.0 snapshot、显式 root 策略、fail-closed 外部可写/write-target/未知字段/重复 root）；policy.py export_policy 1.0（privacy-redacted + sha256）；runtime_policy.py snapshot_hash/validate/build_snapshot/CAS；privacy_class 默认 "public" 无 private 强制；无 3.0 版本化 schema。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——3.0 schema/严格 loader/snapshot hash + privacy_class 强制。
- **Acceptance criteria**：
  - `ROOT_POLICY_3X_SCHEMA_VERSION = "3.0"`：版本化 schema；loader 拒绝非 3.0 schema_version（N/N-1 明确：1.x/2.x 配置在 3.0 loader 下显式拒绝并给出迁移提示）。
  - 严格字段白名单（ALLOWED_ROOT_FIELDS_3X）：仅显式声明字段；未知字段加载即失败。
  - **无隐式权限扩大**：`privacy_class` 必填（无默认值）——缺失即失败；Dropbox 类私密 root（kind 非 company_raw）若声明 `privacy_class != private_user` 即失败；company_raw 可 public。
  - 外部 root write target：kind 非 company_raw 声明 `canonical_write_target` 加载即失败（沿用 2.x 语义并钉死 3.0 层）。
  - snapshot hash：`export_root_policy_3x(config) -> (sha256, canonical_policy_dict)`，privacy-redacted（path token 化，沿用 policy.py 约定）。
  - 生产 config 加载切到 3.0 loader（若现有 config 已是 2.x 语义则增量升级，保持 catalog 兼容）。
  - hermetic 测试：3.0 成功加载、N/N-1（1.x/2.x 拒绝）、privacy_class 缺失/错误拒绝、外部 write target 拒绝、未知字段拒绝、snapshot hash 确定性、复杂度≤10；wiki unit/contract 全绿。
  - 独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、接 resolver 语义变更 → 立即停止。

## Annex：3.0 vs 2.x 差异

| 维度 | 2.x（现有） | 3.0（本卡） |
|---|---|---|
| schema_version | YAML 1.0 + policy 2.0 | **3.0**（loader 只接受 3.0，N/N-1 显式拒绝并提示） |
| privacy_class | 默认 public（隐式） | **必填**（无默认）；非 company_raw 必须 private_user |
| 外部 write target | 已 fail-closed | 3.0 层显式钉死 |
| snapshot hash | export_policy（1.0） | `export_root_policy_3x`（3.0 版本化 + privacy-redacted） |
| 生产加载 | config.py 1.x loader 为主 | 切 3.0 loader（增量） |

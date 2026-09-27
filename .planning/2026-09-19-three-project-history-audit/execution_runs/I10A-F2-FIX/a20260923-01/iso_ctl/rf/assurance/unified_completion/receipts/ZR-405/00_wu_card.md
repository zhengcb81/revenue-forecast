# ZR-405 工作单元卡（preflight）— 透明验证任意 policy-allowed root，不再默认 companies allowlist

- 领取时间：2026-08-18T21:15Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-405`；units.ZR-404.status=accepted + closure.next=ZR-405；锁 ZR-405（owner=zr405-implementer）。
- 依赖：ZR-404（accepted ✅，envelope policy_hash 一致性）。Registry 依赖列=ZR-404。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 透明 root 验证。legacy FC-501（handle containment 契约）implemented_not_independently_verified → 本卡独立验收+生产接线。现状：`validate_handle`（filing_contracts.py:372-454）已实现 policy_snapshot 路径（roots 中 reusable_for_filing=True 的 path_ref 展开为 allowance，hash 绑定 expected_policy_hash，resolve() 后前缀 containment），但**生产从未传 policy_snapshot**——fetch_filing.py:901 调用 `validate_handle(handle, request, root)` 无 policy → 走 legacy `<wiki_root>/companies` 默认（filing_contracts.py:442-443）。即"默认 companies allowlist"仍在生产生效。
2. **production entrypoint 是什么？** filing `_handle_from_resolution`（复用路径 resolve_filing:839 + close-gap 路径 _close_gap_and_return_handle）→ validate_handle。policy 数据源：wiki `export_policy_2x(config)`（policy_hash + roots[{path_ref, reusable_for_filing}]，policy_2x.py:255-278），但 wiki CLI 无导出命令（现有 `export` 是目录索引导出）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 生产用 companies 默认**：fetch_filing 无 policy → Dropbox-only/dayu-only 部署中 companies 默认会误拒绝非 companies 根下的合法 handle（或错误放行不存在的路径）。
   - **G2 无 policy 导出端点**：wiki CLI 无 `policy-export`，filing 无法取得权威 policy（roots+hash）。
   - **G3 无 widen 负例**：无测试证明 allowed_roots 参数不能扩大 policy（policy 优先于任何独立 allowlist）。
   - **G4 无 containment/symlink 负例**：无路径逃逸（.. / symlink resolve 逃出 policy 根）负例测试。
   - **G5 envelope.policy_hash 与导出 policy 交叉校验缺失**：ZR-404 envelope 已带 policy_hash，filing 未将其与 policy 导出 hash 核对（漂移 fail closed 未接线）。
4. **允许改哪些文件？** company-wiki cli.py（新增只读 `policy-export` 子命令 + resolve/ensure 响应内嵌 `policy_export`，复用 export_policy_2x）+ policy.py/policy_2x.py（可复用性归一化：per-root flag 缺省时按 kind ∈ reusable_root_kinds，与 resolver 行为一致）+ wiki 新测试；filing filing_contracts.py（policy hash 改为对 policy DOCUMENT 计算，排除 policy_hash 键自身——与 uc canonical 纪律一致）+ fetch_filing.py（_handle_from_resolution 从响应 `policy_export` 取 policy_snapshot/expected_policy_hash + envelope.policy_hash 交叉校验）+ filing 新测试。**设计定案（避免 89 个既有 subprocess mock 破坏）**：policy 由 wiki resolve/ensure 响应内嵌携带（零新增 subprocess 调用），filing 不额外调用 policy-export；legacy companies 默认仅作 N/N-1 桥（响应无 policy_export 时），当前 triplet 响应恒携带故生产不可达。禁止：改 validate_handle 签名（加性）、真实 catalog 写、下载。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-406。本卡不做：authorization-bound GapPlan（ZR-407）、下载（ZR-408）、production config future_lake 切换（ZR-409）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-404 accepted（机器状态；closure.next=ZR-405）。
- [x] triplet 冻结（领取时重读）：revenue（ZR-404 closure commit 后）、filing `df66796…`、wiki `f45f7ed…`。
- [x] 现状代码事实：validate_handle policy_snapshot 路径完整（hash 绑定+path_ref 展开+resolve containment）；legacy 默认在 filing_contracts.py:442-443；fetch_filing.py:901 无 policy；export_policy_2x 产 roots+hash；policy_3x.py:126-136 有 ${PROJECT_ROOT} token 模式可复用；envelope.policy_hash（ZR-404）。

## 卡片字段（runbook §4）

- **Owner repo**：filing-fetch（生产接线+测试）+ company-wiki（policy-export 端点+契约测试）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——五缺口（G1~G5）。
- **Acceptance criteria**：
  - **C1 policy 导出端点（杀 G2）**：wiki CLI `policy-export` 只读输出 {schema_version, policy_hash, reusable_root_kinds, roots:[10 契约字段]}；policy_hash==export_policy_2x(config)[0]；path_ref 为 verbatim 绝对路径（字节级 hash 契约禁止重塑）；payload 减去 policy_hash 键后重算 hash == policy_hash（filing 侧同规则）；wiki contract 测试钉死。
  - **C2 生产不再默认 companies（杀 G1）**：wiki resolve/ensure 响应内嵌 `policy_export`；filing `_handle_from_resolution` 恒以响应 policy 校验 containment（policy_snapshot+expected_policy_hash），响应携带 policy 时 legacy companies 默认绝不参与；响应无 policy_export（N-1 wiki）保留 legacy 桥（当前 triplet 恒携带，生产不可达）。
  - **C3 policy-allowed 任意根成功（杀 G1）**：Dropbox-only（roots 仅 directory/dropbox reusable）与 dayu-only 策略下，对应根下的合法 handle 通过 containment。
  - **C4 filing 不能扩大 policy（杀 G3）**：policy_snapshot 提供时 allowed_roots 参数（legacy）不参与——不在 policy reusable 根内的 canonical_path 一律拒绝。
  - **C5 containment/symlink 负例（杀 G4）**：`..` 逃逸与 symlink resolve 逃出 policy 根 → 拒绝（resolve() 后前缀检查；Windows symlink 无权限时 skip 记录）。
  - **C6 envelope.policy_hash 交叉校验（杀 G5）**：envelope 存在且 policy_hash 非 None 时，与 policy-export hash 不一致 → fail closed；一致则透传。
  - 质量门：filing 全量 + wiki unit/contract 无回归；mypy/ruff 干净；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、validate_handle 签名破坏 → 立即停止。

## Annex：containment 矩阵

| 场景 | policy roots | canonical_path | 预期 |
|---|---|---|---|
| Dropbox-only 成功 | [dropbox(directory) reusable] | dropbox/2025.pdf | 通过 |
| dayu-only 成功 | [dayu reusable] | portfolio/.../x.pdf | 通过 |
| companies 不在 policy | [dropbox] | companies/Acme/.../2025.pdf | 拒绝（无默认） |
| widen 尝试 | [dropbox] + allowed_roots=[companies] | companies/.../2025.pdf | 拒绝（policy 优先） |
| .. 逃逸 | [dropbox] | dropbox/../outside.pdf | 拒绝 |
| symlink 逃逸 | [dropbox] | dropbox/link.pdf→outside | 拒绝 |
| hash 漂移 | policy-export hash ≠ envelope.policy_hash | 任意 | fail closed |

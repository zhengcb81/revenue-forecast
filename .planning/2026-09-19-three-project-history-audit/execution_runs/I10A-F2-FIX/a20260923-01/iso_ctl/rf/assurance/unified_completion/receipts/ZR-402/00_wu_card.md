# ZR-402 工作单元卡（preflight）— adapter registry：path/sidecar 差异隔离在 adapter

- 领取时间：2026-08-18T18:56Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-402`；units.ZR-401.status=accepted + closure.next=ZR-402；锁 ZR-402（owner=zr402-implementer）。
- 依赖：ZR-401（accepted ✅）。Registry 依赖列=ZR-401。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D adapter registry 验收。legacy FC-302/303（adapter registry 基础 + scanner/admission seam）均为 implemented_not_independently_verified → 本卡独立验收钉死。现有机制：`adapters/registry.py`（静态注册表 + admission profile）、`adapter_dispatch.py`（按 adapter_id 路由，unknown fail closed）、`adapters/interface.py`（SPI + 确定性检查）、`adapters/conformance.py`（一致性 kit）、三 adapter（sidecar/company_raw/dayu）、scanner facade v2 seam（v2_scan_shadow）。Registry 验收三证据：**core 无 root kind/ID 特判**；**unknown adapter fail**；**adapter contract mutation**。
2. **production entrypoint 是什么？** 验收侧：`tests/contract/test_zr402_adapter_route_contract.py`（新增）；产品零改动（机制已实现）。生产入口现状：scanner.py `scan_root_strategy(v2_scan_shadow=True)` → `adapter_dispatch.scan_root_via_adapter`；shadow_parity.py 与 dropbox_governance.py 为 v2 生产调用方。
3. **哪个 current-triplet 行为是 RED（验证缺口/幸存突变体）？**（RED 探针机器确认：`receipts/ZR-402/red/zr402_red_evidence.json`，red_confirmed=true）
   - **S2 kind 路由幸存体（M8，确认）**：无测试钉死"adapter_for 结果只依赖 adapter_id"。进程内应用 kind 路由突变体后，现有 dispatch 测试断言全绿（现有测试只用 canonical kind↔adapter 配对）；2 个错配 kind 场景无 killer。
   - **S3 determinism 负例缺失（M1，确认）**：conformance kit 有 determinism 检查但无非确定性 adapter 负例测试（现有突变体仅 hash/role/duplicate/write/escape）。
   - **S4 adapter 路由 core kind 特判门缺失（确认）**：五路由模块（adapter_dispatch/admission/adapters.registry/adapters.interface/adapters.conformance）今日零 kind 分支但无机械门钉死；FC-1201 是 token-mention ratchet 且 adapter_dispatch.py/admission.py 在 allowlist 内（新增 kind 分支不会被任何现有门抓到）；test_spi02 只冻结 scanner.py。
   - **S1 诚实负例（非缺口）**：facade 失败封闭已被完整钉死——missing id（seam02）、bogus id（ex08_future_root_unknown_adapter_blocks）、运行时失败无 v1 回退（ex08_adapter_error_fails_closed_not_legacy_fallback，_BoomAdapter）。本卡不重复造 killer，仅在击杀表引用。
4. **允许改哪些文件？** company-wiki 新增 `tests/contract/test_zr402_adapter_route_contract.py`（如发现真实行为缺口则最小改 adapter_dispatch.py/scanner.py，需逐条记录）；revenue 侧 receipts/ZR-402/** 与 state.json。禁止：真实 catalog 写、下载、v1 scanner 重写（legacy 删除属阶段 I）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-403（dedupe/resolver 泛化）。本卡不做：dedupe/resolver 泛化（ZR-403）、v1→v2 切换与 legacy 删除（后续卡/阶段 I）、`_to_scanner_candidate` 的 `_infer_company` 路径推断语义（登记给 ZR-403）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-401 accepted（机器状态；closure.next=ZR-402）。
- [x] triplet 冻结（领取时重读）：revenue `b0140a2e…`、filing `df66796…`、wiki `251615e…`。
- [x] 现状代码事实：registry 静态表 4 adapter + 2 admission profile；adapter_dispatch 按 adapter_id 三厂 + 双重 fail closed（missing/unknown）；facade v2 捕获 AdapterDispatchError→ScannerFacadeError、捕获任意异常→ScannerFacadeError（无 v1 回退）；conformance 六检查（determinism/no_duplicates/primary_unique/role_separation/read_only/hash_accuracy）；现有测试 5 突变体（hash/role/duplicate/write/escape）无 determinism 负例；scanner.py legacy kind 分支冻结 ≤5（test_spi02）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（验收测试）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——机制本体已实现（FC-302/303）且失败封闭完整；真缺口 = 三处验证钉死缺失（S2 kind 无关路由、S3 determinism 负例、S4 路由 kind 分支机械门）。
- **Acceptance criteria**：
  - **C1 core 无 kind/ID 特判（机械门，杀 S4）**：五路由模块源内零 `.kind ==`/`.kind in`/`root_id ==` 字面分支（逐模块 count==0 断言）；对抗负例：临时模块植入 kind 分支 → 同一扫描逻辑必须检出（门能抓新增）。
  - **C2 kind/ID 无关路由（行为，杀 M8/S2）**：对每个注册 adapter × 每个 ROOT_KINDS 值 × 伪造 kind × 多个 root_id：adapter_for(root(kind=K, adapter_id=A)).adapter_id == A（路由只认 adapter_id）；进程内重放 kind 路由突变体 → 断言被 C2 违反（kill 证明）。
  - **C3 unknown adapter fail（全入口复核）**：registry unknown→None、dispatch unknown/missing→AdapterDispatchError、facade bogus id→ScannerFacadeError（复述式断言，与既有 seam02/ex08 共同构成全入口矩阵）。
  - **C4 adapter contract mutation（击杀表）**：参数化突变体每个被生产契约检查检出——M1 非确定性→determinism FAILED（**新增负例**，杀 S3）；M2 hash 谎报→hash_accuracy；M3 role 误判→role_separation；M4 重复→no_duplicates；M5 写 fixture→read_only；M6 路径逃逸→任一 FAILED；M7 registry fail-open→unknown None 断言；M8 kind 路由→C2；M9 facade 回退→既有 ex08（电池内复述场景）。kill 表以"突变体→检出者"机器断言全覆盖（表驱动，缺行即失败）。
  - hermetic 全绿；wiki unit/contract 无回归；复杂度 ratchet 不涉及（无 src 改动）；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、需要改 v1 scanner 语义 → 立即停止并登记。

## Annex：突变体击杀矩阵

| 突变体 | 违反契约 | 检出者 |
|---|---|---|
| M1 非确定性 enumerate（顺序翻转） | SPI-03 确定性 | conformance.determinism（新增负例） |
| M2 hash 谎报 | 候选哈希=文件字节 | conformance.hash_accuracy |
| M3 markdown 误判 primary | role 分离 | conformance.role_separation |
| M4 重复候选 | SPI-03b | conformance.no_duplicates |
| M5 写 fixture | 只读保证 | conformance.read_only |
| M6 路径逃逸 | 组内相对路径 | conformance（任一 FAILED） |
| M7 registry fail-open（unknown 返默认） | fail closed | registered_adapter(None) 断言 |
| M8 dispatch 按 kind 路由 | kind 无关路由 | C2 行为测试 |
| M9 facade 异常回退 v1 | EX-08 无回退 | C4 行为测试 |

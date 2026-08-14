# ZR-105 工作单元卡（preflight）— current-triplet required checks 契约

- 领取时间：2026-08-14T09:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-105`；units.ZR-104.status=accepted + closure.next=ZR-105。
- 依赖：ZR-101~104（均 accepted ✅）。Registry 依赖列=ZR-101~104。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 出口：三仓 CI 必须验证 current triplet，不再验证陈旧/浮动组合。现状（current_state_audit §5）：workflow 只有 push/pull_request、无 schedule；compatibility current triplet 陈旧；CI 可能 checkout 旧 sibling。按 README §7（"current-triplet PR fan-out → CA-201 → ZR-105、ZR-901；CA拥有调度/attestation；ZR提供required checks"），本卡冻结 **required checks 契约 + 现状 gap 评估**，不重写任何 workflow（重接线归 CA-201，与 LEGACY-CALLER-001 一致）。
2. **production entrypoint 是什么？** 三仓唯一 CI 文件：revenue `.github/workflows/quality.yml`、filing `.github/workflows/quality.yml`、wiki `.github/workflows/ci.yml`（只读扫描对象）。
3. **哪个 current-triplet 行为是 RED？** 现状 gap 即 RED：三仓 workflow 均无 current-triplet 精确绑定门、无受影响三仓 fan-out、无 collected/skip delta 控制。gap 评估器必须如实报告。
4. **允许改哪些文件？** revenue `assurance/unified_completion/ci/**`（契约 JSON + 扫描器）、`uc/ci_contract.py` + `uc/cli.py`（ci-gap 子命令）、`tests/test_zr105_*.py`、receipts/ZR-105/**、state.json。禁止：修改任何 .github/workflows 文件（CA-201 专属）。
5. **下一单元解锁条件？本单元不解决什么？** C 阶段出口 → D（ZR-301 起，依赖链按 DAG）。本卡不实现 fan-out 调度/attestation（CA-201）、不改 CI 文件、不把 gap 伪装成 green。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-104 accepted（机器状态；closure.next=ZR-105）。
- [x] triplet 冻结：revenue `19cb45aed2807374abf3de783b709f403bf51a27`（ZR-104 closure，领取时重读）；filing `83c638e…`；wiki `b661755…`。
- [x] 扫描对象确认：三仓各 1 个 CI 文件（revenue/filing quality.yml、wiki ci.yml），均为只读扫描。

## 卡片字段（runbook §4）

- **Owner repo**：三仓 CI（revenue 承载契约注册表）。
- **Current-state drift verdict**：`still_missing`——无 required checks 契约 + gap 评估。
- **Acceptance criteria**：`ci/current_triplet_contract.json` 冻结三要素（任一仓变更触发受影响三仓；collected/skip delta 受控；三仓 HEAD 精确绑定）逐条机器评估现状；gap 评估器对当前 triplet 输出诚实 gap 清单（每项 → CA-201 successor）；契约测试含负例（陈旧 triplet/skip 增长/单仓验证必须被识别为 gap）；三仓套件绿；不改任何 workflow。
- **Stop conditions / handoff**：修改 workflow 文件、gap 伪绿 → 立即停止。

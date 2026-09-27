# ZR-1103 工作单元卡（preflight）— Phase 11：真实用户旅程复验

- 领取时间：2026-08-31T19:55Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1103`（ZR-1102 closure → ZR-1103）；锁 ZR-1103（owner=zr1103-implementer，nonce 821dfe56…）。
- 依赖：ZR-1102（对抗式审查，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** Phase 11 第三卡——真实用户旅程复验（registry："companies/dayu/Dropbox、旧+新、已处理、broker/mine、CN/HK/US、Windows 中文路径"）。现状缺口（RED）：无复验组合。
2. **production entrypoint 是什么？** company-wiki SourceResolver（三 root 只读 exact resolve）；spy wiki（已处理复用 single-flight，CA-203 基建）；filing-fetch T3 套件（CN/HK/US opt-in）；golden corpus broker 7 + ZR-709 mine 链；Windows 中文路径（CJK entity/security）。
3. **RED？** glob tests/**/*zr1103* → 零命中；无复验组合验收。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1103_journey_reverify.py`；receipts/ZR-1103/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实下载（T3 opt-in 不触发）、下载、LLM。
5. **下一单元解锁？** ZR-1104（观察期与真实 rollback drill）→ ZR-1105 → ZR-801 处置。本卡不做：真实 provider 下载（部署/授权）。

## Acceptance criteria

- **C1 三 root 复验**：companies 紫金 FY2025 + dayu 金斯瑞 1548 FY2021 REUSED_EXACT；Dropbox 星环 MISSING fail-closed（production resolver 只读）。
- **C2 已处理复用**：spy wiki 二次同请求 zero fetch/zero write（single-flight）。
- **C3 CN/HK/US 市场面**：filing-fetch T3 套件覆盖三市场 + opt-in（FILING_FETCH_E2E_DOWNLOAD）。
- **C4 broker/mine 链**：golden corpus broker ≥7 + ZR-709 mine 链 engine draft 路径。
- **C5 Windows 中文路径**：中文实体/security 输入在 Windows 精确 resolve（CJK 身份进 trace）。
- **C6 质量门（卡级）**：相邻回归（CA-302/CA-203）零回退、revenue 全量零回归（基线 1042+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 真实 catalog 只读（mode=ro）；spy wiki tmp；T3 opt-in 不触发真实下载；零网络/LLM。

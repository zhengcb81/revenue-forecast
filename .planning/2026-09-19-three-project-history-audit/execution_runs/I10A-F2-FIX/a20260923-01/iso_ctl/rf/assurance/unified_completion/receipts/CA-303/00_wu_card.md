# CA-303 工作单元卡（preflight）— J：架构、硬编码与代码质量终审

- 领取时间：2026-08-31T17:13Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-303`（CA-302 closure → CA-303）；锁 CA-303（owner=ca303-implementer，nonce b79eec89…）。
- 依赖：CA-301（clean checkout，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 J 第三卡——架构/硬编码/代码质量终审（registry："CodeGraph production caller/impact、dead dual paths、root/company/path hardcode、模块边界、strict types、复杂度趋势、docs/schema/skill drift；required CI 无 `|| true`；core root/company 硬编码 0、legacy caller 0、关键新/改函数 CC≤10、历史高 CC 逐波下降、required CI 无 || true"）。现状缺口（RED）：六门分项存在无终审组合。
2. **production entrypoint 是什么？** `tools/final_ratchet`（scan_hardcode/scan_legacy/scan_encoding/gate_type/gate_complexity，MYPY_BASELINE=69）；`codegraph_freeze.json`（caller_report.targets + blocking_findings_registered）；`uc.cli manifest-verify`；`.github/workflows/*`（CI 无 || true）；state.json。
3. **RED？** glob tests/**/*ca303* → 零命中；无组合终审；当前 scanners 三门全绿 + mypy 69==基线（6s 实测）。
4. **允许改哪些文件？** revenue：新 `tests/test_ca303_arch_quality.py`；receipts/CA-303/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、CI 配置改动、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** CA-304（R9 分批删除与真实 rollback drill，依赖 CA-206/302/303/ZR-1008）。本卡不做：R9 删除（CA-304）、真实 mypy/coverage CI 全跑（CI 门）。

## Acceptance criteria

- **C1 零硬编码/零 legacy/零编码问题**：final_ratchet scanners（code-level company hardcode、legacy-engine callers、BOM/undecodable）全零。
- **C2 CI 无 silent-pass**：.github/workflows 全部 yml/yaml 无 `|| true`（required check 必须响亮失败）。
- **C3 复杂度/覆盖**：test_complexity_ratchet 绿（新/改函数有界）；coverage-gate 工具面存在（全跑为 CI 级）。
- **C4 type 门**：mypy scripts/ errors ≤ 冻结基线 69（gate_type 封装，独立 6s 实测 69）。
- **C5 docs/schema 漂移**：uc manifest-verify 离线 OK；state.json sha256 确定性 + current_next/phase 在位。
- **C6 架构 caller 表面**：codegraph freeze caller_report.targets 覆盖三仓；blocking_findings_registered 非空且 severity=blocking（诚实注册不静默）。
- **C7 质量门（卡级）**：相邻回归（ZR-906/907）零回退、revenue 全量零回归（基线 990+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 只读扫描 + subprocess（mypy 独立线程防 pytest-timeout 冲突）；零产品/CI 改动；coverage 全跑为 CI 门（本卡验证表面）。

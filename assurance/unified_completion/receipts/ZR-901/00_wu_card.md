# ZR-901 工作单元卡（吸收卡：current-triplet PR 门 required checks，revenue）

- 领取时间：2026-08-23（ZR-801 closure 后）；唯一入口：audit_review/README.md §0 current_next=ZR-901；units.ZR-901.status=preflight_locked（lock nonce f443bd73…）。
- 依赖：ZR-105（accepted，契约+评估器）；CA-201 拥有调度/attestation（吸收表 §7 行 132）。

## 领取前五问（弱模型清单 §1）
1. **推进哪个用户目标/痛点？** 阶段 J 出口最后一块：current-triplet PR 门 required checks 的落实证据。三仓 CI 只读扫描在 ZR-105 已冻结契约（exact_triplet_binding / affected_repo_fanout / collected_skip_delta_controlled）；本卡验证 revenue PR 面（quality.yml + ci_checkout_siblings.py + current.json）确实按契约落实（manifest 驱动、无 || true、无浮动 clone、triplet 可解析），并保持 ci-gap 诚实报告（gap → successor=CA-201）。
2. **production entrypoint 是什么？** revenue `.github/workflows/quality.yml`（push/pull_request）；`tools/ci_checkout_siblings.py`（manifest 驱动 checkout）；`compatibility/current.json`（current_triplet）。
3. **哪个行为是 RED？** tests 无 `test_zr901_*`；required checks 落实证据无机器断言（无测试钉住 quality.yml 的 manifest 驱动/无 swallow/无浮动 clone、sibling 工具仅读 manifest、triplet 可解析、契约三要素与吸收行）。
4. **允许改哪些文件？** revenue `tests/test_zr901_pr_fanout.py`、`receipts/ZR-901/**`、`state.json`。禁止：任何 `.github/workflows` 修改（CA-201 专属）、`tools/ci_checkout_siblings.py`/`compatibility/current.json`/契约/评估器改动（既有冻结面）、产品代码。
5. **下一单元解锁条件？** 本卡不实现 fan-out 调度/attestation（CA-201 拥有）、不刷 manifest（CA-201）、不改 CI 文件。本卡 closure 后 DAG 无后继 → 全部 117 单元闭环。

## 领取前机器门（弱模型清单 §2）
- [x] ZR-801 accepted + closure.next=ZR-901（机器状态）。
- [x] 契约在位：ci/current_triplet_contract.json（ZR-105 冻结，三要素 successor=CA-201）。
- [x] 扫描对象确认：revenue quality.yml 47 行、无 || true、无裸 clone、含 manifest 驱动 sibling checkout 步骤。

## 卡片字段（runbook §4）
- **Owner repo**：revenue（PR 门 required checks 证据）。
- **Current-state drift verdict**：`still_missing`——required checks 落实证据无机器测试。
- **Acceptance criteria**：`tests/test_zr901_pr_fanout.py` 钉住——①quality.yml 引用 manifest 驱动 sibling checkout（compatibility/current.json + ci_checkout_siblings）；②quality.yml 无裸 `git clone`、无 `|| true`；③ci_checkout_siblings.py 仅 manifest current_triplet 驱动（无硬编码 pin），`--help` 可运行；④current.json 的 current_triplet/frozen_baseline 六 commit 全部 `git cat-file -e` 有效；⑤契约三要素 required_checks + successors=CA-201 + machine_rules 在位，workflow_files.sha256 与 quality.yml 字节一致；⑥ci-gap 评估器（uc.cli）输出确定性 JSON，revenue 三检查均在，不满足项 successor=CA-201（诚实，不 fake green）；⑦README §7 吸收行（CA-201 | ZR-105、ZR-901）在位。零 workflow/产品改动；三仓套件绿。
- **Stop conditions / handoff**：修改 workflow 文件 / 篡改 manifest / fake green → 立即停止；gap 归属 CA-201 不得在本卡消除。

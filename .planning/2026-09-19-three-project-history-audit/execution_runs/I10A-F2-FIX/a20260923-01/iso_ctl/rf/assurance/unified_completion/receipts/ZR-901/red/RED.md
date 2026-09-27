# ZR-901 RED 探针（current-triplet PR 门 required checks，吸收卡，CA-201 拥有调度/attestation）

探针时间：2026-08-23（ZR-801 closure 后，lock nonce f443bd73…）

## 目标面
- `.github/workflows/quality.yml`（revenue 唯一 PR/push CI 面）
- `tools/ci_checkout_siblings.py`（FC-1101 manifest 驱动 sibling checkout）
- `compatibility/current.json`（current_triplet 冻结基线）
- `assurance/unified_completion/ci/current_triplet_contract.json`（ZR-105 冻结契约）
- `assurance/unified_completion/uc/ci_contract.py`（ci-gap 诚实评估器）
- README §7 吸收行（ZR-901 由 CA-201 吸收）

## 探针结果（只读）
1. tests 无 `*zr901*` 文件：`Get-ChildItem tests -Filter "*zr901*"` → 零命中（RED）。
2. quality.yml（47 行）存在：manifest 校验步骤（FC-1101）+ `ci_checkout_siblings.py --manifest compatibility/current.json` 步骤；无 `|| true`；无裸 `git clone`（Select-String 零命中）。
3. tools/ci_checkout_siblings.py 存在：只从 manifest `current_triplet` 取 commit；无硬编码 40-hex pin；dest 布局镜像本地三仓。
4. compatibility/current.json：schema_version "1.0"、frozen_baseline_triplet + current_triplet 各 3 个 40-hex；current_triplet=1b41d62f…/592fae61…/f6eb5841…。
5. ZR-105 契约在位：三要素 required_checks（exact_triplet_binding / affected_repo_fanout / collected_skip_delta_controlled），successor 均 CA-201。
6. ZR-105 评估器（ci-gap）：只读扫描三仓 workflow，gap 映射 successor=CA-201（ZR-105 评估时 9/9 gap）。
7. README §7 行 132：`current-triplet PR fan-out | CA-201 | ZR-105、ZR-901 | CA拥有调度/attestation；ZR提供required checks`（在位）。

## 结论
required checks 面（ZR 职责）已由 ZR-105 契约冻结 + 本卡验证落实证据；调度/attestation 与 manifest 刷新属 CA-201（吸收表唯一拥有）。RED = tests 无 ZR-901 卡验证。

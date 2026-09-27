# CA-201 RED 探针（current-triplet PR fan-out 吸收卡，DAG 第 117 单元/最后一个）

探针时间：2026-08-23（ZR-901 closure 后，lock nonce 7a9e04dd…）

## 目标面
- README §7 吸收行 132：current-triplet PR fan-out | CA-201 | ZR-105、ZR-901 | CA拥有调度/attestation；ZR提供required checks
- ZR-105 契约（ci/current_triplet_contract.json）三要素 successor=CA-201
- ZR-901 已验证 revenue PR 面（quality.yml manifest 驱动、无浮动 clone、无 || true）
- ci-gap 评估器（uc/ci_contract.py）诚实报告 gap → successor=CA-201
- 依赖：CA-107、ZR-105、ZR-901（机器状态均 accepted）

## 探针结果（只读）
1. tests 无 `*ca201*` 文件（RED）。
2. tools/ 无 fanout/fan* 工具（零重复实现——调度/attestation 由 ZR-105/ZR-901 required checks 吸收）。
3. ci_contract.py 中 successor 均=CA-201（行 131/144/163/203）。
4. README 行 132 吸收行在位。
5. DAG：CA-201 deps = [CA-107, ZR-105, ZR-901]；state 116 units 全 accepted，CA-201 为 DAG 第 117 单元（state 无条目，本次领取创建）。
6. ci-gap 现状：9 项 gap（revenue manifest triplet 陈旧 vs 冻结、filing 浮动 clone、wiki 无 sibling checkout、三仓无 fan-out 标记、无 collected/skip delta）全部 successor=CA-201 —— 诚实报告，不 fake green。

## 结论
CA-201 是吸收卡：CA 拥有调度/attestation 职责，required checks 由 ZR-105/ZR-901 提供（均 accepted）。RED = tests 无 CA-201 卡验证（吸收关系 + DAG 依赖 + 契约 successor + 诚实 gap 映射 + 零重复实现）。

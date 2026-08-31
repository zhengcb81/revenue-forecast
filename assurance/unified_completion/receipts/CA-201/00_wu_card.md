# CA-201 工作单元卡（吸收卡：current-triplet PR fan-out，DAG 最后一个单元）

- 领取时间：2026-08-23（ZR-901 closure 后，closure.next=CA-201）；唯一入口：audit_review/README.md §0 current_next=CA-201；lock nonce 7a9e04dd…。
- 依赖：CA-107、ZR-105、ZR-901（机器状态均 accepted，DAG 解锁）。

## 领取前五问（弱模型清单 §1）
1. **推进哪个用户目标/痛点？** 阶段 J 终局最后一块：current-triplet PR fan-out 吸收卡。README §7 行 132：CA-201 拥有调度/attestation；ZR-105、ZR-901 提供 required checks（均 accepted）。本卡验证吸收关系成立：契约三要素 successor=CA-201、revenue PR 面落实证据（ZR-901）、诚实 gap 映射、DAG 依赖闭环、零重复实现——closure 后 117/117 全部闭环。
2. **production entrypoint 是什么？** 三仓 CI（revenue/filing quality.yml、wiki ci.yml）+ compatibility/current.json + ci/current_triplet_contract.json + uc/ci_contract.py。
3. **哪个行为是 RED？** tests 无 `test_ca201_*`；吸收卡验收无机器断言。
4. **允许改哪些文件？** revenue `tests/test_ca201_pr_fanout_ownership.py`、`receipts/CA-201/**`、`state.json`。禁止：任何 `.github/workflows`、`tools/ci_checkout_siblings.py`、`compatibility/current.json`、契约/评估器改动（CA-201 拥有但调度/attestation 实现由 ZR 吸收；workflow 修改不属于本卡验收面）、产品代码。
5. **下一单元解锁条件？** 本卡为 DAG 无后继的最后单元；closure 后全部 117 单元闭环，无下一单元。

## 领取前机器门（弱模型清单 §2）
- [x] ZR-901 accepted + closure.next=CA-201（机器状态）。
- [x] DAG：CA-201 deps [CA-107, ZR-105, ZR-901] 全 accepted（next_units 输出 unlocked=[CA-201]）。
- [x] 吸收表行 132 在位；ci-gap 9 项 gap 全部 successor=CA-201。

## 卡片字段（runbook §4）
- **Owner repo**：revenue（吸收卡验收：PR fan-out 所有权与 required-checks 吸收关系）。
- **Current-state drift verdict**：`still_missing`——吸收卡验收无机器测试。
- **Acceptance criteria**：`tests/test_ca201_pr_fanout_ownership.py` 钉住——①DAG 依赖 CA-107/ZR-105/ZR-901 全 accepted（state.json 读取）；②README §7 吸收行（CA-201 | ZR-105、ZR-901 | CA拥有调度/attestation；ZR提供required checks）；③ZR-105 契约三要素 successors 均=CA-201；④ci-gap 输出诚实 JSON，revenue 三检查均在，unsatisfied 项 successor=CA-201（不 fake green）；⑤revenue PR 面落实证据：quality.yml 含 manifest 驱动 sibling checkout + 无 || true + 无裸 clone（ZR-901 吸收面存在性）；⑥零重复实现：tools/ 无 fanout 工具、uc/ 无第二 PR-fanout 模块、ci/ 无第二契约文件；⑦机器状态 CA-201 条目存在且依赖单元 accepted。零 workflow/产品改动；三仓套件绿。
- **Stop conditions / handoff**：修改 workflow / 契约 / manifest / 评估器 / 新建调度实现 → 立即停止（吸收卡禁止重复实现）。

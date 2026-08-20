# ZR-705 RED 探针证据（2026-08-21）

探针（revenue-forecast, HEAD 328f807）：
```
revenue_publication.py:
  build_draft_receipt: gate_ids=[], formal_output_mode="draft", verification_context_sha256=None
  build_publication_receipt: 需 VerificationContext（无则 TypeError），gate_ids=强门列表，attestation_status ∈ {host_signed, unattested}
  validate_publication_receipt: 校验 schema/engine/payload hash/gate_ids vs expected_publication_gates

RED gaps:
  - G1: draft/formal 互换攻击（formal_output_mode 篡改）失败路径无钉死测试
  - G2: 重 hash 攻击（篡改 result 数值 → payload hash 失配）失败路径无钉死测试
  - G3: draft 可 render 不发布（registry entry 数不变）无钉死测试
```

结论（G1~G3 坐实）：机制存在但互换/重 hash 攻击失败与 draft 不发布无钉死。

GREEN 对照（实现后）：test_zr705_draft_formal_swap.py 钉死 REV-06~08 全矩阵。

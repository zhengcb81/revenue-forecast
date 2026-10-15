# 进度

2026-10-15 ROOT已创建独立稀疏工作树及启动文档，尚未开始实现/测试。源码来自明确committed base；主目录WIP/密钥/原件未复制。

2026-10-15 A 完成：读完实际源码/W08/consumer 调用面，冻结旧记录与旧 builder 输出，先写真实行为 RED（receipts/red-first-behavior.json，50 failed/94 passed）。缺陷 H1/H2/H3 探针结论与正控见 findings.md。W08 C01-HKD-C 原因改跨币、加 C01-HKD-L/C01-UNK-C。

2026-10-15 B 完成：Currency×Scale 唯一责任层 + validate_input_quantity_for_parameter consumer 核对落地；集中回归 216 passed/10 skipped（receipts/final-central.json）、pre-push smoke 416 passed、ruff/mypy 干净。zr804 安装副本 3 失败为工作树缺 agents/claude/codex 目录（环境性，非本卡文件），照实保留。

2026-10-15 C 完成：E2E 全绿（receipts/e2e-run.json 23 checks；e2e-cleanup.json sentinel/registry隔离/temp全删）；手算 7.25亿=725百万、5十亿=5000百万及反向与实现一致，725 shock 进入 revenue delta；同数字不同币种/篡改记录被公开 CLI 拒绝；旧 USD/RMB 样例不回归。交付 references/money-unit-conversion.md 与 handoff；commit 后 STOP。

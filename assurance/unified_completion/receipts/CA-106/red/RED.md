# CA-106 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：side_effect_counts 是声明而非测量

旧 FC receipt（如 FC-1001/FC-1003/FC-1004 的 11_implementer_receipt.json 第 82/85/124
行）与现有 CA receipt 的 `side_effect_counts` 均为手写声明字段，无 ledger/journal/
OS fingerprint 支撑——"伪填 download/parser/LLM=0"无法机器检出。

## RED-B：无 root before/after fingerprint 机制

任何工具都未对 roots 做文件数/字节/mtime 快照对比；外部 root 被写、T2 零写承诺
无法独立验证。

## RED-C：隐私路径无脱敏规范

receipt 中出现绝对路径（如 RED 证据文件路径、clone 路径），无"路径 hash + 仅
basename"规范。

## 新工具对照（本卡实现）

`uc.ledger`：JSONL side-effect ledger（13 种事件 kind）、OS 级 root fingerprint
（文件数/字节/mtime 边界/逐文件 token）、before/after diff oracle、声明计数对账
（多报/漏报都红）、路径隐私（完整路径永不落盘，仅 path_sha256 + basename）。
8 个测试覆盖指纹 diff、隐私、往返、未知 kind、对账多报/漏报。

# DU6-RF-TARGET-MEASURES

状态：READY；2026-10-16。工区 `C:/Users/郑曾波/Projects/revenue-forecast-du6-targets`。

分支 `codex/du6-rf-targets-20261016`；源码基线 `5122107bbc86c3d1e79886b372700c05d19bb349`，另外只有启动PWF种子。

先读[施工卡](construction_card.md)和[接口](INTERFACES.md)。本卡可现在独立启动，不等待 ROOT v4 或另外两卡。

## A：接口与行为RED

Status: pending

实际入口验证卡中假说，保留旧正确行为。

## B：共同责任实现和集中回归

Status: pending

严格白名单和冻结接口，不修改旧金标洗绿。

## C：实际CLI、清理与交付

Status: pending

一次大节点端到端和独立质量检查，隔离全部输出与registry，恢复Temp/sentinel。正常commit后handoff.md/json，STOP，不并主线或安装。

## Next Step

执行A；只有A/B/C大节点，不增加小节点人工许可。

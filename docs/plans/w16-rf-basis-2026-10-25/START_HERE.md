# W16-RF-BASIS 开工入口

本卡READY，可立即A/B/C施工，不等待ROOT另行签字。产品实现尚未开始。

- 工作目录：`C:/Users/郑曾波/Projects/revenue-forecast-w16-basis`
- 分支：`codex/w16-rf-basis-20261025`
- 冻结代码基线：`094d55ad884e4a886b1537c0e76f3a0bede16ca2`；文档seed是在其上额外提交。
- PLAN_ID：`w16-rf-basis-2026-10-25`；PWF_PLAN_ROOT：`docs/plans`。
- 施工要求：[construction_card.md](construction_card.md)；共同接口：[COMMON.md](COMMON.md)。这两份为总控发包时的完整副本，不需要本聊天历史。
- 自己只维护本目录PWF；中央PWF由ROOT归总。先核branch/status，读施工卡、共同接口、task_plan/findings/progress与仓内AGENTS。

```powershell
$env:PLAN_ID='w16-rf-basis-2026-10-25'
$env:PWF_PLAN_ROOT='docs/plans'
```

工区使用sparse省略.planning/；这些是预设省略，不是待提交删除。源代码已从冻结HEAD真实检出。不要展开历史运行全集或清理原主工区。原件和外部引用只读；0模型/下载，独占测试目录恢复原样。

完成前必须调用未参与实现的独立agent读完整diff、独立跑关键链并加反例；修完全部问题，复测及复审最终代码后才交COMPLETE。只在A/B/C大节点集中审查。交接路径`delivery/w16/handoff.json`及同名md，格式见handoff.template.json。

若缺真实资料或外部接口阻止核心验收，写具体证据和恢复入口，不造PASS；其余可独立工作继续。正常提交自己的文件及codex支线，主线并入/安装归ROOT。

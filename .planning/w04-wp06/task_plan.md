# W04 WP06 — 研究 authoring 文档

## Goal
只更新隔离树三个排他文档，依据真实 schema/CLI、既有 P7 接受记录及原三公司 sealed 审查，把 87 keys 的研究方法残余转成有序执行指引。工程文档验收与下一轮经济验收分开。

## Current Phase
STOP: handoff to ROOT

### Phase 1 — 读取真实证据与接口
**Status:** complete

### Phase 2 — 三份文档改写与87 keys映射
**Status:** complete

### Phase 3 — 集中兼容核验、交接 STOP
**Status:** complete

## Next Step
ROOT接收独立文档大节点审查/正常发布，随后新attempt真实研究；本worker已STOP。

## Boundaries
产品写集仅 SKILL.md、references/research-coverage.md、docs/w04_research_authoring_card.md；自身 .planning/w04-wp06。零 HTTP/provider/model/费用，旧封存 input/run/report、ROOT PWF、代码、配置、安装皆不改。无新许可链。

## Errors Encountered
| Error | Attempt | Resolution |
|---|---|---|
| 沙箱 git status 说 must be run in work tree | 1 | 真实只读 git 状态在既有授权 require_escalated 核对 |
| HEAD 无 AGENTS.md | 1 | 如实记录不存在，遵守任务和已提供 AGENTS；不自行增加 |

已完整解析12sealed reports及87项 coverage。后续只按实际路径读取；communications.py和forecast/sensitivity.py路径猜测失败已记录，实际communication_scope.py/targets.py已读，未创建替代模块。

| Windows argv WinError206 | 单命令包含三份长文档，进程未启动 | 分成短命令逐文档/段落写入；无产品partial |

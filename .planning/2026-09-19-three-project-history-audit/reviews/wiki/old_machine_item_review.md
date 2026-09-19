# 旧版机器条目语义复审映射

旧 test registry 实际 286 个对象与 v5 对应对象逐字段相同，v5 新增 29 个；旧文若仍写 283，属于旧草稿状态漂移，不能称旧版跑过 315 个测试。共同对象的逐 ID 规划评估见 item_ledger.jsonl 的 WIKI-TEST 条目；映射仅复用人工语义阅读，不继承通过状态。

旧 DAG 113 节点，112 与 v5 对象相同，D12C 的 requires 从 G12B-POST 变为 G12C-RT；新增 D12C-RT/G12C-RT，引入两条 purpose-bound 用户授权及 disjoint 约束。全部差异已阅读 old_json_semantic_diff.json；共同节点人工评估见 WIKI-NODE 条目。旧 113 节点链不能得到新授权防护的信用。

判定：两个旧机器文件均 superseded。它们是计划数据，不是产品实现或成功运行台账；未选分支也不能统计为已通过。字节/字段相同映射不得用来跨版本继承 reviewer 签字。

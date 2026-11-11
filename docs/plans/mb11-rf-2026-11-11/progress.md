# 进度

- 已基于 RF 当前 main 建立 C:/Users/郑曾波/Projects/mb11-rf。
- 已记录参考候选和全树差额，明确只处理原 MB-RF 卡中的最小公开合同路径。
- 下一步先在无源码改动的基线上运行既有 compare/scope/publication 与 job/recovery/source-port 相关测试，随后引入 B37 候选测试作为 TDD 输入。
- 当前无产品文件改动，无测试结论，无提交或并线。


## compare模块接收进展（本轮）

- 只测试的B37 RED：当前main收集失败，`ModuleNotFoundError: report_catalog_compare`，见 `b37_compare_red.log`。
- 先接入 compare.py 与固定CLI，B37 synthetic比较合同 51 passed/1 skip；job/recovery/source-port既有基线51 passed。
- 独立审查指出 512行及1MiB响应固定门槛无预算依据。已移除，并以600期完整归属和>1MiB完整CLI响应覆盖；compare+job/recovery/source-port合并回归102 passed/1 skip（门槛修正前），门槛修正后compare套件52 passed/1 skip。
- 门槛修正后的ruff与mypy均通过。测试使用仓外Temp basetemp，运行后已删除；环境性skip是未设置Dashboard合同目录。
- 只接入两个RF源码模块与一个测试文件。独立审查员在复核门槛修正，本地分支尚未commit/push/main merge。余下B37目录/身份/publication功能尚未开始。

- 独立只读审查对 compare 三文件给出 PASS；结果和范围保存在 review/compare_api_review.md。审查指出的“每行完整期次、左右定位都保留”断言已补上并重测。
- 最终compare测试52 passed/1环境skip；Ruff、mypy通过。此前102 passed/1 skip是去掉结果门槛之前的组合回归，只作补充证据，不冒充门槛修正后的全组合结果。
- 本地提交/并线目标为 compare纯模块与CLI，不包括余下 B37 scope/subject/publication 模块。

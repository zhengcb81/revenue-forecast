# 进度

- 已基于 RF 当前 main 建立 C:/Users/郑曾波/Projects/mb11-rf。
- 已记录参考候选和全树差额，明确只处理原 MB-RF 卡中的最小公开合同路径。
- 开工时先记录的基线：无compare模块；当前job/recovery/source-port相关回归51 passed。后续各阶段结果按下文分别记录。


## compare模块接收进展（本轮）

- 只测试的B37 RED：当前main收集失败，`ModuleNotFoundError: report_catalog_compare`，见 `b37_compare_red.log`。
- 先接入 compare.py 与固定CLI，B37 synthetic比较合同 51 passed/1 skip；job/recovery/source-port既有基线51 passed。
- 独立审查指出 512行及1MiB响应固定门槛无预算依据。已移除，并以600期完整归属和>1MiB完整CLI响应覆盖；compare+job/recovery/source-port合并回归102 passed/1 skip（门槛修正前），门槛修正后compare套件52 passed/1 skip。
- 门槛修正后的ruff与mypy均通过。测试使用仓外Temp basetemp，运行后已删除；环境性skip是未设置Dashboard合同目录。
- compare代码最终由 `e060a8607` 并入RF `main`，PWF进度随后记录于 `33d880826`；compare功能不是本工作树剩余待并的项目。
- 独立只读审查对 compare 三文件给出 PASS；结果和范围保存在 review/compare_api_review.md。审查指出的“每行完整期次、左右定位都保留”断言已补上并重测。
- 最终compare测试52 passed/1环境skip；Ruff、mypy通过。此前102 passed/1 skip是去掉结果门槛之前的组合回归，只作补充证据，不冒充门槛修正后的全组合结果。

- compare并入main后的既有主线观测：compare + job/recovery/source-port 为102 passed、2 skipped，固定push smoke为12 passed；本轮更新的更完整组合是171 passed、1 skipped。main上的 `assurance/runs/daily_alert.jsonl` 有后台追加，本次保留原内容，不纳入提交或回滚。

## B37部署与来源测试增量

- 从候选中独立保留了 `tests/test_report_catalog_deployment.py` 和 `tests/b37_publication_sources/`；publication-source owner实现与main同blob，无生产代码复制。
- 锁文件测试原本要求稳定的 `catalog.jsonl.lock` 不存在，与RF `OwnerFileLock` 协议冲突。改成检查根目录文件集不变且锁未持有；没有更改owner锁实现。
- 首轮长 `--basetemp` 下出现4个RF-job用例路径创建失败；短临时根使用相同命令复验后，最终聚焦集合为171 passed、1 skipped、71.41s。最终日志为 `b37_combined_final.log`，首轮失败数与根因在findings.md留档；pytest basetemp均在命令结束后清除。
- 独立只读审查 PASS，见 `review/deployment_source_regressions.md`。最终部署文件单测38 passed；Ruff通过。测试文件还未提交/推送；计划更新随本次提交一起入main。
- scope/subject/verified-comparison测试中的3个缺口和候选实现跨模块私有调用/市场范围固定问题已归因并写入findings.md。对应候选代码留在源分支，不复制到本工区；scope功能后续先补公开边界和泛化测试，再判断并线。

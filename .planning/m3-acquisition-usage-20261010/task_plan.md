# RF lane record — M3-USAGE (RF 子仓步骤，唯一总执行 PWF 在 CWP 工作树)

## Scope
RF client→source_preparation 保真传递 acquisition-observation/1；失败观察进
FilingSourcePreparationError/_ClientError/CLI stderr 文档；成功 envelope 原样随行。
不从磁盘补网络账、不重验身份/MIME。

## Steps
1. filing_upstream_cause.validated_acquisition_observation + failure_observation 投影
   （顶层优先、detail 兜底）✓
2. filing_fetch_client._ClientError/_emit_error/CLI 接线 ✓
3. source_preparation.FilingSourcePreparationError/exit-3 文档接线 ✓
4. tests/test_m3_acquisition_usage_rf.py（19）✓
5. tests/test_m3_acquisition_usage_e2e.py：真实子进程 CWP CLI→FF CLI→RF preparation
   离线链（loopback、两市场、reuse、missing）✓

## Next Step
无（本仓 GREEN；共享入口集成由 MAIN 大节点负责）。

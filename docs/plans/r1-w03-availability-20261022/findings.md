# Findings

根因位于同一RF wire责任层：raw receipt required-field exact集合拒绝现有来源证明扩展，manifest时间检查只认pub；该单消费者尚未复用已经存在的source-clock。修复应只在receipt资格判断接线，不重hash原文、不建第二proof/身份链。

source-clock已支持 prior_verified_capture、primary_archive、current_verified_open；已知发布日期先判未来，再校验proof；未知日期可用同SHA证明且不能倒填cutoff。当前as_of=None仍允许未知pub，新增proof若提供仍须形状/SHA正确。

CodeGraph对该隔离工区返回not initialized；本线不扩大目录写入创建索引，基于已明确打开的消费者和测试文件工作。初次沙箱git status错误，授权主机读取确认tracked clean，未改Git配置。

ROOT concentrated review at6efbebc3 identified an omitted existing clock edge: qualifier eligibility was discarded and actual read/retrieval events were only typed, so proof later than actual read could qualify a later cutoff. Add 3 contradictory event RED controls plus2 known-publication priority controls, then reuse validate_source_events, not a bespoke comparison. Current unknown/no-proof mode remains accepted; if metadata supplies an actual eligibility, use real read UTC day for current-mode qualification.

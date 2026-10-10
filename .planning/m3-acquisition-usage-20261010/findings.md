# RF findings
- source_candidate 严格 8 键闭集（company_wiki_source_v2._validate_candidate）不是本线写集：
  观察放 envelope 顶层后闭集合同零改动即通过（E2E 实测）。
- failure_observation 是唯一投影点（attempts 取 detail，calls/downloads 取顶层）——观察同样
  顶层优先、detail 兜底，兼容平铺旧形状。
- resolve_filing_result 返回完整 envelope（usage stays producer-owned）：成功侧零改动随行。
- 测试 runner 是 pytest（与 FF 一致）；三仓 E2E 沿 FF_V2_CODE_ROOT/CWP_V2_CODE_ROOT env 惯例。

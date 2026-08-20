# ZR-704 RED 探针证据（2026-08-21）

探针（revenue-forecast, HEAD 50a2f52）：
```
revenue_forecast.py --validate-only path:
  mode="draft" → run_forecast(data, mode="draft") + validate_forecast_output
  success: print "valid", exit 0
  failure: ForecastInputError → print error, exit 2
  draft mode: validate_published_forecast (strong) + build_draft_receipt (in-memory) + NO register_publication

RED gaps:
  - G1: failure path zero-residue (no tmp files, no registry mutation) untested
  - G2: registry hash unchanged (content-addressed chain identical before/after) untested
  - G3: malformed JSON input zero-residue untested
```

结论（G1~G3 坐实）：validate-only draft mode 现有实现路径正确（draft 不注册），但 REV-05 门测试（success/failure/malformed 三路零残留 + registry hash 不变）未钉死。

GREEN 对照（实现后）：test_zr704_validate_only_gate.py 钉死 REV-05 三路零残留 + registry hash 不变。

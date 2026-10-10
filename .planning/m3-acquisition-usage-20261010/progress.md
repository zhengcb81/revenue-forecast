# RF progress — M3-USAGE
- 2026-10-10：RED（base 上 15 失败/4 过，日志在 CWP PWF red_rf_projection.log）→ GREEN 19/19；
  责任回归 187/187（test_source_failure_observations 等 5 套件）。
- 公共 E2E 2/2 绿：us_download（3 exchanges，wire 191<entity 4553，cost 0.0009）、us_reuse
  （0 body GET）、cn_download（第二市场）、us_missing（RF exit 3 携带观察）；argv/stdout/stderr/exit
  全存 CWP PWF e2e_logs/。

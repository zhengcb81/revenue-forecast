# ZR-805 工作单元卡（preflight）— G：CN/HK/US T3 首次下载+二次零下载（严格授权）

- 领取时间：2026-08-23T13:00Z；current_next=ZR-805（ZR-804 closure 后推进）；锁 owner=zr805-implementer。
- 依赖：ZR-407/ZR-408 ✅（D 阶段已闭）。
- 分层归属：真实 T3 执行套件由 filing-fetch tests/test_e2e_download.py 唯一拥有（FILING_FETCH_E2E_DOWNLOAD=1 显式 opt-in；CN/US/HK 三市场 + 损坏拒绝 + 二次运行零下载 + staging/lock 无残留）；本卡钉 revenue 侧授权语义与跨仓桥接，不建第二套下载器。
- production entrypoint：scripts/source_preparation.py（--allow-download 默认 False）；oracle=filing-fetch acquisition_attempts.jsonl journal（AUD2-04 对账）。
- RED：grep zr805 → 零命中。
- AC：①T3 套件存在且 opt-in 门+三市场+损坏拒绝标记齐备；②未授权 missing 请求 journal 零 downloaded_new 且 stdout 空；③入口显式 --allow-download 且无第二下载器。真实三市场 T3 实跑=需用户网络授权的设计内 blocked/opt-in（卡面「网络缺失 blocked」语义）。

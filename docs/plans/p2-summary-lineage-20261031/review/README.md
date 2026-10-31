# P2 v5 有界工程验收

独立审查[最终报告](review-v5-final.md)，[32项纯离线探针](probe-v5.json)；原始input/forecast/snapshot/report及失败与通过日志以gzip保全在receipts。包内原始字节SHA见manifest.json，不含密钥、原PDF或整库。

可复验：在本仓运行宿主Python `-B -X utf8 docs/plans/p2-summary-lineage-20261031/review/replay.py`。仅解压冻结输入到临时独立publication registry，用真实RF引擎验证并重算三情景；零网络/模型/来源解析，退出恢复临时目录。

完整公司研究仍OPEN，不能把engineering formal当作整轮RF-audit通过。实际来源链与恢复由CWP总控对应P1/P2包留证；本包不凭metadata代替真实来源读取。

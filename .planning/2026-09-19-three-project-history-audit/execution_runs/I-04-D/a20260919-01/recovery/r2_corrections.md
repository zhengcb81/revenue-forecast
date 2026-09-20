## r2 更正（追加；不得改写上文既有字节）

- **F7 更正**：上文中若干处声称 `decision.md` 不存在 —— 那是**时序误判**。该文件实际存在，
  写于 03:50:35，**早于** `review.md`/`handoff.json` 约一小时；当时那份 31332 B /
  `c3b8633615f1df60c5abab206fef1a5de3ae892555b22443d5d32f1c771ac8aa` 的副本就是交付版。
  carry 2 / carry 6 / R4 世系登记**都有正式落点**。
- **R1-9 的缺陷**（释放路径 R5 兜底格把"存活第三方 owner"当成可 resume）已修复，
  缺陷台账因此是 **10 条**，不是 9 条。
- **封盘纪律（reviewer 要求）**：宣布完成后**不再写入 attempt 目录**；此后再写入即判定本轮
  失效，需重新点审。本轮返工（r2）完成时以本文件末尾的 `sealed_at` 与 `final_hashes` 封盘。
- **编码声明**：`evidence/negative-case-*.txt` 为 **UTF-16LE**（PowerShell 5.1 重定向默认），
  读取时请指定该编码。
- **pid 边界**：`participants.<tag>.pid` 是 venv **启动器** pid（reviewer 实测启动器 37284 对
  子进程 18548），所以"只 kill 已记录 pid"的准确含义是"只 kill 该启动器进程树"。
- **HEAD 漂移**：`binding.json` 的 revenue-forecast `1ac01f0` 是**绑定时**捕获值；本次返工收尾
  又观察到 `569d113e`，下一卡必须重新绑定。

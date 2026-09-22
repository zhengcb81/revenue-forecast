# before/ — 修改前状态

本卡**没有产品修改**（allowlist = isolated publication-transaction tests + this fault harness；
产品树与 iso 树零字节改动），因此不存在“修改前产品状态”快照可放。

本卡的**运行前状态**由以下文件承担（均写于任何运行之前）：

- `binding.json` — 输入哈希、I-09-A oracle 三文件 pin、锚点四元组、cwd/解释器绑定
- `preflight_anchors.md` — 锚点实测（卡值/盘值/已登记漂移/EOL 重建）、STOP 触发与裁决 B 解除留痕
- `oracle.md` — 运行前冻结的独立预期（P-C1..P-C5 + 失败停止条件 + 关闭标准 + F1–F12 逐字）

运行后的对照测量在 `../after/production_and_iso_hashes_after.txt`
（生产 6 脚本 = 预检值；iso 6 文件 = I-09-B handoff 值 ⇒ 前后一致）。

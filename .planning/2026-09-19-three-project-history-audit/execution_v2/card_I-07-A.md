本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-07-A — 固定样本与前置状态建档
Parent：I-07。依赖：I-00-B。Owner：独立真实验收者。

输入：[sample_manifest.json](sample_manifest.json)，其中紫金FY2025、小米FY2025、微软FY2026原件引用来自旧只读证据。允许写：隔离case数据/配置与证据；不搬动真实原件。

1. 按manifest路径重哈希目标，匹配company/market/year/provider ID与请求，不凭文件名判断。
2. 复制必要原件/sidecar到隔离root，保留原hash；不同测试状态只在隔离catalog构建，不UPDATE生产review或删除生产副本。
3. 三种状态分别建立独立case目录：已索引合格；文件存在但未注册；确实缺失。原样本当前已有文件，第三种仅是隔离模拟，不能叫真实缺失live样本。
4. 固定as-of 2026-09-18用于旧失败恢复。9/19后获取的capture时间保留真实值；若现契约不允许重建，记历史重建不支持，不倒填时间，另开当前as-of研究case。
5. 外部only合格真实样本暂未绑定，保持blocked；不删其它位置制造only。

验收：状态区分可由文件/hash和catalog查证；缺失模拟与真实live标签分开。交付case输入快照及before计数，不计预测成功。

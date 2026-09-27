# ZR-804 工作单元卡（preflight）— G：平台与安装形态（大小写/sibling/installed skill/跨平台语义）

- 领取时间：2026-08-23T12:10Z；current_next=ZR-804（ZR-803 closure 推进）；锁 owner=zr804-implementer。
- 依赖：ZR-802 ✅。fc1004 已钉：路径空格、UTF-8 stdio 全链、install-sync drift 门。本卡补缺口。
- 目标：①Windows 大小写不敏感路径变体下旅程行为一致；②无显式 --filing-fetch-root/--company-wiki-config 时 fail-closed（绝不静默回退 sibling 固定路径）；③安装副本作为入口可执行且 manifest hash 与 canonical 一致（sync-first 语义）；④跨平台语义：活跃生产脚本无 Windows-only 构造（CREATE_NO_WINDOW 属合理守卫放行）。
- production entrypoint：source_preparation 三进程链、revenue_forecast.py --version、tools/sync_installations。
- RED：grep zr804/case-insensitive/installed-copy journey → 零命中；探针确认缺省参数 fail-closed 形态与大小写变体复用行为。
- allowlist：新 tests/test_zr804_platform_shape.py + receipts/state/docs；产品代码禁改。
- AC：四类断言全绿且 golden trace 语义与 fc1004 既有基线一致（不降门）。

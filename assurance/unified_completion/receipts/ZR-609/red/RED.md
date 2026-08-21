# ZR-609 RED 探针证据

- 日期：2026-08-22
- 探针：company-wiki companies/紫金矿业 存在真实年报 PDF（2024/2025 两份 + source.json），但 revenue 侧无紫金结构演示；F2 契约链（ZR-605~608/610/611）已就绪但未对真实结构做逐矿演示。
- RED：真实结构演示旅程缺失（紫金主要资产逐矿可回答 + 第二家泛化未串起来）——非产品缺口。
- drift verdict: `still_missing`（演示旅程缺失）。修复：test-only——新 `tests/test_zr609_zijin_pilot.py` 合成紫金结构（3 矿+权益链+内部流）走 F2 全链 + 第二家纯金矿商泛化；生产代码零改动。

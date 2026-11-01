# P2 摘要实际采用持久链根修

ROOT内部主线修复，不是新外包卡。总控唯一入口为company-wiki的
`docs/plans/du11-source-closure-2026-10-18/CURRENT_STATUS.md/json`。

## Next Step

本卡工程已独审闭合；ROOT负责总控主线的发布CI/定点部署收据与P1长文余项。实际发布状态只看总控CURRENT_STATUS.json，不能凭本卡签整家公司研究。

- A COMPLETE：独审v3暴露完整语义/理由只在旁收据、错误操作数锚、小非零单价显示0.00；先写真正能失败的回归。
- B COMPLETE：RF纯证据DTO贯穿input/forecast/snapshot/report，闭包复用既有owner，投影复用wire，实际参数反向引用。计算层零来源IO；旧无summary-use行为保留。
- C ENGINEERING_REVIEW_PASS：实际v5同一M8 artifact→native公式/正式产物；32独立断言、1%参数扰动6断言；最终新29例通过，既有域/安装闭包亦验证。详见review。

验收范围：工程采用链，不代签整家公司研究、P1整体或P3公司循环。原件不改，原语言，不新增人工许可。不碰RF主工区的3个assurance定时产物WIP。

2026-11-01：同一新版华利artifact v6经实际native链及45独立断言通过，0新POST/下载；正式产物和收据见review/v6，replay.py --case v6可隔离离线重跑。生产代码无delta；v5原签名保留，公司研究/P3仍OPEN。

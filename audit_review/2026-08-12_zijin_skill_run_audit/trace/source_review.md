# 隔离来源安全审阅

审阅日期：2026-08-12

边界：此处只记录本次审计代理对 isolated source snapshots 的只读检查，生成的是 unsigned/self-reported host receipt 所需事实。它没有回填 company-wiki 的 `prompt_injection_review`，也不等于平台级签名审查。

## 方法

- 对 FY2024/FY2025 canonical PDF 以 `pdftotext -enc UTF-8 ... -` 流式提取，不创建衍生文件。
- 对三个已落盘 HTML 读取原始字节/文本。
- 扫描 `ignore/disregard previous`、`system prompt`、`prompt injection`、`you are ChatGPT` 以及“忽略之前/以上/先前”“系统提示词”“提示注入”“作为 AI/人工智能”“请执行以下指令”等中英文模式。
- 两份年报还通过现有 normalized MD 定位并人工核对营收、分部、收入确认与产量计划；Results/Norton 页面通过浏览器和 HTML 精确片段核对。

## 结果

| 来源 | 物理 SHA-256 | 自动模式命中 | 人工结论 | 本次 capture 状态 |
|---|---|---:|---|---|
| FY2025 canonical PDF | `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d` | 0 | 未发现把来源内容伪装成代理指令的文本 | `not_detected` |
| FY2024 canonical PDF | `004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89` | 0 | 未发现把来源内容伪装成代理指令的文本 | `not_detected` |
| 2025 Results HTML | `08bbc18f4dcb2bce1cd0af21075ae10155fe69beeb178e73768a3fa410d648fe` | 0 | 内容为公司结果、指引与矿山表 | `not_detected` |
| Norton commissioning HTML | `a9662471d15bf8ac287c179d3ae67cf3e35465b39425637119f25e1152f00b12` | 0 | 内容为项目投产新闻 | `not_detected` |
| 原拟 strategy HTML | `b2d215df1c6f2049a6d07c4cfe340b7a247efcaa94ba916695fc10173a25b420` | 0 | **来源错配**：实际 title 为“上杭县紫金中学运动场地扩建工程流标公示”，不得用于矿业预测 | 不注册来源 |

所有内容继续按 `untrusted_data_only` 处理。未下载成功的 Q1/H1/Allied Gold 仅保留浏览器事件，不生成伪 snapshot hash 或 capture receipt。

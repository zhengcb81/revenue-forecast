# 官方网络研究事件

> 边界：这是 `revenue-forecast` 原生数据发现的一部分。先通过浏览器搜索/打开，后仅在隔离审计目录成功冻结 Results 与 Norton 两个 HTML；始终未写入 company-wiki、source catalog、索引或 worker 队列。内部搜索结果编号不作为来源标识，正式来源使用稳定 URL。

## W-001 — 2025 年报/2026–2028 规划

- 查询主题：紫金矿业官网、2025 年度报告、2026/2028 产量计划。
- 浏览器打开事件：[Zijin Announces 2026–2028 Three-Year Plan](https://www.zijinmining.com/news/news-detail-122478.htm)（当时显示官方公司沟通，2026-02-14）。
- 结果：浏览器读取确认金、铜、银、锂、钼 2028 production guidance；它不是营收目标。
- 冻结异常：随后直连相同 URL 得到的 HTML title/body 是无关的紫金中学工程页面，因此该本地快照被排除，不能作为强契约来源。

## W-002 — 2026Q1

- 查询主题：紫金矿业官网/上交所、2026 第一季度报告。
- 打开：[First Quarterly Report 2026](https://www.zijinmining.com/upload/file/2026/04/27/a96f9899e33b42b099a2c5de59e9206e.pdf)（官方监管报告，报告日 2026-04-21）。
- 结果：取得 Q1 营收、矿产品产量/售价/成本、项目爬坡信息和内部抵销限定。

## W-003 — 2025 Results / 演示

- 打开：[2025 Results](https://www.zijinmining.com/investor/2025-newyeji.htm)（官方业绩页）。
- 结果：取得 production guidance、公司储量资源汇总、主要金/铜/锌铅矿资源量/品位/持股/产量表。
- 异常：年度业绩演示 PDF 的一次点击返回 host internal error；没有反复调用。

## W-004 — 全球矿山与资源汇总

- 打开：[Reserves and Resources](https://www.zijinmining.com/global/zi-yuan-yu-chu.htm)（官方运营页）。
- 结果：取得 2025 年末六类矿产公司级储量/资源量及 100%/权益混合口径说明；没有逐矿储量。

## W-005 — 2025 股东大会沟通

- 打开：紫金矿业官网 2025 年度股东大会沟通页面（2026-06-06；稳定 URL 将在来源冻结时补录）。
- 结果：确认 2026 LCE 12 万吨、2028 LCE 27–32 万吨及 19 国/五洲/30+ 矿山项目概况。

## W-006 — 年报后重大公告/项目新闻

- 检索区间：2026 年报发布后至 2026-08-12。
- 打开：[Announcements](https://www.zijinmining.com/investor/Agu.jsp) 与 [Media Center](https://www.zijinmining.com/news/news_list.jsp)。
- 命中：2026H1 归母利润预告、Allied Gold 交易方案变更、Norton 破碎系统投产。
- 口径：利润预告不替代收入；交易变更/产能新闻只作为相关 revenue driver 或反证，不自动写入模型。
- 原始/稳定来源：
  - [H1 operating update](https://www.zijinmining.com/news/news-detail-122842.htm)
  - [H1 results increase announcement PDF](https://www.zijinmining.com/upload/file/2026/07/09/06b57b716de246f782abca6f4597a310.pdf)
  - [Allied Gold transaction change PDF](https://www.zijinmining.com/upload/file/2026/07/29/ecc0a08c29c5469ea40abbaf50c0de6a.pdf)
  - [Norton crushing system commissioning](https://www.zijinmining.com/news/news-detail-122827.htm)

## W-007 — 年度业绩说明会与演示

- [Convening notice PDF](https://www.zijinmining.com/upload/file/2026/03/13/c50df5e4ba53435192722fc091411d93.pdf)：说明会时间为 2026-03-23 10:00–11:30，上证路演中心直播/文字互动。
- [Presentation listing](https://www.zijinmining.com/investor/lu-yan.jsp)：列有 2025 Annual Results Presentation；一次 PDF 点击失败。
- [2025 Results HTML](https://www.zijinmining.com/investor/2025-newyeji.htm)：成功读取核心图表与主要矿山表。
- 搜索结论：未找到可稳定引用的紫金会后问答/文字实录；记录为 capture gap，而非“未召开”。

## 最终保存状态

- 未把任一网页/PDF 下载到 company-wiki。
- 未调用 source catalog ingest/scan、normalize、summary、chunk/tag 或 worker priority。
- 隔离审计目录只保存了有效的 2025 Results、Norton HTML，以及一个被排除的错误 strategy HTML；它们不是共享 source handle。
- Q1/H1/Allied Gold 与演示/说明会内容没有本地快照，只保留浏览器事件。
- 最终预测因此降级为 isolated draft，并在 TRUST_BOUNDARY 披露。

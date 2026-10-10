# FLOW 补充验收：年度消费角色

仅接受 typed period-flow 输入还不够；原实现允许 H1 110 直接成为年度收入 110，也允许 H1 reported_total/segment_base 作年度基数。六个 public/validate-only 反例是真实产品 RED。

新增 contracts/annual_consumption.py 的单一纯责任合同，MAIN 接入 input failfast/collector 和 strong 输出边界。不展开 derived 祖先，不推断日期，不加身份或许可。年度flow只接 annual 或覆盖实际完整FY的 period_flow；明确 stock/rate 的 point_in_time 原样保留。3.7/3.8 保持旧语义。

正控含 full FY、H1+H2 显式derived、未消费H1旁证、非12月财年、三个stock桥真实compute→strong。最终组合责任验证109 passed /46 subtests；ruff/mypy绿。TEMP及一次独立mypy-cache已删除；零外部调用，生产原件/配置未改。

初次RED中另有 helper缺失和一个positive fixture claim/source注册缺陷，分别记录，不能都冒认产品缺陷。完整SHA/日志/角色覆盖见 annual-acceptance.json。仅新增两个文件，不改calc/doc/report，不提交。最终发布/安装/真实研究仍MAIN负责。

最终补充：AUM inflows 不能因 monetary_balance 维度成为 stock，renewable average_commissioned_mw 不能因 quantity 维度被误当 flow。已独立TDD 2F/1P→修复；stock/rate按明确业务角色划分，原失败日志保留，最终annual-final-green2.log 109PASS。源码稳定，供MAIN正常提交/推送。

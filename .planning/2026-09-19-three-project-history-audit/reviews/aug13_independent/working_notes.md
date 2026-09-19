# 2026-08-13 两项计划的独立全文复核

2026-09-19：已完成 CA 15 MD、ZR 13 MD 全文复核（不把计划完成误写成产品完成），并读取两份 TERMINAL_NOTICE.json。3818行、2959非空原文行覆盖闭合：2497语义occurrence+462结构上下文，97人工区间判定，pending/extra=0。原规格、执行卡、收据与当前入口的比较及26+30hash复算已落盘，见 review.md、coverage.json、item_ledger.jsonl、manual_cases.json、checks.json。

重点：71 行登记不等于 71 门通过；5 FC150x 已包括在 71，不能无解释重复计入；117 DAG 包括明文要求由 CA304/CA301–306 接替的 ZR1009/ZR1101–1105。CA306 当前 next=ZR1101，须判断后继执行是否仅镜像、是否缩门。原计划有多版本状态词、授权 discovery 和自然周期阈值，须保留版本，不推断未经证实的现状。

当前证据复核范围：CA003/CA105、CA202/CA206、CA301/302/304/306、ZR205/409/713/1104，以及 original hashes、197个scenario ID的结构统计与运行门的区别。只执行文件读与精确AST纯函数，写入审计目录；未运行生产worker、数据库或下载。

后续独立交叉复核已完成：../second_wave/filing_cross_review.md，全部31模型+24深层条款、F01/F02已修、host_signed与整组发布反例范围、矿业helper口径、主实施计划。11测试源码hash、24深层条款源hash均匹配。矿业TC的800严格为按每saleable单位且该量已扣payability的条件值；deadline10→14为模拟9秒调用后旧remaining允许5秒退避，不是第二调用或墙钟14秒。

# 可替换来源端口

RF读取来源只通过SourceRef/版本化公开资料包与进程端口，不导入CWP实现、不读取其数据库、不判断其内部目录。

- prepare_source_result/prepare_source：source_reader_command为原文公开CLI的argv前缀；narrative_reader_command独立配置摘要公开CLI。CLI分别提供--source-reader-command-json与--narrative-reader-command-json。
- prepare_registered_source_result：同样支持原文command注入，复用已有逻辑来源。
- command省略时保留既有本地CWP CLI部署；显式command的catalog_config是绝对不透明句柄，由所选生产者解释。RF不要求该句柄指向本机source_catalog.yaml。
- metadata/reference只表示定位，真正使用仍读原始或资料包字节，按实收SHA/大小、核心身份/期次/as-of及公开质量语义解释。摘要只作来源材料，不能自己变成已验证的预测。

JSON排版、key顺序、空白不构成拒绝理由。成功receipt/bundle可附extensions对象作为非权威诊断；它不能覆盖core字段。重复键、非有限数、错原文字节、错身份和不支持的核心版本仍报告真实原因。SHA绑定实际字节，不把解析后重编码的字节当原件。

普通CI只含本仓和普通依赖，不检出CWP/FF。原有涉及生产者SQL/实际湖的测试断言由company-wiki/integration的ROOT系统套件维护；25文件迁移表及混合函数迁移表保留去向。大节点执行真实组合，历史canary/人工签收套件只作显式历史重放，不成为日常运行许可。

本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-10-A · 先行完成实际采用模型的专业披露适配

Parent：I-10；状态：planned；Owner：行业/会计reviewer主责；独立验证者核对原文和历史收入；依赖：I-07-B、M01、M02、M03、M04、M05、M06、M07、M08、M09、M10、M11、M12、M13、M14、M15、M16、M17、M18、M19、M20、M21、M22、M23、M24、M25、M26、M27、M28、M29、M30、M31。

前提：

- I-07-B已提供实际公司、信息日及可读取来源；M01–M31的A–C公式资格已独立验收。
- 先冻结本次实际采用的公司/分部/模型清单；只要求这些模型完成企业披露适配，不要求未使用模型全部适配。
- 执行位置由I-00-B绑定隔离checkout；所有证据相对本轮新attempt_root，禁止覆盖旧审计或生产数据。

动作：

1. 从I-07-B公司材料建立selected_model_manifest：逐公司/分部列model_id、对应M卡、生命周期、会计口径、采用原因及适配范围。未使用模型标not_selected，不宣称企业适配通过。
2. 逐个实际采用模型执行M卡D：逐字段原文/页码/hash/available_at/单位转换/参数ID映射，明确可选默认的经济依据、期初锚点和special_review。行业/会计reviewer对口径及约束签署；保险复杂口径加入精算reviewer。
3. 执行M卡E的历史段对账：使用独立披露的已结束期间经营数据复建收入，与同口径已披露收入核对，先冻结容差，再解释量/价/汇率/范围/确认时间残差。不能用收入倒推参数后称独立验证。
4. 通过calculate_model_path验证字段→参数→模型→输出的接线。此阶段可用已披露历史参数在low/base/high三个键上保持同值以验证映射，无需等待I-11的定性参数校准；必须标historical_mapping_probe，不称三情景预测。
5. 逐公司/模型签署disclosure_adaptation资格，附对应M卡D/E产物及独立review。先行适配完成后，I-11-B可在已审定口径内校准参数值，I-07-E消费该资格进行最终公司预测；本卡不依赖I-11或I-07-E。
6. 若后续仅改变同一口径下假设值，保留适配引用并记录参数delta；若改模型、单位、会计、分部范围或收入确认逻辑，则创建新适配版本，使依赖旧口径的下游结果失效并按顺序重跑，不能以旧资格覆盖新口径。

停止：

- 实际采用清单不明确或来源不可读取→STOP_SELECTION_OR_EVIDENCE。
- 任一实际采用模型公式资格未通过→STOP_FORMULA_DEPENDENCY。
- 单位/会计/期初锚点/收入历史桥未解决→STOP_DISCLOSURE_ADAPTATION；允许其他已合格分部保留局部结果，但不放行整个公司正式预测。
- 只有历史映射probe却声称真实三情景/准确性通过→STOP_QUALIFICATION_SCOPE。

验收：每个实际采用的公司/分部/模型完成M卡D/E专业适配与独立签署，证据可复核，口径范围明确；未使用模型只标not_selected。该卡不授予准确性，不要求I-11或I-07-E产物。

证据：`evidence/I-10-A/selected_model_manifest.json`、`evidence/I-10-A/disclosure_mapping.json`、`evidence/I-10-A/accounting_decision.md`、`evidence/I-10-A/historical_reconciliation.json`、`evidence/I-10-A/historical_mapping_probe.json`、`evidence/I-10-A/model_DE_evidence_manifest.json`、`evidence/I-10-A/disclosure_qualification.json`、`evidence/I-10-A/independent_adaptation_review.md`。

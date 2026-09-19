本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-11-A · 冻结定性到参数的可证伪命题

Parent：I-11；状态：planned；Owner：行业reviewer主责，弱模型可整理证据；依赖：I-00-B、I-00-C。

前提：

- 基期公司/分部/信息日确定；只用可核验来源。

动作：

1. 逐个命题填qualitative_template，禁止空着source、driver或单位。
2. 把管理层目标单列source_type，按原始来源归并independence_group；十篇转述同一电话会算一个来源。
3. 写完整机制链，指定唯一或显式多个parameter_id；‘品牌好’等不能量化的判断保留叙述，不强行加百分点。
4. 行业reviewer审定可观测性、时间滞后及是否已在基期/其他driver反映。

停止：

- 无法定位模型driver/收入确认环节→仅保留定性未量化。
- 来源晚于as_of或原文无法核查→STOP_EVIDENCE。

验收：每命题有可追溯来源、机制、driver、时点、双计排除和明确unquantified/approved状态；不要求全部强行量化。

证据：`evidence/I-11-A/hypotheses.json`、`evidence/I-11-A/source_map.json`、`evidence/I-11-A/mechanism_review.md`。

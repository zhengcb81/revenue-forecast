本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-14-B — 自然时间与UI观察证据
Parent：I-14。依赖：I-14-A。Owner：独立观测者。

必读：../reviews/wiki_legacy/review.md的WR窗口；../reviews/aug09_plans/manual_cases.json中A09-055/056；旧原义务的实际观察周期。允许写证据，默认不启动后台。

1. 将scheduled_at、started_at、sampled_at、finished_at、quick_check耗时分列。重叠窗口不能相加制造自然时长。
2. 合成时间输入：观察00:00–00:29，结束后quick_check8分钟；oracle观察29分钟而不是37分钟。此例只验证计时算法，不是真实观察资格。
3. 登录30/60/120秒检查使用同一事件锚点和预定时间窗，时间容差在试验前由reviewer冻结；实际支持的UI捕获能力未具备时标blocked，不用事后日志造即时截图。
4. 把自然日/周/月需求原文ID映射到I-17待运行日历；未到时点保留pending，不能用模拟clock达标。

退出：计算和证据分类正确，未执行的自然/UI格仍未完成。恢复：停止本次观察，不改变worker原暂停意图。

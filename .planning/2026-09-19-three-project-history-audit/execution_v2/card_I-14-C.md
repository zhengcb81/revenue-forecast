本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-14-C — 在真实异常出口验证脱敏
Parent：I-14。依赖：I-00-B。Owner：日志维护者。

锚点：CW/src/company_wiki/source_catalog/worker.py::_write_unhandled_exception_event；旧证据../reviews/wiki_legacy/review.md。允许改异常出口、现有redactor及关联隔离测试。

1. 创建纯合成异常值含Authorization: Bearer SYNTHETIC_AUDIT_TOKEN和token查询参数，不能读取实际密钥。
2. 通过真实异常事件写出路径进入scratch日志，检查整行/嵌套cause/截断边界，不仅检查键名或独立helper。
3. 原始秘密marker在stdout/stderr/事件中不得出现；保留非敏感error code、stage和request ID便于定位。
4. 加一条无敏感数据正常异常，确保错误语义不被整体吞掉；定好脱敏规则后复验未知键的敏感值。

退出：实际出口不泄露合成marker且仍可诊断；不声称覆盖全部未知secret形式。恢复：撤回隔离实现，保留合成日志。

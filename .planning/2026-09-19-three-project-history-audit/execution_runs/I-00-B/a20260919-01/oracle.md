# I-00-B 冻结预期
1. 8个源码锚点存在且sha记录于binding.json；任何漂移 => 受影响卡重绑，不按旧行硬改。
2. 样本3/3精确hash匹配（sample_rehash.json raw_all_match=true），不按公司名替换相似年报。
3. 旧run.json只作参数来源参考；禁 --allow-download 重放、禁生产cwd；source_preparation/fetch_filing无--config参数=>隔离能力须在I-01/I-04等卡验证，不得猜参数。
4. 负例绑定规则已在binding.json.negative_binding_test：写生产DB路径/不存在参数的绑定不得执行。
5. 从本卡起，所有卡运行cwd=per-attempt隔离目录；解释器=per-attempt iso venv；全局Miniconda python禁用。

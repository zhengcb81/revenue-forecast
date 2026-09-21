本卡由[model_cards.md](model_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[model_cards.md共用规则](common_model_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-10-B — model_registry 的静默补 0 与按名字定符号

Parent：I-10。依赖：I-00-B。Owner：模型注册维护者；独立 reviewer。

来源：`OWNER_DECISIONS.md` §5 第 1/2 项 + §13 **T1-22**（授权立卡，**两项同卡**）。

锚点：RF/scripts/model_registry.py 的 `MODEL_REGISTRY` 与 `driver_value_bounds`。
本卡**不改任何 M01–M31 的公式**、**不动任何冻结件**。

1. **缺陷①：`model_registry.py:335` 静默补 0。**
   现行 `values = drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))`
   ⇒ 无显式 default 的 optional driver 被补 `0.0`（**31 个槽位 / 24 个模型**）。
   这把"**不存在**"与"**没找到**"编码成**同一输入**，D 阶段会直接产出错误映射。
   修复：省缺即抛 `ModelRegistryError`；**仅当** `spec.defaults` 有显式值时才允许省缺。
   注意：把隐式 0 变显式 0 **仍无法区分**"没找到"，故不采用"补显式 0"方案。
2. **缺陷②：`_SIGNED_DRIVERS` 按名字定符号。**
   现状：`other_revenue` signed 而 `usage_revenue` 非 signed；而
   `franchise_system_sales`/`supply_revenue`/`recognized_performance_fees` 同属
   "**可冲回已确认金额**"却在 `[0, inf)` ⇒ 名字与语义不符。
   修复：改为基于**语义角色**的规则（例如按 dimension 与显式的"可冲回"角色位判定），
   不按 driver 名字硬编码集合。
3. **兼容性（必须先声明）**：改②会改变部分 driver 的值域上下界。
   25 个既有 driver 的边界是否受影响须**逐个列出**；任何边界变化都要附"哪个 M 卡的哪个用例会受影响"。
   受影响的历史期望**一律追加更正、不回改**（沿用 T1-12 的统一规则）。
4. 负例（可失败用例）：①某个只有 optional driver 且无显式 default 的模型，省缺时**必须抛**；
   ②`franchise_system_sales` 传入负值时必须**被接受**（语义角色为可冲回）；
   ③一个名不在任何角色表里的新 driver 必须**不得**静默获得"按名字猜测"的符号。
5. 不得为本卡扩大 allowlist 去改 31 张 M 卡的正文或证据；
   本卡产出的是**注册层契约**，由 I-10-A 在后续复验中消费。
6. `code_root` 锚点按事故教训**每次复算**：`scripts/model_registry.py` 与
   `scripts/model_extensions.py` 的哈希必须与本卡绑定值一致；不一致即停止并登记漂移。

退出：省缺不再静默补 0；符号按语义角色判定且兼容性影响逐项列出。
恢复：回退注册层改动；保留边界影响清单与全部负例输出。

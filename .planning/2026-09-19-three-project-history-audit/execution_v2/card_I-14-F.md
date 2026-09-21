本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-14-F — 深层 cwd 下的 WinError 206（产品侧短 basetemp 约定）

Parent：I-14。依赖：I-00-B。Owner：测试维护者；独立 reviewer。

来源：I-14-C r5 的 `decision.md` §19-③（`OWNER_DECISIONS.md` §13 T1-7 授权立卡）。

1. 观测（已实测）：cwd 路径 166/167 字符时，两种节点**在两棵树上 3/3 全部失败**；
   改短 basetemp（74/75 字符）后 **3/3 全部通过**。⇒ 与 cwd 深度强相关，与树无关。
2. 这是 `WinError 206`（文件名或扩展名太长）在**产品侧**的约定问题：应为测试/子进程建立
   **短路径 basetemp 约定**，而不是要求调用方把 cwd 挪浅。
3. 约定须写成可判据：给定 `cwd` 与 `basetemp` 长度，何时使用短路径回退、回退到哪里、如何清理。
4. 负例：一个故意超深的 cwd 必须**被约定接住并成功**，而不是报 206；一个正常深度的 cwd
   不得被无谓地改道（否则掩盖真实路径问题）。
5. 不得以"把 cwd 缩短"当作修复——那是绕开问题。也不得靠改 `pytest` 全局配置放宽。
6. `START_HERE.md` 已有纪律：`pytest --basetemp` 只能指向**本次新建的空目录**，
   不得指向 attempt 根、证据根或上次测试目录；本卡约定必须与该纪律一致。

退出：深 cwd 下不再出现 206，且正常 cwd 行为不变。
恢复：回退约定实现；保留 166/167 与 74/75 两组原始观测。

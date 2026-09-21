本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-14-D — 脱敏裸值贪婪语义收窄到单 token（C13 立卡）

Parent：I-14。依赖：I-00-B。Owner：日志维护者；独立 reviewer。

来源：I-14-C r5 的 `decision.md` §C13。该缺陷已**冻结不改**（`test_f08_c13_multiline_loss_is_frozen_not_hidden`），
因为它**改则破坏 E4b 的 193 字符基线**；故本卡是它独立的、有自己 oracle 的收窄卡。

锚点：CW/src/company_wiki/source_catalog/redactor（`_BARE_VALUE`，源自 r1，`X+(?:\s+X+)*`）；
I-14-C 的 `iso/product_r2` 证明该行为**继承自 r1、非 r3/r4 引入**。

1. 先量出**当前**基线：裸值停止集为 `,;&"'|` 加空白，且**未加引号的值跨换行**。
   实测（F-I14C-R4-02）：`a=1 token=<marker> b=2` → `a=1 token=<redacted>`；
   而 `'upload failed for token=<marker> doc=17\nstage=summarize code=llm_global_failure request_id=req-1'`
   → `'upload failed for token=<redacted>'`（reviewer 的 24 字符 marker：**112 字符进、34 字符出**，
   `doc=17`、`stage=summarize`、`code=llm_global_failure`、`request_id=req-1` 全部丢失）。
2. 收窄候选：裸值只吃**单个 token**（遇空白即停）。注意这不是"截断"——34 ≪ 200 的截断上限。
3. **新 oracle 必写**：E4b 的 193 字符接受长度**正是由当前行为导出的**；收窄后该基线必然改变，
   信封宽度也会变。新 oracle 必须在改代码**之前**冻结，且不得调用被测函数生成 expected。
4. 负例：多行诊断（`doc=17`/`stage=`/`code=`/`request_id=`）在收窄后**必须存活**；
   纯合成 marker 必须仍被脱敏；既有 rule table `cred-multiline-swallow` 系列需按新语义更新
   （更新的是**语义期望**，不是把失败改绿）。
5. 不得以"冻结测试失败"为据回退；该冻结测试的**唯一正当结局**是本卡写完新 oracle 后由 reviewer 改写它。

退出：裸值不再跨行吞掉后续诊断键，且 E4b 新基线经独立 reviewer 复算。
恢复：回退 redactor 与 rule table 到本卡前像；保留合成日志。

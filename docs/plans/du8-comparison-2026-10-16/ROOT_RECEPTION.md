# DU8 RF ROOT接收 — 2026-10-17

状态：最终独审PASS、未解决0，main/origin已正常发布且精确CI成功，技能定点同步与清理完成。作者最终8845bc18，ROOT保留完整历史合流6bd53b78；ROOT修复b41dceef。原handoff中最终67b15a60/125等为历史，不代表当前源码或测试；不得按其冻结声明接收。

## 实际改进与最终回归

唯一target_comparison owner承载显式legacy兼容和typed委托，生产及报告共同使用；报告仍绑定独立输入，两个owner参数剥离被审比较行，防止回声自证。legacy/typed历史容差差异明确保留，不更改原有数字/单位/季度路径和gold。

ROOT独审发现Python bool()和dict==可把0/1当false/true，共用report边界已改为严格owner bool/None singleton保真；typed合法未知null仍not_comparable。先独立RED28FAIL/29PASS，再修复；第一稿48FAIL包含20消息regex过窄，原日志保留、测试更正单列。新增57回归覆盖7模型/4伪值/两验证入口及合法null。

作者最终实际27目录504PASS/7SKIP；ROOT最终28目录558PASS/7SKIP＋163subtests，26.09秒。中间559PASS/2FAIL是两个重复AST要求内联调用而拒绝中间变量；原FAIL保留，移除3个重复/无效AST测试及专用helper142行，保留所有gold、手算、CLI、篡改、owner poisoning和echo行为检查。独立agent另检查owner返回值必须真实消费，未新增运行时人工许可/身份/签收。

## 隔离与记录

原始UTF16作者收据按历史保留，ROOT UTF8收据见receipts/root-reception。测试均隔离registry/output/pytest临时目录、sentinel字节和mtime不变、自有Temp清理，0API/0下载/0原件复制，作者树只读。RF main原三条告警WIP及147个output文件保持，未混入本卡。ROOT新增接收工作树发布后核干净移除；原作者树不删。

这些都是合成模型工程验收，不是真实公司数据、CWP来源生产或买方模型质量验收。主线并入和安装同步只由ROOT定点处理。

## 最终独立审查

[独立报告](du8_rf_root_review.md)绑定b41dceef，12源/测试原始SHA和Git blob一致（CRLF/LF分别列出）。7正常模型、35篡改全部拒绝、38行为及4owner消费检查通过；代码未变不重复测试。独立脚本原始路径为审查工作区，归档脚本是历史探针，不在归档目录直接执行/覆盖原收据；固定57回归和原CLI套件可从干净检出复现。

## 发布与安装完成

main/origin已正常发布c984a8fa，pre-push416PASS＋36subtests、36.90秒；[精确CI39016431219](https://github.com/zhengcb81/revenue-forecast/actions/runs/39016431219) SUCCESS。三份.agents/.claude/.codex各4文件先核旧主线后定点同步，6正常模型/6数字伪装拒绝通过，实际导入安装目录而非仓库源码。配置/output及其他文件保留。发布收据见receipts/root-reception/publication.json。

本次ROOT临时接收工区已用正常git worktree remove移除，核对确为本轮绝对路径、树干净、全部历史已并入main才移除，未force、未删作者树；清理约866MB逻辑检出文件（不冒称磁盘实际可用空间增长相同）。main既有3条告警WIP和147output元数据未变。随后收据脚本一次默认GBK读取中文路径报错、缺收据级联导致空commit未创建；改明确UTF8复核并补收据，没有重复删目录或改源码。后续只补此发布文档，工程仍冻结b41dceef；返回CWP生产接线，不能以本包通过宣称真实PDF/正式摘要已完成。

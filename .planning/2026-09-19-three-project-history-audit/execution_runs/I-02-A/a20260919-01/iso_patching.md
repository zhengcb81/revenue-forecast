# iso_patching — 隔离环境缺失依赖与结构决策记录（I-02-A / a20260919-01）

1. `yaml`(PyYAML) / `requests` + `urllib3 / idna / charset_normalizer / certifi`：
   从 I-01-A attempt 的 `iso/venv/Lib/site-packages` **离线复制**到本 attempt 同名字目录
   （生产 `company_wiki/__init__.py` 与 source_catalog 顶层 import 链需要）。无 pip、无网络。
   运行时仅出现 `RequestsDependencyWarning`（stderr），不参与判定。

2. override 结构：`scripts/w02a_bootstrap.py` 沿用 I-01-A 同一手法——合成 package
   （company_wiki / source_catalog / adapters，`__path__` 指向只读仓库 src），按依赖顺序从
  `iso/override` 注册本卡修改文件副本（models / scanner / canonical_writer + 继承的 config /
   adapter_dispatch / service 副本），其余模块按文件路径从只读 src 按需加载；最后把真实的包
   `__init__.py` 编译执行到合成包模块里，使 runner 的
   `from company_wiki.source_catalog import …` 也走 override 链。prod 模式下直接
   `sys.path.insert(0, REPO_SRC)` 全走生产原文（before 基线）。

3. 产品副本差异范围：除 decision.md 冻结的回执字段/四道门逻辑外无任何其他行为变更
 （早前编辑过程中曾出现的重复 mkdir 行已删除）。

4. Windows MAX_PATH 处理（重要，非产品逻辑）：本 attempt 深路径 + canonical 副车临时文件名会
   越过 260 字符上限；曾尝试 subst 虚拟盘，但 writer 内部 `Path.resolve()` 会把 subst/8.3 展开
   回物理长路径，因此样例 scratch 树放在**短物理路径**
   `%TEMP%/w02a/a20260919-01_case_scratch`，每次运行结束时全量复制回
   `after/case_scratch_retained/`（sqlite journal 除外）。每 case 复用同一短根并在开始时
   rmtree 重建，保证库隔离。命令与快照路径都在 commands/binding 中留痕。

5. fake 注入边界：所有故障注入（scan_root_strategy 抛错/裁剪候选/BogusResolver）都在
   `scripts/w02a_cases.py` 内以属性替换完成（先捕获原函数），产品副本中不含任何 fake 代码；
   正例（P1）完全走真实 scanner/resolver/writer。

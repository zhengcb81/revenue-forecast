# iso_patching — 隔离环境缺失依赖与结构决策记录（I-02-B / a20260919-01）

1. `yaml`(PyYAML) / `requests` + `urllib3 / idna / certifi / charset_normalizer`：
   真实 `company_wiki/__init__` 与 `source_catalog/__init__` 的 import 链需要（bootstrap 会 exec
   真包 `__init__`）。从 I-02-A attempt 的 `iso/venv/Lib/site-packages` **离线复制**到本 attempt
   同名目录。无 pip、无网络。运行时仅出现 `RequestsDependencyWarning`（stderr），不影响判定
   （shim 按最后一个 JSON 行转发信封，警告行留在 stderr 透传）。

2. override 结构：`scripts/w02b_bootstrap.py` 沿用 I-01-A/I-02-A 同一合成 package 手法
   （company_wiki / source_catalog / adapters，`__path__` 指向只读 RFC 仓库 src），预注册本卡
   6 个修改副本中的 4 个 CW 文件（error_taxonomy / acquisition_service / acquisition_journal /
   cli），其余模块按需从只读 src 加载；RF 两个文件不进包，直接以脚本路径执行（cwd=A）。
   `source_preparation.py` 副本：`FILING_FETCH_CLIENT` 指向同目录的 override 兄弟副本；
   非 allowlist 的 helper（company_wiki_source / processing_demand）保持从**只读** RF scripts
   目录加载；在规范化 envelope 时通过 `w02b_bootstrap`（合成包 shim）按真实模块名接线 CW
   error_taxonomy（幂等，try-import 已注册则跳过）。

3. 产品副本差异范围：decision.md 冻结的信封字段/规范化/fail-closed 行为 + journal additive
   字段 + cli 出口结构化组装，无其他行为变更（diff 见 changes.diff；scratch 里没有任何
   pseudo-XX/pycache 混入）。

4. Windows MAX_PATH 处理（同 I-02-A）：scratch 树放在短物理路径 `%TEMP%/w02b/a20260919-01/<case>`，
   每次运行结束时把 case 现场全量复制回 `after/case_scratch_retained/<case>/`（含 catalog
   journal 与 staging 种子文件），sqlite journal 同样保留。

5. fake/subprocess 注入边界（I-02-A 同一约定）：所有故障注入（stub coordinator / failing
   writer / provider 文档）都构造在 `scripts/w02b_cw_ensure_runner.py` 与 `samples/fake_
   upstream_cli.py`（shim 声明路径）内；产品 override 副本不含任何 harness 代码。shim 属于本
   卡「固定样本」条款明确允许的 hermetic upstream CLI，bind copy 为
   `samples/upstream_root/scripts/fetch_filing.py`，无产品命令新增。

6. 深层分类路径：`SourceAcquisitionService._record_failure` 中异常类的
   `error_code/retryable` 属性（adapter/harness 声明）优先透传；`classify_exception` 的
   N/N-1 fail-closed 规则不变。`SourceRequest.request_id` 是派生属性
   （`urn:company-wiki:source-request:sha256:<identity-hash>`），journal/信封保留该 urn 形式；
   固定 `execv2-w02b` 在 RF/shim/provider 层逐字透传（oracle 已按原文 amendment 记录此差异）。

7. exit_probe 用真实修改后的 `cli.main()`（进程内属性替换 cli.SourceCatalog 为 harness stub，
   先加载真实 scratch config 使 load_catalog_config 成功）验证真实出口的组装语义；不改产品
   argv 形状，不新增产品命令。

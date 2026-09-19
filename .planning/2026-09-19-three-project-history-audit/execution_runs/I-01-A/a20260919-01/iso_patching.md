# iso_patching — 隔离环境缺失依赖记录

attempt：a20260919-01。production 仓零写；以下全部发生在本 attempt 的 iso/venv 内。

1. `yaml`（PyYAML 纯 Python 包）与 `_yaml`（标准 C 加速扩展，可选）：
   从本机 Miniconda `C:\Miniconda\Lib\site-packages\{yaml,_yaml}` **离线复制**到
   `iso/venv/Lib/site-packages/`（隔离 venv 原本只有 pip）。无网络访问，无 pip install。
2. `requests` 及其传递依赖 `urllib3 / idna / charset_normalizer / certifi`：
   同样离线复制，因为生产 `company_wiki/source_catalog/__init__.py` 顶层 import
   `security_identity`（其 import requests）——任何常规 package 导入路径都会先执行该 __init__。
   运行时 RequestsDependencyWarning（charset detection）只出现在 stderr，不影响判定。
3. 未安装 pytest（本卡全部用源码级 runner `scripts/w01_cases.py`，仅断言/JSON 输出）。

导入结构：override 模式由 `scripts/w01_bootstrap.py` 完成——
- 先注册合成 package（company_wiki / source_catalog / adapters，__path__ 指向仓库 src，只读）；
- 按叶到根顺序把 src 的 flags/adapters/store/runtime_policy 等按文件路径加载到 sys.modules；
- 最后把本卡修改的 5 文件副本（models/config/adapter_dispatch/scanner/service + config_doctor）
  以同名模块注册进 sys.modules，使 doctor 与 scan 都命中副本；
- prod 模式直接 sys.path 指向仓库 src（只读）并按文件路径加载生产 config_doctor。

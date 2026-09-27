"""B2-PROMOTION 测试环境 shim（只作用于测试进程，不改产品仓任何字节）。

问题：本沙箱内 Python 以 mode `0o700` 建目录（`tempfile.mkdtemp` /
`TemporaryDirectory` / pytest `tmp_path` 均如此）会得到一个本进程既不能写
也不能删的目录（`PermissionError [WinError 5]`），导致
`dayu-agent/tests/conftest.py` 的 symlink 探针在清理阶段抛错、pytest
`tmp_path` 不可用 —— 复审报告 §5.6 记录的是同一现象。

对策（与复审所用 "mkdtemp/mkdir mode shim" 同类）：在 pytest 加载最早期把
`os.mkdir` 的 mode 恒等放大为 `0o777`（仅影响目录权限位，不影响任何产品
逻辑、不写入产品仓）。`os.makedirs` / `pathlib.Path.mkdir` /
`tempfile.mkdtemp` 均在调用期解析 `os.mkdir`，故一并生效。

用法：`python -m pytest -p b2_promo_shim ...`（本目录加入 `PYTHONPATH`）。
"""
from __future__ import annotations

import os as _os

_orig_mkdir = _os.mkdir


def _mkdir(path, mode=0o777, *, dir_fd=None):  # noqa: D401
    """Wrap os.mkdir forcing 0o777 so the sandbox can use the directory."""
    return _orig_mkdir(path, 0o777, dir_fd=dir_fd)


_os.mkdir = _mkdir  # type: ignore[assignment]

__all__: list[str] = []

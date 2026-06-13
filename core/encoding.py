"""
Windows UTF-8 编码统一引导 v1.0
创建日期: 2026-06-13

用途:
    在所有脚本入口处调用 setup_utf8_console()，
    将 stdout / stderr 强制为 UTF-8 输出，避免中文乱码。

问题根源:
    Windows 默认 locale.getpreferredencoding() = cp936，
    sys.stdout.encoding = gbk，内联 `python << EOF` 执行时
    中文字符串以 UTF-8 写入、GBK 编码输出 → 乱码。

使用方法:
    # 顶层脚本（与 core/ 同级，如 validate_report.py）
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from core.encoding import setup_utf8_console
    setup_utf8_console()

    # core/ 子目录下的脚本
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.encoding import setup_utf8_console
    setup_utf8_console()
"""

import sys
import io

_setup_done = False


def setup_utf8_console():
    """统一设置 stdout/stderr 为 UTF-8 编码。

    幂等：重复调用安全。
    Windows: 用 TextIOWrapper 包装 buffer，errors='replace' 兜底。
    其他平台: 优先使用 reconfigure (Python 3.7+)。
    """
    global _setup_done
    if _setup_done:
        return

    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except AttributeError:
            # 某些嵌入环境没有 buffer 属性，跳过
            pass
    else:
        for stream_name in ("stdout", "stderr"):
            stream = getattr(sys, stream_name, None)
            if stream is not None and hasattr(stream, "reconfigure"):
                try:
                    stream.reconfigure(encoding="utf-8")
                except Exception:
                    pass

    _setup_done = True

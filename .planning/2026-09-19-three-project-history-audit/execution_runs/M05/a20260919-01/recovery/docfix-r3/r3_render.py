"""Shared renderer for the r3 block inserted into oracle.md.

The block states its own size in bytes AND the resulting file size, so rendering is a
joint fixed-point problem: the digits of both numbers are part of the text whose size is
being stated. render_block() iterates until size and the size-dependent placeholders all
stop changing (a handful of iterations).

Callers:
  f06_dedupe.py          fresh merge of a two-section document
  f13_fold_wording.py    re-render of the block against the preserved pre image
Both go through here, so both paths produce byte-identical output.
"""
from __future__ import annotations

from typing import Callable


def render_block(template: str, values: dict,
                 size_dependent: Callable[[int], dict] | None = None,
                 max_iter: int = 16) -> tuple[str, int]:
    """Render template with self-consistent {inserted_bytes} (and derived keys).

    The template is expected to use LF; the result is normalised to CRLF because the
    appended/inserted region of oracle.md uses CRLF.
    Returns (text, size_in_bytes).
    """
    tpl = template.replace("\r\n", "\n")
    size = 0
    extra: dict = size_dependent(size) if size_dependent else {}
    for _ in range(max_iter):
        vals = dict(values)
        vals.update(extra)
        vals["inserted_bytes"] = size
        text = tpl.format(**vals).replace("\n", "\r\n")
        new_size = len(text.encode("utf-8"))
        new_extra = size_dependent(new_size) if size_dependent else {}
        if new_size == size and new_extra == extra:
            return text, new_size
        size, extra = new_size, new_extra
    raise RuntimeError("r3 block size did not reach a fixed point")

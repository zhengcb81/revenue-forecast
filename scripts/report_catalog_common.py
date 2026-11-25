"""Value-level report catalog contracts shared by its readers and writers."""

from __future__ import annotations

import re
from typing import Any


SOURCE_REF_FIELDS = frozenset(
    {"document_id", "source_id", "content_sha256", "byte_size", "mime_type", "schema_version"}
)


class CatalogError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise CatalogError(code, message)


def assert_pathless(value: Any) -> None:
    """Refuse accidental publication of a private Windows/Unix file locator."""
    if isinstance(value, dict):
        require(not any(key in {"path", "relative_path", "original_path", "doc_root"} for key in value),
                 "path_leak", "public projection contains a path key")
        for child in value.values():
            assert_pathless(child)
    elif isinstance(value, list):
        for child in value:
            assert_pathless(child)
    elif isinstance(value, str):
        require(not re.search(r"(?:[A-Za-z]:[\\/]|\\\\|/(?:Users|home|tmp|var)/)", value),
                 "path_leak", "public projection contains a physical locator")

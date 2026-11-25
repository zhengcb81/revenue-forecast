"""Retired WU-1304 diagnostic. Original implementation and receipts are in Git.

This path is kept for historical references. Processed-artifact reuse and
binding validation belong to company-wiki's source and extraction layer.
"""

from __future__ import annotations

import sys


if __name__ == "__main__":
    print(
        "WU-1304 canary retired. Use company-wiki's public source and extraction "
        "interfaces for current observations. Historical results remain in Git.",
        file=sys.stderr,
    )
    raise SystemExit(2)

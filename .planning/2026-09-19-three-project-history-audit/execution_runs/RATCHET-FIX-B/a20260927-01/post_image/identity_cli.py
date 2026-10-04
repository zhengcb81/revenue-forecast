"""Standalone console entry point for read-only listed-company identification.

Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only;
behaviour unchanged — ``main`` was split into straight-line steps so every
top-level function stays well under the frozen ceiling (6).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .security_identity import (
    IdentityStatus,
    OfficialSecurityMasterRefresher,
    SECURITY_MARKETS,
    SecurityIdentityResolver,
    SecurityMasterStore,
    load_identity_master,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="company-wiki-identify",
        description="Resolve a company name, alias, or ticker to a verified listed security.",
    )
    parser.add_argument("query", help="company name, alias, or ticker")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".source_catalog/security_master"),
        help="versioned per-market security-master cache directory",
    )
    parser.add_argument("--market", choices=SECURITY_MARKETS)
    parser.add_argument("--exchange")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="refresh official snapshots before resolving; failures keep stale snapshots",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser


def _configure_stdio() -> None:
    """UTF-8 console output, best effort (mirrors the original guards)."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _refreshed(store: SecurityMasterStore, args: argparse.Namespace):
    """Refresh official snapshots when ``--refresh`` was passed, else None."""
    if not args.refresh:
        return None
    refresh_markets = (args.market,) if args.market else SECURITY_MARKETS
    return OfficialSecurityMasterRefresher(store).refresh(markets=refresh_markets)


def _resolved_payload(args: argparse.Namespace):
    """``(payload, result)`` for the parsed CLI args.

    Everything the original ``try`` block did — store construction, optional
    refresh, resolution, payload assembly — so a failure still propagates to
    ``main``'s handler and is reported exactly as before.
    """
    store = SecurityMasterStore(args.cache_dir)
    refresh = _refreshed(store, args)
    result = SecurityIdentityResolver(
        load_identity_master(store, market=args.market)
    ).identify(
        args.query,
        market=args.market,
        exchange=args.exchange,
    )
    payload = result.to_dict()
    if refresh is not None:
        payload["refresh"] = refresh
    return payload, result


def main(argv: Sequence[str] | None = None) -> int:
    _configure_stdio()
    args = _parser().parse_args(argv)
    try:
        payload, result = _resolved_payload(args)
    except Exception as exc:
        # ZR-204: unified error taxonomy emission (canonical code + retryable).
        from .error_taxonomy import structured_error

        print(
            json.dumps(structured_error(exc), ensure_ascii=False, sort_keys=True),
            file=sys.stderr,
        )
        return 1
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0 if result.status is IdentityStatus.RESOLVED else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]

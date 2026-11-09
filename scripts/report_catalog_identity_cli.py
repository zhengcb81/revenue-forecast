"""Explicit admin CLI wiring the trusted StockWiki resolver into W09 import.

Commands:
  python scripts/report_catalog_identity_cli.py resolve --entity-id ENT_... [--listing-id LST_...]
  python scripts/report_catalog_identity_cli.py import-w09 --entity-id ENT_... \
      [--analysis-subject-id ...] [--listing-id LST_...]

Both commands read the trusted deployment config (``--config`` or
``RF_IDENTITY_BRIDGE_CONFIG``) exactly like
``report_catalog_identity_resolver``; identity evidence always comes from a
real public lookup through that config, never from inline caller JSON.  The
default ``report_catalog_cli.py`` stays resolver-less and disabled; this
CLI is the only explicit management path that can hand ``import_w09`` a
trusted resolver.  ``--catalog-file`` is the same trusted in-process
catalog injection the owner tests use; without it the managed owner root
applies. Explicit ``--owner-root`` (before or after the subcommand) selects
an existing trusted RF business workspace for this management entry only;
it refuses a conflicting catalog injection and never enables writes on the
read-only CLI. A first import requires the fixed pre-existing W09 source
package when no managed catalog exists. No root is created or guessed.
No research, model, network, or download runs from here.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_catalog import CatalogError, ReportCatalog, import_w09  # noqa: E402
from report_catalog_deployment import DeploymentError, split_owner_root  # noqa: E402
from report_catalog_research_attempt import import_research_attempt  # noqa: E402
from report_catalog_research_publication import import_research_publication  # noqa: E402
from report_catalog_research_identity import make_research_source_alias_resolver  # noqa: E402
from report_catalog_source_alias import make_source_alias_resolver  # noqa: E402
from report_catalog_identity_resolver import (  # noqa: E402
    IdentityBridgeError,
    load_bridge_config,
    make_identity_resolver,
    resolve_identity,
)


def _fail(error_code: str, detail: str) -> None:
    print(
        json.dumps({"error_code": error_code, "detail": detail},
                   ensure_ascii=False, sort_keys=True),
        file=sys.stderr,
    )


def _admin_owner_root(value: str | None, *, catalog_file: str | None) -> Path | None:
    """Validate an explicit management workspace without creating anything.

    A first W09 import may have no managed catalog yet. Its fixed, existing
    source package is the alternative owner-root marker. The content and SHA
    checks remain in import_w09; these markers do not establish identity.
    """
    if value is None:
        return None
    if catalog_file is not None:
        raise DeploymentError("owner_root_catalog_conflict", "owner root and catalog injection cannot be combined")
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise DeploymentError("owner_root_invalid", "owner root must be an absolute existing workspace")
    path = Path(value)
    if not path.is_absolute():
        raise DeploymentError("owner_root_invalid", "owner root must be an absolute existing workspace")
    try:
        root = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise DeploymentError("owner_root_absent", "owner root does not exist") from exc
    except (OSError, RuntimeError, ValueError) as exc:
        raise DeploymentError("owner_root_invalid", "owner root must be an absolute existing workspace") from exc
    if not root.is_dir():
        raise DeploymentError("owner_root_invalid", "owner root must be an absolute existing workspace")
    package = root / "delivery" / "w09"
    markers = (package / "recorder" / "w09-rf-research-20261023" / "run.json",
               package / "recorder" / "native-calls.jsonl",
               package / "registry" / "publications.jsonl")
    try:
        managed = (root / "artifacts" / "report_catalog").resolve()
        if not managed.is_relative_to(root):
            raise DeploymentError("owner_root_invalid", "managed catalog must stay inside owner root")
        if not managed.is_dir() and not all(p.is_file() for p in markers):
            raise DeploymentError("owner_root_missing", "owner root has neither managed catalog nor fixed W09 package")
    except DeploymentError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise DeploymentError("owner_root_invalid", "owner workspace cannot be inspected") from exc
    return root


def main(argv: list[str] | None = None) -> int:
    # Public protocol bytes remain UTF-8 on Windows operator consoles as well.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="strict")
            except (ValueError, OSError):
                pass
    try:
        owner_root_text, raw = split_owner_root(sys.argv[1:] if argv is None else list(argv))
    except DeploymentError as exc:
        _fail(exc.code, exc.message)
        return 2
    parser = argparse.ArgumentParser(
        description="Trusted StockWiki identity seam for the RF report catalog"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--config", help="trusted bridge deployment config JSON path")
    resolve = commands.add_parser("resolve", parents=[shared])
    resolve.add_argument("--entity-id", required=True)
    resolve.add_argument("--listing-id")
    migration = commands.add_parser("import-w09", parents=[shared])
    migration.add_argument("--entity-id", required=True)
    migration.add_argument("--listing-id")
    migration.add_argument("--analysis-subject-id")
    migration.add_argument("--catalog-file", help="trusted owner/test catalog injection path")
    research = commands.add_parser("import-research-attempt", parents=[shared])
    research.add_argument("--entity-id", required=True)
    research.add_argument("--listing-id")
    research.add_argument("--analysis-subject-id")
    research.add_argument("--run-id", required=True)
    research.add_argument("--recorder-sha256", required=True, help="trusted operator SHA256 of the actual research recorder")
    research.add_argument("--identity-anchor-capture-id",
                          help="trusted operator selection of a prior complete source-preparation capture in this run")
    research.add_argument("--deployment-snapshot",
                          help="trusted operator deployment snapshot basename within this run's execution directory")
    publication = commands.add_parser("import-research-publication", parents=[shared])
    publication.add_argument("--entity-id", required=True)
    publication.add_argument("--listing-id")
    publication.add_argument("--analysis-subject-id")
    publication.add_argument("--run-id", required=True)
    publication.add_argument("--recorder-sha256", required=True)
    publication.add_argument(
        "--review-receipt-sha256",
        required=True,
        help="trusted operator SHA256 of the exact completed independent-review receipt",
    )
    publication.add_argument("--identity-anchor-capture-id", required=True)
    publication.add_argument(
        "--deployment-snapshot",
        required=True,
        help="one trusted snapshot basename within this run's execution directory",
    )
    publication.add_argument("--source-stage-failure-capture-id")
    publication.add_argument(
        "--publication-version",
        default="v1",
        help="one trusted v1..v999 publication basename",
    )
    publication.add_argument(
        "--source-evidence",
        help="opt-in multi-source evidence JSON basename in this run execution directory",
    )
    args = parser.parse_args(raw)
    try:
        owner_root = _admin_owner_root(owner_root_text, catalog_file=getattr(args, "catalog_file", None))
        if args.command in {"import-research-attempt", "import-research-publication"} and owner_root is None:
            raise DeploymentError("owner_root_required", "research admission requires an explicit trusted owner root")
        explicit_catalog = ReportCatalog(root=owner_root) if owner_root is not None else None
        config = load_bridge_config(args.config)
        if args.command == "resolve":
            output = resolve_identity(args.entity_id, config=config, listing_id=args.listing_id)
        elif args.command == "import-research-publication":
            resolver = make_identity_resolver(config, listing_id=args.listing_id)
            assert explicit_catalog is not None
            output = import_research_publication(
                explicit_catalog,
                run_id=args.run_id,
                entity_id=args.entity_id,
                listing_id=args.listing_id,
                analysis_subject_id=args.analysis_subject_id,
                identity_resolver=resolver,
                recorder_sha256=args.recorder_sha256,
                review_receipt_sha256=args.review_receipt_sha256,
                identity_anchor_capture_id=args.identity_anchor_capture_id,
                deployment_snapshot=args.deployment_snapshot,
                source_stage_failure_capture_id=args.source_stage_failure_capture_id,
                publication_version=args.publication_version,
                source_evidence=args.source_evidence,
                source_alias_resolver=make_research_source_alias_resolver(
                    config, listing_id=args.listing_id
                ),
            )
        elif args.command == "import-research-attempt":
            resolver = make_identity_resolver(config, listing_id=args.listing_id)
            assert explicit_catalog is not None
            output = import_research_attempt(explicit_catalog, run_id=args.run_id,
                                             entity_id=args.entity_id, listing_id=args.listing_id,
                                             analysis_subject_id=args.analysis_subject_id,
                                             identity_resolver=resolver, recorder_sha256=args.recorder_sha256,
                                             identity_anchor_capture_id=args.identity_anchor_capture_id,
                                             deployment_snapshot=args.deployment_snapshot,
                                             source_alias_resolver=make_research_source_alias_resolver(
                                                 config, listing_id=args.listing_id))
        else:
            resolver = make_identity_resolver(config, listing_id=args.listing_id)
            identity_evidence = resolver(args.entity_id)
            catalog = explicit_catalog if explicit_catalog is not None else ReportCatalog(
                catalog_file=Path(args.catalog_file) if args.catalog_file else None
            )
            output = import_w09(
                catalog,
                entity_id=args.entity_id,
                analysis_subject_id=args.analysis_subject_id,
                identity_evidence=identity_evidence,
                listing_id=args.listing_id,
                identity_resolver=resolver,
                source_alias_resolver=make_source_alias_resolver(config, listing_id=args.listing_id),
            )
        print(json.dumps(output, ensure_ascii=False, sort_keys=True, allow_nan=False))
        return 0
    except DeploymentError as exc:
        _fail(exc.code, exc.message)
        return 2
    except (IdentityBridgeError, CatalogError, OSError, ValueError, KeyError) as exc:
        code = getattr(exc, "error_code", None) or getattr(exc, "code", None)
        _fail(code or "identity_cli_failed", str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

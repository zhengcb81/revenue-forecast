"""Trusted operator deployment seam for the owner report-catalog readers.

The public catalog and comparison CLIs are read-only, but they always
default to the workspace that holds the running code. A deployment that
keeps the real owner workspace -- the one holding the managed catalog and
the frozen report artifacts -- in a different directory needs exactly one
trusted way to point those same readers at it.

This module owns that argument and nothing else:

    --owner-root <absolute owner workspace>

It is a deployment parameter, never business input. It never enters a
request body, never selects a command, a catalog file or an environment
variable, and it never writes. Without the argument every reader keeps its
original code-root behaviour, so the seam adds no default path and no
default data.

The selected workspace is read through the existing ``ReportCatalog`` with
``root=``, so the managed catalog location, the relative artifact
locators, the byte SHA check, the admission and lineage rules, the
revision, the cursor binding and the immutability of older reports all
stay exactly as the owner core defines them. The same-root rule of
``REVENUE_REPORT_CATALOG`` is not widened: the owner core still refuses a
catalog environment path that belongs to another root.

Failure is named and pathless. The operator's physical workspace never
reaches stdout or stderr.
"""

from __future__ import annotations

from pathlib import Path

from report_catalog import ReportCatalog

DEPLOYMENT_SCHEMA_VERSION = "rf-report-catalog-deployment/1"
OWNER_ROOT_OPTION = "--owner-root"

# The owner core keeps the managed catalog under "<root>/artifacts/report_catalog".
# The seam repeats that location so it can tell an owner workspace apart from
# an unrelated directory; tests/test_report_catalog_deployment.py pins it to
# the location the owner core itself uses.
MANAGED_CATALOG_DIRECTORY = ("artifacts", "report_catalog")

# Read-only commands the trusted root may serve. Every other command of the
# public catalog CLI writes to the owner workspace and must never inherit it.
READ_ONLY_COMMANDS = frozenset({
    "list-runs", "list-reports", "get-run", "get-report", "get-model",
    "get-attempt", "get-calculation", "get-calculation-trace", "get-source-snapshot",
})
WRITE_COMMANDS = frozenset({"import-w09"})

_INVALID_ROOT_MESSAGE = "the owner root must be an absolute workspace path"
_ABSENT_ROOT_MESSAGE = "the owner root does not exist"
_MISSING_ROOT_MESSAGE = "the owner root has no managed report catalog"


class DeploymentError(RuntimeError):
    """A named, pathless failure of the trusted deployment argument."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def split_owner_root(argv: list[str]) -> tuple[str | None, list[str]]:
    """Take the trusted root option out of ``argv``.

    The option is removed before any request parser sees it, so no business
    request can carry it. The returned value is the raw option text; it is
    validated separately by :func:`resolve_owner_root`.

    An absolute workspace path never starts with "-", so a following option
    token is refused here instead of being swallowed as the workspace path.
    That keeps a malformed deployment argument a named, pathless failure
    rather than a parser usage error.
    """
    owner_root: str | None = None
    remaining: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == OWNER_ROOT_OPTION:
            if owner_root is not None:
                raise DeploymentError("owner_root_invalid", "the owner root option may be given once")
            if index + 1 >= len(argv):
                raise DeploymentError("owner_root_invalid", _INVALID_ROOT_MESSAGE)
            value = argv[index + 1]
            if value.startswith("-"):
                raise DeploymentError("owner_root_invalid", _INVALID_ROOT_MESSAGE)
            owner_root = value
            index += 2
            continue
        if token.startswith(OWNER_ROOT_OPTION + "="):
            if owner_root is not None:
                raise DeploymentError("owner_root_invalid", "the owner root option may be given once")
            owner_root = token[len(OWNER_ROOT_OPTION) + 1:]
            index += 1
            continue
        remaining.append(token)
        index += 1
    return owner_root, remaining


def managed_catalog_directory(root: Path) -> Path:
    """Return the managed catalog directory of an owner workspace."""
    return (root / Path(*MANAGED_CATALOG_DIRECTORY)).resolve()


def resolve_owner_root(value: str | None) -> Path | None:
    """Validate the trusted owner workspace.

    ``None`` means "keep the original code-root behaviour" and resolves to
    ``None``. Any other value must be an absolute path to an existing owner
    workspace that holds a managed report catalog; anything else is refused
    by name without echoing the path.
    """
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise DeploymentError("owner_root_invalid", _INVALID_ROOT_MESSAGE)
    candidate = Path(value)
    if not candidate.is_absolute():
        raise DeploymentError("owner_root_invalid", _INVALID_ROOT_MESSAGE)
    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise DeploymentError("owner_root_invalid", _INVALID_ROOT_MESSAGE) from exc
    if not resolved.exists():
        raise DeploymentError("owner_root_absent", _ABSENT_ROOT_MESSAGE)
    if not resolved.is_dir():
        raise DeploymentError("owner_root_invalid", _INVALID_ROOT_MESSAGE)
    if not managed_catalog_directory(resolved).is_dir():
        raise DeploymentError("owner_root_missing", _MISSING_ROOT_MESSAGE)
    return resolved


def build_catalog(root: Path | None) -> ReportCatalog | None:
    """Return the catalog for an already validated owner workspace.

    ``None`` is returned when no owner root was selected, so the caller keeps
    the original owner-core default instead of inventing a path.
    """
    if root is None:
        return None
    return ReportCatalog(root=root)


def assert_read_only_command(command: str, owner_root_text: str | None) -> None:
    """Refuse the trusted root for commands that write to the owner workspace.

    A write command keeps its own existing flow. It must never inherit an
    operator-supplied workspace by accident, so the combination is refused
    by name instead of being silently ignored.
    """
    if owner_root_text is None:
        return
    if command in WRITE_COMMANDS:
        raise DeploymentError("owner_root_write_forbidden",
                              "the owner root option is not available for write commands")

"""Keep the owner-root catalog boundary independent of the job facade.

The catalog deployment suite owns the public command inventory. These checks
exercise how the trusted workspace is handled for those commands and keep
job actions outside the catalog boundary.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from report_catalog_deployment import (  # noqa: E402
    DeploymentError,
    READ_ONLY_COMMANDS,
    WRITE_COMMANDS,
    assert_read_only_command,
    resolve_owner_root,
    split_owner_root,
)


def test_assert_read_only_command_still_refuses_write_commands(tmp_path):
    for command in WRITE_COMMANDS:
        with pytest.raises(DeploymentError) as excinfo:
            assert_read_only_command(command, str(tmp_path))
        assert excinfo.value.code == "owner_root_write_forbidden"


def test_assert_read_only_command_allows_reads_with_the_trusted_root():
    for command in READ_ONLY_COMMANDS:
        assert assert_read_only_command(command, "<trusted-owner-root>") is None
    assert assert_read_only_command("get-report", None) is None


def test_split_owner_root_still_lifts_the_option_before_the_command():
    owner_root, remaining = split_owner_root(
        ["--owner-root", "<trusted-owner-root>", "list-runs", "--entity-id", "E"])
    assert owner_root == "<trusted-owner-root>"
    assert remaining == ["list-runs", "--entity-id", "E"]
    owner_root, remaining = split_owner_root(["list-runs"])
    assert owner_root is None and remaining == ["list-runs"]


def test_resolve_owner_root_still_requires_a_managed_catalog(tmp_path):
    assert resolve_owner_root(None) is None
    with pytest.raises(DeploymentError) as excinfo:
        resolve_owner_root(str(tmp_path))  # exists but has no managed catalog
    assert excinfo.value.code == "owner_root_missing"
    with pytest.raises(DeploymentError) as excinfo:
        resolve_owner_root("relative/path")
    assert excinfo.value.code == "owner_root_invalid"


def test_facade_commands_are_not_catalog_commands():
    """The facade adds no read-only catalog command and never widens the seam."""
    assert "submit" not in READ_ONLY_COMMANDS
    assert "get-status" not in READ_ONLY_COMMANDS
    assert "act" not in READ_ONLY_COMMANDS
    assert "list-jobs" not in READ_ONLY_COMMANDS
    assert not (READ_ONLY_COMMANDS & WRITE_COMMANDS)

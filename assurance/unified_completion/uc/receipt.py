"""Content-addressed receipt schema (CA-102).

Receipts are typed (implementer / reviewer / closure), carry required fields
per kind, and are sealed by a canonical hash: serialize the receipt without
its ``canonical_hash`` field (sorted keys, UTF-8) and SHA-256 it — any byte
tampering makes the stored hash unrecomputable.

Schema policy (N/N-1): unknown FIELDS are tolerated (forward compatibility);
unknown schema VERSIONS are rejected.  Triplet values must be real git
objects in the matching repository; ``policy_sha256`` must be a real 64-hex
hash, never a placeholder string.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
RECEIPT_KINDS = ("implementer", "reviewer", "closure")
REVIEWER_VERDICTS = ("accepted", "changes_required", "blocked", "rejected")

REQUIRED_COMMON = ("schema_version", "unit", "kind", "created_at_utc")
REQUIRED_BY_KIND: dict[str, tuple[str, ...]] = {
    "implementer": (
        "base_triplet",
        "result_triplet",
        "plan_sha256",
        "commands",
        "touched_files",
        "side_effect_counts",
        "implementer",
    ),
    "reviewer": (
        "reviewer",
        "verdict",
        "reviewed_object_sha256",
        "commands",
    ),
    "closure": (
        "closure",
        "state_sha256",
        "manifest_sha256",
        "control_page_sha256",
    ),
}

REPO_KEYS = ("revenue", "filing", "wiki")


def canonical_bytes(receipt: dict[str, Any]) -> bytes:
    """Canonical serialization: canonical_hash excluded, keys sorted."""
    payload = {k: v for k, v in receipt.items() if k != "canonical_hash"}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")


def canonical_hash(receipt: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(receipt)).hexdigest()


def sign(receipt: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the receipt sealed with its canonical hash."""
    sealed = dict(receipt)
    sealed["canonical_hash"] = canonical_hash(sealed)
    return sealed


def _git_object_exists(repo: Path, sha: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-t", sha],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return proc.returncode == 0


def _is_hex(value: str, length: int) -> bool:
    return len(value) == length and all(ch in "0123456789abcdef" for ch in value)


def validate(
    receipt_path: Path,
    repo_roots: dict[str, Path] | None = None,
) -> list[str]:
    """Validate one receipt.  Returns problems (empty = valid)."""
    roots = repo_roots or {}
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"unreadable: {exc}"]
    if not isinstance(receipt, dict):
        return ["receipt root is not an object"]

    problems: list[str] = []
    version = receipt.get("schema_version")
    if version != SCHEMA_VERSION:
        return [
            f"schema_version {version!r} not supported (N/N-1: current={SCHEMA_VERSION})"
        ]

    kind = receipt.get("kind")
    if kind not in RECEIPT_KINDS:
        return [f"kind {kind!r} not in {RECEIPT_KINDS}"]

    for field in REQUIRED_COMMON:
        if receipt.get(field) in (None, ""):
            problems.append(f"missing required field: {field}")
    for field in REQUIRED_BY_KIND[kind]:
        if receipt.get(field) in (None, "", [], {}):
            problems.append(f"missing required field for {kind}: {field}")

    stored = receipt.get("canonical_hash")
    if not stored:
        problems.append("missing canonical_hash (receipt unsigned)")
    elif stored != canonical_hash(receipt):
        problems.append("canonical_hash mismatch (content tampered)")

    for triplet_field in ("base_triplet", "result_triplet"):
        triplet = receipt.get(triplet_field)
        if not isinstance(triplet, dict):
            continue
        for repo_key, sha in triplet.items():
            if not isinstance(sha, str) or not _is_hex(sha, 40):
                problems.append(f"{triplet_field}.{repo_key} is not a 40-hex sha")
                continue
            repo = roots.get(repo_key)
            if repo is not None and not _git_object_exists(repo, sha):
                problems.append(
                    f"{triplet_field}.{repo_key} is not a real git object: {sha}"
                )

    policy = receipt.get("policy_sha256")
    if policy is not None:
        if not (isinstance(policy, str) and _is_hex(policy, 64)):
            problems.append(
                "policy_sha256 must be a real 64-hex hash or omitted with a "
                "policy_note (placeholder strings are not hashes)"
            )

    if kind == "implementer":
        commands = receipt.get("commands", [])
        if commands:
            for index, command in enumerate(commands):
                if not isinstance(command, dict) or "exit_code" not in command:
                    problems.append(f"commands[{index}] lacks exit_code")
    if kind == "reviewer":
        verdict = receipt.get("verdict")
        if verdict not in REVIEWER_VERDICTS:
            problems.append(f"verdict {verdict!r} not in {REVIEWER_VERDICTS}")
        reviewed = receipt.get("reviewed_object_sha256")
        if reviewed is not None and not (
            isinstance(reviewed, str) and _is_hex(reviewed, 64)
        ):
            problems.append(
                "reviewed_object_sha256 is not a 64-hex sha "
                "(it references the reviewed receipt's canonical hash)"
            )
    return problems

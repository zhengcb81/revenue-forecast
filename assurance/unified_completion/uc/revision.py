"""Revision selector and reviewer pairing (CA-103).

A unit's receipt set forms a revision chain: each implementer receipt may
declare ``revision`` and ``supersedes`` (the previous revision id).  The
selector:

- validates the supersedes chain (no cycles, no forks);
- selects the LATEST valid implementer revision;
- requires exactly one reviewer decision referencing that revision's
  canonical hash, by an identity distinct from the implementer;
- never lets an older ``accepted`` decision override a newer
  ``changes_required``/``rejected`` one;
- enforces finding closure: P1/P2 findings and promised P3 findings must
  carry successors (or ``closed`` status).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from uc.receipt import canonical_hash

SEVERITIES = ("P1", "P2", "P3")
DECISION_PRIORITY = {"rejected": 3, "changes_required": 2, "blocked": 1, "accepted": 0}


def _load_receipts(unit_dir: Path) -> dict[str, dict[str, Any]]:
    receipts: dict[str, dict[str, Any]] = {}
    if not unit_dir.is_dir():
        return receipts
    for path in sorted(unit_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            receipts[path.name] = payload
    return receipts


def select(unit_dir: Path) -> tuple[dict[str, Any], list[str]]:
    """Return (selection, problems).  ``selection`` is the machine result:
    latest implementer revision + reviewer decision + findings; problems are
    the reasons the set is not a unique valid pair (empty = valid)."""
    receipts = _load_receipts(unit_dir)
    problems: list[str] = []
    implementer = [
        (name, payload)
        for name, payload in receipts.items()
        if payload.get("kind") == "implementer"
    ]
    reviewer = [
        (name, payload)
        for name, payload in receipts.items()
        if payload.get("kind") == "reviewer"
    ]
    if not implementer:
        problems.append("no implementer receipt")
        return {"implementer_receipts": 0, "reviewer_receipts": len(reviewer)}, problems

    by_revision: dict[str, dict[str, Any]] = {}
    for name, payload in implementer:
        revision = payload.get("revision") or name
        if revision in by_revision:
            problems.append(f"duplicate revision id: {revision}")
        by_revision[revision] = payload

    # Validate supersedes edges: single chain, no cycles, no forks.
    children: dict[str, str] = {}
    for revision, payload in by_revision.items():
        supersedes = payload.get("supersedes")
        if supersedes:
            if supersedes not in by_revision:
                problems.append(f"revision {revision} supersedes unknown {supersedes}")
            elif supersedes in children:
                problems.append(f"fork: {supersedes} superseded by two revisions")
            else:
                children[supersedes] = revision
    latest = [revision for revision in by_revision if revision not in children]
    if len(latest) != 1:
        problems.append(f"expected exactly 1 latest revision, found {latest}")

    selection: dict[str, Any] = {
        "revisions": sorted(by_revision),
        "latest_revision": latest[0] if len(latest) == 1 else None,
    }
    latest_payload = by_revision.get(latest[0]) if len(latest) == 1 else None
    if latest_payload is not None:
        selection["latest_canonical_hash"] = canonical_hash(latest_payload)
        implementer_id = latest_payload.get("implementer")
        selection["implementer"] = implementer_id
        matching_reviews = [
            (name, payload)
            for name, payload in reviewer
            if payload.get("reviewed_object_sha256")
            == selection["latest_canonical_hash"]
        ]
        if not matching_reviews:
            problems.append("no reviewer receipt references the latest revision")
        elif len(matching_reviews) > 1:
            problems.append(
                f"{len(matching_reviews)} reviewer receipts reference the latest revision"
            )
        else:
            _name, review = matching_reviews[0]
            verdict = review.get("verdict")
            if review.get("reviewer") == implementer_id:
                problems.append("reviewer identity equals implementer")
            selection["reviewer"] = review.get("reviewer")
            selection["verdict"] = verdict
            selection["reviewer_receipt"] = _name
            # Older accepted must not override the latest decision.
            older_accepted = [
                payload
                for name, payload in reviewer
                if payload.get("verdict") == "accepted"
                and payload.get("reviewed_object_sha256")
                != selection["latest_canonical_hash"]
            ]
            if older_accepted and verdict != "accepted":
                problems.append(
                    f"{len(older_accepted)} older accepted review(s) exist but "
                    f"latest verdict is {verdict} — stale accepted must not win"
                )
            findings = review.get("findings", [])
            selection["findings"] = findings
            for finding in findings:
                if not isinstance(finding, dict):
                    continue
                severity = finding.get("severity", "").upper()
                if severity in ("P1", "P2"):
                    if (
                        not finding.get("successor")
                        and finding.get("status") != "closed"
                    ):
                        problems.append(
                            f"unclosed {severity} finding without successor: "
                            f"{finding.get('id', '?')}"
                        )
                elif severity == "P3" and finding.get("promised_closure"):
                    if (
                        not finding.get("successor")
                        and finding.get("status") != "closed"
                    ):
                        problems.append(
                            f"P3 finding promised closure but no successor: "
                            f"{finding.get('id', '?')}"
                        )
    return selection, problems

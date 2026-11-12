"""RF-owned public subject DTO and the read-only subject resolver port.

The AnalysisSubject authority is StockWiki. This module never imports a
StockWiki module, opens a neighbouring database or reconstructs a private
layout. A deployment binds :class:`SubjectResolver` to a frozen public
fixture (RF-local verification) or, later, to a public CLI adapter owned by
ROOT. The DTO only carries fields a public authority can actually state; it
does not invent entity, listing or subject identifiers.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol

from contracts.evidence import canonical_sha256

SUBJECT_SCHEMA = "rf-report-subject-snapshot/1"
FIXTURE_SCHEMA = "rf-subject-snapshot-fixture/1"
TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,191}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")
PERIMETER_COVERAGE = frozenset({"not_enumerated", "partial", "complete_as_disclosed"})
SNAPSHOT_FIELDS = frozenset({
    "schema_version", "entity_id", "listing_id", "analysis_subject_id",
    "analysis_subject_revision", "scope_kind", "perimeter_coverage",
    "memberships", "evidence_sha256",
})


class ScopeContractError(RuntimeError):
    """Named, pathless failure of the public scope/subject contract."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def need(condition: Any, code: str, message: str) -> None:
    if not condition:
        raise ScopeContractError(code, message)


def _token(value: Any) -> bool:
    return isinstance(value, str) and TOKEN.fullmatch(value) is not None


def known_text(value: Any, limit: int = 128) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and len(value) <= limit
            and all(ord(char) >= 32 and ord(char) != 127 for char in value)
            and value.strip().lower() != "unknown")


@dataclass(frozen=True)
class SubjectQuery:
    entity_id: str
    listing_id: str
    analysis_subject_id: str
    analysis_subject_revision: int

    def to_public_dict(self) -> dict[str, Any]:
        return {"entity_id": self.entity_id, "listing_id": self.listing_id,
                "analysis_subject_id": self.analysis_subject_id,
                "analysis_subject_revision": self.analysis_subject_revision}

    @property
    def key(self) -> tuple[str, str, str, int]:
        return (self.entity_id, self.listing_id, self.analysis_subject_id,
                self.analysis_subject_revision)


@dataclass(frozen=True)
class SubjectSnapshot:
    entity_id: str
    listing_id: str
    analysis_subject_id: str
    analysis_subject_revision: int
    scope_kind: str
    perimeter_coverage: str
    memberships: tuple[tuple[str, str], ...]
    evidence_sha256: str

    def to_public_dict(self) -> dict[str, Any]:
        return {"schema_version": SUBJECT_SCHEMA,
                "entity_id": self.entity_id, "listing_id": self.listing_id,
                "analysis_subject_id": self.analysis_subject_id,
                "analysis_subject_revision": self.analysis_subject_revision,
                "scope_kind": self.scope_kind,
                "perimeter_coverage": self.perimeter_coverage,
                "memberships": [{"entity_id": entity, "role": role}
                                for entity, role in self.memberships],
                "evidence_sha256": self.evidence_sha256}

    @property
    def snapshot_sha256(self) -> str:
        return canonical_sha256(self.to_public_dict())


class SubjectResolver(Protocol):
    """Public port: one exact immutable subject revision, read-only."""

    def resolve(self, query: SubjectQuery) -> SubjectSnapshot: ...


def validate_subject_snapshot(value: Any) -> SubjectSnapshot:
    """Validate the public wire shape; never sign or invent an authority."""
    need(isinstance(value, dict) and set(value) == SNAPSHOT_FIELDS,
         "subject_snapshot_invalid", "public subject snapshot fields differ")
    need(value.get("schema_version") == SUBJECT_SCHEMA, "subject_snapshot_invalid",
         "public subject snapshot schema differs")
    need(all(_token(value.get(key)) for key in
             ("entity_id", "listing_id", "analysis_subject_id")),
         "subject_snapshot_invalid", "public subject identifiers are not opaque tokens")
    revision = value.get("analysis_subject_revision")
    need(type(revision) is int and 0 < revision <= 2**31 - 1, "subject_snapshot_invalid",
         "public subject revision is not a positive integer")
    need(known_text(value.get("scope_kind")), "subject_snapshot_invalid",
         "public subject scope kind is unknown")
    need(value.get("perimeter_coverage") in PERIMETER_COVERAGE, "subject_snapshot_invalid",
         "public subject perimeter coverage is unknown")
    members = value.get("memberships")
    need(isinstance(members, list) and len(members) >= 1, "subject_snapshot_invalid",
         "public subject memberships are absent")
    pairs: list[tuple[str, str]] = []
    for member in members:
        need(isinstance(member, dict) and set(member) == {"entity_id", "role"}
             and _token(member.get("entity_id")) and known_text(member.get("role"), 64),
             "subject_snapshot_invalid", "public subject membership is malformed")
        pairs.append((member["entity_id"], member["role"]))
    need(len({entity for entity, _ in pairs}) == len(pairs), "subject_snapshot_invalid",
         "public subject memberships are duplicated")
    primary = [entity for entity, role in pairs if role == "primary_issuer"]
    need(primary == [value["entity_id"]], "subject_snapshot_invalid",
         "public subject has no exact primary issuer")
    evidence = value.get("evidence_sha256")
    need(isinstance(evidence, str) and HEX64.fullmatch(evidence) is not None,
         "subject_snapshot_invalid", "public subject evidence hash is invalid")
    return SubjectSnapshot(
        entity_id=value["entity_id"], listing_id=value["listing_id"],
        analysis_subject_id=value["analysis_subject_id"],
        analysis_subject_revision=revision, scope_kind=value["scope_kind"],
        perimeter_coverage=value["perimeter_coverage"],
        memberships=tuple(sorted(pairs)), evidence_sha256=evidence)


class FrozenSubjectResolver:
    """Read a frozen set of public subject snapshots; no network or owner DB."""

    def __init__(self, snapshots: Iterable[SubjectSnapshot]):
        grouped: dict[tuple[str, str, str, int], set[str]] = {}
        resolved: dict[tuple[str, str, str, int], SubjectSnapshot] = {}
        for snapshot in snapshots:
            need(isinstance(snapshot, SubjectSnapshot), "subject_snapshot_invalid",
                 "frozen resolver accepts validated public snapshots only")
            key = (snapshot.entity_id, snapshot.listing_id,
                   snapshot.analysis_subject_id, snapshot.analysis_subject_revision)
            grouped.setdefault(key, set()).add(snapshot.snapshot_sha256)
            resolved.setdefault(key, snapshot)
        for key, hashes in grouped.items():
            need(len(hashes) == 1, "subject_ambiguous",
                 "frozen public fixture has conflicting subject snapshots")
        self._snapshots = {key: resolved[key] for key in grouped}

    @classmethod
    def from_public_fixture(cls, path: str | Path) -> FrozenSubjectResolver:
        try:
            raw = Path(path).read_bytes()
            value = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise ScopeContractError("subject_fixture_invalid",
                                     "public subject fixture is not readable JSON") from exc
        need(isinstance(value, dict) and set(value) == {"schema_version", "snapshots"}
             and value.get("schema_version") == FIXTURE_SCHEMA
             and isinstance(value.get("snapshots"), list) and value["snapshots"],
             "subject_fixture_invalid", "public subject fixture schema differs")
        return cls(validate_subject_snapshot(item) for item in value["snapshots"])

    def resolve(self, query: SubjectQuery) -> SubjectSnapshot:
        need(isinstance(query, SubjectQuery), "subject_query_invalid",
             "subject lookup requires a public query DTO")
        snapshot = self._snapshots.get(query.key)
        need(snapshot is not None, "subject_unavailable",
             "the exact public subject revision is unavailable")
        assert snapshot is not None
        return snapshot

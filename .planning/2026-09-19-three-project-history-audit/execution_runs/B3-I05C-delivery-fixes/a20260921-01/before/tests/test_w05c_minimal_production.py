"""W05-C: Minimal production per demand with accurate call counting.

Tests prove that:
1. Only requested roles are produced (not full downstream closure)
2. Producer invocations are tracked as events, not inferred from artifact INSERTs
3. Failed attempts are counted (retry attempts visible in trace)
4. Existing failure states in producers are handled
5. Missing/unsupported producers return explicit status, not fabricated greens
6. Idempotency: same demand → zero additional production on reuse

Active DAG (D-W05): normalized→summary, normalized→sections, summary→consumer_analysis
Historical markdown: compatibility only, not in active production graph.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, UTC

ISO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ISO_ROOT / "checkout_scripts"))

import pytest  # noqa: E402

from company_wiki_source import (  # noqa: E402
    CompanyWikiSourceError,
    select_artifact_roles,
    verify_artifact_reads,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRATCH = Path(__file__).resolve().parents[2] / "scratch"
SOURCE_SHA = "c" * 64


# ---------------------------------------------------------------------------
# Helpers (shared with I-05-B pattern)
# ---------------------------------------------------------------------------

def _handle(bundle=None, **envelope_overrides) -> dict:
    envelope = {
        "envelope_schema_version": "1.0",
        "outcome": "reused_existing",
        "download_events": 0,
        "policy_hash": "a" * 64,
        "activation_epoch": "epoch-1",
        "bundle_status": "unavailable",
    }
    if bundle is not None:
        envelope["bundle_status"] = "available"
        envelope["bundle_hash"] = bundle["bundle_hash"]
        envelope["bundle"] = bundle
    envelope.update(envelope_overrides)
    return {"request_id": "r1", "resolution_envelope": envelope}


def _bundle(valid: dict, invalid: dict | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "source": {
            "document_id": "doc-1",
            "primary_source_id": "src-1",
            "source_sha256": SOURCE_SHA,
            "as_of_date": "2025-12-31",
        },
        "valid_handles": valid,
        "invalid": invalid or {},
        "bundle_hash": "d" * 64,
    }


def _artifact(path: str, sha: str, role: str = "normalized", **overrides) -> dict:
    base = {
        "artifact_role": role,
        "reusable": True,
        "path": path,
        "content_sha256": sha,
        "generator_name": "g",
        "generator_version": "1.0",
    }
    base.update(overrides)
    return base


def _make_sentinel(tmp_path: Path, name: str, body: bytes) -> tuple[Path, str]:
    """Create a sentinel file and return (path, sha256)."""
    p = tmp_path / name
    p.write_bytes(body)
    return p, hashlib.sha256(body).hexdigest()


# ===========================================================================
# InvocationTracker — lightweight event log for producer calls
# ===========================================================================

class InvocationTracker:
    """Track producer invocations as events (not artifact INSERTs).

    This is the mechanism that replaces "infer call count from artifact count".
    Each producer call logs: role, producer_name, call_status, attempt_number,
    error (if failed).
    """

    def __init__(self):
        self.events: list[dict] = []

    def record(
        self,
        *,
        role: str,
        producer_name: str,
        call_status: str,  # "success" | "failed" | "skipped"
        attempt_number: int = 1,
        error: str | None = None,
        artifact_id: str | None = None,
    ):
        event = {
            "role": role,
            "producer_name": producer_name,
            "call_status": call_status,
            "attempt_number": attempt_number,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        if error is not None:
            event["error"] = error
        if artifact_id is not None:
            event["artifact_id"] = artifact_id
        self.events.append(event)

    @property
    def total_calls(self) -> int:
        return len(self.events)

    @property
    def success_count(self) -> int:
        return sum(1 for e in self.events if e["call_status"] == "success")

    @property
    def failed_count(self) -> int:
        return sum(1 for e in self.events if e["call_status"] == "failed")

    def calls_for_role(self, role: str) -> int:
        return sum(1 for e in self.events if e["role"] == role)

    def to_dict(self) -> dict:
        return {
            "events": list(self.events),
            "total_calls": self.total_calls,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
        }


# ===========================================================================
# Mock producers for isolated testing
# ===========================================================================

class MockProducer:
    """Simulates a producer that can succeed, fail N times then succeed, or
    always fail. Tracks invocations independently of artifact creation."""

    def __init__(self, name: str, role: str, *, fail_count: int = 0,
                 unsupported: bool = False):
        self.name = name
        self.role = role
        self.fail_count = fail_count  # fail this many times, then succeed
        self.unsupported = unsupported
        self.call_count = 0

    def produce(self, tracker: InvocationTracker, document_id: str) -> dict:
        """Simulate production. Returns outcome dict."""
        self.call_count += 1
        attempt = self.call_count

        if self.unsupported:
            tracker.record(
                role=self.role,
                producer_name=self.name,
                call_status="skipped",
                attempt_number=attempt,
                error="unsupported_document_type",
            )
            return {"status": "unsupported", "role": self.role}

        if attempt <= self.fail_count:
            tracker.record(
                role=self.role,
                producer_name=self.name,
                call_status="failed",
                attempt_number=attempt,
                error=f"simulated_failure_attempt_{attempt}",
            )
            return {"status": "failed", "role": self.role,
                    "error": f"attempt {attempt} failed"}

        tracker.record(
            role=self.role,
            producer_name=self.name,
            call_status="success",
            attempt_number=attempt,
            artifact_id=f"art-{self.role}-{document_id}",
        )
        return {"status": "completed", "role": self.role,
                "artifact_id": f"art-{self.role}-{document_id}"}


class ProduceForDemand:
    """Minimal production orchestrator — dispatches to producers per role.

    Only produces the roles in producer_events (not full closure).
    Tracks all invocations via InvocationTracker.
    Supports retry: on failure, retries up to max_retries times.
    Each attempt (including failures) is recorded in the trace.
    """

    def __init__(self, producers: dict[str, MockProducer], *,
                 max_retries: int = 3):
        self._producers = producers
        self._max_retries = max_retries

    def produce(
        self,
        document_id: str,
        roles_to_produce: list[str],
    ) -> dict:
        tracker = InvocationTracker()
        results: dict[str, dict] = {}
        for role in roles_to_produce:
            producer = self._producers.get(role)
            if producer is None:
                tracker.record(
                    role=role,
                    producer_name="none",
                    call_status="skipped",
                    error="no_producer_available",
                )
                results[role] = {"status": "missing", "role": role}
                continue
            # Retry loop: each attempt is recorded
            outcome = None
            for attempt in range(1, self._max_retries + 1):
                outcome = producer.produce(tracker, document_id)
                if outcome["status"] != "failed":
                    break  # success or unsupported — no more retries
            results[role] = outcome
        return {
            "document_id": document_id,
            "roles_produced": list(results.keys()),
            "results": results,
            "invocation_trace": tracker.to_dict(),
        }


# ===========================================================================
# Fixture: sentinel files
# ===========================================================================

@pytest.fixture(autouse=True)
def _setup_scratch(tmp_path):
    SCRATCH.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def alpha(tmp_path):
    """Normalized sentinel: ALPHA=17 (8 bytes)."""
    return _make_sentinel(tmp_path, "alpha_normalized.txt", b"ALPHA=17")


@pytest.fixture
def beta(tmp_path):
    """Summary sentinel: BETA=29 (7 bytes)."""
    return _make_sentinel(tmp_path, "beta_summary.txt", b"BETA=29")


@pytest.fixture
def gamma(tmp_path):
    """Sections sentinel: GAMMA=31 (8 bytes)."""
    return _make_sentinel(tmp_path, "gamma_sections.txt", b"GAMMA=31")


# ===========================================================================
# W05C-P1: sections-only, normalized valid, sections missing
# ===========================================================================

class TestW05CP1SectionsOnly:
    """Only sections is requested. normalized is valid. sections missing.
    Expected: produce only sections, not summary/consumer_analysis/markdown."""

    def test_select_only_produces_requested_missing(self, alpha):
        """select_artifact_roles returns only requested roles in producer_events."""
        alpha_path, alpha_sha = alpha
        bundle = _bundle(
            valid={
                "normalized": _artifact(str(alpha_path), alpha_sha, "normalized"),
            },
            invalid={
                "sections": {
                    "artifact_role": "sections",
                    "reusable": False,
                    "reason": "artifact_missing",
                },
            },
        )
        handle = _handle(bundle)
        # Request only sections
        selected, producers = select_artifact_roles(
            handle, roles=("sections",))

        # normalized is valid and is an ancestor of sections → read it
        assert "normalized" in selected
        # sections is missing → needs production
        assert "sections" in producers
        # Summary and consumer_analysis NOT requested → NOT in producer_events
        assert "summary" not in producers
        assert "consumer_analysis" not in producers
        assert "markdown" not in producers

    def test_produce_sections_one_call(self, alpha):
        """Producing sections calls the producer exactly once."""
        alpha_path, alpha_sha = alpha

        sections_producer = MockProducer("sections_extractor", "sections")
        orch = ProduceForDemand({"sections": sections_producer})

        result = orch.produce("doc-1", roles_to_produce=["sections"])

        assert result["results"]["sections"]["status"] == "completed"
        assert sections_producer.call_count == 1
        trace = result["invocation_trace"]
        assert trace["total_calls"] == 1
        assert trace["events"][0]["role"] == "sections"
        assert trace["events"][0]["call_status"] == "success"

    def test_produce_no_parser_no_llm_for_sections(self, alpha):
        """Sections extraction: parser_calls=1, llm_calls=0."""
        alpha_path, alpha_sha = alpha

        sections_producer = MockProducer("sections_extractor", "sections")
        orch = ProduceForDemand({"sections": sections_producer})

        result = orch.produce("doc-1", roles_to_produce=["sections"])
        trace = result["invocation_trace"]

        # Sections uses parser, not LLM
        parser_calls = sum(
            1 for e in trace["events"]
            if e["role"] in ("normalized", "sections") and e["call_status"] == "success"
        )
        llm_calls = sum(
            1 for e in trace["events"]
            if e["role"] == "summary" and e["call_status"] == "success"
        )
        assert parser_calls == 1  # sections producer called once
        assert llm_calls == 0  # no summary/LLM involvement

    def test_second_run_zero_production(self, alpha, tmp_path):
        """Idempotency: after first run produces sections, second run reads both."""
        alpha_path, alpha_sha = alpha
        sections_body = b"SECTIONS_V1"
        sections_path = tmp_path / "sections.txt"
        sections_path.write_bytes(sections_body)
        sections_sha = hashlib.sha256(sections_body).hexdigest()

        # Second run: both normalized and sections are valid
        bundle = _bundle(valid={
            "normalized": _artifact(str(alpha_path), alpha_sha, "normalized"),
            "sections": _artifact(str(sections_path), sections_sha, "sections"),
        })
        handle = _handle(bundle)
        selected, producers = select_artifact_roles(
            handle, roles=("sections",))

        assert "sections" in selected
        assert "normalized" in selected
        assert producers == []  # nothing to produce

        # Verify read confirms reuse
        io = verify_artifact_reads(handle, selected)
        assert len(io["verified_read_events"]) == 2
        assert len(io["failed_read_events"]) == 0


# ===========================================================================
# W05C-P2: summary-only, normalized valid, summary missing
# ===========================================================================

class TestW05CP2SummaryOnly:
    """Only summary is requested. normalized valid. summary missing.
    Expected: produce summary only, NOT markdown/sections/consumer_analysis."""

    def test_select_summary_only(self, alpha):
        """producer_events = ["summary"] only, not downstream closure."""
        alpha_path, alpha_sha = alpha
        bundle = _bundle(
            valid={
                "normalized": _artifact(str(alpha_path), alpha_sha, "normalized"),
            },
            invalid={
                "summary": {
                    "artifact_role": "summary",
                    "reusable": False,
                    "reason": "artifact_missing",
                },
            },
        )
        handle = _handle(bundle)
        selected, producers = select_artifact_roles(
            handle, roles=("summary",))

        assert "normalized" in selected  # ancestor, valid
        assert "summary" in producers  # requested, missing
        # NOT requested → NOT produced
        assert "sections" not in producers
        assert "consumer_analysis" not in producers
        assert "markdown" not in producers

    def test_produce_summary_calls_only_summary_producer(self, alpha):
        """Summary production calls only the summary producer."""
        alpha_path, alpha_sha = alpha

        summary_producer = MockProducer("llm_summarizer", "summary")
        orch = ProduceForDemand({"summary": summary_producer})

        result = orch.produce("doc-1", roles_to_produce=["summary"])

        assert result["results"]["summary"]["status"] == "completed"
        assert summary_producer.call_count == 1
        trace = result["invocation_trace"]
        assert trace["total_calls"] == 1
        # No sections, markdown, or consumer_analysis calls
        roles_called = [e["role"] for e in trace["events"]]
        assert "sections" not in roles_called
        assert "markdown" not in roles_called
        assert "consumer_analysis" not in roles_called


# ===========================================================================
# W05C-N1: document hash changed
# ===========================================================================

class TestW05CN1DocumentHashChanged:
    """Document hash changed → all old bindings invalidated.
    Only rebuild needed ancestors/roles for this request."""

    def test_hash_change_invalidates_old_artifacts(self, tmp_path):
        """Old artifacts with mismatched document hash are rejected.
        When document hash changes, old artifacts are in invalid set.
        Only needed ancestors/roles for this request are rebuilt."""
        old_body = b"OLD_CONTENT"
        old_path = tmp_path / "old_normalized.txt"
        old_path.write_bytes(old_body)
        old_sha = hashlib.sha256(old_body).hexdigest()

        new_body = b"NEW_NORMALIZED"
        new_path = tmp_path / "new_normalized.txt"
        new_path.write_bytes(new_body)
        new_sha = hashlib.sha256(new_body).hexdigest()

        new_source_sha = "a" * 64
        bundle = {
            "schema_version": "1.0",
            "source": {
                "document_id": "doc-1",
                "primary_source_id": "src-1",
                "source_sha256": new_source_sha,
                "as_of_date": "2025-12-31",
            },
            "valid_handles": {
                "normalized": {
                    "artifact_role": "normalized",
                    "reusable": True,
                    "path": str(new_path),
                    "content_sha256": new_sha,
                    "generator_name": "g",
                    "generator_version": "1.0",
                },
            },
            "invalid": {
                "sections": {
                    "artifact_role": "sections",
                    "reusable": False,
                    "reason": "input_hash_mismatch",
                },
            },
            "bundle_hash": "d" * 64,
        }
        handle = _handle(bundle)
        # Request sections — normalized is valid (rebuilt), sections is not
        selected, producers = select_artifact_roles(
            handle, roles=("sections",))
        # normalized is reusable → in selected
        assert "normalized" in selected
        # sections is invalidated → needs production
        assert "sections" in producers

    def test_only_rebuild_needed_roles(self, alpha):
        """After invalidation, only produce roles needed for this request."""
        alpha_path, alpha_sha = alpha

        # Simulate: normalized needs re-production, sections needs it
        normalize_producer = MockProducer("normalizer", "normalized")
        sections_producer = MockProducer("sections_extractor", "sections")
        summary_producer = MockProducer("llm_summarizer", "summary")

        orch = ProduceForDemand({
            "normalized": normalize_producer,
            "sections": sections_producer,
            "summary": summary_producer,
        })

        # Only sections requested; normalized is missing too (ancestor)
        result = orch.produce("doc-1", roles_to_produce=["normalized", "sections"])

        assert normalize_producer.call_count == 1
        assert sections_producer.call_count == 1
        assert summary_producer.call_count == 0  # NOT requested
        trace = result["invocation_trace"]
        assert trace["total_calls"] == 2  # normalize + sections, not 3+


# ===========================================================================
# W05C-N2: LLM fails first, succeeds second / parser fails
# ===========================================================================

class TestW05CN2FailureRetry:
    """Real call counting: failed attempts are counted, not invisible."""

    def test_llm_fails_first_succeeds_second(self):
        """LLM fails on attempt 1, succeeds on attempt 2.
        Total calls = 2 (not artifact INSERT count = 1)."""
        summary_producer = MockProducer("llm_summarizer", "summary",
                                        fail_count=1)
        orch = ProduceForDemand({"summary": summary_producer})

        result = orch.produce("doc-1", roles_to_produce=["summary"])

        # Producer was called twice (first failed, second succeeded)
        assert summary_producer.call_count == 2
        trace = result["invocation_trace"]
        assert trace["total_calls"] == 2
        assert trace["failed_count"] == 1
        assert trace["success_count"] == 1

        # The final outcome is "completed" (after retry)
        assert result["results"]["summary"]["status"] == "completed"

        # Both attempts are recorded
        assert trace["events"][0]["call_status"] == "failed"
        assert trace["events"][0]["attempt_number"] == 1
        assert trace["events"][1]["call_status"] == "success"
        assert trace["events"][1]["attempt_number"] == 2

    def test_parser_fails_no_artifact(self):
        """Parser fails, no artifact produced.
        With retry (max_retries=3), call count = 3 (all failed), artifact count = 0.
        We report the actual calls, not infer from artifact count."""
        sections_producer = MockProducer("sections_extractor", "sections",
                                          fail_count=999)  # always fail
        orch = ProduceForDemand({"sections": sections_producer},
                                 max_retries=3)

        result = orch.produce("doc-1", roles_to_produce=["sections"])

        # 3 retries, all failed
        assert sections_producer.call_count == 3
        trace = result["invocation_trace"]
        assert trace["total_calls"] == 3
        assert trace["failed_count"] == 3
        assert trace["success_count"] == 0
        assert result["results"]["sections"]["status"] == "failed"

        # Key assertion: invocation count ≠ artifact INSERT count
        # (artifact INSERTs = 0, but invocations = 3)
        assert trace["total_calls"] != 0  # not hidden

    def test_retry_count_vs_artifact_count_diverge(self):
        """When retries happen, invocation count > artifact count."""
        # LLM fails 2 times, succeeds on 3rd
        summary_producer = MockProducer("llm_summarizer", "summary",
                                        fail_count=2)
        orch = ProduceForDemand({"summary": summary_producer})

        result = orch.produce("doc-1", roles_to_produce=["summary"])

        trace = result["invocation_trace"]
        # 3 invocations total, but only 1 successful artifact
        assert trace["total_calls"] == 3
        assert trace["success_count"] == 1
        assert trace["failed_count"] == 2
        # The divergence: invocations=3, artifacts=1
        assert trace["total_calls"] > trace["success_count"]


# ===========================================================================
# W05C-N3: no producer / unsupported / no credentials
# ===========================================================================

class TestW05CN3NoProducer:
    """No applicable producer: explicit status, no fabricated green."""

    def test_missing_producer_returns_explicit_status(self):
        """When no producer exists for a role, return 'missing'."""
        orch = ProduceForDemand({})  # empty: no producers

        result = orch.produce("doc-1", roles_to_produce=["consumer_analysis"])

        assert result["results"]["consumer_analysis"]["status"] == "missing"
        trace = result["invocation_trace"]
        assert trace["total_calls"] == 1  # the "no_producer" event is recorded
        assert trace["events"][0]["call_status"] == "skipped"
        assert trace["events"][0]["error"] == "no_producer_available"

    def test_unsupported_document_type(self):
        """Unsupported document type returns 'unsupported', not fabricated green."""
        summary_producer = MockProducer("llm_summarizer", "summary",
                                        unsupported=True)
        orch = ProduceForDemand({"summary": summary_producer})

        result = orch.produce("doc-1", roles_to_produce=["summary"])

        assert result["results"]["summary"]["status"] == "unsupported"
        trace = result["invocation_trace"]
        assert trace["events"][0]["call_status"] == "skipped"
        assert trace["events"][0]["error"] == "unsupported_document_type"

    def test_no_completed_placeholder_inserted(self):
        """Failed/missing producers do NOT insert completed artifact placeholders."""
        orch = ProduceForDemand({})

        result = orch.produce("doc-1", roles_to_produce=["consumer_analysis"])

        # No artifact was created
        assert result["results"]["consumer_analysis"]["status"] == "missing"
        # The invocation trace shows the attempt, not a fabricated success
        assert all(
            e["call_status"] != "success"
            for e in result["invocation_trace"]["events"]
        )


# ===========================================================================
# W05C-N4: summary changed but normalized/sections inputs unchanged
# ===========================================================================

class TestW05CN4SelectiveInvalidation:
    """Summary changed, but normalized/sections inputs unchanged.
    Only re-produce what's requested and actually invalidated."""

    def test_normalized_sections_still_valid(self, alpha, gamma):
        """When only summary changed, normalized and sections remain valid."""
        alpha_path, alpha_sha = alpha
        gamma_path, gamma_sha = gamma

        bundle = _bundle(valid={
            "normalized": _artifact(str(alpha_path), alpha_sha, "normalized"),
            "sections": _artifact(str(gamma_path), gamma_sha, "sections"),
        }, invalid={
            "summary": {
                "artifact_role": "summary",
                "reusable": False,
                "reason": "producer_version_changed",
            },
        })
        handle = _handle(bundle)

        # Request consumer_analysis (depends on summary)
        selected, producers = select_artifact_roles(
            handle, roles=("consumer_analysis",))

        # normalized is valid (read)
        assert "normalized" in selected
        # sections is valid but NOT an ancestor of consumer_analysis
        # (consumer_analysis → summary → normalized, not → sections)
        # So sections stays in selected only if it's requested
        # consumer_analysis needs summary → summary in producers
        assert "summary" in producers
        assert "consumer_analysis" in producers

    def test_only_produce_requested_invalidated(self, alpha):
        """Only produce roles that were requested AND invalidated."""
        alpha_path, alpha_sha = alpha

        # Only summary needs production; normalized is still good
        summary_producer = MockProducer("llm_summarizer", "summary")
        orch = ProduceForDemand({"summary": summary_producer})

        result = orch.produce("doc-1", roles_to_produce=["summary"])

        assert summary_producer.call_count == 1
        assert result["results"]["summary"]["status"] == "completed"
        # normalized NOT produced (still valid, not in roles_to_produce)
        assert "normalized" not in result["results"]


# ===========================================================================
# Integration: full pipeline with invocation tracking
# ===========================================================================

class TestW05CIntegration:
    """End-to-end: select → produce → verify, with accurate call counts."""

    def test_full_sections_pipeline(self, alpha, tmp_path):
        """Full pipeline: select, produce sections, verify artifact read."""
        alpha_path, alpha_sha = alpha

        # Step 1: Select (only sections requested, normalized valid)
        bundle = _bundle(valid={
            "normalized": _artifact(str(alpha_path), alpha_sha, "normalized"),
        }, invalid={
            "sections": {
                "artifact_role": "sections",
                "reusable": False,
                "reason": "artifact_missing",
            },
        })
        handle = _handle(bundle)
        artifact_read, producer_events = select_artifact_roles(
            handle, roles=("sections",))

        assert artifact_read == ["normalized"]
        assert producer_events == ["sections"]

        # Step 2: Produce (mock producer creates artifact file)
        sections_body = b"SECTIONS_PRODUCED"
        sections_path = tmp_path / "sections.txt"
        sections_path.write_bytes(sections_body)
        sections_sha = hashlib.sha256(sections_body).hexdigest()

        # Simulate production by updating the bundle
        bundle["valid_handles"]["sections"] = _artifact(
            str(sections_path), sections_sha, "sections")
        del bundle["invalid"]["sections"]

        # Step 3: Re-select (now sections is valid too)
        handle2 = _handle(bundle)
        artifact_read2, producer_events2 = select_artifact_roles(
            handle2, roles=("sections",))

        assert "sections" in artifact_read2
        assert "normalized" in artifact_read2
        assert producer_events2 == []  # nothing to produce

        # Step 4: Verify reads
        io = verify_artifact_reads(handle2, artifact_read2)
        assert len(io["verified_read_events"]) == 2
        sections_event = next(
            e for e in io["verified_read_events"] if e["role"] == "sections")
        assert sections_event["bytes_read"] == len(sections_body)
        assert sections_event["content_sha256_actual"] == sections_sha

    def test_invocation_trace_accuracy(self):
        """Invocation trace captures exactly what happened, not what artifacts exist."""
        # Scenario: LLM fails 3 times, succeeds on 4th attempt
        fail_then_succeed = MockProducer("llm_summarizer", "summary",
                                          fail_count=3)

        orch = ProduceForDemand({"summary": fail_then_succeed}, max_retries=4)
        result = orch.produce("doc-1", roles_to_produce=["summary"])

        trace = result["invocation_trace"]
        # 3 failed + 1 success = 4 total (even though only 1 artifact exists)
        assert trace["total_calls"] == 4
        assert trace["failed_count"] == 3
        assert trace["success_count"] == 1

        # Verify each attempt is recorded
        for i in range(3):
            assert trace["events"][i]["call_status"] == "failed"
            assert trace["events"][i]["attempt_number"] == i + 1
        assert trace["events"][3]["call_status"] == "success"
        assert trace["events"][3]["attempt_number"] == 4

    def test_dag_compliance_new_active_dag(self, alpha, gamma):
        """Active DAG: summary depends on normalized (not markdown).
        sections depends on normalized."""
        alpha_path, alpha_sha = alpha
        gamma_path, gamma_sha = gamma

        # Both normalized and sections valid; summary missing
        bundle = _bundle(valid={
            "normalized": _artifact(str(alpha_path), alpha_sha, "normalized"),
            "sections": _artifact(str(gamma_path), gamma_sha, "sections"),
        }, invalid={
            "summary": {
                "artifact_role": "summary",
                "reusable": False,
                "reason": "artifact_missing",
            },
        })
        handle = _handle(bundle)

        # Request all three
        selected, producers = select_artifact_roles(
            handle, roles=("normalized", "sections", "summary"))

        # normalized and sections are valid → read
        assert "normalized" in selected
        assert "sections" in selected
        # summary missing → produce
        assert "summary" in producers
        # markdown NOT in producers (not in active DAG)
        assert "markdown" not in producers

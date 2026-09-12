"""B.VR(B03) independent probe: can the byte entry point hand out bytes that are
NOT the version they were verified against?

Reviewer-owned, read-only w.r.t. product code.  Every scenario builds its own
tmp catalog, resolves a handle, then attacks the read path.  Writes a JSON
result file (utf-8, ensure_ascii=False) -- never prints non-ASCII to the GBK
console.

Usage: python b03_review_bytes.py <out.json>
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(WIKI / "src"))

from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog import resolver as R  # noqa: E402
from company_wiki.source_catalog.resolver import (  # noqa: E402
    SourceRequest,
    SourceResolver,
    _ReadBudget,
)

BODY = b"%PDF-1.4 b03-reviewer-payload-AAAA"
DIGEST = hashlib.sha256(BODY).hexdigest()
OTHER = b"%PDF-1.4 b03-reviewer-payload-BBBB"
assert len(OTHER) == len(BODY), (len(OTHER), len(BODY))
OTHER_DIGEST = hashlib.sha256(OTHER).hexdigest()

FIVE = frozenset({"not_found", "not_indexed", "unavailable", "blocked", "ambiguous"})
RESULTS: list[dict] = []


def record(name: str, **kw) -> None:
    RESULTS.append({"scenario": name, **kw})


def _sidecar(sha: str = DIGEST) -> dict:
    return {
        "schema_version": "1.0",
        "canonical_entity_id": "ent-acme",
        "display_name": "Acme",
        "market": "US",
        "security_id": "ACME",
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "period_end": "2025-12-31",
        "filing_date": "2026-02-20",
        "form_type": "10-K",
        "provider": "sec",
        "provider_document_id": "doc-1",
        "source_url": "https://sec.gov/x/2025",
        "content_sha256": sha,
    }


def fixture(tmp: Path, body: bytes = BODY, name: str = "2025.pdf"):
    """(resolver, handle, path) for a one-copy catalog under ``tmp``."""
    root = tmp / "companies"
    path = root / "Acme" / "raw" / "financial_reports" / "annual" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    (path.parent / f"{name}.source.json").write_text(
        json.dumps(_sidecar(hashlib.sha256(body).hexdigest()), ensure_ascii=False),
        encoding="utf-8",
    )
    catalog = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".source_catalog",
            reusable_root_kinds=("company_raw", "directory"),
            roots=(
                RootSpec(
                    "company_raw",
                    root,
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    read_only=False,
                    canonical_write_target="companies",
                ),
            ),
        )
    )
    catalog.scan()
    request = SourceRequest(
        entity="Acme",
        market="US",
        security_id="ACME",
        document_kind="annual_report",
        form_type="10-K",
        fiscal_year=2025,
        provider="sec",
        provider_document_id="doc-1",
        as_of_date="2026-08-10",
        mode="exact",
    )
    resolver = SourceResolver(catalog)
    result = resolver.resolve(request)
    if len(result.matches) != 1:
        raise SystemExit(f"fixture failed: {result.status} {result.debug_trace}")
    return resolver, result.matches[0], path


def digest_of(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def snapshot(out) -> dict:
    return {
        "ok": out.ok,
        "status": out.status,
        "reason": out.reason,
        "detail": out.detail,
        "data_is_none": out.data is None,
        "byte_size": out.byte_size,
        "bytes_source": out.bytes_source,
        "content_sha256_field": out.content_sha256,
        "data_sha256": digest_of(out.data),
        "data_len": len(out.data) if out.data is not None else 0,
    }


class ReadTap:
    """Counts Path.open / Path.stat calls made while it is installed."""

    def __init__(self):
        self.opens: list[str] = []
        self.stats: list[str] = []
        self._open = Path.open
        self._stat = Path.stat

    def __enter__(self):
        tap = self

        def _open(self, *a, **kw):
            mode = a[0] if a else kw.get("mode", "r")
            tap.opens.append(f"{self}|{mode}")
            return tap._open(self, *a, **kw)

        def _stat(self, *a, **kw):
            tap.stats.append(str(self))
            return tap._stat(self, *a, **kw)

        Path.open = _open
        Path.stat = _stat
        return self

    def __exit__(self, *exc):
        Path.open = self._open
        Path.stat = self._stat
        return False


class AfterNthRead:
    """Wrap the real file object; run ``action`` once while reading.

    ``index`` selects which read() call triggers it (0-based); ``None`` means
    "the read that returns b'' (end of file)".
    """

    def __init__(self, stream, action, index):
        self._stream = stream
        self._action = action
        self._index = index
        self._n = 0
        self._done = False

    def read(self, size=-1):
        chunk = self._stream.read(size)
        trigger = (self._index is None and not chunk) or (
            self._index is not None and self._n == self._index
        )
        self._n += 1
        if trigger and not self._done:
            self._done = True
            self._action()
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._stream.__exit__(*exc)


def patched_open(target: Path, action, index):
    real_open = Path.open

    def fake_open(self, *a, **kw):
        mode = a[0] if a else kw.get("mode", "r")
        stream = real_open(self, *a, **kw)
        if Path(str(self)) == target and mode == "rb":
            return AfterNthRead(stream, action, index)
        return stream

    return fake_open


def restore_mtime(path: Path, stat_result) -> None:
    os.utime(path, ns=(stat_result.st_atime_ns, stat_result.st_mtime_ns))


# ---------------------------------------------------------------------------
# 1. Baseline + the author's own cases, re-measured
# ---------------------------------------------------------------------------


def s_happy(tmp):
    resolver, handle, path = fixture(tmp)
    with ReadTap() as tap:
        out = resolver.read_verified_bytes(handle)
    record(
        "happy_path",
        **snapshot(out),
        matches_handle_digest=out.content_sha256 == handle.content_sha256,
        open_calls=tap.opens,
        stat_calls=tap.stats,
        n_opens=len(tap.opens),
        n_stats=len(tap.stats),
    )


def s_same_size_overwrite(tmp):
    resolver, handle, path = fixture(tmp)
    path.write_bytes(OTHER)
    out = resolver.read_verified_bytes(handle)
    record("same_size_overwrite_before_call", **snapshot(out))


# ---------------------------------------------------------------------------
# 2. Attack on the mid-read guard: same size AND restored mtime
# ---------------------------------------------------------------------------


def s_utime_restored_before_call(tmp):
    """Guard defeated (size and mtime identical) -- does the digest still hold?"""
    resolver, handle, path = fixture(tmp)
    before = path.stat()
    path.write_bytes(OTHER)  # same length
    restore_mtime(path, before)
    after = path.stat()
    out = resolver.read_verified_bytes(handle)
    record(
        "same_size_overwrite_with_mtime_restored",
        guard_defeated=(int(after.st_size) == int(before.st_size)
                        and int(after.st_mtime_ns) == int(before.st_mtime_ns)),
        mtime_ns_before=before.st_mtime_ns,
        mtime_ns_after=after.st_mtime_ns,
        **snapshot(out),
    )


def s_utime_restored_post_read(tmp):
    """Whole file mutated AFTER the last read(), mtime restored.

    The buffer already holds the requested version: the guard cannot see the
    change at all.  Returned bytes must still be the requested version.
    """
    resolver, handle, path = fixture(tmp)
    before = path.stat()

    def action():
        path.write_bytes(OTHER)
        restore_mtime(path, before)

    real = Path.open
    Path.open = patched_open(path, action, None)
    try:
        out = resolver.read_verified_bytes(handle)
    finally:
        Path.open = real
    record(
        "post_read_change_with_mtime_restored",
        **snapshot(out),
        returned_bytes_are_requested_version=(digest_of(out.data) == DIGEST),
        file_now=path.read_bytes()[:16].decode("latin-1"),
    )


def s_mid_read_rewrite_same_size_mtime_restored(tmp):
    """2 MiB file, rewritten (same size) after the first 1 MiB chunk, mtime
    restored: the buffer is a MIX of two revisions and the guard is defeated."""
    big = (b"A" * (1024 * 1024)) + (b"B" * (1024 * 1024))
    big2 = (b"C" * (1024 * 1024)) + (b"D" * (1024 * 1024))
    assert len(big) == len(big2)
    resolver, handle, path = fixture(tmp, body=big, name="big.pdf")
    before = path.stat()

    def action():
        path.write_bytes(big2)
        restore_mtime(path, before)

    real = Path.open
    Path.open = patched_open(path, action, 0)
    try:
        out = resolver.read_verified_bytes(handle)
    finally:
        Path.open = real
    mixed = big[: 1024 * 1024] + big2[1024 * 1024:]
    record(
        "mid_read_rewrite_same_size_mtime_restored",
        mixed_buffer_digest=hashlib.sha256(mixed).hexdigest(),
        requested_digest=hashlib.sha256(big).hexdigest(),
        mixed_equals_requested=(hashlib.sha256(mixed).hexdigest()
                                == hashlib.sha256(big).hexdigest()),
        **snapshot(out),
    )


def s_mid_read_rewrite_then_restore_original(tmp):
    """Mid-read append + truncate back to the original size and mtime.

    Both guard columns are back to their pre-read values, so the guard passes;
    the buffer is the untouched original, so the bytes ARE the requested
    version.  Answers: "does a defeated guard ever yield wrong bytes?"
    """
    resolver, handle, path = fixture(tmp)
    before = path.stat()

    def action():
        path.write_bytes(BODY + b"x" * 64)
        path.write_bytes(BODY)
        restore_mtime(path, before)

    real = Path.open
    Path.open = patched_open(path, action, 0)
    try:
        out = resolver.read_verified_bytes(handle)
    finally:
        Path.open = real
    record(
        "mid_read_append_then_restore_original",
        **snapshot(out),
        returned_bytes_are_requested_version=(digest_of(out.data) == DIGEST),
    )


def s_truncate_and_rewrite_same_length(tmp):
    resolver, handle, path = fixture(tmp)
    with path.open("r+b") as fh:
        fh.truncate(0)
        fh.write(OTHER)
    out = resolver.read_verified_bytes(handle)
    record(
        "truncate_and_rewrite_same_length",
        size_now=path.stat().st_size,
        **snapshot(out),
    )


def s_write_between_last_read_and_post_stat(tmp):
    """A writer appends after the payload was fully read.

    The buffer is exactly the requested version, but the post-read stat sees a
    different size -> the entry point must refuse (fail-closed direction).
    """
    resolver, handle, path = fixture(tmp)

    def action():
        path.write_bytes(BODY + b"late-append")

    real = Path.open
    Path.open = patched_open(path, action, None)
    try:
        out = resolver.read_verified_bytes(handle)
    finally:
        Path.open = real
    record(
        "write_between_last_read_and_post_stat",
        **snapshot(out),
        buffer_would_have_been_correct=True,
    )


# ---------------------------------------------------------------------------
# 3. Can the caller ask for a version the handle does not name?
# ---------------------------------------------------------------------------


def s_caller_supplied_foreign_digest(tmp):
    """``expected_content_sha256`` of ANOTHER document's version, while the file
    on disk holds that other version: what identity does the result carry?"""
    resolver, handle, path = fixture(tmp, body=OTHER, name="2025.pdf")
    # the catalog claims OTHER's digest -> handle.content_sha256 == OTHER_DIGEST
    out_claim = resolver.read_verified_bytes(handle)
    # now ask for a digest that is NOT the handle's version, with the file
    # holding exactly those bytes
    body_c = b"%PDF-1.4 third-version-bytes!!!!"
    path.write_bytes(body_c)
    digest_c = hashlib.sha256(body_c).hexdigest()
    out = resolver.read_verified_bytes(handle, expected_content_sha256=digest_c)
    record(
        "caller_supplied_foreign_digest",
        handle_content_sha256=handle.content_sha256,
        handle_document_id=handle.document_id,
        requested_override=digest_c,
        override_equals_handle_digest=(digest_c == handle.content_sha256),
        claim_only_read=snapshot(out_claim),
        bytes_of_another_version_returned=(digest_of(out.data) == digest_c),
        result_document_id=out.document_id,
        result_content_sha256=out.content_sha256,
        **snapshot(out),
    )


def s_caller_supplied_empty_digest(tmp):
    resolver, handle, path = fixture(tmp)
    out = resolver.read_verified_bytes(handle, expected_content_sha256="")
    record("caller_supplied_empty_digest", **snapshot(out))


def s_non_handle_argument(tmp):
    resolver, handle, path = fixture(tmp)
    try:
        out = resolver.read_verified_bytes(None)  # type: ignore[arg-type]
        record("non_handle_argument", raised=False, **snapshot(out))
    except Exception as exc:  # noqa: BLE001
        record(
            "non_handle_argument",
            raised=True,
            exc_type=type(exc).__name__,
            exc_text=str(exc)[:120],
        )


def s_empty_handle_digest(tmp):
    """A hand-built handle with no version digest: no bytes may be served."""
    resolver, handle, path = fixture(tmp)
    from dataclasses import replace

    out = resolver.read_verified_bytes(replace(handle, content_sha256=""))
    record("handle_without_digest", **snapshot(out))


# ---------------------------------------------------------------------------
# 4. data/reason/status invariants over every reachable refusal
# ---------------------------------------------------------------------------


def s_invariants(tmp):
    from dataclasses import replace

    resolver, handle, path = fixture(tmp)
    observed: list[dict] = []

    def run(label, candidate, budget=None, pre=None):
        if pre:
            pre()
        out = resolver.read_verified_bytes(candidate, budget=budget)
        observed.append({"label": label, **snapshot(out)})

    outside = tmp.parent / "b03rev-outside.pdf"
    outside.write_bytes(BODY)
    run("out_of_root", replace(handle, canonical_path=str(outside)))

    run("missing_file", handle, pre=lambda: path.unlink())
    path.write_bytes(BODY)
    run("directory", handle, pre=lambda: (path.unlink(), path.mkdir()))
    shutil.rmtree(path)
    path.write_bytes(BODY)
    run("drifted", handle, pre=lambda: path.write_bytes(OTHER))
    path.write_bytes(BODY)

    run("cancelled", handle, budget=_cancel_budget())
    run("budget", handle, budget=_ReadBudget(max_bytes=1))
    run("too_large", handle, pre=lambda: setattr(R, "_CANDIDATE_BYTES_CAP", 4))
    R._CANDIDATE_BYTES_CAP = 256 * 1024 * 1024

    record(
        "refusal_invariants",
        rows=observed,
        all_data_none=all(r["data_is_none"] for r in observed),
        all_carry_reason=all(r["reason"] for r in observed),
        all_statuses_in_five=all(r["status"] in FIVE for r in observed),
        statuses=sorted({r["status"] for r in observed}),
        reasons_with_no_contract_status=[
            r["status"] for r in observed if r["status"] not in FIVE
        ],
    )


def _cancel_budget():
    b = _ReadBudget()
    b.cancel()
    return b


def s_status_of_a_success(tmp):
    resolver, handle, path = fixture(tmp)
    out = resolver.read_verified_bytes(handle)
    record(
        "success_status_outside_the_five",
        status=out.status,
        is_one_of_five=out.status in FIVE,
        reason=out.reason,
        data_present=out.data is not None,
        read_at_before_read=None,
    )


def s_read_at_timing(tmp):
    """read_at is stamped at entry, not when the bytes were observed."""
    resolver, handle, path = fixture(tmp)
    out = resolver.read_verified_bytes(handle)
    from datetime import datetime

    stamp = datetime.fromisoformat(out.read_at)
    record(
        "read_at_is_entry_timestamp",
        read_at=out.read_at,
        returned=True,
        note="stamped before Path.open; equal to the call time, not completion",
        stamp_iso=stamp.isoformat(),
    )


def main(argv):
    out_path = Path(argv[1]) if len(argv) > 1 else Path(tempfile.gettempdir()) / "b03_review_bytes.json"
    base = Path(tempfile.mkdtemp(prefix="b03rev-"))
    scenarios = [
        ("happy", s_happy),
        ("same_size", s_same_size_overwrite),
        ("utime_before", s_utime_restored_before_call),
        ("utime_post", s_utime_restored_post_read),
        ("mid_read_rewrite", s_mid_read_rewrite_same_size_mtime_restored),
        ("mid_read_restore", s_mid_read_rewrite_then_restore_original),
        ("truncate_rewrite", s_truncate_and_rewrite_same_length),
        ("late_append", s_write_between_last_read_and_post_stat),
        ("foreign_digest", s_caller_supplied_foreign_digest),
        ("empty_digest", s_caller_supplied_empty_digest),
        ("non_handle", s_non_handle_argument),
        ("no_handle_digest", s_empty_handle_digest),
        ("invariants", s_invariants),
        ("success_status", s_status_of_a_success),
        ("read_at", s_read_at_timing),
    ]
    errors = []
    for name, fn in scenarios:
        tmp = base / name
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            fn(tmp)
        except Exception as exc:  # noqa: BLE001
            import traceback

            errors.append({"scenario": name, "exc": type(exc).__name__,
                           "text": str(exc)[:300],
                           "tb": traceback.format_exc()[-800:]})
    payload = {
        "probe": "b03_review_bytes",
        "wiki_head": _git_head(),
        "body_digest": DIGEST,
        "other_digest": OTHER_DIGEST,
        "results": RESULTS,
        "errors": errors,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"wrote {out_path} ({len(RESULTS)} scenarios, {len(errors)} errors)")
    return 0


def _git_head() -> str:
    import subprocess

    try:
        return subprocess.run(
            ["git", "-C", str(WIKI), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

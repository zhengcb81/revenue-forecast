"""FC-905-a: producer-event journal reads (append-only trace).

Every artifact INSERT is journaled by the ``trg_artifact_producer_event``
trigger into ``producer_events``.  Consumers derive parser/LLM counts from
this journal — never from the resolution output.  Reads only; the journal is
written exclusively by the trigger.

Complexity ratchet (FC-1204, owner §四十二 裁定一, 2026-09-27): split only;
behaviour unchanged.  FC-1204 freezes this module at complexity 1, i.e. every
top-level function must carry ZERO decision points — so both the event_type
filtering (already in the SQL below) and the absent-row default (``_tally``)
are branch-free expressions rather than ``if``/ternary/``and``/``or``.
"""

from __future__ import annotations

from typing import Any

# An absent ``fetchone`` row tallies 0 — selected by index in ``_tally`` so the
# choice costs no decision point (see ``_tally``).
_ZERO_ROW: Any = (0,)


def _tally(row: Any) -> int:
    """``int(row[0])`` for one journal row; an ABSENT row (``None``) tallies 0.

    ``(row, _ZERO_ROW)[row is None]`` is exactly ``row if row is not None
    else _ZERO_ROW`` — a selection, not a branch — because FC-1204 freezes this
    module at complexity 1 (zero decision points).  Behaviour is identical for
    every input: ``None`` -> 0, a row -> its count, an empty row -> IndexError,
    as before.
    """
    return int((row, _ZERO_ROW)[row is None][0])


def count_producer_events(
    store: Any, document_id: str,
) -> dict[str, int]:
    """Return {'parser_calls': n, 'llm_calls': m} for the document.

    ``store`` must expose ``fetchone(sql, params)`` (CatalogStore-compatible).
    The counts are the journal's event_type tallies — zero means the journal
    exists and recorded no such event (honest), not an absence of evidence.
    """
    parser = store.fetchone(
        "SELECT COUNT(*) AS n FROM producer_events "
        "WHERE document_id=? AND event_type='parser'",
        (document_id,),
    )
    llm = store.fetchone(
        "SELECT COUNT(*) AS n FROM producer_events "
        "WHERE document_id=? AND event_type='llm'",
        (document_id,),
    )
    return {
        "parser_calls": _tally(parser),
        "llm_calls": _tally(llm),
    }

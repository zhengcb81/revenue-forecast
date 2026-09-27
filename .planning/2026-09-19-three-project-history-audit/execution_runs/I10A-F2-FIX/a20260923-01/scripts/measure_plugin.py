"""I10A-F2-FIX pre-freeze flip-surface measurement plugin (observation only).

Loaded via `python -m pytest tests -p measure_plugin` from iso/rf with
PYTHONPATH pointing at this directory.  It wraps
``forecast.segments._optional_series`` IN MEMORY (no product file is edited)
and records every call where an optional driver is ABSENT from driver_ids and
carries NO declared default in MODEL_SPECS[model]["defaults"] — i.e. every
call that currently receives the blanket ``0.0`` fill and will flip to a
clean raise once the fix lands.

Output: JSON list of {test, model, driver, blanket_default} written to
$MEASURE_OUT (default: measure_events.json in cwd).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

_events: list[dict] = []
_current: dict = {"id": None}
_patched: dict = {"done": False}


def pytest_runtest_setup(item) -> None:
    _current["id"] = item.nodeid
    if _patched["done"]:
        return
    import sys

    root = Path(os.environ.get("MEASURE_SCRIPTS", "")) or None
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import forecast.segments as seg
    from model_registry import MODEL_SPECS

    original = seg._optional_series

    def wrapper(driver_ids, driver, parameter_index, years, scenario, model, default=0.0):
        if driver not in driver_ids and driver not in MODEL_SPECS[model].get("defaults", {}):
            _events.append(
                {
                    "test": _current["id"],
                    "model": model,
                    "driver": driver,
                    "blanket_default": default,
                }
            )
        return original(driver_ids, driver, parameter_index, years, scenario, model, default)

    seg._optional_series = wrapper  # type: ignore[assignment]
    _patched["done"] = True


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: ARG001
    out = os.environ.get("MEASURE_OUT", "measure_events.json")
    Path(out).write_text(
        json.dumps(_events, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

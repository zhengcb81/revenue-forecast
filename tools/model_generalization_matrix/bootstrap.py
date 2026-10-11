"""Load the real native engine modules for the generalization matrix.

The tool never re-implements a model.  It imports the shipped ``scripts/``
interfaces and hands them to :class:`native.NativeEngine`.  ``sys.path`` is
arranged so the same imports the test-suite uses resolve identically here.
No network, no source DB, no third-party packages.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace


def repo_root() -> Path:
    # tools/model_generalization_matrix/bootstrap.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2]


def load_runtime() -> SimpleNamespace:
    root = repo_root()
    for entry in (root / "scripts", root / "tests", root):
        p = str(entry)
        if p not in sys.path:
            sys.path.insert(0, p)

    from revenue_core import run_forecast  # noqa: E402
    from research.input_quantities import convert_input_quantity  # noqa: E402
    from research_support_diagnostics import build_support_diagnostics  # noqa: E402
    from contracts.period_flow import period_flow_months  # noqa: E402

    return SimpleNamespace(
        run_forecast=run_forecast,
        convert_input_quantity=convert_input_quantity,
        build_support_diagnostics=build_support_diagnostics,
        period_flow_months=period_flow_months,
        root=root,
    )

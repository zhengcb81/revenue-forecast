"""Compose RF's source-tree runtime for the published direct tool scripts."""

from pathlib import Path
import sys

# These tools also run before installation from a checkout. One composition
# point owns the existing scripts directory entry until package migration.
_SCRIPTS = str(Path(__file__).resolve().parents[1] / "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from rf_cli_feedback import (  # noqa: E402
    DiagnosticParser as DiagnosticParser,
    Invocation as Invocation,
    exit_cli as exit_cli,
    observed_entry as observed_entry,
)
from rf_local_diagnostics import (  # noqa: E402
    child_traceback_facts as child_traceback_facts,
    record_local_error as record_local_error,
    traceback_facts as traceback_facts,
)

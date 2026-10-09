"""Research checks use real event dates; information cutoff belongs to sources."""
from copy import deepcopy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from revenue_core import ForecastInputError, run_forecast  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def test_native_forecast_keeps_actual_management_checks_after_information_cutoff():
    data = forecast_document()
    for record in data["management_communication_coverage"]:
        record["checked_date"] = "2026-07-13"
    result = run_forecast(data)
    records = result["management_target_coverage"]["communications"]
    assert all(record["checked_date"] == "2026-07-13" for record in records)
    assert data["as_of_date"] == "2026-07-12"


def test_management_check_cannot_precede_its_actual_source_capture():
    data = forecast_document()
    for record in data["management_communication_coverage"]:
        if record.get("source_ids"):
            record["checked_date"] = "2026-06-30"
    with pytest.raises(ForecastInputError, match="source_clock_conflict"):
        run_forecast(data)


def test_late_check_does_not_admit_future_published_source():
    data = deepcopy(forecast_document())
    for record in data["management_communication_coverage"]:
        record["checked_date"] = "2026-07-13"
    data["sources"][0]["published_date"] = "2026-07-13"
    with pytest.raises(ForecastInputError, match="future information|publication_after_asof|outside as_of"):
        run_forecast(data)


@pytest.mark.parametrize("bad_date", [None, "2026-02-30", "Oct 9", 20261009])
def test_management_check_still_requires_a_real_iso_date(bad_date):
    data = forecast_document()
    data["management_communication_coverage"][0]["checked_date"] = bad_date
    with pytest.raises(ForecastInputError, match="checked_date"):
        run_forecast(data)

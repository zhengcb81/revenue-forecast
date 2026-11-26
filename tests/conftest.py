"""Keep owner outputs from pytest and its CLI children in disposable state."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolate_owner_state(tmp_path_factory):
    registry = tmp_path_factory.mktemp("publication-registry")
    feedback = tmp_path_factory.mktemp("feedback-state")
    with pytest.MonkeyPatch.context() as environment:
        environment.setenv("REVENUE_PUBLICATION_REGISTRY", str(registry))
        environment.setenv("LOCALAPPDATA", str(feedback))
        environment.setenv("XDG_STATE_HOME", str(feedback))
        for name in (
            "RESEARCH_FEEDBACK_DIR", "RESEARCH_FEEDBACK_OUT", "RESEARCH_FEEDBACK_HOSTS",
            "RESEARCH_FEEDBACK_RUN_ID", "RESEARCH_FEEDBACK_ATTEMPT_ID", "RESEARCH_FEEDBACK_PROCESS_STEP_ID",
        ):
            environment.delenv(name, raising=False)
        yield

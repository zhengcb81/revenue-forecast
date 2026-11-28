"""Keep repository-wide pytest and its CLI children in disposable owner state."""

from __future__ import annotations

import os

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



@pytest.fixture
def directory_link():
    """Make a real directory link in a disposable test tree on either OS."""
    def create(link, target):
        if os.name != "nt":
            link.symlink_to(target, target_is_directory=True)
            return

        # CPython exposes its Win32 junction primitive. The tests require a real
        # reparse point without shell startup, Developer Mode or admin privileges.
        from _winapi import CreateJunction

        CreateJunction(str(target.resolve(strict=True)), str(link))
    return create

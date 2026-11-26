"""The system and sandbox state required by offline RF CLI subprocesses."""

import os


_TEST_ENV = frozenset({
    "SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "COMSPEC", "TEMP", "TMP",
    "USERPROFILE", "APPDATA", "LOCALAPPDATA", "HOMEDRIVE", "HOMEPATH",
    "XDG_STATE_HOME", "REVENUE_PUBLICATION_REGISTRY",
})


def isolated_rf_subprocess_env() -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if key.upper() in _TEST_ENV}
    environment.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
    return environment

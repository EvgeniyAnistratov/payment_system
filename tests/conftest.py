"""Load the test environment before the application reads settings.

``app.main`` calls ``load_dotenv()`` without overriding existing variables,
and settings are read at import time. Values from ``.env.test`` are applied
first so e2e tests never talk to the development database.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env.test"


def _load_test_env() -> None:
    if not ENV_FILE.is_file():
        raise RuntimeError(f"Test environment file is missing: {ENV_FILE}")

    from dotenv import dotenv_values

    for key, value in dotenv_values(ENV_FILE).items():
        if value is not None:
            os.environ[key] = value


_load_test_env()

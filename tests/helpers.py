"""Shared test helpers: put the skill's scripts/ on sys.path and load fixtures."""

import contextlib
import json
import sys
import tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "skills" / "content-ideas" / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def load_fixture(name):
    """Load a JSON fixture by filename (with or without .json suffix)."""
    if not name.endswith(".json"):
        name += ".json"
    return json.loads((FIXTURES_DIR / name).read_text())


@contextlib.contextmanager
def tmp_env_file(contents):
    """Write `contents` to a temp .env file, yield its path, clean up after."""
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
        f.write(contents)
        path = f.name
    try:
        yield path
    finally:
        Path(path).unlink(missing_ok=True)

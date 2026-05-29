"""API key loading and persistent-storage paths.

The API key comes from an environment variable or the .env file (env wins).
The persistent base dir (brand/ + research/) is resolved by `content_home()`.
"""

import os
from pathlib import Path

ENV_PATH = Path.home() / ".config" / "content" / ".env"
KEY_NAME = "SCRAPECREATORS_API_KEY"
CONTENT_HOME_VAR = "CONTENT_HOME"
DEFAULT_CONTENT_HOME = Path.home() / "Documents" / "Content"


def content_home():
    """Resolve the persistent base dir holding brand/ and research/.

    Honors the CONTENT_HOME env var; defaults to ~/Documents/Content. This is
    deliberately NOT the current working directory: the skill is invoked from
    anywhere and runs daily, so brand/ (the user's identity) and research/ (the
    dated history that feeds taste memory) must be found again on the next run
    regardless of where the terminal happens to be.
    """
    override = os.environ.get(CONTENT_HOME_VAR, "").strip()
    return Path(override).expanduser() if override else DEFAULT_CONTENT_HOME


def load_api_key(env_path=ENV_PATH):
    """Return the ScrapeCreators API key from the env var or .env file ('' if none)."""
    api_key = os.environ.get(KEY_NAME, "")
    if api_key:
        return api_key
    if env_path and Path(env_path).exists():
        for line in Path(env_path).read_text().splitlines():
            if line.startswith(f"{KEY_NAME}="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return ""

"""API key loading and persistent-storage paths.

Two persistent-storage concepts:

- ``content_home()`` — the per-run base dir holding ``brand/`` and ``research/``.
  In single-project mode this is the install root directly. In multi-project
  mode the caller sets ``CONTENT_HOME`` to the per-project subdir
  (``<install-root>/projects/<slug>/``) before invoking the scripts.

- ``content_ideas_home()`` — the install root, common to single- AND
  multi-project mode. This is what setup writes during first-run
  ("where should content-ideas store your files?"). Persisted in
  ``~/.config/content/.env`` as ``CONTENT_IDEAS_HOME=<path>`` next to the
  API key, so the choice survives across shells and sessions without
  modifying the user's rc files.

The API key comes from an environment variable or the .env file (env wins).
"""

import os
from pathlib import Path

ENV_PATH = Path.home() / ".config" / "content" / ".env"
KEY_NAME = "SCRAPECREATORS_API_KEY"
CONTENT_HOME_VAR = "CONTENT_HOME"
CONTENT_IDEAS_HOME_VAR = "CONTENT_IDEAS_HOME"
DEFAULT_CONTENT_HOME = Path.home() / "Documents" / "Content"


def _read_env_file_value(name, env_path=ENV_PATH):
    """Return the value of `name` from the .env file, or '' if absent/missing file."""
    if not env_path or not Path(env_path).exists():
        return ""
    for line in Path(env_path).read_text().splitlines():
        if line.startswith(f"{name}="):
            return line.split("=", 1)[1].strip().strip("'\"")
    return ""


def content_ideas_home(env_path=ENV_PATH):
    """Resolve the install root — the dir containing brand/ (single-project) or projects/<slug>/ (multi-project).

    Resolution order:
      1. ``CONTENT_IDEAS_HOME`` env var
      2. ``CONTENT_IDEAS_HOME=`` line in ``~/.config/content/.env``
      3. Default: ``~/Documents/Content``

    Honors ``~`` expansion. First-run setup writes the chosen path to the
    .env file (option 2) so the choice persists.
    """
    override = os.environ.get(CONTENT_IDEAS_HOME_VAR, "").strip()
    if not override:
        override = _read_env_file_value(CONTENT_IDEAS_HOME_VAR, env_path)
    return Path(override).expanduser() if override else DEFAULT_CONTENT_HOME


def content_home():
    """Resolve the per-run base dir holding brand/ and research/.

    Honors the CONTENT_HOME env var (set per-invocation in multi-project
    mode); otherwise falls back to ``content_ideas_home()`` (single-project
    mode reads/writes directly under the install root). This is deliberately
    NOT the current working directory: the skill is invoked from anywhere and
    runs daily, so brand/ (the user's identity) and research/ (the dated
    history that feeds taste memory) must be found again on the next run
    regardless of where the terminal happens to be.
    """
    override = os.environ.get(CONTENT_HOME_VAR, "").strip()
    if override:
        return Path(override).expanduser()
    return content_ideas_home()


def load_api_key(env_path=ENV_PATH):
    """Return the ScrapeCreators API key from the env var or .env file ('' if none)."""
    api_key = os.environ.get(KEY_NAME, "")
    if api_key:
        return api_key
    return _read_env_file_value(KEY_NAME, env_path)

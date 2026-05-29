#!/usr/bin/env bash
# SessionStart hook for content-ideas — one-line status so users know what's wired up.
# Silent on the ready state to avoid spam; points at /content-ideas setup otherwise.
set -euo pipefail

CONFIG_FILE="$HOME/.config/content/.env"

# Warn if the secrets file has loose permissions.
if [[ -f "$CONFIG_FILE" ]]; then
  perms=$(stat -c '%a' "$CONFIG_FILE" 2>/dev/null || stat -f '%Lp' "$CONFIG_FILE" 2>/dev/null || echo "")
  if [[ -n "$perms" && "$perms" != "600" && "$perms" != "400" ]]; then
    echo "content-ideas: WARNING — $CONFIG_FILE has permissions $perms (should be 600)."
    echo "  Fix: chmod 600 $CONFIG_FILE"
  fi
fi

# Read a key from the env first, then the config file, without exporting it.
read_key() {
  local name="$1"
  if [[ -n "${!name:-}" ]]; then
    echo "${!name}"
    return
  fi
  if [[ -f "$CONFIG_FILE" ]]; then
    awk -F= -v k="$name" '
      /^[[:space:]]*#/ { next }
      $1 == k {
        sub(/^[[:space:]]*/, "", $2); sub(/[[:space:]]*$/, "", $2);
        gsub(/^["'\'']|["'\'']$/, "", $2);
        print $2; exit
      }
    ' "$CONFIG_FILE"
  fi
}

HAS_KEY="$(read_key SCRAPECREATORS_API_KEY)"
SETUP_COMPLETE="$(read_key SETUP_COMPLETE)"

# Fully configured → silent. Claude surfaces status on demand during a run.
if [[ "$SETUP_COMPLETE" == "true" && -n "$HAS_KEY" ]]; then
  exit 0
fi

# First-run / partially-configured → one-line hint.
if [[ -z "$HAS_KEY" ]]; then
  echo "content-ideas: needs a ScrapeCreators API key. Run \`/content-ideas\` once — setup stores it in ~/.config/content/.env (100 free calls, no card)."
else
  echo "content-ideas: ready."
fi

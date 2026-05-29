#!/usr/bin/env python3
"""Generate and serve the For You feed page.

Reads a run directory containing `feed-data.json`, embeds it (plus any existing
`feedback.json`) into the For You template, and either serves it on a tiny HTTP
server (regenerating on each load, capturing reactions to feedback.json) or
writes a self-contained `for-you.html` with `--static`.

Mirrors skill-creator's eval-viewer/generate_review.py: embed-into-template +
serve-or-static, stdlib only.

Usage:
    python3 generate_feed.py <run-dir>                 # serve + capture feedback
    python3 generate_feed.py <run-dir> --static        # write run-dir/for-you.html
    python3 generate_feed.py <run-dir> --static out.html
    python3 generate_feed.py <run-dir> --feed path/to/feed-data.json --port 3119
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from lib.env import content_home  # noqa: E402

DEFAULT_TEMPLATE = Path(__file__).parent.parent / "assets" / "for-you-template.html"
PLACEHOLDER = "/*__EMBEDDED_DATA__*/"
DEFAULT_PORT = 3119


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_feed(feed_path):
    """Load feed-data.json. Returns the parsed object or None."""
    if feed_path.exists():
        try:
            return json.loads(feed_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not read {feed_path}: {e}", file=sys.stderr)
    return None


def load_feedback_state(feedback_path):
    """Build an item_id -> review map from feedback.json (for prepopulation)."""
    state = {}
    if feedback_path.exists():
        try:
            data = json.loads(feedback_path.read_text())
            for r in data.get("reviews", []):
                item_id = r.get("item_id")
                if item_id:
                    state[item_id] = r
        except (json.JSONDecodeError, OSError):
            pass
    return state


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(feed, feedback_state, mode, template_path=DEFAULT_TEMPLATE):
    """Embed feed + feedback config into the template, returning HTML text."""
    template = template_path.read_text()
    embedded = (
        f"const FEED_DATA = {json.dumps(feed)};\n"
        f"const FEEDBACK_MODE = {json.dumps(mode)};\n"
        f"const FEEDBACK_STATE = {json.dumps(feedback_state)};"
    )
    return template.replace(PLACEHOLDER, embedded)


# ---------------------------------------------------------------------------
# HTTP server (stdlib only)
# ---------------------------------------------------------------------------

def _kill_port(port):
    """Best-effort kill of any process already listening on `port`."""
    try:
        result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True, timeout=5)
        for pid_str in result.stdout.strip().split("\n"):
            if pid_str.strip():
                try:
                    os.kill(int(pid_str.strip()), signal.SIGTERM)
                except (ProcessLookupError, ValueError):
                    pass
        if result.stdout.strip():
            time.sleep(0.5)
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        print("Note: lsof not found, cannot check if port is in use", file=sys.stderr)


class FeedHandler(BaseHTTPRequestHandler):
    """Serves the feed HTML and persists reactions to feedback.json.

    The page is regenerated on each load so re-running the scraper (which
    rewrites feed-data.json) shows up on refresh without a server restart.
    """

    def __init__(self, feed_path, feedback_path, *args, **kwargs):
        self.feed_path = feed_path
        self.feedback_path = feedback_path
        super().__init__(*args, **kwargs)

    def _send(self, code, body, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            feed = load_feed(self.feed_path)
            state = load_feedback_state(self.feedback_path)
            html = generate_html(feed, state, "server").encode("utf-8")
            self._send(200, html, "text/html; charset=utf-8")
        elif self.path == "/api/feedback":
            data = self.feedback_path.read_bytes() if self.feedback_path.exists() else b"{}"
            self._send(200, data)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/feedback":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                if not isinstance(data, dict) or "reviews" not in data:
                    raise ValueError("Expected JSON object with 'reviews' key")
                self.feedback_path.write_text(json.dumps(data, indent=2) + "\n")
                self._send(200, b'{"ok":true}')
            except (json.JSONDecodeError, OSError, ValueError) as e:
                self._send(500, json.dumps({"error": str(e)}).encode())
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate/serve the For You feed page")
    parser.add_argument("run_dir", type=Path, help="Run directory (contains feed-data.json)")
    parser.add_argument("--feed", type=Path, default=None, help="Path to feed-data.json (default: <run-dir>/feed-data.json)")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Template HTML path")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT, help=f"Server port (default {DEFAULT_PORT})")
    parser.add_argument("--static", "-s", nargs="?", const="", default=None,
                        help="Write a self-contained HTML instead of serving. "
                             "Optional path; defaults to <run-dir>/for-you.html")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser")
    args = parser.parse_args(argv)

    # A relative run-dir is resolved under CONTENT_HOME, not the cwd, so the
    # feed lands beside the brand/ and research/ the rest of the skill uses.
    run_dir = args.run_dir
    if not run_dir.is_absolute():
        run_dir = content_home() / run_dir
    run_dir = run_dir.resolve()
    feed_path = (args.feed or run_dir / "feed-data.json").resolve()
    feedback_path = run_dir / "feedback.json"

    if not feed_path.exists():
        print(f"Error: feed data not found at {feed_path}", file=sys.stderr)
        return 1

    # Static mode: write a standalone file (feedback downloads as a file in-browser).
    if args.static is not None:
        out = Path(args.static).resolve() if args.static else run_dir / "for-you.html"
        feed = load_feed(feed_path)
        state = load_feedback_state(feedback_path)
        html = generate_html(feed, state, "static", args.template)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        print(f"\n  For You page written to: {out}\n")
        return 0

    # Server mode.
    port = args.port
    _kill_port(port)
    handler = partial(FeedHandler, feed_path, feedback_path)
    try:
        server = HTTPServer(("127.0.0.1", port), handler)
    except OSError:
        server = HTTPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]

    url = f"http://localhost:{port}"
    print("\n  For You Feed")
    print("  ─────────────────────────────────")
    print(f"  URL:       {url}")
    print(f"  Feed:      {feed_path}")
    print(f"  Feedback:  {feedback_path}")
    print("\n  Press Ctrl+C to stop.\n")

    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""HTTP layer: retrying GET and the ScrapeCreators query helper.

Kept dependency-free (urllib) so the runtime needs no third-party packages.
"""

import json
import sys
import time
import urllib.error
import urllib.request

SC_BASE = "https://api.scrapecreators.com"
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def request(url, headers, retries=MAX_RETRIES):
    """GET request with retry. Returns parsed JSON or None.

    Retries on 429 (with exponential backoff) and transient network errors.
    Gives up immediately on other 4xx responses.
    """
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 429:
                sys.stderr.write(f"[scrape] HTTP {e.code} for {url}\n")
                return None
            if attempt < retries - 1:
                delay = RETRY_DELAY * (2 ** attempt) if e.code == 429 else RETRY_DELAY
                time.sleep(delay)
        except (urllib.error.URLError, OSError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
    return None


def sc_get(path, params, api_key):
    """ScrapeCreators API GET. Returns parsed JSON or None."""
    qs = "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params.items())
    url = f"{SC_BASE}{path}?{qs}"
    headers = {"x-api-key": api_key, "User-Agent": "content/1.0"}
    return request(url, headers)

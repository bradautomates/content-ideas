"""Progress logging to stderr so it doesn't corrupt JSON on stdout."""

import sys


def log(msg):
    """Write a progress line to stderr and flush."""
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

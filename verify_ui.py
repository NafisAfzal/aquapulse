"""Compatibility entry point for the shared Playwright UI checks.

Usage: python verify_ui.py [http://127.0.0.1:8000]
Requires Node.js and the Playwright JS package; see docs/UI_HANDOVER.md.
"""
from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    raise SystemExit(subprocess.call(
        ["node", str(root / "scripts" / "verify_ui.cjs"), *sys.argv[1:]], cwd=root,
    ))

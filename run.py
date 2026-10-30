"""AquaPulse root launcher — works without any environment setup.

Usage:
    python run.py                # launch on http://127.0.0.1:8000
    python run.py --port 9000    # custom port
    python run.py --no-browser   # do not open a browser tab
    python run.py --reload       # auto-reload for development

This file inserts ``src/`` into ``sys.path`` itself, so it works even if the
package has not been installed into the virtual environment.
"""
from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Launch the AquaPulse dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="bind port (default 8000)")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser")
    parser.add_argument("--reload", action="store_true", help="enable auto-reload")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        import uvicorn
    except ImportError:  # pragma: no cover - only on a broken environment
        print('Missing dependencies. Run: pip install -e ".[dev]"', file=sys.stderr)
        return 1

    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    print(f"\n  AquaPulse v1.0.0  ->  {url}")
    print("  Press Ctrl+C to stop.\n")
    uvicorn.run(
        "aquapulse.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

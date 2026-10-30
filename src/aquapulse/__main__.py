"""Run AquaPulse with ``python -m aquapulse``.

Usage:
    python -m aquapulse [--port 8000] [--no-browser] [--reload]
"""
from __future__ import annotations

import argparse
import threading
import webbrowser

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the AquaPulse dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    print(f"\n  AquaPulse v1.0.0  ->  {url}\n  Press Ctrl+C to stop.\n")
    uvicorn.run(
        "aquapulse.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()

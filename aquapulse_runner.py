"""Compatibility alias for the AquaPulse launcher.

Equivalent to ``python run.py``. Imported lazily so it also works when the
package is installed (in which case ``python -m aquapulse`` is preferred).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())

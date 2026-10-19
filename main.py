from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from torretray_pi.app import run


def _parse_test_time(value: str) -> datetime:
    """Accept an ISO date or datetime for the tray app clock override."""
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.combine(date.fromisoformat(value), datetime.min.time())
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "Expected YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS for --test-time."
            ) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the TorreTray tray app.")
    parser.add_argument(
        "--test-time",
        "--testtime",
        dest="test_time",
        type=_parse_test_time,
        help="Override the app clock using ISO date or datetime.",
    )
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    raise SystemExit(run(test_now_override=args.test_time))
